from typing import Dict, List, Literal, Optional
from datetime import datetime

from pydantic import BaseModel, HttpUrl

from enums import DataType, Revenue, ScheduleRelationship, Status, UpdateType


class JsonApiVersion(BaseModel):
    version: str


class Links(BaseModel):
    first: HttpUrl
    last: HttpUrl
    next: HttpUrl


class PredictionAttributes(BaseModel):
    arrival_time: Optional[datetime]
    arrival_uncertainty: Optional[int]
    departure_time: Optional[datetime]
    departure_uncertainty: Optional[int]
    direction_id: int
    last_trip: bool
    revenue: Revenue
    schedule_relationship: Optional[ScheduleRelationship]
    status: Optional[Status]
    stop_sequence: int
    update_type: UpdateType


class Relationship(BaseModel):
    id: str
    type: DataType


class Prediction(BaseModel):
    id: str
    attributes: PredictionAttributes
    relationships: Dict[str, Dict[Literal["data"], Relationship]]
    type: DataType


class PredictionResponse(BaseModel):
    data: List[Prediction]
    jsonapi: JsonApiVersion
    links: Optional[Links] = None
