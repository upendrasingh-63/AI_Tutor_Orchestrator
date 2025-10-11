
# This file defines the Pydantic models for API request and response bodies.
# This ensures that all incoming and outgoing data is validated and typed correctly.

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Literal
from .tool_schemas import UserInfo, ChatMessage

class OrchestratorRequest(BaseModel):
    """
    Defines the structure of the incoming request to the /orchestrate endpoint.
    """
    user_info: UserInfo = Field(
        ...,
        description="Object containing all information about the student."
    )
    chat_history: List[ChatMessage] = Field(
        default_factory=list,
        description="The recent conversation history to provide context."
    )
    current_query: str = Field(
        ...,
        min_length=1,
        description="The latest message/query from the student."
    )

class OrchestratorResponse(BaseModel):
    """
    Defines the structure of the response from the /orchestrate endpoint.
    """
    response_type: Literal["tool_response", "clarification", "error"] = Field(
        ...,
        description="Indicates the nature of the response."
    )
    content: Dict[str, Any] | None = Field(
        description="The JSON response from the executed tool. Null if clarification is needed."
    )
    message: str = Field(
        description="A human-readable message describing the outcome or the clarification question."
    )
