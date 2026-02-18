"""
insights_engine.py

Detects marketing anomalies, trends, high ROAS, and risk patterns.
Outputs structured insight objects. Rule-based logic, extendable to ML.
"""
from typing import Dict, Any, List

class Insight:
    def __init__(self, type: str, message: str, kpi: str = None, severity: str = "info", details: dict = None):
        self.type = type  # e.g., 'anomaly', 'trend', 'high_roas', 'risk'
        self.message = message
        self.kpi = kpi
        self.severity = severity  # e.g., 'info', 'warning', 'critical'
        self.details = details or {}
    def as_dict(self):
        return {
            "type": self.type,
            "message": self.message,
            "kpi": self.kpi,
            "severity": self.severity,
            "details": self.details
        }

def detect_insights(semantic_data: Dict[str, Any], historical_data: Dict[str, Any]) -> List[Insight]:
    """
    Rule-based detection of anomalies, trends, high ROAS, and risks.
    Returns a list of structured Insight objects.
    """
    insights = []
    # 1. Anomaly: KPI drops > 15% vs historical
    for kpi, meta in semantic_data.items():
        val = meta.get("value")
        hist = meta.get("historical_benchmark")
        if val is not None and hist is not None:
            try:
                pct_change = (float(val) - float(hist)) / float(hist)
                if pct_change < -0.15:
                    insights.append(Insight(
                        type="anomaly",
                        message=f"{kpi} down {pct_change*100:.1f}% vs benchmark",
                        kpi=kpi,
                        severity="warning",
                        details={"current": val, "benchmark": hist, "pct_change": pct_change}
                    ))
            except Exception:
                pass
    # 2. Trend acceleration: KPI up > 20% vs last period
    for kpi, meta in semantic_data.items():
        val = meta.get("value")
        last = meta.get("last_period")
        if val is not None and last is not None:
            try:
                pct_change = (float(val) - float(last)) / float(last)
                if pct_change > 0.2:
                    insights.append(Insight(
                        type="trend_acceleration",
                        message=f"{kpi} accelerated by {pct_change*100:.1f}% vs last period",
                        kpi=kpi,
                        severity="info",
                        details={"current": val, "last_period": last, "pct_change": pct_change}
                    ))
            except Exception:
                pass
    # 3. High ROAS: ROAS > 4
    roas = semantic_data.get("ROAS")
    if roas and roas.get("value") is not None:
        try:
            if float(roas["value"]) > 4:
                insights.append(Insight(
                    type="high_roas",
                    message="ROAS exceeds 4: high return on ad spend",
                    kpi="ROAS",
                    severity="info",
                    details={"roas": roas["value"]}
                ))
        except Exception:
            pass
    # 4. Risk: Conversion Rate < 1% or negative trend
    conv = semantic_data.get("Conversion Rate")
    if conv and conv.get("value") is not None:
        try:
            if float(conv["value"]) < 1:
                insights.append(Insight(
                    type="risk",
                    message="Conversion Rate below 1%",
                    kpi="Conversion Rate",
                    severity="critical",
                    details={"conversion_rate": conv["value"]}
                ))
            last = conv.get("last_period")
            if last is not None and float(conv["value"]) < float(last):
                insights.append(Insight(
                    type="risk",
                    message="Conversion Rate declining vs last period",
                    kpi="Conversion Rate",
                    severity="warning",
                    details={"current": conv["value"], "last_period": last}
                ))
        except Exception:
            pass
    return insights
