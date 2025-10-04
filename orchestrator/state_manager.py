
from .schemas import UserInfo, ChatMessage

# This dictionary acts as our mock database for the hackathon.
# The keys are user_id's.
mock_student_db = {
    "student123": {
        "user_info": UserInfo(
            user_id="student123",
            name="Harry",
            grade_level="10",
            learning_style_summary="Prefers outlines and structured notes. Visual learner.",
            emotional_state_summary="Focused and attentive",
            mastery_level_summary="Level 7: Proficient"
        ),
        "chat_history": [
            ChatMessage(role="user", content="Tell me about the causes of WWI."),
            ChatMessage(role="assistant", content="Certainly. The main causes were Militarism, Alliances, Imperialism, and Nationalism.")
        ]
    },
    "student456": {
        "user_info": UserInfo(
            user_id="student456",
            name="Ginny",
            grade_level="9",
            learning_style_summary="Prefers hands-on practice.",
            emotional_state_summary="Anxious about the upcoming test.",
            mastery_level_summary="Level 2: Building foundational knowledge."
        ),
        "chat_history": []
    }
}

def get_student_state(user_id: str) -> dict:
    """
    Retrieves a student's profile and chat history from the mock database.
    """
    student_data = mock_student_db.get(user_id)
    if not student_data:
        raise ValueError(f"No student found with user_id: {user_id}")
    
    # Return the data in a dictionary format that can be used to build the GraphState
    return {
        "user_info": student_data["user_info"].model_dump(),
        "chat_history": [msg.model_dump() for msg in student_data["chat_history"]]
    }

def update_student_chat_history(user_id: str, new_messages: list):
    """
    Updates the chat history for a student in the mock database.
    """
    if user_id in mock_student_db:
        mock_student_db[user_id]["chat_history"].extend(
            [ChatMessage(**msg) for msg in new_messages]
        )
        print(f"\n--- 💾 STATE MANAGER: History updated for {user_id} ---")
