from pydantic_settings import BaseSettings
from enums import StationID


class Settings(BaseSettings):
    mbta_api_key: str
    pixoo_ip_address: str

    model_config = {
        "env_file": ".env"
    }


settings = Settings()

# Commute times in minutes from home to each station
COMMUTE_TIMES = {
    StationID.PARK_STREET_B: 11,
    StationID.PARK_STREET_C: 11,
    StationID.PARK_STREET_D: 11,
    StationID.PARK_STREET_E: 11,
    StationID.PARK_STREET_NORTH: 11,
    StationID.CHARLES_MGH_ALEWIFE: 9,
    StationID.CHARLES_MGH_ASHMONT_BRAINTREE: 9,
    StationID.BOWDOIN_WONDERLAND: 9,
    StationID.DTC_OL_FOREST_HILLS: 13,
    StationID.DTC_OL_OAK_GROVE: 13
}
