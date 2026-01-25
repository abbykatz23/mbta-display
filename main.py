import asyncio
import requests
import os

from models import PredictionResponse


MBTA_API_KEY = os.environ["MBTA_API_KEY"]

headers = {
    "x-api-key": MBTA_API_KEY
}

INTERVAL_SECONDS = 30


async def poll_loop():
    while True:
        try:
            res = requests.get("https://api-v3.mbta.com/predictions?filter[stop]=70073&page[limit]=5&sort=arrival_time", headers=headers, verify=False)
            res_data = res.json()
            normalized_res = PredictionResponse.model_validate(res_data)
            print('res: ', res)
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(10)


async def main():
    task = asyncio.create_task(poll_loop())
    try:
        await task
    except asyncio.CancelledError:
        print('cancelled')

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
