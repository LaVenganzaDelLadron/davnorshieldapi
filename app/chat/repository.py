from __future__ import annotations
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.chat import Conversation, Message, Document, Embedding


class ConversationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, title: str | None = None) -> Conversation:
        conv = Conversation(title=title)
        self.session.add(conv)
        await self.session.flush()
        return conv

    async def get(self, conversation_id: UUID) -> Conversation | None:
        q = select(Conversation).where(Conversation.id == conversation_id)
        result = await self.session.execute(q)
        return result.scalars().first()


class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def append(self, conversation_id: UUID, role: str, content: str, metadata: str | None = None) -> Message:
        msg = Message(conversation_id=conversation_id, role=role, content=content, metadata=metadata)
        self.session.add(msg)
        await self.session.flush()
        return msg

    async def list_for_conversation(self, conversation_id: UUID, limit: int = 100) -> List[Message]:
        q = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc()).limit(limit)
        result = await self.session.execute(q)
        return result.scalars().all()


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, source: str | None, text: str, chunk_count: int = 0) -> Document:
        doc = Document(source=source, text=text, chunk_count=chunk_count)
        self.session.add(doc)
        await self.session.flush()
        return doc


class EmbeddingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, document_id: UUID, chunk_index: int, vector: str, metadata: str | None = None) -> Embedding:
        emb = Embedding(document_id=document_id, chunk_index=chunk_index, vector=vector, metadata=metadata)
        self.session.add(emb)
        await self.session.flush()
        return emb

    async def search(self, query_vector: str, top_k: int = 5) -> List[Embedding]:
        # Placeholder: integrate with pgvector or external vector DB for real search
        return []
