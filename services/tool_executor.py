
# This service acts as a dispatcher. It takes the tool name and parameters from
# the Gemini Executor and calls the actual (mocked) external tool API.
# It handles dynamic dispatching and validation against the tool's Pydantic schema.

import logging
from typing import Dict, Any
from pydantic import ValidationError

from tools.tool_definitions import load_all_tools, Tool
from utils.exceptions import ToolNotFoundException, ToolExecutionException

logger = logging.getLogger(__name__)

class ToolExecutor:
    """
    Executes the specified tool with the given parameters after validation.
    """
    def __init__(self):
        self.tools: Dict[str, Tool] = {tool.name: tool for tool in load_all_tools()}
        logger.info(f"ToolExecutor initialized with tools: {list(self.tools.keys())}")

    async def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finds the tool, validates parameters against its schema, and executes its action.
        """
        if tool_name not in self.tools:
            logger.error(f"Attempted to execute a non-existent tool: {tool_name}")
            raise ToolNotFoundException(f"Tool '{tool_name}' is not a valid or available tool.")

        tool = self.tools[tool_name]

        try:
            # --- Schema Validation ---
            # This is a crucial step. We parse the dictionary of parameters using the
            # tool's specific Pydantic input model. This will raise a ValidationError
            # if any parameters are missing, of the wrong type, or fail validation.
            validated_params = tool.schema.model_validate(parameters)
            logger.debug(f"Parameters for '{tool_name}' validated successfully.")
        except ValidationError as e:
            logger.warning(f"Parameter validation failed for tool '{tool_name}': {e}")
            # We can format the Pydantic error for a more user-friendly message
            error_details = e.errors()
            raise ToolExecutionException(f"Invalid parameters provided for {tool_name}. Details: {error_details}")

        try:
            # --- Tool Execution ---
            # The tool's action is an async function that simulates the API call.
            result = await tool.action(**validated_params.model_dump())
            return result
        except Exception as e:
            logger.error(f"An error occurred while executing tool '{tool_name}': {e}", exc_info=True)
            raise ToolExecutionException(f"An unexpected error occurred while running the {tool_name} tool.")
