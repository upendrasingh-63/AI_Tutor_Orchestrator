from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
import asyncio

# Import the refactored agent functions designed for the multi-tool workflow
from orchestrator.agent import (
    GraphState,
    select_tools_node,
    extract_parameters_for_tool,
    call_tool_api,
    _format_combined_response
)
from orchestrator.state_manager import get_student_state, update_student_chat_history

router = APIRouter(tags=["Main Application"])

class ChatRequest(BaseModel):
    user_id: str
    message: str

@router.post("/chat")
async def chat_handler(request: ChatRequest = Body(...)):
    """
    This is the main endpoint that runs the full multi-tool orchestrator workflow.
    """
    try:
        print(f"\n--- 🚀 RECEIVED MULTI-TOOL REQUEST for user: {request.user_id} ---")

        # 1. Fetch State & Populate Initial State
        student_state = get_student_state(request.user_id)
        initial_state = GraphState(
            student_message=request.message,
            chat_history=student_state["chat_history"],
            user_info=student_state["user_info"],
            selected_tools=[], tool_api_responses=[], final_answer=""
        )

        # 2. Run Tool Selection to get the plan
        state_after_selection = select_tools_node(initial_state)
        selected_tools = state_after_selection.get("selected_tools", [])

        if not selected_tools:
            # If no tools are selected, provide a default response
            final_answer = "I'm not sure which tool to use for your request. Could you please rephrase?"
            tool_responses = []
        else:
            # 3. --- Orchestration Loop ---
            # Create a list of tasks to run concurrently for efficiency
            tasks = []
            for tool_name in selected_tools:
                # For each tool, we create a task that chains parameter extraction and the API call
                async def tool_task(current_tool_name: str):
                    params = extract_parameters_for_tool(state_after_selection, current_tool_name)
                    response = await call_tool_api(current_tool_name, params)
                    return response
                tasks.append(tool_task(tool_name))

            # Run all tool tasks in parallel
            tool_responses = await asyncio.gather(*tasks)

            # 4. Normalize the combined results into a single answer
            final_answer = _format_combined_response(tool_responses)

        # 5. Save the new conversation turn to memory
        new_messages = [
            {"role": "user", "content": request.message},
            {"role": "assistant", "content": final_answer}
        ]
        update_student_chat_history(request.user_id, new_messages)

        # 6. Return the final, combined answer and the raw data
        return {
            "chat_response": final_answer,
            "tools_used": selected_tools,
            "tool_data": tool_responses
        }

    except Exception as e:
        print(f"--- 🚨 ERROR in workflow: {e} ---")
        # Provide a more detailed error message for debugging
        raise HTTPException(status_code=500, detail=f"An internal error occurred in the AI workflow: {str(e)}")

