
# --- Modular Executive Summary Generation Pipeline ---
# Raw Input -> Semantic Normalization -> Context Enrichment -> Prompt Builder -> LLM Call

import openai
import os
from typing import List, Dict, Any
from data_models.marketing_objects import Campaign, Attendee, Response, Activity, Contact, Account, Opportunity
from semantic_layer.metric_normalizer import normalize_marketing_metrics
from context_layer.narrative_memory import NarrativeMemory
from context_layer.retrieval_engine import RetrievalEngine
from context_layer.context_builder import ContextBuilder
from genai.prompt_builder import PromptBuilder

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable not set. Please set it in your environment.")
openai.api_key = OPENAI_API_KEY


def _extract_raw_metrics(campaigns, attendees, responses, activities, contacts, accounts, opportunities) -> Dict[str, Any]:
    metrics = {}
    # Example calculations (customize as needed for your business logic):
    metrics["Number of attendees"] = len(attendees)
    metrics["Number of opportunities"] = len(opportunities)
    metrics["Pipeline"] = sum(getattr(o, 'amount', 0) for o in opportunities)
    # Calculate CAC, LTV, ROAS, CTR, Conversion Rate if possible
    # CAC: Total marketing spend / new customers (stub: use opportunity count as proxy)
    if len(opportunities) > 0:
        metrics["customer acquisition cost"] = metrics["Pipeline"] / len(opportunities)
    # LTV: Use opportunity value as proxy
    metrics["LTV"] = metrics["Pipeline"] / len(attendees) if attendees else 0
    # ROAS: Revenue from ads / ad spend (stub: use pipeline as revenue, divide by 1 for demo)
    metrics["roas"] = metrics["Pipeline"] / 1 if metrics["Pipeline"] else 0
    # CTR: Clicks / Impressions (stub: use activities as clicks, attendees as impressions)
    metrics["Click Through Rate"] = (len(activities) / len(attendees) * 100) if attendees else 0
    # Conversion Rate: Opportunities / attendees
    metrics["Conversion Rate"] = (len(opportunities) / len(attendees) * 100) if attendees else 0
    return metrics


def generate_summary(
    campaigns: List[Campaign],
    attendees: List[Attendee],
    responses: List[Response],
    activities: List[Activity],
    contacts: List[Contact],
    accounts: List[Account],
    opportunities: List[Opportunity],
    program_name: str = None,
    user_prompt: str = None,
    debug: bool = False,
    business_id: str = None
) -> str:
    """
    Executive summary pipeline:
    Raw Input -> Semantic Normalization -> Context Enrichment -> Prompt Builder -> LLM Call
    """
    # 1. Semantic Normalization
    raw_metrics = _extract_raw_metrics(
        campaigns, attendees, responses, activities, contacts, accounts, opportunities)
    normalized_metrics = normalize_marketing_metrics(raw_metrics)
    strategic_tags = list(
        {meta["category"] for meta in normalized_metrics.values() if "category" in meta})

    # 2. Context Enrichment
    memory = NarrativeMemory()
    retriever = RetrievalEngine()
    context_builder = ContextBuilder(memory, retriever)
    # For demo: retrieve historical context using a key metric or campaign name
    hist_context = context_builder.build_context(
        user_query=program_name or "", business_id=business_id)
    historical_comparisons = hist_context.get("retrieved", [])


    # --- Extract key contacts and notable accounts ---
    key_contacts = []
    for att in attendees:
        for c in contacts:
            if att.name == c.name and att.email == c.email:
                key_contacts.append(f"{c.name} ({c.email})")
                break
        if len(key_contacts) >= 3:
            break
    if not key_contacts and attendees:
        key_contacts = [f"{a.name} ({a.email})" for a in attendees[:3]]

    attendee_account_ids = set(a.account_id for a in attendees if a.account_id)
    notable_accounts = [a.name for a in accounts if a.id in attendee_account_ids]

    # 3. Prompt Builder
    prompt_builder = PromptBuilder()
    # Inject key contacts and accounts into user instructions if not already present
    extra_context = ""
    if key_contacts:
        extra_context += "\nKey Contacts:\n" + '\n'.join(key_contacts)
    if notable_accounts:
        extra_context += f"\nNotable Accounts: {', '.join(notable_accounts)}"
    combined_user_prompt = (user_prompt or "") + extra_context
    prompt_dict = prompt_builder.build_prompt(
        normalized_metrics=normalized_metrics,
        strategic_tags=strategic_tags,
        historical_context=historical_comparisons,
        user_instructions=combined_user_prompt
    )

    if debug:
        print("[DEBUG] System prompt:\n", prompt_dict["system"])
        print("[DEBUG] User prompt:\n", prompt_dict["user"])

    # 4. LLM Call (business logic separated)
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        chat_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt_dict["system"]},
                {"role": "user", "content": prompt_dict["user"]}
            ],
            max_tokens=400
        )
        return chat_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Exception during OpenAI call: {e}")
        return "[ERROR] Failed to generate summary. Please check your OpenAI API key and try again."
