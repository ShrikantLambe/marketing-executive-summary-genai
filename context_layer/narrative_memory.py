"""
narrative_memory.py

Defines the NarrativeMemory class for the context layer, which stores and retrieves business memory and historical marketing context.
This enables LLMs to generate outputs grounded in organizational history and prior campaign learnings.
"""

from typing import Optional, Dict, Any, List
import re
try:
    from genai.embeddings_service import EmbeddingsService
except ImportError:
    EmbeddingsService = None


class NarrativeMemory:
    """
    Memory engine for storing and retrieving executive summaries and campaign results.
    - Stores previous executive summaries and campaign results.
    - Retrieves last 3 relevant summaries by semantic similarity (OpenAI+FAISS) or keyword.
    - Modular: can use EmbeddingsService, or fallback to in-memory/keyword search.
    """

    def __init__(self, backend=None, use_embeddings: bool = True):
        """
        backend: Optional pluggable backend (e.g., Pinecone, Weaviate, FAISS, EmbeddingsService). Defaults to in-memory list or embeddings.
        use_embeddings: If True and EmbeddingsService available, use vector search.
        """
        self.backend = backend
        self.use_embeddings = use_embeddings and EmbeddingsService is not None
        if self.use_embeddings and backend is None:
            self.embeddings = EmbeddingsService()
        else:
            self.embeddings = None
        if backend is None:
            self._summaries: List[dict] = []

    def add_summary(self, business_id: str, summary: str, campaign: str = None, timestamp: str = None, metadata: dict = None):
        """
        Store an executive summary or campaign result. Adds to embeddings if enabled.
        """
        record = {
            "business_id": business_id,
            "summary": summary,
            "campaign": campaign,
            "timestamp": timestamp,
            "metadata": metadata or {}
        }
        if self.backend:
            self.backend.add(record)
        else:
            self._summaries.append(record)
            if self.embeddings:
                # Store summary in vector DB for semantic search
                meta = record.copy()
                self.embeddings.add_summary(summary, metadata=meta)

    def retrieve_relevant_context(self, query: str, business_id: str = None, top_k: int = 3) -> List[dict]:
        """
        Retrieve last top_k summaries relevant to the query (semantic similarity if embeddings enabled, else keyword).
        Optionally filter by business_id.
        """
        if self.backend:
            return self.backend.query(query, business_id=business_id, top_k=top_k)
        if self.embeddings:
            results = self.embeddings.search(query, top_k=top_k)
            if business_id:
                results = [r for r in results if r["metadata"].get(
                    "business_id") == business_id]
            return results[:top_k]
        # Fallback: keyword search
        results = []
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        for record in reversed(self._summaries):
            if business_id and record["business_id"] != business_id:
                continue
            if pattern.search(record.get("summary", "")) or pattern.search(record.get("campaign", "")):
                results.append(record)
            if len(results) >= top_k:
                break
        return results

    def add_narrative(self, business_id: str, narrative: str):
        """
        (Legacy) Add or update the narrative memory for a given business or campaign.
        """
        self.add_summary(business_id, summary=narrative)

    def get_narrative(self, business_id: str) -> str:
        """
        (Legacy) Retrieve the most recent narrative for a business. Returns empty string if not found.
        """
        for record in reversed(self._summaries):
            if record["business_id"] == business_id:
                return record["summary"]
        return ""
