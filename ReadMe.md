YoLearn.ai - Autonomous AI Tutor Orchestrator
This project is an intelligent middleware orchestrator designed to connect a conversational AI tutor with a vast library of educational tools. It acts as the "brain" that understands a student's conversational request, selects the best tool for the job, extracts the necessary parameters, and executes the tool, all without manual configuration.

This implementation follows a scalable, two-stage Router-Executor pattern.

Features
Scalable Tool Integration: Designed to handle 80+ tools efficiently. Adding a new tool only requires defining its schema and action.

Semantic Tool Routing: A fast, non-LLM based router uses vector similarity search (FAISS & Sentence-Transformers) to instantly find the most relevant tools for a user's query, drastically reducing latency.

Intelligent Parameter Extraction: A single, precise call to the Gemini API is used to select the best tool from the routed candidates and extract all required parameters, inferring missing values from the conversation and student context.

Robust Error Handling: Gracefully handles cases like missing parameters (by asking clarifying questions), tool execution failures, and schema validation errors.

State Management: Maintains conversation history and student personalization context for each user session.

Modern Tech Stack: Built with Python, FastAPI, Pydantic, and Google's Gemini API.

Project Structure
/ai_orchestrator/
├── .env # For storing environment variables like API keys
├── main.py # Main FastAPI application entrypoint
├── requirements.txt # Python dependencies
│
├── schemas/ # Pydantic models for data validation
│ ├── api_schemas.py # Schemas for the main API endpoints
│ └── tool_schemas.py # Input/output schemas for all educational tools
│
├── services/ # Core business logic
│ ├── semantic_router.py # Stage 1: Fast filtering of tools
│ ├── gemini_executor.py # Stage 2: LLM-based tool selection & param extraction
│ ├── tool_executor.py # Dispatches calls to the actual tools
│ └── state_manager.py # Manages conversation state
│
├── tools/ # Definitions of the educational tools
│ └── tool_definitions.py # Contains the name, description, schema, and action for each tool
│
└── utils/ # Utility modules
├── config.py # Application configuration management
└── exceptions.py # Custom exception classes

Setup and Installation
Clone the repository:

git clone <repository_url>
cd ai_orchestrator

Create a virtual environment:

python -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`

Install dependencies:

pip install -r requirements.txt

Configure environment variables:
Create a file named .env in the project root directory and add your Gemini API key:

GEMINI_API_KEY="your_google_ai_studio_api_key"

How to Run
Start the FastAPI server:

uvicorn main:app --reload

The server will be running at http://127.0.0.1:8000.

Access the API Documentation:
Once the server is running, you can access the interactive OpenAPI documentation at http://127.0.0.1:8000/docs.

How to Use the /orchestrate Endpoint
You can send a POST request to http://127.0.0.1:8000/orchestrate with a JSON body like the following:

{
"user_info": {
"user_id": "student123",
"name": "Alex",
"grade_level": "10",
"learning_style_summary": "Prefers visual examples and step-by-step instructions.",
"emotional_state_summary": "Confused",
"mastery_level_summary": "Level 3: Has some basic knowledge but struggles with application."
},
"chat_history": [
{
"role": "user",
"content": "What is photosynthesis?"
},
{
"role": "assistant",
"content": "Photosynthesis is the process used by plants, algae, and certain bacteria to harness energy from sunlight and turn it into chemical energy."
}
],
"current_query": "I'm still a bit lost, can you make that simpler and give me some flashcards to practice?"
}

The orchestrator will first use the ConceptExplainerTool to simplify the explanation and then could use the FlashcardGeneratorTool based on the user's combined request. (Note: The current implementation handles one tool per query, but could be extended with LangGraph for multi-tool execution).
