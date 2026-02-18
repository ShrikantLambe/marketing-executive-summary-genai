"""
Unit tests for NarrativeMemory lightweight memory engine.
"""
from context_layer.narrative_memory import NarrativeMemory

def test_add_and_retrieve_summary():
    mem = NarrativeMemory()
    mem.add_summary("biz1", "Q1 summary: campaign alpha won", campaign="Alpha", timestamp="2026-01-01")
    mem.add_summary("biz1", "Q2 summary: campaign beta lost", campaign="Beta", timestamp="2026-02-01")
    mem.add_summary("biz2", "Q1 summary: campaign gamma won", campaign="Gamma", timestamp="2026-01-15")
    # Retrieve by keyword
    results = mem.retrieve_relevant_context("alpha")
    assert len(results) == 1
    assert results[0]["campaign"] == "Alpha"
    # Retrieve by business_id
    results = mem.retrieve_relevant_context("summary", business_id="biz1")
    assert len(results) == 2
    # Only last 3
    mem.add_summary("biz1", "Q3 summary: campaign delta won", campaign="Delta", timestamp="2026-03-01")
    mem.add_summary("biz1", "Q4 summary: campaign epsilon won", campaign="Epsilon", timestamp="2026-04-01")
    results = mem.retrieve_relevant_context("summary", business_id="biz1", top_k=3)
    assert len(results) == 3
    assert results[0]["campaign"] == "Epsilon"
    assert results[1]["campaign"] == "Delta"
    assert results[2]["campaign"] == "Beta"

def test_legacy_narrative():
    mem = NarrativeMemory()
    mem.add_narrative("bizX", "Legacy narrative")
    assert mem.get_narrative("bizX") == "Legacy narrative"
    assert mem.get_narrative("notfound") == ""
