from fastapi import APIRouter, Body
from orchestrator.schemas import NoteMakerInput, FlashcardGeneratorInput, ConceptExplainerInput
import json

# Create a router to hold all our tool endpoints
router = APIRouter(prefix="/tools")

# Load the example success responses from a simple JSON file or define them here
# For the hackathon, defining them here is fine.
NOTE_MAKER_SUCCESS_RESPONSE = {
    "topic": "World War II", "title": "Key Causes of World War II", "summary": "A summary of the primary factors leading to WWII...",
    "note_sections": [{"title": "Treaty of Versailles", "content": "...", "key_points": ["..."]}, {"title": "Rise of Fascism", "content": "...", "key_points": ["..."]}],
    "key_concepts": ["Appeasement", "Blitzkrieg"], "connections_to_prior_learning": [], "visual_elements": [],
    "practice_suggestions": ["Research the impact of the Great Depression on German politics."], "source_references": [], "note_taking_style": "structured"
}

FLASHCARDS_SUCCESS_RESPONSE = {
    "flashcards": [
        {"title": "Photosynthesis", "question": "What is the formula for photosynthesis?", "answer": "6CO2 + 6H2O → C6H12O6 + 6O2", "example": "Plants use this process to convert light into energy."},
        {"title": "Photosynthesis", "question": "Where does photosynthesis occur?", "answer": "In the chloroplasts of plant cells.", "example": "null"}
    ],
    "topic": "Photosynthesis", "adaptation_details": "Flashcards were generated at a medium difficulty...", "difficulty": "medium"
}

CONCEPT_EXPLAINER_SUCCESS_RESPONSE = {
    "explanation": "The water cycle is the continuous movement of water on, above, and below the surface of the Earth...",
    "examples": ["Rainfall in your city.", "Morning dew on the grass."],
    "related_concepts": ["Evaporation", "Condensation", "Precipitation"],
    "visual_aids": ["A diagram showing the sun heating water..."],
    "practice_questions": ["What is the main driver of the water cycle?"], "source_references": []
}


@router.post("/notemaker", tags=["Mock Tools"])
async def notemaker_tool(data: NoteMakerInput = Body(...)):
    """Mocks the NoteMaker tool. It receives the validated input and returns a pre-defined success response."""
    print(f"\n--- 📞 MOCK API: NoteMaker tool called with valid data ---")
    print(data)
    return NOTE_MAKER_SUCCESS_RESPONSE

@router.post("/flashcards", tags=["Mock Tools"])
async def flashcards_tool(data: FlashcardGeneratorInput = Body(...)):
    """Mocks the Flashcard Generator tool."""
    print(f"\n--- 📞 MOCK API: Flashcards tool called with valid data ---")
    print(data)
    return FLASHCARDS_SUCCESS_RESPONSE

@router.post("/conceptexplainer", tags=["Mock Tools"])
async def concexplainer_tool(data: ConceptExplainerInput = Body(...)):
    """Mocks the Concept Explainer tool."""
    print(f"\n--- 📞 MOCK API: ConceptExplainer tool called with valid data ---")
    print(data)
    return CONCEPT_EXPLAINER_SUCCESS_RESPONSE
