from typing import TypedDict, List, Dict
import httpx 

from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_community.vectorstores.faiss import FAISS
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from dotenv import load_dotenv

from .prompts import SCALABLE_TOOL_SELECTOR_PROMPT, PARAMETER_EXTRACTOR_PROMPT
from .schemas import NoteMakerInput, FlashcardGeneratorInput, ConceptExplainerInput
from .config import TOOL_REGISTRY, TOOL_API_ENDPOINTS, BASE_API_URL

load_dotenv()

# --- 1. Define Graph State for Multi-Tool Workflows ---
class GraphState(TypedDict):
    student_message: str
    chat_history: List[Dict]
    user_info: Dict
    # --- NEW: Fields to handle lists of tools ---
    selected_tools: List[str]
    tool_api_responses: List[Dict] 
    final_answer: str

# --- 2. Initialize Models & Retriever ---
try:
    embeddings = HuggingFaceEndpointEmbeddings(model="sentence-transformers/all-MiniLM-L6-v2")
    tool_descriptions = list(TOOL_REGISTRY.values())
    vector_store = FAISS.from_texts(texts=tool_descriptions, embedding=embeddings)
    # Retrieve more tools for better context in multi-step tasks
    retriever = vector_store.as_retriever(search_kwargs={"k": 5}) 
    print("✅ Tool retriever created successfully.")
except Exception as e:
    print(f"❌ Error creating tool retriever: {e}")
    retriever = None

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0, convert_system_message_to_human=True)

# --- 3. Define Graph Nodes (Functions) ---

# --- Node 3a: Tool Selector ---
class ToolSelector(BaseModel):
    # --- NEW: Expect a list of tool names ---
    tools: List[str] = Field(..., description="A list of tool names to use, in the correct sequence.")

tool_selector_parser = PydanticOutputParser(pydantic_object=ToolSelector)
tool_selector_prompt = ChatPromptTemplate.from_template(
    template=SCALABLE_TOOL_SELECTOR_PROMPT,
    partial_variables={"format_instructions": tool_selector_parser.get_format_instructions()}
)
tool_selector_chain = tool_selector_prompt | llm | tool_selector_parser

def select_tools_node(state: GraphState) -> GraphState:
    print("\n--- 🧠 NODE: SELECTING TOOL(S) ---")
    student_message = state["student_message"]
    if not retriever: raise ValueError("Retriever not initialized.")
    
    retrieved_docs = retriever.invoke(student_message)
    retrieved_tool_names = [list(TOOL_REGISTRY.keys())[list(TOOL_REGISTRY.values()).index(doc.page_content)] for doc in retrieved_docs]
    formatted_tools = "".join(f"- **{name}**: {TOOL_REGISTRY[name]}\n" for name in retrieved_tool_names)
    
    print(f"Top {len(retrieved_tool_names)} relevant tools found: {retrieved_tool_names}")
    
    # The chain now returns an object with a 'tools' list
    selected_tools_result = tool_selector_chain.invoke({
        "student_message": state["student_message"], "chat_history": state["chat_history"], "tools": formatted_tools
    })
    
    state["selected_tools"] = selected_tools_result.tools
    print(f"Tool(s) selected by LLM: {state['selected_tools']}")
    return state

# --- Node 3b: Parameter Extractor (Now takes a specific tool as input) ---
tool_schema_router = {
    "NoteMaker": NoteMakerInput, "Flashcards": FlashcardGeneratorInput, "ConceptExplainer": ConceptExplainerInput,
    "QuizGenerator": FlashcardGeneratorInput, "AnalogyCreator": ConceptExplainerInput,
}
parameter_extractor_prompt = ChatPromptTemplate.from_template(PARAMETER_EXTRACTOR_PROMPT)

def extract_parameters_for_tool(state: GraphState, tool_name: str) -> dict:
    print(f"\n--- 🧠 NODE: EXTRACTING PARAMETERS for {tool_name} ---")
    output_schema = tool_schema_router.get(tool_name)
    if not output_schema: raise ValueError(f"No schema defined for tool: {tool_name}")
        
    extraction_chain = parameter_extractor_prompt | llm.with_structured_output(output_schema)
    
    extracted_params = extraction_chain.invoke({
        "student_message": state["student_message"], "chat_history": state["chat_history"], "user_info": state["user_info"]
    })
    
    print(f"Extracted parameters: {extracted_params.model_dump()}")
    return extracted_params.model_dump()
    
# --- Node 3c: Tool Orchestrator (Now takes a specific tool and its params) ---
async def call_tool_api(tool_name: str, parameters: dict) -> dict:
    print(f"\n--- ⚙️ NODE: ORCHESTRATING TOOL CALL for {tool_name} ---")
    endpoint_path = TOOL_API_ENDPOINTS.get(tool_name)
    if not endpoint_path: raise ValueError(f"No API endpoint defined for tool: {tool_name}")
    
    full_url = f"{BASE_API_URL}{endpoint_path}"
    print(f"Calling API at {full_url}...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(full_url, json=parameters, timeout=30.0)
        response.raise_for_status() 
        api_response = response.json()
        print("API call successful.")
        # --- NEW: Add the tool name to the response for the normalizer ---
        api_response["_tool_name_"] = tool_name 
        return api_response
    except httpx.RequestError as e:
        print(f"API call failed: {e}")
        return {"error": str(e), "_tool_name_": tool_name}

# --- Node 3d: Response Normalizer (Now handles a list of responses) ---
def _format_combined_response(responses: List[dict]) -> str:
    if not responses: return "I'm not sure how to help with that. Could you please rephrase your request?"
    
    formatted_responses = []
    for response in responses:
        tool_name = response.get("_tool_name_")
        formatter = RESPONSE_FORMATTERS.get(tool_name)
        if formatter:
            formatted_responses.append(formatter(response))
        else:
            formatted_responses.append(f"Received a response from an unknown tool: {tool_name}")
            
    # Combine all formatted strings with a clear separator
    return "\n\n---\n\n".join(formatted_responses)

def _format_notemaker_response(response: dict) -> str:
    """Formats the NoteMaker JSON into a readable string."""
    if "error" in response:
        return "Sorry, I encountered an error while creating your notes."
    title = response.get('title', 'your notes')
    summary = response.get('summary', 'Here are the notes I created:')
    sections_str = ""
    for section in response.get('note_sections', []):
        key_points = "\n".join(f"  - {point}" for point in section.get('key_points', []))
        sections_str += f"\n\n### {section.get('title', 'Section')}\n{section.get('content', '')}\n**Key Points:**\n{key_points}"
    return f"Great! I've prepared a summary for you on **{response.get('topic', 'your topic')}**.\n\n## {title}\n\n**Summary:** {summary}{sections_str}"

def _format_flashcards_response(response: dict) -> str:
    """Formats the Flashcard Generator JSON into a detailed, readable string."""
    if "error" in response:
        return "Sorry, I had trouble creating the flashcards."
    flashcards = response.get('flashcards', [])
    topic = response.get('topic', 'your topic')
    if not flashcards:
        return f"I couldn't generate any flashcards for **{topic}**. Please try another topic."
    intro = f"Additionally, I've created {len(flashcards)} flashcards for you on **{topic}**. Here are the details:\n"
    flashcard_details = []
    for i, card in enumerate(flashcards):
        question = card.get('question', 'No question provided.')
        answer = card.get('answer', 'No answer provided.')
        card_str = f"\n--- Card #{i+1} ---\n**Question:** {question}\n**Answer:** {answer}"
        flashcard_details.append(card_str)
    return intro + "\n".join(flashcard_details)

def _format_conceptexplainer_response(response: dict) -> str:
    """Formats the Concept Explainer JSON into a readable string."""
    if "error" in response:
        return "Sorry, I couldn't find a good explanation for that concept right now."
    explanation = response.get('explanation', 'Here is the explanation you requested.')
    return f"Of course! Here is an explanation of the concept:\n\n{explanation}"

RESPONSE_FORMATTERS = {
    "NoteMaker": _format_notemaker_response, "Flashcards": _format_flashcards_response,
    "ConceptExplainer": _format_conceptexplainer_response, "QuizGenerator": _format_flashcards_response,
    "AnalogyCreator": _format_conceptexplainer_response,
}

