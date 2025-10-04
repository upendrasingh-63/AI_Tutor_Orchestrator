# run_evaluation.py

import asyncio
from orchestrator.graph import select_tool_node, GraphState
from tests.evaluation_dataset import EVALUATION_DATASET

async def run_evaluation():
    """
    Runs the tool selection node against the evaluation dataset and reports accuracy.
    """
    print("--- 🚀 STARTING TOOL SELECTION EVALUATION ---")

    correct_predictions = 0
    incorrect_predictions = []

    for i, item in enumerate(EVALUATION_DATASET):
        message = item["message"]
        expected_tool = item["expected_tool"]

        print(f"\n🧪 Running Test Case #{i+1}...")
        print(f"   Message: '{message}'")
        print(f"   Expected Tool: {expected_tool}")

        # Create the initial state for the node
        initial_state = GraphState(
            student_message=message,
            chat_history=[],
            user_info={},
            selected_tool="",
            extracted_parameters={},
            api_response={},
            final_answer=""
        )

        # Run the tool selection node
        try:
            updated_state = select_tool_node(initial_state)
            actual_tool = updated_state["selected_tool"]

            print(f"   Actual Tool:   {actual_tool}")

            if actual_tool == expected_tool:
                print("   Result: ✅ Correct")
                correct_predictions += 1
            else:
                print(f"   Result: ❌ Incorrect")
                incorrect_predictions.append({
                    "id": i+1,
                    "message": message,
                    "expected": expected_tool,
                    "actual": actual_tool
                })
        except Exception as e:
            print(f"   Result: 🚨 Error: {e}")
            incorrect_predictions.append({
                "id": i+1,
                "message": message,
                "expected": expected_tool,
                "actual": f"ERROR - {e}"
            })


    # --- Generate Final Report ---
    total_tests = len(EVALUATION_DATASET)
    accuracy = (correct_predictions / total_tests) * 100

    print("\n\n--- 📊 EVALUATION REPORT ---")
    print(f"Total Test Cases: {total_tests}")
    print(f"Correct Predictions: {correct_predictions}")
    print(f"Accuracy: {accuracy:.2f}%")

    if incorrect_predictions:
        print("\n--- ❌ Failed Test Cases ---")
        for failed in incorrect_predictions:
            print(f"  - Case #{failed['id']}: '{failed['message']}'")
            print(f"    Expected: {failed['expected']}, Got: {failed['actual']}")

    print("\n--- ✅ EVALUATION COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(run_evaluation())