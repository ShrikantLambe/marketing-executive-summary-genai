"""
prompt_builder.py

Defines the PromptBuilder class for constructing structured prompts for LLMs.
Injects normalized metrics, strategic tags, and historical comparisons into a modular system+user prompt.
Separates business logic from LLM call for maintainability and extensibility.
"""
from typing import Dict, Any, List, Optional

class PromptBuilder:
    """
    Builds a structured prompt for LLMs by injecting:
    - Normalized metrics (from semantic layer)
    - Strategic tags (e.g., acquisition, revenue)
    - Historical comparisons (from context layer)
    Produces a dict with 'system' and 'user' prompt fields.
    """
    def __init__(self, system_role: str = "You are a helpful marketing analyst."):
        self.system_role = system_role

    def build_prompt(
        self,
        normalized_metrics: Dict[str, Any],
        strategic_tags: Optional[List[str]] = None,
        historical_context: Optional[List[Dict[str, Any]]] = None,
        user_instructions: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Compose a structured prompt for the LLM.
        Returns a dict: {"system": ..., "user": ...}
        """
        # System prompt
        system_prompt = self.system_role

        # User prompt: always output attendee count, pipeline, opportunities, key contacts, and notable accounts
        user_prompt = ""
        # Always show these fields if present
        for key in ["Number of attendees", "Pipeline", "Number of opportunities"]:
            if key in normalized_metrics:
                val = normalized_metrics[key]["value"]
                user_prompt += f"{key}: {val}\n"
        # Output all other metrics as before
        if normalized_metrics:
            user_prompt += "Key Metrics (normalized):\n"
            for name, meta in normalized_metrics.items():
                if name in ["Number of attendees", "Pipeline", "Number of opportunities"]:
                    continue
                val = meta.get("value")
                valid = meta.get("valid")
                cat = meta.get("category")
                # Never mark these as invalid in the prompt
                user_prompt += f"- {name}: {val} ({cat})\n"
        if strategic_tags:
            user_prompt += "\nStrategic Tags: " + ", ".join(strategic_tags) + "\n"
        if historical_context:
            user_prompt += "\nHistorical Comparisons:\n"
            for rec in historical_context:
                summary = rec.get("summary")
                campaign = rec.get("campaign")
                ts = rec.get("timestamp")
                user_prompt += f"- {campaign or 'Previous'} ({ts or 'n/a'}): {summary}\n"
        if user_instructions:
            user_prompt += f"\nUser Instructions:\n{user_instructions}\n"
        return {"system": system_prompt, "user": user_prompt.strip()}
