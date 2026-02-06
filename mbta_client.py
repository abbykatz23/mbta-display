from datetime import datetime
import requests
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urljoin

from enums import StationID
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

    def _get_prediction(self, station_id: StationID):
        params = {
            "filter[stop]": station_id.value,
            "page[limit]": 10,
            "sort": "arrival_time",
        }
        headers = get_headers()
        res = requests.get(
            self.PREDICTIONS_URL, params=params, headers=headers, verify=False
        )
        res_data = res.json()
        print("res: ", res)
        return PredictionResponse.model_validate(res_data)

    def get_predictions_of_interest(
        self,
        station_id: StationID,
        now: datetime,
        min_to_walk_to_station,  # todo: put walking time to station elsewhere?
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
