"""
schema.py

Defines the core schema for the semantic abstraction layer for marketing metrics.
This layer provides canonical, extensible business definitions for key marketing metrics,
allowing downstream systems to reason about metrics in a consistent, production-ready way.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class MarketingMetric(BaseModel):
    """
    Canonical definition of a marketing metric for the semantic layer.
    This abstraction enables consistent metric handling, normalization, and extension.
    """
    name: str = Field(..., description="Canonical metric name (e.g., CAC, LTV)")
    description: str = Field(..., description="Business definition of the metric")
    formula: Optional[str] = Field(None, description="Formula for calculating the metric, if applicable")
    aliases: List[str] = Field(default_factory=list, description="Alternative names or synonyms for the metric")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., $, %, ratio)")
    is_ratio: bool = Field(False, description="True if the metric is a ratio or percentage")
