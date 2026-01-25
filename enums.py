from enum import StrEnum


class DataType(StrEnum):
    PREDICTION = "prediction"
    ROUTE = "route"
    STOP = "stop"
    TRIP = "trip"
    VEHICLE = "vehicle"



class UpdateType(StrEnum):
    REVERSE_TRIP = "REVERSE_TRIP"
    MID_TRIP = "MID_TRIP"
    AT_TERMINAL = "AT_TERMINAL"


class ScheduleRelationship(StrEnum):
    ADDED = "ADDED"
    CANCELLED = "CANCELLED"

class Revenue(StrEnum):
    REVENUE = "REVENUE"

class Status(StrEnum):
    dummy = "DUMMY" #havent seen this filled out in the response yet
