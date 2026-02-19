import openai
import os
from typing import List
from data_models.marketing_objects import Campaign, Attendee, Response, Activity, Contact, Account, Opportunity


# Set your OpenAI API key as an environment variable ONLY
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "OPENAI_API_KEY environment variable not set. Please set it in your environment.")
openai.api_key = OPENAI_API_KEY


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
    debug: bool = True
) -> str:
    """
    Generate an executive summary using OpenAI GPT based on provided marketing data.
    """
    # Prepare a prompt with key metrics and context, plus key contacts and notable accounts
    # Get up to 3 key contacts (attendees with matching contacts)
    key_contacts = []
    for att in attendees:
        for c in contacts:
            if att.name == c.name and att.email == c.email:
                key_contacts.append(f"- {c.name} ({c.email})")
                break
        if len(key_contacts) >= 3:
            break
    if not key_contacts and attendees:
        # fallback: just use up to 3 attendees
        key_contacts = [f"- {a.name} ({a.email})" for a in attendees[:3]]

    # Get notable accounts (accounts of attendees)
    attendee_account_ids = set(
        [a.account_id for a in attendees if a.account_id])
    notable_accounts = [
        a.name for a in accounts if a.id in attendee_account_ids]
    notable_accounts_str = ', '.join(
        notable_accounts[:5]) if notable_accounts else 'N/A'

    prompt = (
        f"Generate an executive-ready summary for the following marketing program"
        f"{f' ({program_name})' if program_name else ''}.\n\n"
        f"Key Data:\n"
        f"- Number of campaigns: {len(campaigns)}\n"
        f"- Number of attendees: {len(attendees)}\n"
        f"- Number of responses: {len(responses)}\n"
        f"- Number of activities: {len(activities)}\n"
        f"- Number of contacts/leads: {len(contacts)}\n"
        f"- Number of accounts: {len(accounts)}\n"
        f"- Number of opportunities: {len(opportunities)}\n\n"
        f"Key Contacts (for visibility):\n"
        + '\n'.join(key_contacts)
        + f"\n\nNotable Accounts Attending: {notable_accounts_str}\n"
    )
    if user_prompt:
        prompt += f"\nUser Instructions:\n{user_prompt}\n"

    if debug:
        print("[DEBUG] Prompt sent to OpenAI:\n", prompt)
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        chat_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful marketing analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=400
        )
        return chat_response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[ERROR] Exception during OpenAI call: {e}")
        return f"[ERROR] Exception during OpenAI call: {e}"
