from datetime import datetime
import requests
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urljoin

from enums import RouteID, StationID
from settings import settings
from models import PredictionResponse


def get_headers(headers: Optional[Dict[str, Any]] = None):
    base = {"x-api-key": settings.mbta_api_key}
    return {**base, **(headers or {})}


def train_is_arriving(now, train_arrival_time):
    # todo: will need to figure out how to make sure a given arrival is only signaled one time -> use train ID or something?
    time_delta_until_train = train_arrival_time - now
    return abs(int(time_delta_until_train.total_seconds())) <= 60


class MBTAClient:
    MBTA_BASE_URL = "https://api-v3.mbta.com"
    PREDICTIONS_URL = urljoin(MBTA_BASE_URL, "/predictions")

    def _get_prediction(self, station_id: StationID, limit=10):
        params = {
            "filter[stop]": station_id.value,
            "page[limit]": limit,
            "sort": "arrival_time",
        }
        headers = get_headers()
        res = requests.get(
            self.PREDICTIONS_URL, params=params, headers=headers, verify=False
        )
        res_data = res.json()
        print("res: ", res)
        return PredictionResponse.model_validate(res_data)

    def get_predictions_of_interest_gl_n(
            self,
            now: datetime,
            min_to_walk_to_station: int
    ) -> Tuple[bool, Optional[int], Optional[int], bool, Optional[int], Optional[int]]:
        station_id = StationID.PARK_STREET_NORTH
        #todo: put the specialiszation that this function provides elsewhere, DRY it up
        predictions: PredictionResponse = self._get_prediction(station_id, 30)

        north_d_currently_arriving: bool = (
            False  # todo: improve naming? train_currently_arriving and train_is_arriving -> not great
        )
        north_d_min_to_nct_1: Optional[int] = None
        north_d_min_to_nct_2: Optional[int] = None
        north_e_currently_arriving: bool = (
            False  # todo: improve naming? train_currently_arriving and train_is_arriving -> not great
        )
        north_e_min_to_nct_1: Optional[int] = None
        north_e_min_to_nct_2: Optional[int] = None

        for prediction in predictions.data:
            arrival_time = prediction.attributes.arrival_time
            relationships = prediction.relationships
            e_or_d = None
            if isinstance(relationships, dict) and relationships.get('route'):
                route = relationships.get('route')
                if isinstance(route, dict) and route.get('data'):
                    route_data = route.get('data')
                    if isinstance(route_data, dict):
                        if route_data.get('id') == RouteID.GREEN_D.value:
                            e_or_d = 'd'
                        elif route_data.get('id') == RouteID.GREEN_E.value:
                            e_or_d = 'e'
                    else:
                        continue #todo: flatten all this my god
                else:
                    continue
            else:
                continue

            if arrival_time and e_or_d == 'e':
                if not north_e_currently_arriving and train_is_arriving(
                    now, arrival_time
                ):
                    north_e_currently_arriving = True
                    continue

                min_until_train = int((arrival_time - now).total_seconds() // 60) + 1

                if (
                    not north_e_min_to_nct_1
                    and min_until_train >= min_to_walk_to_station
                ):
                    north_e_min_to_nct_1 = min_until_train

                elif (
                    north_e_min_to_nct_1
                    and not north_e_min_to_nct_2
                    and min_until_train >= min_to_walk_to_station
                ):
                    north_e_min_to_nct_2 = min_until_train
                    if north_d_min_to_nct_2:
                        break

            if arrival_time and e_or_d == 'd':
                if not north_d_currently_arriving and train_is_arriving(
                    now, arrival_time
                ):
                    north_d_currently_arriving = True
                    continue

                min_until_train = int((arrival_time - now).total_seconds() // 60) + 1

                if (
                    not north_d_min_to_nct_1
                    and min_until_train >= min_to_walk_to_station
                ):
                    north_d_min_to_nct_1 = min_until_train

                elif (
                    north_d_min_to_nct_1
                    and not north_d_min_to_nct_2
                    and min_until_train >= min_to_walk_to_station
                ):
                    north_d_min_to_nct_2 = min_until_train
                    if north_e_min_to_nct_2:
                        break

        return (
            north_d_currently_arriving,
            north_d_min_to_nct_1,
            north_d_min_to_nct_2,
            north_e_currently_arriving,
            north_e_min_to_nct_1,
            north_e_min_to_nct_2
        )

    def get_eol_predictions_of_interest(
        self,
        station_id: StationID,
        now: datetime,
        min_to_walk_to_station: int,  # todo: put walking time to station elsewhere?
    ) -> Tuple[bool, Optional[int], Optional[int]]:
        predictions: PredictionResponse = self._get_prediction(station_id)

        train_currently_arriving: bool = (
            False  # todo: improve naming? train_currently_arriving and train_is_arriving -> not great
        )
        mins_until_next_catchable_train: Optional[int] = None
        mins_until_second_next_catchable_train: Optional[int] = None

        for prediction in predictions.data:
            departure_time = prediction.attributes.departure_time
            if departure_time:
                if not train_currently_arriving and train_is_arriving(
                    now, departure_time
                ):
                    train_currently_arriving = True
                    continue

                min_until_train = int((departure_time - now).total_seconds() // 60) + 1

                if (
                    not mins_until_next_catchable_train
                    and min_until_train >= min_to_walk_to_station
                ):
                    mins_until_next_catchable_train = min_until_train

                elif (
                    mins_until_next_catchable_train
                    and not mins_until_second_next_catchable_train
                    and min_until_train >= min_to_walk_to_station
                ):
                    mins_until_second_next_catchable_train = min_until_train
                    break

        return (
            train_currently_arriving,
            mins_until_next_catchable_train,
            mins_until_second_next_catchable_train,
        )


    def get_predictions_of_interest(
        self,
        station_id: StationID,
        now: datetime,
        min_to_walk_to_station: int,  # todo: put walking time to station elsewhere?
    ) -> Tuple[bool, Optional[int], Optional[int]]:
        predictions: PredictionResponse = self._get_prediction(station_id)

        train_currently_arriving: bool = (
            False  # todo: improve naming? train_currently_arriving and train_is_arriving -> not great
        )
        mins_until_next_catchable_train: Optional[int] = None
        mins_until_second_next_catchable_train: Optional[int] = None

        for prediction in predictions.data:
            arrival_time = prediction.attributes.arrival_time
            if arrival_time:
                if not train_currently_arriving and train_is_arriving(
                    now, arrival_time
                ):
                    train_currently_arriving = True
                    continue

                min_until_train = int((arrival_time - now).total_seconds() // 60) + 1

                if (
                    not mins_until_next_catchable_train
                    and min_until_train >= min_to_walk_to_station
                ):
                    mins_until_next_catchable_train = min_until_train

                elif (
                    mins_until_next_catchable_train
                    and not mins_until_second_next_catchable_train
                    and min_until_train >= min_to_walk_to_station
                ):
                    mins_until_second_next_catchable_train = min_until_train
                    break

        return (
            train_currently_arriving,
            mins_until_next_catchable_train,
            mins_until_second_next_catchable_train,
        )
