
# This file defines the actual educational tools. Each tool has a name, a
# detailed description (for the semantic router), an input schema (Pydantic model),
# and an action function that simulates the tool's execution.

import logging
from typing import List, Callable, Awaitable, Any, Type
from pydantic import BaseModel
import asyncio

from schemas.tool_schemas import NoteMakerInput, FlashcardGeneratorInput, ConceptExplainerInput

logger = logging.getLogger(__name__)

class Tool(BaseModel):
    """A definition for a single educational tool."""
    name: str
    description: str
    schema: Type[BaseModel]
    action: Callable[..., Awaitable[Any]]

    class Config:
        arbitrary_types_allowed = True


# --- Mock Tool Actions ---
# In a real application, these functions would make authenticated API calls
# to external microservices. Here, we simulate that with asyncio.sleep and
# return mock data that matches the expected response format.

async def note_maker_action(**kwargs) -> dict:
    logger.info(f"Executing Note Maker tool with args: {kwargs}")
    await asyncio.sleep(0.5) # Simulate network latency
    topic = kwargs.get("topic", "Unknown Topic")
    return {
        "status": "success",
        "topic": topic,
        "title": f"Comprehensive Notes on {topic}",
        "summary": "These notes cover the key concepts, examples, and main ideas related to the topic.",
        "note_sections": [
            {"title": "Key Concept 1", "content": "Detailed explanation of the first key concept."},
            {"title": "Example", "content": "A practical example illustrating the concept."}
        ]
    }

async def flashcard_generator_action(**kwargs) -> dict:
    logger.info(f"Executing Flashcard Generator tool with args: {kwargs}")
    await asyncio.sleep(0.3) # Simulate network latency
    count = kwargs.get("count", 5)
    return {
        "status": "success",
        "topic": kwargs.get("topic", "Unknown Topic"),
        "flashcards_generated": count,
        "flashcards": [
            {"question": f"What is a key aspect of {kwargs.get('topic')}?", "answer": "This is the answer."}
            for _ in range(count)
        ]
    }

async def concept_explainer_action(**kwargs) -> dict:
    logger.info(f"Executing Concept Explainer tool with args: {kwargs}")
    await asyncio.sleep(0.7) # Simulate network latency
    concept = kwargs.get("concept_to_explain", "the concept")
    return {
        "status": "success",
        "concept": concept,
        "explanation": f"A clear, step-by-step explanation of {concept} tailored to the student's level.",
        "examples": ["Here is a simple example to help you understand."],
        "related_concepts": ["Here is a related concept you might want to learn next."]
    }


# --- Tool Library ---
# A list containing all available tools. This list is imported by other services.
# Adding a new tool is as simple as defining its action and schema, then adding it here.

_tools = [
    Tool(
        name="NoteMakerTool",
        description="Generates structured, detailed notes on a specific academic topic and subject. Ideal for when a student wants to review or create study materials for a lesson.",
        schema=NoteMakerInput,
        action=note_maker_action
    ),
    Tool(
        name="FlashcardGeneratorTool",
        description="Creates a set of flashcards with questions and answers for a given topic. Best for active recall, practice, and memorization of key facts or vocabulary.",
        schema=FlashcardGeneratorInput,
        action=flashcard_generator_action
    ),
    Tool(
        name="ConceptExplainerTool",
        description="Provides a simple, clear explanation of a specific concept, term, or idea. Use this when a student is confused, asks 'what is...?', or needs a foundational understanding of a topic.",
        schema=ConceptExplainerInput,
        action=concept_explainer_action
    ),
    # To add more tools (up to 80+), simply append them to this list.
    # For example:
    # Tool(
    #     name="QuizGeneratorTool",
    #     description="Generates a multiple-choice quiz on a topic with a specified difficulty.",
    #     schema=QuizGeneratorInput,
    #     action=quiz_generator_action
    # ),
]

def load_all_tools() -> List[Tool]:
    """Returns a list of all defined tools."""
    return _tools
