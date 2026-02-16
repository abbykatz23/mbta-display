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


class RouteID(Enum):
    GREEN_D = "Green-D"
    GREEN_E = "Green-E"


class TextColor(Enum):
    RED = (218, 41, 28)
    ORANGE = (237, 139, 0)
    GREEN = (0, 132, 61)
    BLUE = (0, 61, 165)


class AnimationDirection(StrEnum):
    LEFT_TO_RIGHT = "left_to_right"
    RIGHT_TO_LEFT = "right_to_left"
