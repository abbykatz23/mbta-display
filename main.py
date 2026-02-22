import asyncio
from datetime import datetime, timedelta
from dateutil.tz import tzoffset

from mbta_client import MBTAClient
from enums import StationID, RouteID, TextColor
from display import Display
from settings import COMMUTE_TIMES

INTERVAL_SECONDS = 20
EST = tzoffset(None, -18000)
ARRIVAL_ANIMATION_COOLDOWN_MINUTES = 3


async def poll_loop(mbta_client: MBTAClient, display: Display):
    last_animation_at_by_station: dict[StationID, datetime] = {}

    while True:
        try:
            now = datetime.now(EST)

            (
                b_currently_arriving,
                b_min_to_nct_1,
                b_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.PARK_STREET_B, now, COMMUTE_TIMES[StationID.PARK_STREET_B]
            )
            (
                c_currently_arriving,
                c_min_to_nct_1,
                c_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.PARK_STREET_C, now, COMMUTE_TIMES[StationID.PARK_STREET_C]
            )
            (
                d_currently_arriving,
                d_min_to_nct_1,
                d_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.PARK_STREET_D, now, COMMUTE_TIMES[StationID.PARK_STREET_D]
            )
            (
                e_currently_arriving,
                e_min_to_nct_1,
                e_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.PARK_STREET_E, now, COMMUTE_TIMES[StationID.PARK_STREET_E]
            )

            (
                north_d_currently_arriving,
                north_d_min_to_nct_1,
                north_d_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.PARK_STREET_NORTH,
                now,
                COMMUTE_TIMES[StationID.PARK_STREET_NORTH],
                RouteID.GREEN_D,
            )

            (
                north_e_currently_arriving,
                north_e_min_to_nct_1,
                north_e_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.PARK_STREET_NORTH,
                now,
                COMMUTE_TIMES[StationID.PARK_STREET_NORTH],
                RouteID.GREEN_E,
            )

            (
                alewife_currently_arriving,
                alewife_min_to_nct_1,
                alewife_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.CHARLES_MGH_ALEWIFE, now, COMMUTE_TIMES[StationID.CHARLES_MGH_ALEWIFE]
            )

            (
                ashmont_braintree_currently_arriving,
                ashmont_braintree_min_to_nct_1,
                ashmont_braintree_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.CHARLES_MGH_ASHMONT_BRAINTREE, now, COMMUTE_TIMES[StationID.CHARLES_MGH_ASHMONT_BRAINTREE]
            )

            (
                won_currently_arriving,
                won_min_to_nct_1,
                won_min_to_nct_2,
            ) = mbta_client.get_eol_predictions_of_interest(
                StationID.BOWDOIN_WONDERLAND, now, COMMUTE_TIMES[StationID.BOWDOIN_WONDERLAND]
            )

            (
                ol_n_currently_arriving,
                ol_n_min_to_nct_1,
                ol_n_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.DTC_OL_OAK_GROVE, now, COMMUTE_TIMES[StationID.DTC_OL_OAK_GROVE]
            )

            (
                ol_s_currently_arriving,
                ol_s_min_to_nct_1,
                ol_s_min_to_nct_2,
            ) = mbta_client.get_predictions_of_interest(
                StationID.DTC_OL_FOREST_HILLS, now, COMMUTE_TIMES[StationID.DTC_OL_FOREST_HILLS]
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

            arrivals_to_animate: list[tuple[tuple[int, int, int], tuple[int, int]]] = []

            def should_animate(station_key: StationID) -> bool:
                last_animation_at = last_animation_at_by_station.get(station_key)
                if (
                    last_animation_at is not None
                    and now - last_animation_at <= timedelta(minutes=ARRIVAL_ANIMATION_COOLDOWN_MINUTES)
                ):
                    return False
                last_animation_at_by_station[station_key] = now
                return True

            if ashmont_braintree_currently_arriving and should_animate(StationID.CHARLES_MGH_ASHMONT_BRAINTREE):
                arrivals_to_animate.append((TextColor.RED.value, display.BOTTOM_RIGHT_ALERT_LOCATION))
            if ol_s_currently_arriving and should_animate(StationID.DTC_OL_FOREST_HILLS):
                arrivals_to_animate.append((TextColor.ORANGE.value, display.BOTTOM_RIGHT_ALERT_LOCATION))

            bottom_right_green_station_ids = [
                StationID.PARK_STREET_B if b_currently_arriving else None,
                StationID.PARK_STREET_C if c_currently_arriving else None,
                StationID.PARK_STREET_D if d_currently_arriving else None,
                StationID.PARK_STREET_E if e_currently_arriving else None,
            ]
            if any(station_id and should_animate(station_id) for station_id in bottom_right_green_station_ids):
                arrivals_to_animate.append((TextColor.GREEN.value, display.BOTTOM_RIGHT_ALERT_LOCATION))

            if alewife_currently_arriving and should_animate(StationID.CHARLES_MGH_ALEWIFE):
                arrivals_to_animate.append((TextColor.RED.value, display.TOP_LEFT_ALERT_LOCATION))
            if ol_n_currently_arriving and should_animate(StationID.DTC_OL_OAK_GROVE):
                arrivals_to_animate.append((TextColor.ORANGE.value, display.TOP_LEFT_ALERT_LOCATION))
            if won_currently_arriving and should_animate(StationID.BOWDOIN_WONDERLAND):
                arrivals_to_animate.append((TextColor.BLUE.value, display.TOP_LEFT_ALERT_LOCATION))

            top_left_green_station_ids = [
                StationID.PARK_STREET_NORTH if north_d_currently_arriving else None,
                StationID.PARK_STREET_NORTH if north_e_currently_arriving else None,
            ]
            if any(station_id and should_animate(station_id) for station_id in top_left_green_station_ids):
                arrivals_to_animate.append((TextColor.GREEN.value, display.TOP_LEFT_ALERT_LOCATION))

            if arrivals_to_animate:
                display.blink_and_animate_arrivals(arrivals_to_animate)

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
