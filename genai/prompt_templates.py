"""
prompt_templates.py

Provides deterministic, enterprise-ready prompt templates for executive summary generation.
Includes generate_executive_prompt for structured, board-ready LLM prompts.
"""
from typing import Dict, Any

def generate_executive_prompt(semantic_data: Dict[str, Any], contextual_data: Dict[str, Any]) -> str:
    """
    Build a structured prompt for LLMs with:
    1. Executive Overview
    2. KPI Performance (vs historical benchmarks)
    3. Strategic Insights (highlight anomalies)
    4. Risks
    5. Recommendations
    Returns a deterministic, enterprise-ready prompt string.
    """
    # Section 1: Executive Overview
    overview = contextual_data.get("narrative") or "No executive overview available."

    # Section 2: KPI Performance
    kpi_lines = []
    for kpi, meta in semantic_data.items():
        val = meta.get("value")
        valid = meta.get("valid")
        hist = meta.get("historical_benchmark")
        diff = None
        if val is not None and hist is not None:
            try:
                diff = float(val) - float(hist)
            except Exception:
                diff = None
        line = f"- {kpi}: {val}"
        if hist is not None:
            line += f" (Benchmark: {hist})"
        if diff is not None:
            line += f" | Δ: {diff:+.2f}"
        if not valid:
            line += " [Check: Unusual Value]"
        kpi_lines.append(line)
    kpi_section = "\n".join(kpi_lines) if kpi_lines else "No KPI data available."

    # Section 3: Strategic Insights (anomalies)
    anomalies = []
    for kpi, meta in semantic_data.items():
        if meta.get("anomaly"):
            anomalies.append(f"- {kpi}: {meta['anomaly']}")
    if not anomalies:
        anomalies.append("- No significant anomalies detected.")
    insights_section = "\n".join(anomalies)

    # Section 4: Risks
    risks = contextual_data.get("risks") or "No major risks identified."

    # Section 5: Recommendations
    recs = contextual_data.get("recommendations") or "No recommendations available."

    prompt = f"""
Executive Overview:
{overview}

KPI Performance vs Benchmarks:
{kpi_section}

Strategic Insights:
{insights_section}

Risks:
{risks}

Recommendations:
{recs}
"""
    return prompt.strip()
