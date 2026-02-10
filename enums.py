from enum import Enum,StrEnum

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

class StationID(Enum):
    CHARLES_MGH_ALEWIFE = 70074
    CHARLES_MGH_ASHMONT_BRAINTREE = 70073
    PARK_STREET_B = 70196
    PARK_STREET_C = 70197
    PARK_STREET_D = 70198
    PARK_STREET_E = 70199
    PARK_STREET_NORTH = 70200
    BOWDOIN_WONDERLAND = 70038
    DTC_OL_OAK_GROVE = 70021
    DTC_OL_FOREST_HILLS = 70020
