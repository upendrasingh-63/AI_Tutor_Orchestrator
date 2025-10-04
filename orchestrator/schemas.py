from pydantic import BaseModel, Field
from typing import Literal

# --- Common User Info Schema ---
# This object represents the student's profile and is required by all tools.
class UserInfo(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the student",min_length=1)
    name: str = Field(..., description="Student's full name",min_length=1)
    grade_level: str = Field(..., description="Student's current grade level")
    learning_style_summary: str = Field(..., description="Summary of student's preferred learning style",min_length=1,max_length=1000)
    emotional_state_summary: str = Field(..., description="Current emotional state of the student, e.g., 'Focused', 'Anxious'",min_length=1,max_length=1000)
    mastery_level_summary: str = Field(..., description="Current mastery level description, e.g., 'Level 2: Beginner'",min_length=1,max_length=1000)

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(..., min_length=1)
# --- Schemas for Each Tool's Input ---

class NoteMakerInput(BaseModel):
    """Input schema for the NoteMaker tool."""
    topic: str = Field(..., description="The main topic for note generation, extracted from the conversation.")
    subject: str = Field(..., description="The academic subject area, inferred from the topic and conversation (e.g., 'History' for 'World War II').")
    note_taking_style: Literal["outline", "bullet_points", "narrative", "structured"] = Field(default="structured", description="The preferred format for the notes. Infer from learning style or default to 'structured'.")
    include_examples: bool = Field(default=True, description="Whether to include practical examples in the notes. Set to true if learning style is 'Visual'.")
    include_analogies: bool = Field(default=False, description="Whether to include explanatory analogies in the notes.")

class FlashcardGeneratorInput(BaseModel):
    """Input schema for the FlashcardGenerator tool."""
    topic: str = Field(..., description="The topic for flashcard generation, extracted from the conversation.")
    subject: str = Field(..., description="The academic subject area, inferred from the topic and conversation.")
    count: int = Field(default=5, description="The number of flashcards to create. Infer from the user's request if possible, otherwise default to 5.", ge=1, le=20)
    difficulty: Literal["easy", "medium", "hard"] = Field(..., description="Difficulty level of the flashcards. Infer from emotional state and mastery level (e.g., 'Anxious' implies 'easy').")
    include_examples: bool = Field(default=True, description="Whether to include practical examples in the notes. Set to true if learning style is 'Visual'.")


class ConceptExplainerInput(BaseModel):
    """Input schema for the ConceptExplainer tool."""
    concept_to_explain: str = Field(..., description="The specific concept to explain, extracted directly from the user's message.")
    current_topic: str = Field(..., description="The broader subject or topic context for the explanation.")
    desired_depth: Literal["basic", "intermediate", "advanced", "comprehensive"] = Field(..., description="The level of detail for the explanation. Infer based on the student's mastery level and grade level.")
