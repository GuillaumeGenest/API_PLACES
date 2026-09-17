from sqlalchemy import Column, Integer, Text, BigInteger, ARRAY, String
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional
from app.core.database import Base

class Country_info(Base):
    __tablename__ = "country_travel_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    country_code = Column(String(2), unique=True, nullable=False)
    capital = Column(Text, nullable=False)
    population = Column(BigInteger)
    currency = Column(Text, nullable=False)
    currency_symbol = Column(Text, nullable=False)
    phone_code = Column(Text, nullable=False)
    utc_offset = Column(Integer, nullable=False)
    visa = Column(Text)
    climate = Column(Text)
    religion = Column(Text)
    culinary_customs = Column(ARRAY(Text))
    social_customs = Column(ARRAY(Text))
    politeness_phrases = Column(JSONB)
    basic_vocabulary = Column(JSONB)
    numbers = Column(JSONB)
    emergency_numbers = Column(JSONB)


class CountryInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country_code: str
    capital: str
    population: Optional[int] = None
    currency: str
    currency_symbol: str
    phone_code: str
    utc_offset: int
    visa: Optional[str] = None
    climate: Optional[str] = None
    religion: Optional[str] = None
    culinary_customs: Optional[List[str]] = None
    social_customs: Optional[List[str]] = None
    politeness_phrases: Optional[Dict] = None
    basic_vocabulary: Optional[Dict] = None
    numbers: Optional[Dict] = None
    emergency_numbers: Optional[Dict] = None