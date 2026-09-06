from __future__ import annotations
from typing import List
from uuid import UUID
import httpx
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Responsible for creating embeddings from text. GROQ doesn't support embeddings natively.
    This returns placeholder vectors for now. Replace with sentence-transformers or OpenAI embeddings."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GROQ_API_KEY1
        self.base_url = settings.GROQ_BASE_URL
        if not self.api_key:
            logger.warning("EmbeddingService initialized without API key")
        if not self.base_url:
            logger.warning("EmbeddingService initialized without base URL")

    async def embed(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts and return vectors. Currently returns placeholder vectors.
        
        TODO: Implement with sentence-transformers, OpenAI, or a dedicated embedding service.
        GROQ API does not provide embeddings endpoint.
        """
        if not texts:
            return []
        
        try:
            logger.debug(f"Generating placeholder embeddings for {len(texts)} text(s)")
            
            # Generate placeholder embeddings (deterministic hash-based vectors)
            # In production, replace with real embedding service
            embeddings = []
            for text in texts:
                # Simple deterministic embedding: hash each text to a fixed-size vector
                # This is NOT for production use - just a placeholder for development
                hash_val = hash(text)
                # Create a consistent 384-dim vector (common for sentence transformers)
                vector = [(hash_val + i) % 1000 / 1000.0 for i in range(384)]
                embeddings.append(vector)
            
            logger.debug(f"Generated {len(embeddings)} placeholder embeddings (384-dim)")
            return embeddings
        
        except Exception as e:
            logger.exception(f"Unexpected error in embedding: {type(e).__name__}: {str(e)}")
            raise


class VectorStoreService:
    """Abstract vector store operations. Replace with pgvector or external store logic."""

    def __init__(self):
        pass

    async def upsert(self, doc_id: UUID, chunk_index: int, vector: List[float], metadata: dict | None = None):
        """Persist embedding to vector store."""
        logger.warning("VectorStoreService.upsert not implemented - returning no-op")
        # TODO: Implement with pgvector or external vector DB

    async def search(self, vector: List[float], top_k: int = 5):
        """Search vector store for top_k similar vectors."""
        logger.debug(f"Vector store search requested for top_k={top_k}, but search not implemented - returning empty results")
        # TODO: Implement with pgvector or external vector DB
        return []


class RAGChatService:
    """High-level chat service that retrieves relevant docs, constructs prompt, calls LLM, and stores results."""

    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStoreService, llm_api_key: str | None = None):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_api_key = llm_api_key or settings.AI_API_KEY
        self.base_url = settings.GROQ_BASE_URL

    async def chat(self, conversation_id: UUID | None, prompt: str, top_k: int = 5, temperature: float = 0.0):
        """Execute a chat query with RAG retrieval and LLM completion."""
        try:
            # 1. Embed the prompt (currently placeholder)
            logger.debug(f"Embedding prompt for conversation {conversation_id}")
            vectors = await self.embedding_service.embed([prompt])
            
            if not vectors or not vectors[0]:
                logger.warning("Embedding service returned empty vector")
                query_vector = []
            else:
                query_vector = vectors[0]

            # 2. Retrieve from vector store (currently disabled)
            logger.debug(f"Searching vector store with top_k={top_k} (not implemented)")
            hits = await self.vector_store.search(query_vector, top_k=top_k)

            # 3. Assemble system prompt + retrieved snippets
            system_context = "You are a helpful security assistant. Answer questions about cybersecurity, phishing prevention, hacking awareness, and threat intelligence."
            retrieved_text = "\n\n".join([h.get("snippet", "") for h in hits]) if hits else "(No vector database configured yet - providing general knowledge response)"
            
            # 4. Call LLM via GROQ
            logger.debug(f"Calling LLM with model {settings.AI_MODEL}")
            headers = {
                "Authorization": f"Bearer {self.llm_api_key}",
                "Content-Type": "application/json"
            }
            
            # Use messages format for GROQ chat/completions API
            payload = {
                "model": settings.AI_MODEL,
                "messages": [
                    {"role": "system", "content": system_context},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": settings.DEFAULT_MAX_CONTEXT_TOKENS
            }
            
            async with httpx.AsyncClient(timeout=settings.GROQ_TIMEOUT) as client:
                # Use the base URL directly for chat completions
                url = f"{self.base_url}/chat/completions"
                logger.debug(f"Calling LLM endpoint: {url}")
                r = await client.post(url, headers=headers, json=payload)
                r.raise_for_status()
                data = r.json()

            # 5. Parse response and return structured result
            text = ""
            if "choices" in data and data["choices"]:
                choice = data["choices"][0]
                # Handle both 'text' and 'message.content' formats
                if "text" in choice:
                    text = choice["text"]
                elif "message" in choice and "content" in choice["message"]:
                    text = choice["message"]["content"]
            
            logger.debug(f"LLM response received: {len(text)} characters")
            
            return {
                "conversation_id": conversation_id,
                "message": text or "I encountered an issue generating a response. Please try again.",
                "sources": [
                    {"id": h.get("id"), "score": h.get("score", 0.0), "snippet": h.get("snippet")} for h in hits
                ] if hits else [],
            }
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during chat: {e}")
            return {
                "conversation_id": conversation_id,
                "message": f"LLM service error: {str(e)}",
                "sources": [],
            }
        except Exception as e:
            logger.exception(f"Unexpected error in RAG chat: {type(e).__name__}: {str(e)}")
            return {
                "conversation_id": conversation_id,
                "message": f"Chat service error: {str(e)}",
                "sources": [],
            }
