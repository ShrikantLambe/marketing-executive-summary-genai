from pyairtable import Table
from data_models.marketing_objects import Campaign, Attendee, Response, Activity, Contact, Account, Opportunity
from typing import List
import os
from datetime import datetime

# Set these as environment variables or replace directly
API_TOKEN = os.getenv("AIRTABLE_TOKEN")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")

if not API_TOKEN or not BASE_ID:
    raise EnvironmentError(
        "Missing AIRTABLE_TOKEN or AIRTABLE_BASE_ID environment variable. Set them securely before running.")

TABLES = {
    "Campaigns": Campaign,
    "Accounts": Account,
    "Contacts": Contact,
    "Attendees": Attendee,
    "Responses": Response,
    "Activities": Activity,
    "Opportunities": Opportunity,
}


def load_airtable_table(table_name: str, model) -> List:
    try:
        table = Table(API_TOKEN, BASE_ID, table_name)
        records = table.all()
    except Exception as e:
        print(f"Error loading table '{table_name}' from Airtable: {e}")
        return []
    objs = []
    for rec in records:
        fields = rec['fields']
        for k, v in fields.items():
            if 'date' in k.lower() and isinstance(v, str):
                fields[k] = parse_datetime(v)
        try:
            objs.append(model(**fields))
        except Exception as e:
            print(f"Error parsing {fields} for {table_name}: {e}")
    return objs


def load_all_airtable():
    data = {}
    for table_name, model in TABLES.items():
        data[table_name.lower()] = load_airtable_table(table_name, model)
    return data


def parse_datetime(dt_str):
    """Parse ISO8601 or common date formats from Airtable fields."""
    try:
        # Try ISO8601 first
        return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except Exception:
        try:
            # Try common formats
            return datetime.strptime(dt_str, "%Y-%m-%d")
        except Exception:
            return dt_str  # Return original if parsing fails


if __name__ == "__main__":
    all_data = load_all_airtable()
    for k, v in all_data.items():
        print(f"Loaded {len(v)} records for {k}")
