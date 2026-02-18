"""
ontology.py

Defines the ontology and canonical mapping for marketing metrics in the semantic abstraction layer.
This enables mapping of aliases and synonyms to canonical metric definitions for robust, extensible analytics.
"""
from typing import Dict, List
from .schema import MarketingMetric

# Canonical marketing metrics
CANONICAL_METRICS: Dict[str, MarketingMetric] = {
    "CAC": MarketingMetric(
        name="CAC",
        description="Customer Acquisition Cost: The total cost to acquire a new customer, including marketing and sales expenses.",
        formula="Total Marketing & Sales Spend / Number of New Customers",
        aliases=["customer acquisition cost", "acquisition cost"],
        unit="$",
        is_ratio=False
    ),
    "LTV": MarketingMetric(
        name="LTV",
        description="Lifetime Value: The predicted net profit attributed to the entire future relationship with a customer.",
        formula="Average Revenue per Customer * Gross Margin * Customer Lifespan",
        aliases=["lifetime value", "customer lifetime value", "ltv"],
        unit="$",
        is_ratio=False
    ),
    "ROAS": MarketingMetric(
        name="ROAS",
        description="Return on Ad Spend: Revenue generated for every dollar spent on advertising.",
        formula="Revenue from Ads / Ad Spend",
        aliases=["return on ad spend", "roas"],
        unit="ratio",
        is_ratio=True
    ),
    "CTR": MarketingMetric(
        name="CTR",
        description="Click-Through Rate: The percentage of people who clicked an ad or link out of total impressions.",
        formula="(Clicks / Impressions) * 100",
        aliases=["click through rate", "ctr"],
        unit="%",
        is_ratio=True
    ),
    "Conversion Rate": MarketingMetric(
        name="Conversion Rate",
        description="The percentage of users who take a desired action (e.g., purchase, signup) out of total visitors.",
        formula="(Conversions / Visitors) * 100",
        aliases=["conversion rate", "cr"],
        unit="%",
        is_ratio=True
    ),
}

# Alias map for fast lookup
ALIAS_TO_CANONICAL: Dict[str, str] = {}
for canonical, metric in CANONICAL_METRICS.items():
    ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in metric.aliases:
        ALIAS_TO_CANONICAL[alias.lower()] = canonical

def get_canonical_metric_name(alias: str) -> str:
    """
    Returns the canonical metric name for a given alias or synonym.
    Raises KeyError if not found.
    """
    key = alias.strip().lower()
    if key not in ALIAS_TO_CANONICAL:
        raise KeyError(f"Unknown metric alias: {alias}")
    return ALIAS_TO_CANONICAL[key]

def get_metric(alias: str) -> MarketingMetric:
    """
    Returns the MarketingMetric object for a given alias or canonical name.
    Raises KeyError if not found.
    """
    canonical = get_canonical_metric_name(alias)
    return CANONICAL_METRICS[canonical]
