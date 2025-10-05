
SCALABLE_TOOL_SELECTOR_PROMPT = """
You are an expert AI agent. Your task is to analyze a student's request and identify all the educational tools required to fulfill it.

**Here are the most relevant tools for this specific request:**
{tools}

**Conversation History:**
{chat_history}

**Student's Latest Message:**
{student_message}

Based on the student's message, identify the sequence of tools that should be used. It is possible that one or more tools are required. If no tools are relevant, return an empty list.

{format_instructions}
"""

PARAMETER_EXTRACTOR_PROMPT = """
You are an expert AI assistant. Your task is to extract structured information to populate the parameters for a selected tool based on the student's message, their profile, and the conversation history.

**Student Profile (State Manager Data):**
{user_info}

**Conversation History:**
{chat_history}

**Student's Latest Message:**
{student_message}

**Instructions:**
1.  Analyze the student's message in the context of their profile and the conversation.
2.  Extract all necessary information to fill the fields for the tool's required input schema.
3.  **Crucially, use the Student Profile to infer values.** For example:
    - If the student's emotional state is 'Anxious' or 'Confused', or their mastery level is low (1-3), infer a 'difficulty' of 'easy' or a 'desired_depth' of 'basic'.
    - If the student is 'Focused' and has a high mastery level (7+), you can infer a 'difficulty' of 'hard' or a 'desired_depth' of 'advanced'.
    - If the student's learning style is 'Visual', set 'include_examples' to true.
4.  If a parameter cannot be found or inferred, use a sensible default (e.g., 5 for `count`, 'structured' for `note_taking_style`).
5.  You MUST provide the output in the requested structured JSON format.
"""