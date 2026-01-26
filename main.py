import asyncio
import os

from models import PredictionResponse
from mbta_client import MBTAClient
from enums import StationID


INTERVAL_SECONDS = 30


async def poll_loop(mbta_client: MBTAClient):
    while True:
        try:
            client = MBTAClient()
            res = client.get_prediction(StationID.CHARLES_MGH_ALEWIFE)
            print('res: ', res)
        except asyncio.CancelledError:
            raise
        except Exception:
            await asyncio.sleep(10)


async def main():
    mbta_client = MBTAClient()
    task = asyncio.create_task(poll_loop(mbta_client))
    try:
        await task
    except asyncio.CancelledError:
        print('cancelled')

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
