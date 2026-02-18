"""
metric_normalizer.py

Provides normalization utilities for mapping raw metric names to canonical business definitions
using the semantic abstraction layer. This enables consistent analytics and reporting across sources.
"""
from .ontology import get_metric
from .schema import MarketingMetric
from typing import Optional, Dict, Any


def normalize_metric_name(raw_name: str) -> Optional[MarketingMetric]:
    """
    Normalize a raw metric name or alias to its canonical MarketingMetric definition.
    Returns None if no match is found.
    """
    try:
        return get_metric(raw_name)
    except KeyError:
        return None


def _tag_category(metric_name: str) -> str:
    """
    Tag the metric by business category for downstream analytics.
    """
    name = metric_name.lower()
    if name in {"cac", "customer acquisition cost", "acquisition cost"}:
        return "acquisition"
    if name in {"ltv", "lifetime value", "customer lifetime value"}:
        return "revenue"
    if name in {"roas", "return on ad spend"}:
        return "revenue"
    if name in {"ctr", "click through rate"}:
        return "acquisition"
    if name in {"conversion rate", "cr"}:
        return "acquisition"
    return "other"


def _validate_range(metric: MarketingMetric, value: Any) -> bool:
    """
    Validate the value for the metric based on type and reasonable business ranges.
    """
    try:
        if metric.is_ratio or (metric.unit and metric.unit == "%"):
            v = float(value)
            return 0 <= v <= 100
        if metric.unit == "$":
            v = float(value)
            return v >= 0
        # For ratios (e.g., ROAS), allow any positive float
        if metric.unit == "ratio":
            v = float(value)
            return v >= 0
        # Default: just check it's a number
        float(value)
        return True
    except Exception:
        return False


def normalize_marketing_metrics(raw_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a dict of raw marketing metrics:
    - Map aliases to canonical names
    - Validate numeric ranges
    - Enrich with semantic metadata
    - Tag by business category
    Returns a dict: {canonical_name: {value, valid, metadata, category}}
    """
    result = {}
    for raw_name, value in raw_input.items():
        metric = normalize_metric_name(raw_name)
        if not metric:
            # Treat non-canonical metrics (e.g., attendee count, pipeline) as valid if they are numbers
            try:
                float_val = float(value)
                valid = True
            except Exception:
                valid = False
            result[raw_name] = {"value": value, "valid": valid, "error": "Unknown metric" if not valid else None, "category": "other"}
            continue
        valid = _validate_range(metric, value)
        category = _tag_category(metric.name)
        result[metric.name] = {
            "value": value,
            "valid": valid,
            "metadata": metric.dict(),
            "category": category
        }
    return result

# -------------------
# Inline unit tests (pytest style)
# -------------------


def test_normalize_marketing_metrics():
    raw = {
        "customer acquisition cost": 120.5,
        "LTV": 9000,
        "roas": 3.2,
        "Click Through Rate": 2.5,
        "Conversion Rate": 105,  # invalid
        "unknown_metric": 42
    }
    norm = normalize_marketing_metrics(raw)
    assert norm["CAC"]["valid"] is True
    assert norm["LTV"]["valid"] is True
    assert norm["ROAS"]["valid"] is True
    assert norm["CTR"]["valid"] is True
    assert norm["Conversion Rate"]["valid"] is False  # >100% invalid
    assert norm["unknown_metric"]["valid"] is False
    assert norm["CAC"]["category"] == "acquisition"
    assert norm["LTV"]["category"] == "revenue"
    assert norm["ROAS"]["category"] == "revenue"
    assert norm["CTR"]["category"] == "acquisition"
    assert norm["Conversion Rate"]["category"] == "acquisition"
    print("All tests passed.")


if __name__ == "__main__":
    test_normalize_marketing_metrics()
