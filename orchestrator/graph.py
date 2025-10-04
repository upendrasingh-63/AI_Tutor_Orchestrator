import os
from typing import TypedDict, List, Dict

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from dotenv import load_dotenv

from .prompts import SCALABLE_TOOL_SELECTOR_PROMPT, PARAMETER_EXTRACTOR_PROMPT
from .schemas import UserInfo,ChatMessage, NoteMakerInput, FlashcardGeneratorInput, ConceptExplainerInput

load_dotenv()

# --- 1. Define Graph State ---
class GraphState(TypedDict):
    student_message: str
    chat_history: List[ChatMessage]= Field(default_factory=list, max_items=10)
    user_info: Dict
    selected_tool: str
    extracted_parameters: Dict
    api_response: Dict
    final_answer: str

# --- 2. Tool Registry & Retriever ---
TOOL_REGISTRY = {
    "NoteMaker": "Use this tool to summarize, organize, or take notes on a topic. Ideal for creating outlines, lists of key points, or structured summaries.",
    "Flashcards": "Creates digital flashcards for studying and memorization. Best for learning vocabulary, key terms, dates, and important facts. Keywords: study, review, memorize, prepare for a test.",
    "ConceptExplainer": "Use this tool when the student asks for an explanation of a concept, topic, or question. Answers 'what is', 'how does', or 'tell me about' style questions.",
    "QuizGenerator": "Generates practice problems, multiple-choice questions, or tests to assess a student's knowledge. Keywords: test me, check my understanding, practice problems, assessment.",
    "AnalogyCreator": "Explains a complex topic by providing a simple analogy or a real-world comparison. Use when a student wants to understand something by comparing it to something else.",
}

try:
    embeddings = HuggingFaceEndpointEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
    tool_descriptions = list(TOOL_REGISTRY.values())
    vector_store = FAISS.from_texts(texts=tool_descriptions, embedding=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    print("✅ Tool retriever created successfully.")
except Exception as e:
    print(f"❌ Error creating tool retriever: {e}")
    retriever = None

# --- 3. Initialize LLM ---
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0, convert_system_message_to_human=True)

# --- 4. Define Tool Selector Node ---
class ToolSelector(BaseModel):
    tool: str = Field(..., description="The name of the single best tool to use.")

tool_selector_parser = PydanticOutputParser(pydantic_object=ToolSelector)
tool_selector_prompt = ChatPromptTemplate.from_template(
    template=SCALABLE_TOOL_SELECTOR_PROMPT,
    partial_variables={"format_instructions": tool_selector_parser.get_format_instructions()}
)
tool_selector_chain = tool_selector_prompt | llm | tool_selector_parser

def select_tool_node(state: GraphState) -> GraphState:
    print("\n--- 🧠 NODE: SELECTING TOOL ---")
    student_message = state["student_message"]
    if not retriever:
        raise ValueError("Retriever not initialized.")
    
    retrieved_docs = retriever.invoke(student_message)
    retrieved_tool_names = [list(TOOL_REGISTRY.keys())[list(TOOL_REGISTRY.values()).index(doc.page_content)] for doc in retrieved_docs]
    formatted_tools = "".join(f"- **{name}**: {TOOL_REGISTRY[name]}\n" for name in retrieved_tool_names)
    
    print(f"Top 3 relevant tools found: {retrieved_tool_names}")
    
    selected_tool_result = tool_selector_chain.invoke({
        "student_message": student_message,
        "chat_history": state["chat_history"],
        "tools": formatted_tools
    })
    
    state["selected_tool"] = selected_tool_result.tool
    print(f"Tool selected by LLM: {state['selected_tool']}")
    return state

# --- 5. Define Parameter Extractor Node ---
tool_schema_router = {
    "NoteMaker": NoteMakerInput,
    "Flashcards": FlashcardGeneratorInput,
    "ConceptExplainer": ConceptExplainerInput,
    "QuizGenerator": FlashcardGeneratorInput, # Placeholder for actual schema
    "AnalogyCreator": ConceptExplainerInput,  # Placeholder for actual schema
}

parameter_extractor_prompt = ChatPromptTemplate.from_template(PARAMETER_EXTRACTOR_PROMPT)

def extract_parameters_node(state: GraphState) -> GraphState:
    print("\n--- 🧠 NODE: EXTRACTING PARAMETERS ---")
    selected_tool = state["selected_tool"]
    
    output_schema = tool_schema_router.get(selected_tool)
    if not output_schema:
        raise ValueError(f"No schema defined for tool: {selected_tool}")
        
    extraction_chain = parameter_extractor_prompt | llm.with_structured_output(output_schema)
    
    print(f"Extracting parameters for tool: {selected_tool}")
    
    extracted_params = extraction_chain.invoke({
        "student_message": state["student_message"],
        "chat_history": state["chat_history"],
        "user_info": state["user_info"]
    })
    
    state["extracted_parameters"] = extracted_params.model_dump()
    print(f"Extracted parameters: {state['extracted_parameters']}")
    return state
    
# --- 6. Test the Full Sequence ---
if __name__ == "__main__":
    # Mock User Info from a State Manager
    mock_user_info = UserInfo(
        user_id="student123",
        name="Harry",
        grade_level="10",
        learning_style_summary="Prefers outlines and structured notes. Visual learner.",
        emotional_state_summary="Focused and attentive",
        mastery_level_summary="Level 7: Proficient"
    ).model_dump()
    
    # Test case from user prompt
    test_message = "I need to study for my big history final tomorrow."
    
    initial_state = GraphState(
        student_message=test_message,
        chat_history=[],
        user_info=mock_user_info,
        selected_tool="",
        extracted_parameters={},
        api_response={},
        final_answer=""
    )
    
    # Run the sequence: 1. Select Tool -> 2. Extract Params
    state_after_selection = select_tool_node(initial_state)
    final_state = extract_parameters_node(state_after_selection)
    
    print("\n--- ✅ TEST COMPLETE ---")
    print(f"Final Extracted Parameters for NoteMaker: {final_state['extracted_parameters']}")
