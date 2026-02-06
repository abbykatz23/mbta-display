from typing import Any, List, Optional
from datetime import datetime

from pydantic import BaseModel, HttpUrl

from enums import DataType, Revenue, ScheduleRelationship, UpdateType


class JsonApiVersion(BaseModel):
    version: str


class Links(BaseModel):
    first: Optional[HttpUrl] = None
    last: Optional[HttpUrl] = None
    next: Optional[HttpUrl] = None


class PredictionAttributes(BaseModel):
    arrival_time: Optional[datetime]
    arrival_uncertainty: Optional[int]
    departure_time: Optional[datetime]
    departure_uncertainty: Optional[int]
    direction_id: int
    last_trip: bool
    revenue: Revenue
    schedule_relationship: Optional[ScheduleRelationship]
    status: Optional[str]
    stop_sequence: int
    update_type: Optional[UpdateType]


class Relationship(BaseModel):
    id: str
    type: DataType


class Prediction(BaseModel):
    id: str
    attributes: PredictionAttributes
    relationships: Any  # Dict[str, Dict[Literal["data"], Relationship]] -> maybe add this?
    type: DataType


class PredictionResponse(BaseModel):
    data: List[Prediction]
    jsonapi: JsonApiVersion
    links: Optional[Links] = None
