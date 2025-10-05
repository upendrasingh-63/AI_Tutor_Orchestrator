from fastapi import FastAPI
# --- FIX: Import the api router as well ---
from . import api, mock_tools
from fastapi.middleware.cors import CORSMiddleware

# Create the main FastAPI application instance
app = FastAPI(
    title="AI Tutor Orchestrator",
    description="The intelligent middleware connecting an AI Tutor to educational tools.",
    version="1.0.0",
)

origins = [
    "*", # Allow all origins for development. For production, you'd list specific domains.
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

# --- Include the API Routers ---

# --- FIX: Add this line to include the /chat endpoint ---
app.include_router(api.router)

# This adds all the mock tool endpoints (e.g., `/tools/notemaker`)
app.include_router(mock_tools.router)


# --- Define Root and Health Check Routes ---

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint to confirm the server is running."""
    return {"status": "ok", "message": "Welcome to the AI Tutor Orchestrator!"}

