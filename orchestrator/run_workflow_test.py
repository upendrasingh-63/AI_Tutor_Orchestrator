
import json
from orchestrator.agent import GraphState, select_tool_node, extract_parameters_node, tool_orchestrator_node
from orchestrator.state_manager import get_student_state, update_student_chat_history

def run_test():
    """
    Runs a full end-to-end test of the orchestrator workflow.
    """
    print("--- 🚀 STARTING FULL WORKFLOW TEST ---")
    
    # Step 1: A new request comes in
    user_id = "student123"
    test_message = "Okay, great. Now can you summarize the main causes of World War II for me?"

    # Step 2: Fetch state
    print(f"\n--- FETCHING STATE for user: {user_id} ---")
    student_state = get_student_state(user_id)
    print(f"Retrieved chat history with {len(student_state['chat_history'])} messages.")

    # Step 3: Populate initial state
    initial_state = GraphState(
        student_message=test_message,
        chat_history=student_state["chat_history"],
        user_info=student_state["user_info"],
        selected_tool="", extracted_parameters={}, api_response={}, final_answer=""
    )
    
    # Step 4: Run the graph sequence node by node
    state_after_selection = select_tool_node(initial_state)
    state_after_extraction = extract_parameters_node(state_after_selection)
    final_state = tool_orchestrator_node(state_after_extraction)
    
    # (Placeholder for the final Response Normalizer node)
    final_state["final_answer"] = "This is a mock response about WWII."

    # Step 5: Update the state manager
    new_messages_to_save = [
        {"role": "user", "content": test_message},
        {"role": "assistant", "content": final_state["final_answer"]}
    ]
    update_student_chat_history(user_id, new_messages_to_save)
    
    print("\n--- ✅ FULL WORKFLOW TEST COMPLETE ---")
    print("\nFinal API Response from Mock Tool:")
    print(json.dumps(final_state['api_response'], indent=2))

if __name__ == "__main__":
    run_test()

