import requests
from typing import Optional, Dict, Any
from urllib.parse import urljoin

from enums import StationID
from settings import settings
from models import PredictionResponse


def get_headers(headers: Optional[Dict[str, Any]] = None):
    base = {"x-api-key": settings.mbta_api_key}
    return {**base, **(headers or {})}


class MBTAClient():
    MBTA_BASE_URL = "https://api-v3.mbta.com"
    PREDICTIONS_URL = urljoin(MBTA_BASE_URL, '/predictions')

    def get_prediction(self, station_id: StationID):
        params = {'filter[stop]': station_id.value, 'page[limit]': 5, 'sort': 'arrival_time'}
        headers = get_headers()
        res = requests.get(self.PREDICTIONS_URL, params=params, headers=headers, verify=False)
        res_data = res.json()
        print('res: ', res)
        return PredictionResponse.model_validate(res_data)
