from fastapi import FastAPI
from . import mock_tools

app = FastAPI(
    title="AI Tutor Orchestrator",
    description="The intelligent middleware for the Autonomous AI Tutor.",
    version="1.0.0"
)

# Include the mock tool endpoints from our other file
app.include_router(mock_tools.router)

@app.get("/", tags=["Health Check"])
def read_root():
    """A simple health check endpoint to confirm the server is running."""
    return {"status": "ok", "message": "Welcome to the AI Tutor Orchestrator!"}
