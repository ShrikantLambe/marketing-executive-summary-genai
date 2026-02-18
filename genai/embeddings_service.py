"""
embeddings_service.py

Provides embedding generation (OpenAI), local FAISS storage, and similarity search for executive summaries.
Modular, production-ready for future backend swap.
"""
import os
from typing import List, Dict, Any, Optional
import numpy as np
import faiss
import openai

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
openai.api_key = OPENAI_API_KEY

class EmbeddingsService:
    def __init__(self, dim: int = 1536):
        self.dim = dim
        self.index = faiss.IndexFlatL2(dim)
        self.records: List[Dict[str, Any]] = []  # Store metadata for each vector

    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate OpenAI embedding for a given text.
        """
        response = openai.embeddings.create(
            input=[text],
            model="text-embedding-ada-002"
        )
        vec = np.array(response.data[0].embedding, dtype=np.float32)
        if vec.shape[0] != self.dim:
            raise ValueError(f"Embedding dimension mismatch: {vec.shape[0]} != {self.dim}")
        return vec

    def add_summary(self, summary: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Embed and store a summary with optional metadata.
        """
        vec = self.embed_text(summary)
        self.index.add(np.expand_dims(vec, axis=0))
        self.records.append({"summary": summary, "metadata": metadata or {}})

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Embed query and return top_k most similar summaries (with metadata).
        """
        if len(self.records) == 0:
            return []
        qvec = self.embed_text(query)
        D, I = self.index.search(np.expand_dims(qvec, axis=0), top_k)
        results = []
        for idx in I[0]:
            if idx < len(self.records):
                results.append(self.records[idx])
        return results
