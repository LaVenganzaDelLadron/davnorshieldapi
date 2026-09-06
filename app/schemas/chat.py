from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class MessageCreate(BaseModel):
    """Request schema: accepts incoming key `metadata` but maps to internal `meta_data`."""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    role: str
    content: str
    meta_data: Optional[dict] = Field(default=None, validation_alias="metadata")


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    role: str
    content: str
    # Internal name is meta_data, but serialize/deserialize using 'metadata' in JSON
    meta_data: Optional[dict] = Field(
        default=None,
        validation_alias=AliasChoices("meta_data", "metadata"),
        serialization_alias="metadata",
    )
    created_at: Optional[str]


class ConversationCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    title: Optional[str] = None


class ConversationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    title: Optional[str]
    created_at: Optional[str]


class ChatRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    conversation_id: Optional[UUID] = None
    prompt: str
    top_k: int = 5
    temperature: float = 0.0


class SourceDoc(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    score: float
    snippet: Optional[str]


class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    conversation_id: UUID
    message: str
    sources: List[SourceDoc] = []
