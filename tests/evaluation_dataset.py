# tests/evaluation_dataset.py

EVALUATION_DATASET = [
    # --- Direct Requests for each tool ---
    {
        "message": "Can you make me some flashcards for the parts of a cell?",
        "expected_tool": "Flashcards"
    },
    {
        "message": "Explain the concept of photosynthesis to me.",
        "expected_tool": "ConceptExplainer"
    },
    {
        "message": "Can you summarize the main causes of World War II?",
        "expected_tool": "NoteMaker"
    },
    {
        "message": "Give me 5 practice problems for basic algebra.",
        "expected_tool": "QuizGenerator"
    },
    {
        "message": "What is gravity like? Can you give me a simple comparison?",
        "expected_tool": "AnalogyCreator"
    },

    # --- Conversational & Indirect Requests ---
    {
        "message": "I need a quick way to memorize the US presidents in order.",
        "expected_tool": "Flashcards"  # Memorization strongly implies Flashcards.
    },
    {
        "message": "Whip up an outline for my essay on the water cycle.",
        "expected_tool": "NoteMaker" # "Outline" is a key indicator for notes.
    },
    {
        "message": "How can I check if I really understand Shakespeare's Macbeth?",
        "expected_tool": "QuizGenerator" # "Check my understanding" implies a quiz. //got ConceptExplainer
    },
    {
        "message": "I just don't get how a computer's CPU works.",
        "expected_tool": "ConceptExplainer" # "I don't get" is a clear signal for an explanation.
    },
    {
        "message": "Can you compare how the internet works to something in the real world?",
        "expected_tool": "AnalogyCreator" # "Compare to something" is a direct request for an analogy.
    },

    # --- Ambiguous Requests (to test nuanced selection) ---
    {
        "message": "I need to study for my big history final tomorrow.",# got QuizGenerator
        "expected_tool": "Flashcards"  # This is ambiguous (could be notes or quiz), but flashcards are a primary tool for last-minute studying. A failure here is understandable but tests the model's bias.
    },
    {
        "message": "Let's work on the American Revolution.",
        "expected_tool": "ConceptExplainer" # A very general request. The default safe action is to start with an explanation.
    }
]