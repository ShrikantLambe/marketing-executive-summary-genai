import pandas as pd
from data_models.marketing_objects import Campaign, Attendee, Response, Activity, Contact, Account, Opportunity
from typing import List, Type, TypeVar
import os

T = TypeVar('T')


def load_from_csv(file_path: str, model: Type[T]) -> List[T]:
    df = pd.read_csv(file_path)
    # Convert NaN to None and floats to str for optional string fields

    def clean_row(row):
        return {k: (str(v) if isinstance(v, float) and not pd.isna(v) and k in ["region", "industry", "description"] else (None if pd.isna(v) else v)) for k, v in row.items()}
    return [model(**clean_row(row)) for row in df.to_dict(orient='records')]

# Example usage:
# campaigns = load_from_csv('dummy_output/campaigns.csv', Campaign)
# accounts = load_from_csv('dummy_output/accounts.csv', Account)

# Add similar functions for JSON if needed
