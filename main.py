# --- main.py ---
# This is the main entry point for the FastAPI application.
# It now initializes and uses the LangGraph-based orchestrator for handling requests.

import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from schemas.api_schemas import OrchestratorRequest, OrchestratorResponse
from services.semantic_router import SemanticRouter
from services.gemini_executor import GeminiExecutor
from services.tool_executor import ToolExecutor
from services.state_manager import StateManager
from services.graph_orchestrator import GraphOrchestrator # <-- IMPORT THE GRAPH
from tools.tool_definitions import load_all_tools
from utils.config import settings
from utils.exceptions import OrchestratorException

# --- Logging Configuration ---
logging.basicConfig(level=settings.LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Application State ---
app_state = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown."""
    logger.info("Application startup...")
    tools = load_all_tools()
    if not tools:
        logger.critical("No tools loaded. Exiting.")
        raise RuntimeError("No tools loaded.")
    logger.info(f"Loaded {len(tools)} tools.")

    # Initialize individual services
    semantic_router = SemanticRouter(tools)
    await semantic_router.initialize()
    
    gemini_executor = GeminiExecutor(api_key=settings.GEMINI_API_KEY)
    tool_executor = ToolExecutor()
    
    # Initialize the Graph Orchestrator with the services
    app_state["graph_orchestrator"] = GraphOrchestrator(
        router=semantic_router,
        gemini_executor=gemini_executor,
        tool_executor=tool_executor
    )
    logger.info("Graph Orchestrator initialized successfully.")

    app_state["state_manager"] = StateManager()
    logger.info("State Manager initialized.")

    yield
    logger.info("Application shutdown...")
    app_state.clear()


app = FastAPI(
    title="YoLearn.ai - Autonomous AI Tutor Orchestrator",
    description="Intelligent middleware to connect a conversational AI tutor with educational tools using LangGraph.",
    version="2.0.0", # Version bump!
    lifespan=lifespan
)

# --- Exception Handlers ---
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"An unhandled exception occurred: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "Internal Server Error"})

# --- API Endpoint ---

@app.get("/")
async def home():
    return "hello world"
@app.post("/orchestrate", response_model=OrchestratorResponse)
async def orchestrate(request: OrchestratorRequest):
    """
    This endpoint is the core of the orchestrator. It now uses the LangGraph
    workflow to handle the user's query and context.
    """
    logger.info(f"Received orchestration request for user: {request.user_info.user_id}")
    orchestrator: GraphOrchestrator = app_state["graph_orchestrator"]
    
    try:
        # --- Invoke the LangGraph Workflow ---
        result = await orchestrator.invoke(request)
        
        # Here you can update state manager if needed, for example:
        # state_manager = app_state["state_manager"]
        # state_manager.add_assistant_message(request.user_info.user_id, result['message'])
        
        return OrchestratorResponse(**result)

    except OrchestratorException as e:
        logger.warning(f"Orchestration failed with a known exception: {e}")
        raise HTTPException(status_code=400, detail={"error": e.__class__.__name__, "message": str(e)})
    except Exception as e:
        logger.error(f"An unexpected error occurred during graph invocation: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

