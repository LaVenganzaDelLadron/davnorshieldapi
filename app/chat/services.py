from __future__ import annotations
from typing import List
from uuid import UUID
import httpx
import json
from app.config import settings


class EmbeddingService:
    """Responsible for creating embeddings from text. Stub uses GROQ/OpenAI-compatible endpoint settings."""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GROQ_API_KEY1
        self.base_url = settings.GROQ_BASE_URL

    async def embed(self, texts: List[str]) -> List[List[float]]:
        # Minimal example: call GROQ embedding endpoint or OpenAI-compatible wrapper
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {"model": settings.AI_MODEL, "input": texts}
        async with httpx.AsyncClient(timeout=settings.GROQ_TIMEOUT) as client:
            r = await client.post(f"{self.base_url}/embeddings", headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
        # Parse response to list of vectors; adjust according to provider
        return [item.get("embedding") for item in data.get("data", [])]


class VectorStoreService:
    """Abstract vector store operations. Replace search/upsert with pgvector or external store logic."""

    def __init__(self):
        pass

    async def upsert(self, doc_id: UUID, chunk_index: int, vector: List[float], metadata: dict | None = None):
        # Persist embedding via EmbeddingRepository or external DB
        raise NotImplementedError

    async def search(self, vector: List[float], top_k: int = 5):
        # Return list of (doc_id, score, snippet)
        return []


class RAGChatService:
    """High-level chat service that retrieves relevant docs, constructs prompt, calls LLM, and stores results."""

    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStoreService, llm_api_key: str | None = None):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_api_key = llm_api_key or settings.AI_API_KEY
        self.base_url = settings.GROQ_BASE_URL

    async def chat(self, conversation_id: UUID | None, prompt: str, top_k: int = 5, temperature: float = 0.0):
        # 1. Embed prompt
        vectors = await self.embedding_service.embed([prompt])
        query_vector = vectors[0]

        # 2. Retrieve from vector store
        hits = await self.vector_store.search(query_vector, top_k=top_k)

        # 3. Assemble system prompt + retrieved snippets + history (omitted here)
        system_context = "You are an assistant that answers using retrieved documents and short summaries."
        retrieved_text = "\n\n".join([h.get("snippet", "") for h in hits])
        assembled_prompt = f"{system_context}\n\nContext:\n{retrieved_text}\n\nUser: {prompt}\nAssistant:"

        # 4. Call LLM (GROQ/OpenAI-compatible)
        headers = {"Authorization": f"Bearer {self.llm_api_key}", "Content-Type": "application/json"}
        payload = {"model": settings.AI_MODEL, "input": assembled_prompt, "temperature": temperature}
        async with httpx.AsyncClient(timeout=settings.GROQ_TIMEOUT) as client:
            r = await client.post(f"{self.base_url}/completions", headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()

        # 5. Parse response and return structured result
        text = ""
        if "choices" in data and data["choices"]:
            text = data["choices"][0].get("text") or data["choices"][0].get("message", {}).get("content", "")

        return {
            "conversation_id": conversation_id,
            "message": text,
            "sources": [
                {"id": h.get("id"), "score": h.get("score", 0.0), "snippet": h.get("snippet")} for h in hits
            ],
        }
