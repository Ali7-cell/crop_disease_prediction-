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
    message: Optional[str] = Field(
        default="",
        description="The query / message from the user to the AI assistant."
    )
    audio_b64: Optional[str] = Field(
        default=None,
        description="Base64 encoded voice recording from browser MediaRecorder."
    )
    audio_mime: Optional[str] = Field(
        default="audio/webm",
        description="MIME type of the base64 audio recording."
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
