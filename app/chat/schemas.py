from __future__ import annotations
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel


class MessageCreate(BaseModel):
    role: str
    content: str
    metadata: Optional[dict] = None


class MessageRead(BaseModel):
    id: UUID
    role: str
    content: str
    metadata: Optional[dict] = None
    created_at: Optional[str]

    class Config:
        orm_mode = True


class ConversationCreate(BaseModel):
    title: Optional[str] = None


class ConversationRead(BaseModel):
    id: UUID
    title: Optional[str]
    created_at: Optional[str]

    class Config:
        orm_mode = True


class ChatRequest(BaseModel):
    conversation_id: Optional[UUID] = None
    prompt: str
    top_k: int = 5
    temperature: float = 0.0


class SourceDoc(BaseModel):
    id: UUID
    score: float
    snippet: Optional[str]


class ChatResponse(BaseModel):
    conversation_id: UUID
    message: str
    sources: List[SourceDoc] = []
