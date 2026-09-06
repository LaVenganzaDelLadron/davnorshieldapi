from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import get_db
from app.chat.schemas import ChatRequest, ChatResponse, ConversationCreate, ConversationRead, MessageRead, MessageCreate
from app.chat.services import EmbeddingService, VectorStoreService, RAGChatService
from app.chat.repository import ConversationRepository, MessageRepository, DocumentRepository

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest, db: AsyncSession = Depends(get_db)):
    """Simple chat endpoint that runs a RAG retrieval + LLM call and returns a response with sources."""
    conv_repo = ConversationRepository(db)
    msg_repo = MessageRepository(db)

    # create or get conversation
    conversation = None
    if payload.conversation_id:
        conversation = await conv_repo.get(payload.conversation_id)
    if not conversation:
        conversation = await conv_repo.create(title=None)

    # append user message
    await msg_repo.append(conversation.id, role="user", content=payload.prompt)

    # instantiate services (replace with DI in real app)
    emb = EmbeddingService()
    vect = VectorStoreService()
    rag = RAGChatService(emb, vect)

    result = await rag.chat(conversation.id, payload.prompt, top_k=payload.top_k, temperature=payload.temperature)

    # append assistant message
    await msg_repo.append(conversation.id, role="assistant", content=result.get("message", ""))

    return result


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageRead])
async def list_messages(conversation_id: str, limit: int = 100, db: AsyncSession = Depends(get_db)):
    msg_repo = MessageRepository(db)
    msgs = await msg_repo.list_for_conversation(conversation_id, limit=limit)
    return msgs


@router.post("/documents/upload")
async def upload_document(source: str | None, text: str, db: AsyncSession = Depends(get_db)):
    doc_repo = DocumentRepository(db)
    doc = await doc_repo.create(source=source, text=text, chunk_count=1)
    return {"id": str(doc.id), "chunk_count": doc.chunk_count}
