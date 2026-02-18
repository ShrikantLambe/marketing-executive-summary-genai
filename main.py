from data_ingestion.dummy_data import (
    generate_campaigns, generate_accounts, generate_contacts, generate_attendees,
    generate_responses, generate_activities, generate_opportunities
)


def main():
    # Generate dummy data
    campaigns = generate_campaigns()
    accounts = generate_accounts()
    contacts = generate_contacts(accounts)
    attendees = generate_attendees(campaigns, contacts)
    responses = generate_responses(attendees, campaigns)
    activities = generate_activities(attendees, campaigns)
    opportunities = generate_opportunities(accounts, campaigns)

    print(f"Generated {len(campaigns)} campaigns")
    print(f"Generated {len(accounts)} accounts")
    print(f"Generated {len(contacts)} contacts/leads")
    print(f"Generated {len(attendees)} attendees")
    print(f"Generated {len(responses)} responses")
    print(f"Generated {len(activities)} activities")
    print(f"Generated {len(opportunities)} opportunities")

    # Save dummy data to CSV files
    import pandas as pd
    import os
    output_dir = "dummy_output"
    os.makedirs(output_dir, exist_ok=True)

    pd.DataFrame([c.dict() for c in campaigns]).to_csv(
        f"{output_dir}/campaigns.csv", index=False)
    pd.DataFrame([a.dict() for a in accounts]).to_csv(
        f"{output_dir}/accounts.csv", index=False)
    pd.DataFrame([c.dict() for c in contacts]).to_csv(
        f"{output_dir}/contacts.csv", index=False)
    pd.DataFrame([a.dict() for a in attendees]).to_csv(
        f"{output_dir}/attendees.csv", index=False)
    pd.DataFrame([r.dict() for r in responses]).to_csv(
        f"{output_dir}/responses.csv", index=False)
    pd.DataFrame([a.dict() for a in activities]).to_csv(
        f"{output_dir}/activities.csv", index=False)
    pd.DataFrame([o.dict() for o in opportunities]).to_csv(
        f"{output_dir}/opportunities.csv", index=False)
    print(f"Dummy data saved to '{output_dir}/' as CSV files.")

    # Generate executive summary using GenAI
    from genai.summary import generate_summary
    summary = generate_summary(
        campaigns=campaigns,
        attendees=attendees,
        responses=responses,
        activities=activities,
        contacts=contacts,
        accounts=accounts,
        opportunities=opportunities,
        program_name=campaigns[0].name if campaigns else None
    )
    print("\nExecutive Summary:\n")
    print(summary)


if __name__ == "__main__":
    main()
