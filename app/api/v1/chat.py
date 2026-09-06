from __future__ import annotations
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from app.database.session import get_db
from app.dependencies import get_current_active_user_dependency
from app.core.permissions import require_role
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, MessageRead
from app.services.chat_service import EmbeddingService, VectorStoreService, RAGChatService
from app.repositories.chat_repository import ConversationRepository, MessageRepository, DocumentRepository
from app.services.rag_policy import OutOfScopeQueryError, sanitize_for_rag, validate_public_query
from uuid import UUID

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(
    payload: ChatRequest,
    current_user: Annotated[User, Depends(get_current_active_user_dependency)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Chat endpoint with RAG retrieval + LLM call. Returns response with retrieved sources."""
    try:
        validate_public_query(payload.prompt)
        conv_repo = ConversationRepository(db)
        msg_repo = MessageRepository(db)

        # Create or get conversation
        conversation = None
        if payload.conversation_id:
            conversation = await conv_repo.get_for_user(payload.conversation_id, current_user.id)
            if conversation is None:
                raise HTTPException(status_code=404, detail="Conversation not found.")
        if not conversation:
            conversation = await conv_repo.create(owner_id=current_user.id, title=None)
            await db.commit()
            logger.info(f"Created conversation {conversation.id}")

        # Append user message
        await msg_repo.append(
            conversation.id,
            role="user",
            content=sanitize_for_rag(payload.prompt),
        )
        await db.commit()
        logger.debug(f"Appended user message to conversation {conversation.id}")

        # Instantiate services
        emb = EmbeddingService()
        vect = VectorStoreService()
        rag = RAGChatService(emb, vect)

        # Call RAG chat service
        result = await rag.chat(conversation.id, payload.prompt, top_k=payload.top_k, temperature=payload.temperature)

        # Append assistant message
        await msg_repo.append(conversation.id, role="assistant", content=result.get("message", ""))
        await db.commit()
        logger.debug(f"Appended assistant message to conversation {conversation.id}")

        # Return ChatResponse model (not raw dict)
        return ChatResponse(**result)

    except OutOfScopeQueryError as e:
        await db.rollback()
        raise HTTPException(status_code=403, detail=str(e)) from e
    except Exception as e:
        await db.rollback()
        logger.exception(f"Chat endpoint failed: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageRead])
async def list_messages(
    conversation_id: str,
    current_user: Annotated[User, Depends(get_current_active_user_dependency)],
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: int = 100,
):
    """List messages for a conversation."""
    try:
        # Convert string UUID to UUID object
        conv_id = UUID(conversation_id)
        msg_repo = MessageRepository(db)
        msgs = await msg_repo.list_for_conversation(
            conv_id, owner_id=current_user.id, limit=limit
        )
        return msgs
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation_id UUID format")
    except Exception as e:
        logger.exception(f"List messages failed: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve messages")


@router.post("/documents/upload")
async def upload_document(
    current_user: Annotated[User, Depends(require_role(UserRole.municipality_admin))],
    db: Annotated[AsyncSession, Depends(get_db)],
    source: str | None = None,
    text: str = "",
):
    """Upload and index a document."""
    try:
        if not text.strip():
            raise HTTPException(status_code=400, detail="Document text cannot be empty")
        
        doc_repo = DocumentRepository(db)
        doc = await doc_repo.create(source=source, text=text, chunk_count=1)
        await db.commit()
        logger.info(f"Uploaded document {doc.id} from source {source}")
        return {"id": str(doc.id), "chunk_count": doc.chunk_count}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.exception(f"Upload document failed: {type(e).__name__}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload document")
