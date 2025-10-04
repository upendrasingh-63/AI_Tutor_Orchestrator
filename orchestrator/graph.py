import os
from typing import TypedDict, List, Dict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.vectorstores.faiss import FAISS
from dotenv import load_dotenv

# Import the new, scalable prompt
from .prompts import SCALABLE_TOOL_SELECTOR_PROMPT

# Load environment variables from .env file
load_dotenv()

# --- 1. Define the State of our Graph ---
class GraphState(TypedDict):
    student_message: str
    chat_history: List[Dict]
    user_info: Dict
    selected_tool: str
    extracted_parameters: Dict
    api_response: Dict
    final_answer: str

# --- 2. Create a Tool Registry and Retriever ---

# This simulates our database of 80+ tools.
# For a real application, this would come from a database or a config file.
TOOL_REGISTRY = {
    "NoteMaker": "Use this tool when the student wants to summarize, organize, or take notes on a specific topic. Keywords: make notes, summarize, key points, outline.",
    "Flashcards": "Use this tool when the student wants to create flashcards for studying or quiz themselves on a topic. Keywords:study, review, memorize, make flashcards, quiz me, test my knowledge.",
    "ConceptExplainer": "Use this tool when the student is asking for an explanation of a concept, topic, or question. Keywords: explain, what is, how does, tell me about.",
    "QuizGenerator": "Generates practice problems or multiple-choice questions on a given subject and topic, with adjustable difficulty. Keywords:check my understanding, practice problems, give me a quiz, test me.",
    "AnalogyCreator": "Explains a complex topic by providing a simple analogy or a real-world comparison. Keywords: explain with an analogy, what is this like, compare this to.",
    # ... imagine 75+ more tools here
}

# The "Retrieval" part of our two-stage approach
# We use vector embeddings to find the most semantically similar tools.
try:
    # Initialize the embeddings model
    print("Initializing Hugging Face Endpoint embeddings...")
    embeddings = HuggingFaceEndpointEmbeddings(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    print("Online embeddings model configured.")
    
    # Create a list of tool descriptions for embedding
    tool_descriptions = list(TOOL_REGISTRY.values())
    
    # Create the FAISS vector store from the descriptions
    # This is an in-memory vector store, perfect for a hackathon.
    vector_store = FAISS.from_texts(texts=tool_descriptions, embedding=embeddings)
    
    # Create a retriever which will find the top K most relevant tools
    retriever = vector_store.as_retriever(search_kwargs={"k": 3}) # Retrieve top 3 tools
    
    print("✅ Tool retriever created successfully.")
except Exception as e:
    print(f"❌ Error creating tool retriever: {e}")
    retriever = None

# --- 3. Initialize the LLM for Ranking/Selection ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0)

# Define the structured output
class ToolSelector(BaseModel):
    tool: str = Field(..., description="The name of the single best tool to use.")

tool_selector_parser = PydanticOutputParser(pydantic_object=ToolSelector)

# Create the prompt template
tool_selector_prompt = ChatPromptTemplate.from_template(
    template=SCALABLE_TOOL_SELECTOR_PROMPT,
    partial_variables={"format_instructions": tool_selector_parser.get_format_instructions()}
)

# Create the final selection chain
tool_selector_chain = tool_selector_prompt | llm | tool_selector_parser

def select_tool_node(state: GraphState) -> GraphState:
    """
    This node implements the Retrieval and Ranking strategy to select a tool.
    """
    print("--- 🧠 NODE: SELECTING TOOL (SCALABLE) ---")
    student_message = state["student_message"]
    chat_history = state.get("chat_history", [])

    if not retriever:
        raise ValueError("Retriever not initialized. Cannot select tool.")

    # 1. RETRIEVAL: Find the most relevant tools
    retrieved_docs = retriever.invoke(student_message)
    
    # Format the retrieved tools for the prompt
    retrieved_tool_names = [list(TOOL_REGISTRY.keys())[list(TOOL_REGISTRY.values()).index(doc.page_content)] for doc in retrieved_docs]
    
    formatted_tools = ""
    for name, desc in TOOL_REGISTRY.items():
        if name in retrieved_tool_names:
            formatted_tools += f"- **{name}**: {desc}\n"

    print(f"Top {len(retrieved_tool_names)} relevant tools found: {retrieved_tool_names}")

    # 2. RANKING/SELECTION: Pass the relevant tools to the LLM for a final decision
    selected_tool_result = tool_selector_chain.invoke({
        "student_message": student_message,
        "chat_history": chat_history,
        "tools": formatted_tools
    })

    print(f"Tool selected by LLM: {selected_tool_result.tool}")
    state["selected_tool"] = selected_tool_result.tool
    
    return state

# --- Simple Test ---
if __name__ == "__main__":
    test_message = "Can you give me 5 practice problems for calculus derivatives?"
    
    initial_state = GraphState(
        student_message=test_message,
        chat_history=[],
        user_info={},
        selected_tool="",
        extracted_parameters={},
        api_response={},
        final_answer=""
    )

    updated_state = select_tool_node(initial_state)

    print("\n--- TEST COMPLETE ---")
    print(f"Message: '{test_message}'")
    print(f"Selected Tool: {updated_state['selected_tool']}")

    # Another test
    test_message_2 = "Can you explain the water cycle with a simple analogy?"
    initial_state_2 = GraphState(student_message=test_message_2, chat_history=[], user_info={}, selected_tool="", extracted_parameters={}, api_response={}, final_answer="")
    updated_state_2 = select_tool_node(initial_state_2)
    print("\n--- TEST 2 COMPLETE ---")
    print(f"Message: '{test_message_2}'")
    print(f"Selected Tool: {updated_state_2['selected_tool']}")

    # python -m orchestrator.graph