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

            commute_times = {
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

            (
                gl_north_currently_arriving,
                b_min_to_nct_1,
                b_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.PARK_STREET_B, now, commute_times[StationID.PARK_STREET_B]
            )
            (
                gl_north_currently_arriving,
                c_min_to_nct_1,
                c_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.PARK_STREET_C, now, commute_times[StationID.PARK_STREET_C]
            )
            (
                gl_north_currently_arriving,
                d_min_to_nct_1,
                d_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.PARK_STREET_D, now, commute_times[StationID.PARK_STREET_D]
            )
            (
                gl_north_currently_arriving,
                e_min_to_nct_1,
                e_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.PARK_STREET_E, now, commute_times[StationID.PARK_STREET_E]
            )

            (
                north_d_currently_arriving,
                north_d_min_to_nct_1,
                north_d_min_to_nct_2,
                north_e_currently_arriving,
                north_e_min_to_nct_1,
                north_e_min_to_nct_2
            ) = mbta_client.get_predictions_of_interest_gl_n(
                now, commute_times[StationID.PARK_STREET_NORTH]
            )  #TODO: split these out into northern e and northern d predictions


            (
                alewife_currently_arriving,
                alewife_min_to_nct_1,
                alewife_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.CHARLES_MGH_ALEWIFE, now, commute_times[StationID.CHARLES_MGH_ALEWIFE]
            )

            (
                ashmont_braintree_currently_arriving,
                ashmont_braintree_min_to_nct_1,
                ashmont_braintree_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.CHARLES_MGH_ASHMONT_BRAINTREE, now, commute_times[StationID.CHARLES_MGH_ASHMONT_BRAINTREE]
            )

            (
                won_currently_arriving,
                won_min_to_nct_1,
                won_min_to_nct_2,
            ) = mbta_client.get_eol_predictions_of_interest(
                StationID.BOWDOIN_WONDERLAND, now, commute_times[StationID.BOWDOIN_WONDERLAND]
            )

            (
                ol_n_currently_arriving,
                ol_n_min_to_nct_1,
                ol_n_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.DTC_OL_OAK_GROVE, now, commute_times[StationID.DTC_OL_OAK_GROVE]
            )

            (
                ol_s_currently_arriving,
                ol_s_min_to_nct_1,
                ol_s_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.DTC_OL_FOREST_HILLS, now, commute_times[StationID.DTC_OL_FOREST_HILLS]
            )

            display.display_train_statuses(
                b_min_to_nct_1,
                b_min_to_nct_2,
                c_min_to_nct_1,
                c_min_to_nct_2,
                d_min_to_nct_1,
                d_min_to_nct_2,
                e_min_to_nct_1,
                e_min_to_nct_2,
                north_d_min_to_nct_1,
                north_d_min_to_nct_2,
                north_e_min_to_nct_1,
                north_e_min_to_nct_2,
                alewife_min_to_nct_1,
                alewife_min_to_nct_2,
                ashmont_braintree_min_to_nct_1,
                ashmont_braintree_min_to_nct_2,
                won_min_to_nct_1,
                won_min_to_nct_2,
                ol_n_min_to_nct_1,
                ol_n_min_to_nct_2,
                ol_s_min_to_nct_1,
                ol_s_min_to_nct_2
            )

            await asyncio.sleep(INTERVAL_SECONDS)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            await asyncio.sleep(INTERVAL_SECONDS)


async def main():
    mbta_client = MBTAClient()
    display = Display()
    display.black_screen()
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
