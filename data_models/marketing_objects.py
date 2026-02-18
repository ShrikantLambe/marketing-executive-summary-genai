from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Campaign(BaseModel):
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    description: Optional[str]


class Attendee(BaseModel):
    id: str
    name: str
    email: str
    campaign_id: str
    account_id: Optional[str]


class Response(BaseModel):
    id: str
    attendee_id: str
    campaign_id: str
    response_type: str  # e.g., registered, attended, no-show
    timestamp: datetime


class Activity(BaseModel):
    id: str
    campaign_id: str
    attendee_id: Optional[str]
    type: str  # e.g., email_open, click, meeting
    timestamp: datetime


class Contact(BaseModel):
    id: str
    name: str
    email: str
    lead: bool
    account_id: Optional[str]


class Account(BaseModel):
    id: str
    name: str
    industry: Optional[str]
    region: Optional[str]


class Opportunity(BaseModel):
    id: str
    account_id: str
    campaign_id: Optional[str]
    amount: float
    stage: str
    close_date: Optional[datetime]
