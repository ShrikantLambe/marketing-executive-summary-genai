import pandas as pd
from data_models.marketing_objects import Campaign, Attendee, Response, Activity, Contact, Account, Opportunity
from typing import List
from datetime import datetime, timedelta
import random
import uuid
from faker import Faker

faker = Faker()
Faker.seed(42)

# Dummy data generation utilities


def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))


def generate_campaigns(n=8) -> List[Campaign]:
    base_date = datetime.now()
    campaign_types = [
        "Executive Roundtable", "Product Launch", "Webinar Series", "Customer Summit",
        "Industry Conference", "Partner Enablement", "Thought Leadership", "Innovation Forum"
    ]
    return [
        Campaign(
            id=str(uuid.uuid4()),
            name=f"{faker.bs().title()} {random.choice(campaign_types)}",
            start_date=base_date - timedelta(days=30*i),
            end_date=base_date - timedelta(days=30*i-10),
            description=faker.sentence(nb_words=10)
        ) for i in range(n)
    ]


def generate_accounts(n=10) -> List[Account]:
    real_companies = [
        "Google", "Microsoft", "Amazon", "Apple", "Meta", "Tesla", "Netflix", "Salesforce",
        "Adobe", "Oracle", "IBM", "Coca-Cola", "PepsiCo", "Nike", "Walmart", "Pfizer"
    ]
    industries = ["Tech", "Finance", "Retail",
                  "Healthcare", "Manufacturing", "CPG", "Automotive"]
    regions = ["NA", "EMEA", "APAC", "LATAM"]
    return [
        Account(
            id=str(uuid.uuid4()),
            name=random.choice(real_companies),
            industry=random.choice(industries),
            region=random.choice(regions)
        ) for _ in range(n)
    ]


def generate_contacts(accounts: List[Account], n=30) -> List[Contact]:
    departments = ["Marketing", "Sales", "Product",
                   "Engineering", "Finance", "HR", "Customer Success"]
    return [
        Contact(
            id=str(uuid.uuid4()),
            name=faker.name(),
            email=faker.email(),
            lead=bool(random.getrandbits(1)),
            account_id=random.choice(accounts).id
        ) for _ in range(n)
    ]


def generate_attendees(campaigns: List[Campaign], contacts: List[Contact], n=40) -> List[Attendee]:
    return [
        Attendee(
            id=str(uuid.uuid4()),
            name=contact.name,
            email=contact.email,
            campaign_id=random.choice(campaigns).id,
            account_id=contact.account_id
        ) for contact in random.sample(contacts, min(n, len(contacts)))
    ]


def generate_responses(attendees: List[Attendee], campaigns: List[Campaign], n=80) -> List[Response]:
    response_types = ["registered", "attended",
                      "no-show", "interested", "declined", "waitlisted"]
    return [
        Response(
            id=str(uuid.uuid4()),
            attendee_id=random.choice(attendees).id,
            campaign_id=random.choice(campaigns).id,
            response_type=random.choice(response_types),
            timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
        ) for _ in range(n)
    ]


def generate_activities(attendees: List[Attendee], campaigns: List[Campaign], n=60) -> List[Activity]:
    activity_types = ["email_open", "click",
                      "meeting", "demo", "call", "webinar_join"]
    return [
        Activity(
            id=str(uuid.uuid4()),
            campaign_id=random.choice(campaigns).id,
            attendee_id=random.choice(attendees).id,
            type=random.choice(activity_types),
            timestamp=datetime.now() - timedelta(days=random.randint(0, 30))
        ) for _ in range(n)
    ]


def generate_opportunities(accounts: List[Account], campaigns: List[Campaign], n=20) -> List[Opportunity]:
    stages = ["Open", "In Progress", "Closed Won", "Closed Lost"]
    return [
        Opportunity(
            id=str(uuid.uuid4()),
            account_id=random.choice(accounts).id,
            campaign_id=random.choice(campaigns).id,
            amount=round(random.uniform(5000, 250000), 2),
            stage=random.choice(stages),
            close_date=datetime.now() + timedelta(days=random.randint(10, 90))
        ) for _ in range(n)
    ]
