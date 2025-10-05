# tools.py
from typing import Dict, Any

def call_tool(tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name == "NoteMaker":
        return note_maker(payload)
    if tool_name == "FlashCardGenerator":
        return flashcard_generator(payload)
    if tool_name == "ConceptExplainer":
        return concept_explainer(payload)
    return {"error": "Unknown tool"}

def note_maker(payload: Dict[str, Any]) -> Dict[str, Any]:
    topic = payload.get("topic", "General Topic")
    depth = payload.get("desired_depth", "basic")
    notes = f"📘 Notes on **{topic}** ({depth} level)\n- Definition\n- Key Concepts\n- Examples\n- Summary"
    return {"notes": notes}

def flashcard_generator(payload: Dict[str, Any]) -> Dict[str, Any]:
    topic = payload.get("topic", "Topic")
    num = int(payload.get("num_questions", 5))
    cards = []
    for i in range(1, num + 1):
        q = f"What is concept {i} about {topic}?"
        a = f"Explanation {i} for {topic}."
        cards.append({"q": q, "a": a})
    return {"flashcards": cards}

def concept_explainer(payload: Dict[str, Any]) -> Dict[str, Any]:
    topic = payload.get("topic", "Topic")
    depth = payload.get("desired_depth", "basic")
    explanation = f"Detailed explanation of {topic} at {depth} level."
    return {"explanation": explanation}
