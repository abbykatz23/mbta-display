import asyncio
import os
from datetime import datetime
from dateutil.tz import tzoffset
from typing import Optional

from pyfiglet import figlet_format
from termcolor import colored

from models import PredictionResponse
from mbta_client import MBTAClient
from enums import StationID


INTERVAL_SECONDS = 20


async def poll_loop(client: MBTAClient):
    while True:
        try:
            time_zone = -18000
            tz = tzoffset(None, time_zone)
            now = datetime.now(tz)

            charles_mgh_alewife_prediction = client.get_prediction(StationID.CHARLES_MGH_ALEWIFE)
            charles_mgh_ashmont_braintree_prediction = client.get_prediction(StationID.CHARLES_MGH_ASHMONT_BRAINTREE)
            arrival_time_alewife: Optional[datetime] = None

            #todo: add a file where you can specify the stations you want instead of hardcoding them

            i = 0
            while i < 10:
                next_arrival = charles_mgh_alewife_prediction.data[i].attributes.arrival_time
                if next_arrival and next_arrival > now:
                    arrival_time_alewife = next_arrival
                    break
                i += 1
            time_delta_until_train = arrival_time_alewife - now
            int(time_delta_until_train.total_seconds() // 60) + 1
            print(figlet_format('charles/mgh alewife'))#, charles_mgh_alewife)
            print(figlet_format('charles/mgh ashmont/braintree'))#, charles_mgh_alewife)
            # print('charles/mgh ashmont/braintree', charles_mgh_ashmont_braintree)
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            raise
        except Exception as e:
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
