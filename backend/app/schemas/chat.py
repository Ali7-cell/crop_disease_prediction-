"""
Pydantic schemas for the AI assistant chat endpoint.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single turn in the chat history."""
    role: str = Field(
        ...,
        description="The role of the message author. Typically 'user' or 'model'."
    )
    content: str = Field(
        ...,
        description="The text content of the message."
    )


class ChatRequest(BaseModel):
    """POST /chat request body."""
    message: str = Field(
        ...,
        min_length=1,
        description="The query / message from the user to the AI assistant."
    )
    history: Optional[List[ChatMessage]] = Field(
        default=None,
        description="Optional chat history for multi-turn conversations."
    )


class ChatResponse(BaseModel):
    """POST /chat response body."""
    response: str = Field(
        ...,
        description="The generated response from the AI assistant."
    )
