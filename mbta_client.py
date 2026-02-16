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
    time_delta_until_train = train_arrival_time - now
    return abs(int(time_delta_until_train.total_seconds())) <= 60


class MBTAClient:
    MBTA_BASE_URL = "https://api-v3.mbta.com"
    PREDICTIONS_URL = urljoin(MBTA_BASE_URL, "/predictions")

    def _get_prediction(self, station_id: StationID, limit=10, sort_field: str = "arrival_time"):
        params = {
            "filter[stop]": station_id.value,
            "page[limit]": limit,
            "sort": sort_field,
        }
        headers = get_headers()
        res = requests.get(
            self.PREDICTIONS_URL, params=params, headers=headers, verify=False
        )
        res_data = res.json()
        print("res: ", res)
        return PredictionResponse.model_validate(res_data)

    def get_eol_predictions_of_interest(
        self,
        station_id: StationID,
        now: datetime,
        min_to_walk_to_station: int,  # todo: put walking time to station elsewhere?
    ) -> Tuple[bool, Optional[int], Optional[int]]:
        predictions: PredictionResponse = self._get_prediction(
            station_id,
            sort_field="departure_time",
        )

        train_currently_arriving: bool = False
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
        min_to_walk_to_station: int,
        route_id: Optional[RouteID] = None,
    ) -> Tuple[bool, Optional[int], Optional[int]]:
        predictions: PredictionResponse = self._get_prediction(
            station_id, 30 if route_id else 10
        )

        train_currently_arriving: bool = False
        mins_until_next_catchable_train: Optional[int] = None
        mins_until_second_next_catchable_train: Optional[int] = None

        for prediction in predictions.data:
            arrival_time = prediction.attributes.arrival_time
            if not arrival_time:
                continue

            if route_id:
                relationships = prediction.relationships
                if not isinstance(relationships, dict) or not relationships.get('route'):
                    continue
                route = relationships.get('route')

                if not isinstance(route, dict) or not route.get('data'):
                    continue
                route_data = route.get('data')

                if not isinstance(route_data, dict):
                    continue

                if route_data.get('id') != route_id.value:
                    continue

            if not train_currently_arriving and train_is_arriving(now, arrival_time):
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
                and min_until_train > (mins_until_next_catchable_train + 1)
                and min_until_train >= min_to_walk_to_station
            ):
                mins_until_second_next_catchable_train = min_until_train
                break

        return (
            train_currently_arriving,
            mins_until_next_catchable_train,
            mins_until_second_next_catchable_train,
        )
