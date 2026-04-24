from datetime import date
from typing import Optional

from pydantic import BaseModel


class Address(BaseModel):
    address_line_1: Optional[str] = None
    address_line_2: Optional[str] = None
    locality: Optional[str] = None
    region: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class RawEvent(BaseModel):
    company_number: str
    company_name: str
    incorporated_date: date
    company_type: Optional[str] = None
    registered_office_address: Optional[Address] = None


class EnrichedCompany(BaseModel):
    company_number: str
    company_name: str
    incorporated_date: date
    company_type: Optional[str] = None
    company_status: Optional[str] = None
    registered_office_address: Optional[Address] = None
    region: Optional[str] = None
    company_age_days: Optional[int] = None
    sic_codes: Optional[list[str]] = None


class LeadScore(BaseModel):
    company_number: str
    score: int  # 0-100
    band: str   # low / medium / high
    score_reasons: list[str]


class DeliveryRecord(BaseModel):
    company_number: str
    company_name: str
    event_date: date
    score: int
    band: str
    why_it_matters: Optional[str] = None
    suggested_outreach_line: Optional[str] = None
