
# --- API Configuration ---
BASE_API_URL = "http://127.0.0.1:8000/tools"

# --- Tool Routing & Registration ---

# The scalable router dictionary for API calls
TOOL_API_ENDPOINTS = {
    "NoteMaker": "/notemaker",
    "Flashcards": "/flashcards",
    "ConceptExplainer": "/conceptexplainer",
    "QuizGenerator": "/flashcards", # Placeholder
    "AnalogyCreator": "/conceptexplainer", # Placeholder
}

# The registry of tool descriptions for the vector retriever
TOOL_REGISTRY = {
    "NoteMaker": "Use this tool to summarize, organize, or take notes on a topic. Ideal for creating outlines, lists of key points, or structured summaries.",
    "Flashcards": "Creates digital flashcards for studying and memorization. Best for learning vocabulary, key terms, dates, and important facts. Keywords: study, review, memorize, prepare for a test.",
    "ConceptExplainer": "Use this tool when the student asks for an explanation of a concept, topic, or question. Answers 'what is', 'how does', or 'tell me about' style questions.",
    "QuizGenerator": "Generates practice problems, multiple-choice questions, or tests to assess a student's knowledge. Keywords: test me, check my understanding, practice problems, assessment.",
    "AnalogyCreator": "Explains a complex topic by providing a simple analogy or a real-world comparison. Use when a student wants to understand something by comparing it to something else.",
}
