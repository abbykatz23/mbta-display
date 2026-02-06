import asyncio
from datetime import datetime
from dateutil.tz import tzoffset
from typing import Optional

from mbta_client import MBTAClient
from enums import StationID
from display import Display

INTERVAL_SECONDS = 20
EST = tzoffset(None, -18000)


async def poll_loop(mbta_client: MBTAClient, display: Display):
    while True:
        try:
            now = datetime.now(EST)

            (
                alewife_currently_arriving,
                alewife_mins_until_next_catchable_train,
                alewife_mins_until_second_next_catchable_train,
            ) = mbta_client.get_predictions_of_interest(
                StationID.CHARLES_MGH_ALEWIFE, now, 9
            )

            (
                ashmont_braintree_currently_arriving,
                ashmont_braintree_mins_until_next_catchable_train,
                ashmont_braintree_mins_until_second_next_catchable_train,
            ) = mbta_client.get_predictions_of_interest(
                StationID.CHARLES_MGH_ASHMONT_BRAINTREE, now, 9
            )

            display.display_train_statuses(
                alewife_mins_until_next_catchable_train,
                alewife_mins_until_second_next_catchable_train,
                ashmont_braintree_mins_until_next_catchable_train,
                ashmont_braintree_mins_until_second_next_catchable_train
            )

            arrival_time_alewife: Optional[datetime] = None

            await asyncio.sleep(INTERVAL_SECONDS)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            await asyncio.sleep(INTERVAL_SECONDS)


async def main():
    mbta_client = MBTAClient()
    display = Display()
    display.black_screen()
    display.push_screen()
    task = asyncio.create_task(poll_loop(mbta_client, display))
    try:
        await task
    except asyncio.CancelledError:
        print("cancelled")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
