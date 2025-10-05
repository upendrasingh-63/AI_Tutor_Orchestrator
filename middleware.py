# middleware.py
import os, json
from typing import Dict, Any
from dotenv import load_dotenv
from tools import call_tool

# Load environment variables
load_dotenv()

# === LLM Setup ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

try:
    from groq import ChatGroq
except ImportError:
    ChatGroq = None

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="gemma2-9b-it",
    temperature=0.1,
    max_tokens=1024
) if GROQ_API_KEY and ChatGroq else None

# Available tools
TOOL_SCHEMAS = ["NoteMaker", "FlashCardGenerator", "ConceptExplainer"]

class Orchestrator:
    def __init__(self):
        self.llm = llm

    def get_best_tool(self, prompt: str) -> Dict[str, Any]:
        """
        Use LLM to select the best tool and generate payload.
        """
        if not self.llm:
            # fallback heuristic
            intent = "NoteMaker"
            text = prompt.lower()
            if "flashcard" in text or "practice" in text or "question" in text:
                intent = "FlashCardGenerator"
            elif "explain" in text or "teach" in text:
                intent = "ConceptExplainer"
            payload = {"topic": prompt[:80], "desired_depth": "basic", "num_questions": 5, "difficulty": "beginner"}
            return {"tool": intent, "payload": payload}

        llm_query = f"""
You are an assistant deciding the best educational tool for a student query.
Available tools: {TOOL_SCHEMAS}

Tool requirements:
- NoteMaker: topic, desired_depth
- FlashCardGenerator: topic, num_questions, difficulty
- ConceptExplainer: topic, desired_depth

Analyze the following prompt and return ONLY JSON in this format:
{{
"tool": "<best tool name from above>",
"payload": {{
    "topic": "<topic extracted from prompt>",
    "desired_depth": "<basic/intermediate/advanced>",
    "num_questions": <number, if applicable>,
    "difficulty": "<difficulty if applicable>"
}}
}}

Student prompt: "{prompt}"
"""
        try:
            res = self.llm.chat(llm_query)
            data = json.loads(res)
            return data
        except Exception:
            # fallback if LLM fails
            payload = {"topic": prompt[:80], "desired_depth": "basic", "num_questions": 5, "difficulty": "beginner"}
            return {"tool": "NoteMaker", "payload": payload}

    def select_and_run(self, prompt: str) -> Dict[str, Any]:
        """
        Select the best tool using LLM and return its response.
        """
        selection = self.get_best_tool(prompt)
        tool = selection["tool"]
        payload = selection.get("payload", {})
        response = call_tool(tool, payload)
        return {
            "chosen_tool": tool,
            "payload": payload,
            "tool_response": response
        }
