"""
context_builder.py

Defines the ContextBuilder class for the context layer, which enriches LLM prompts with business memory and historical marketing context.
This abstraction enables more relevant, accurate, and business-aware AI outputs by injecting context from narrative memory and retrieval engines.
"""
from typing import Any, Dict
from .narrative_memory import NarrativeMemory
from .retrieval_engine import RetrievalEngine

class ContextBuilder:
    """
    ContextBuilder orchestrates the enrichment of LLM prompts with business context and memory.
    It composes context from NarrativeMemory and RetrievalEngine, supporting dependency injection for extensibility.
    Designed for future integration with vector databases and advanced retrieval systems.
    """
    def __init__(self, memory: NarrativeMemory, retriever: RetrievalEngine):
        self.memory = memory
        self.retriever = retriever

    def build_context(self, user_query: str, business_id: str = None) -> Dict[str, Any]:
        """
        Build a context dictionary for LLM prompts, including historical narrative and retrieved facts.
        """
        narrative = self.memory.get_narrative(business_id)
        retrieved = self.retriever.retrieve(user_query, business_id)
        return {
            "narrative": narrative,
            "retrieved": retrieved,
            "user_query": user_query
        }
