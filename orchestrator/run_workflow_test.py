from orchestrator.agent import (
    GraphState, 
    select_tool_node, 
    extract_parameters_node, 
    tool_orchestrator_node, 
    response_normalizer_node
)
from orchestrator.state_manager import get_student_state, update_student_chat_history

def run_full_workflow():
    """
    Runs a full end-to-end test of the orchestrator workflow, simulating a real user interaction.
    """
    print("--- 🚀 STARTING FULL WORKFLOW TEST ---")
    
    # --- Step 1: A new request arrives from a student ---
    user_id = "student123"
    test_message = "Okay, great. Now can you summarize the main causes of World War II for me?"

    # --- Step 2: Fetch the student's state (long-term memory) from the State Manager ---
    print(f"\n--- FETCHING STATE for user: {user_id} ---")
    student_state = get_student_state(user_id)
    print(f"Retrieved chat history with {len(student_state['chat_history'])} messages.")

    # --- Step 3: Populate the initial state for the agent's current task ---
    initial_state = GraphState(
        student_message=test_message,
        chat_history=student_state["chat_history"],
        user_info=student_state["user_info"],
        selected_tool="", 
        extracted_parameters={}, 
        api_response={}, 
        final_answer=""
    )
    
    # --- Step 4: Run the agent's "thought process" by calling each node in sequence ---
    state_after_selection = select_tool_node(initial_state)
    state_after_extraction = extract_parameters_node(state_after_selection)
    state_after_tool_call = tool_orchestrator_node(state_after_extraction)
    final_state = response_normalizer_node(state_after_tool_call)
    
    # --- Step 5: Update the State Manager with the new conversation turn ---
    print("\n--- 💾 SAVING STATE ---")
    new_messages_to_save = [
        {"role": "user", "content": test_message},
        {"role": "assistant", "content": final_state["final_answer"]}
    ]
    update_student_chat_history(user_id, new_messages_to_save)
    print("Conversation history has been updated.")
    
    # --- Step 6: Present the final result ---
    print("\n--- ✅ FULL WORKFLOW TEST COMPLETE ---")
    print("\nFinal Human-Readable Answer to be shown to the student:")
    print("---------------------------------------------------------")
    print(final_state['final_answer'])
    print("---------------------------------------------------------")


if __name__ == "__main__":
    run_full_workflow()

