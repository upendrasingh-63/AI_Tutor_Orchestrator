
# This service is the "brain" of the operation. It interacts with the Gemini API.
# It now asks the model to return a LIST of tool calls to support multi-tool execution.

import logging
import json
import google.generativeai as genai
from typing import List

from schemas.tool_schemas import UserInfo, ChatMessage, ToolCallRequest
from tools.tool_definitions import Tool
from utils.exceptions import ParameterExtractionException, ClarificationNeededException
from utils.config import settings

logger = logging.getLogger(__name__)

class GeminiExecutor:
    """
    Uses the Gemini API to select one or more tools and extract their parameters.
    """
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required.")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=settings.GEMINI_MODEL,
            generation_config={"response_mime_type": "application/json"}
        )
        logger.info(f"Gemini model '{settings.GEMINI_MODEL}' configured.")

    def _construct_system_prompt(self, user_info: UserInfo, candidate_tools: List[Tool]) -> str:
        """Constructs the detailed system prompt for the LLM."""
        tool_schemas_json = [tool.schema.model_json_schema() for tool in candidate_tools]
        
        system_prompt = f"""
        You are an expert AI orchestrator for an Autonomous AI Tutor named YoLearn.
        Your task is to analyze a student's query and the conversation context, then select the most appropriate educational tools and extract ALL their required parameters.

        # Student Context:
        - Name: {user_info.name}
        - Grade Level: {user_info.grade_level}
        - Learning Style: {user_info.learning_style_summary}
        - Emotional State: {user_info.emotional_state_summary}
        - Mastery Level: {user_info.mastery_level_summary}

        # Rules:
        1.  Analyze the student's emotional and mastery state to infer missing parameters. For example, if the student is 'Confused' or has a low mastery level, infer 'easy' difficulty or 'basic' depth.
        2.  Your response MUST be a JSON object containing a single key "tool_calls".
        3.  The value of "tool_calls" MUST be a LIST of JSON objects. Each object represents a tool to be called.
        4.  Each object in the list must contain "tool_name" and "parameters", which must strictly match the selected tool's schema.
        5.  If the user's query requires multiple actions (e.g., "explain this and give me flashcards"), add a separate object for each action to the "tool_calls" list.
        6.  If a required parameter is truly missing and cannot be inferred, the list should contain one object:
            {{"tool_name": "clarification_needed", "parameters": {{"missing_info": "Politely ask the user for the specific missing information."}}}}

        # Available Tools and their JSON Schemas:
        {json.dumps(tool_schemas_json, indent=2)}
        """
        return system_prompt

    async def get_tool_calls(self, user_query: str, user_info: UserInfo, chat_history: List[ChatMessage], candidate_tools: List[Tool]) -> List[ToolCallRequest]:
        """
        Makes a single call to the Gemini API to get a list of desired tool calls.
        """
        system_prompt = self._construct_system_prompt(user_info, candidate_tools)
        
        history = [{"role": msg.role, "parts": [msg.content]} for msg in chat_history]
        
        # --- FIX: Ensure all parts of the prompt are in the correct dictionary format ---
        prompt_parts = [
            # The system prompt is formatted as the first user message
            {"role": "user", "parts": [system_prompt]},
            # Add a priming response to set the model in the correct mode
            {"role": "model", "parts": ["Understood. I am ready to act as an expert AI orchestrator and will provide my response in the specified JSON format."]},
            *history,
            {"role": "user", "parts": [f"Here is my latest request: {user_query}"]}
        ]

        logger.debug(f"Sending request to Gemini API. Prompt parts: {json.dumps(prompt_parts, indent=2)}")

        try:
            response = await self.model.generate_content_async(prompt_parts)
            response_text = response.text.strip()
            logger.debug(f"Raw Gemini response: {response_text}")

            response_json = json.loads(response_text)
            tool_calls_data = response_json.get("tool_calls")

            if not isinstance(tool_calls_data, list):
                raise ParameterExtractionException("LLM response did not contain a valid 'tool_calls' list.")
            
            tool_calls = []
            for call_data in tool_calls_data:
                tool_name = call_data.get("tool_name")
                parameters = call_data.get("parameters", {})

                if not tool_name:
                    raise ParameterExtractionException("A tool call was missing a 'tool_name'.")

                if tool_name == "clarification_needed":
                    raise ClarificationNeededException(parameters.get("missing_info", "I need a bit more information."))

                if tool_name not in [tool.name for tool in candidate_tools]:
                    logger.warning(f"LLM selected a tool '{tool_name}' not in candidate list. Ignoring.")
                    continue

                tool_calls.append(ToolCallRequest(tool_name=tool_name, parameters=parameters))
            
            if not tool_calls and tool_calls_data:
                 raise ParameterExtractionException("LLM returned tool calls, but none were valid or in the candidate list.")

            return tool_calls

        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON from Gemini response: {response_text}")
            raise ParameterExtractionException("Failed to get a valid JSON response from the AI model.")
        except Exception as e:
            logger.error(f"An unexpected error occurred with the Gemini API: {e}", exc_info=True)
            raise ParameterExtractionException(f"An error occurred while communicating with the AI model: {e}")

