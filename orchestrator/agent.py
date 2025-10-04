# orchestrator/agent.py

import os
from typing import TypedDict, List, Dict
import requests 

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from dotenv import load_dotenv

# --- Import configurations and schemas ---
from .prompts import SCALABLE_TOOL_SELECTOR_PROMPT, PARAMETER_EXTRACTOR_PROMPT
from .schemas import UserInfo, NoteMakerInput, FlashcardGeneratorInput, ConceptExplainerInput, ChatMessage
from .config import TOOL_REGISTRY, TOOL_API_ENDPOINTS, BASE_API_URL

load_dotenv()

# --- 1. Define Graph State ---
class GraphState(TypedDict):
    student_message: str
    chat_history: List[Dict]
    user_info: Dict
    selected_tool: str
    extracted_parameters: Dict
    api_response: Dict 
    final_answer: str

# --- 2. Initialize Models & Retriever ---
try:
    embeddings = HuggingFaceEndpointEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
    tool_descriptions = list(TOOL_REGISTRY.values())
    vector_store = FAISS.from_texts(texts=tool_descriptions, embedding=embeddings)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    print("✅ Tool retriever created successfully.")
except Exception as e:
    print(f"❌ Error creating tool retriever: {e}")
    retriever = None

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0, convert_system_message_to_human=True)

# --- 3. Define Graph Nodes ---

# --- Node 3a: Tool Selector ---
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
    # ... (Logic remains the same)
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

# --- Node 3b: Parameter Extractor ---
tool_schema_router = {
    "NoteMaker": NoteMakerInput, "Flashcards": FlashcardGeneratorInput, "ConceptExplainer": ConceptExplainerInput,
    "QuizGenerator": FlashcardGeneratorInput, "AnalogyCreator": ConceptExplainerInput,
}
parameter_extractor_prompt = ChatPromptTemplate.from_template(PARAMETER_EXTRACTOR_PROMPT)

def extract_parameters_node(state: GraphState) -> GraphState:
    print("\n--- 🧠 NODE: EXTRACTING PARAMETERS ---")
    # ... (Logic remains the same)
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
    
# --- Node 3c: Tool Orchestrator ---
def tool_orchestrator_node(state: GraphState) -> GraphState:
    print("\n--- ⚙️ NODE: ORCHESTRATING TOOL CALL ---")
    # ... (Logic remains the same)
    selected_tool = state["selected_tool"]
    parameters = state["extracted_parameters"]
    
    endpoint_path = TOOL_API_ENDPOINTS.get(selected_tool)
    if not endpoint_path:
        raise ValueError(f"No API endpoint defined for tool: {selected_tool}")
    
    full_url = f"{BASE_API_URL}{endpoint_path}"
        
    print(f"Calling API for {selected_tool} at {full_url}...")
    
    try:
        response = requests.post(full_url, json=parameters)
        response.raise_for_status() 
        state["api_response"] = response.json()
        print("API call successful. Response received.")
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        state["api_response"] = {"error": str(e)}

    return state
