from fastapi import FastAPI

app = FastAPI(
    title="AI Tutor Orchestrator",
    description="The intelligent middleware for the Autonomous AI Tutor.",
    version="1.0.0"
)

@app.get("/", tags=["Health Check"])
def read_root():
    return {"status": "ok", "message": "Welcome to the AI Tutor Orchestrator!"}