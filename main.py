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

            bottom_right_alert_color = None
            bottom_right_alert_station_key = None
            if (
                ashmont_braintree_currently_arriving
                or ol_s_currently_arriving
                or b_currently_arriving
                or c_currently_arriving
                or d_currently_arriving
                or e_currently_arriving
            ):
                if ashmont_braintree_currently_arriving:
                    bottom_right_alert_color = TextColor.RED.value
                    bottom_right_alert_station_key = StationID.CHARLES_MGH_ASHMONT_BRAINTREE
                elif ol_s_currently_arriving:
                    bottom_right_alert_color = TextColor.ORANGE.value
                    bottom_right_alert_station_key = StationID.DTC_OL_FOREST_HILLS
                else:
                    bottom_right_alert_color = TextColor.GREEN.value
                    if b_currently_arriving:
                        bottom_right_alert_station_key = StationID.PARK_STREET_B
                    elif c_currently_arriving:
                        bottom_right_alert_station_key = StationID.PARK_STREET_C
                    elif d_currently_arriving:
                        bottom_right_alert_station_key = StationID.PARK_STREET_D
                    elif e_currently_arriving:
                        bottom_right_alert_station_key = StationID.PARK_STREET_E

            top_left_alert_color = None
            top_left_alert_station_key = None
            if (
                alewife_currently_arriving
                or won_currently_arriving
                or ol_n_currently_arriving
                or north_d_currently_arriving
                or north_e_currently_arriving
            ):
                if alewife_currently_arriving:
                    top_left_alert_color = TextColor.RED.value
                    top_left_alert_station_key = StationID.CHARLES_MGH_ALEWIFE
                elif ol_n_currently_arriving:
                    top_left_alert_color = TextColor.ORANGE.value
                    top_left_alert_station_key = StationID.DTC_OL_OAK_GROVE
                elif won_currently_arriving:
                    top_left_alert_color = TextColor.BLUE.value
                    top_left_alert_station_key = StationID.BOWDOIN_WONDERLAND
                else:
                    top_left_alert_color = TextColor.GREEN.value
                    if north_d_currently_arriving:
                        top_left_alert_station_key = StationID.PARK_STREET_NORTH
                    elif north_e_currently_arriving:
                        top_left_alert_station_key = StationID.PARK_STREET_NORTH

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

            if bottom_right_alert_color and bottom_right_alert_station_key:
                last_animation_at = last_animation_at_by_station.get(bottom_right_alert_station_key)
                if (
                    last_animation_at is None
                    or now - last_animation_at > timedelta(minutes=ARRIVAL_ANIMATION_COOLDOWN_MINUTES)
                ):
                    arrivals_to_animate.append(
                        (bottom_right_alert_color, display.BOTTOM_RIGHT_ALERT_LOCATION)
                    )
                    last_animation_at_by_station[bottom_right_alert_station_key] = now

            if top_left_alert_color and top_left_alert_station_key:
                last_animation_at = last_animation_at_by_station.get(top_left_alert_station_key)
                if (
                    last_animation_at is None
                    or now - last_animation_at > timedelta(minutes=ARRIVAL_ANIMATION_COOLDOWN_MINUTES)
                ):
                    arrivals_to_animate.append(
                        (top_left_alert_color, display.TOP_LEFT_ALERT_LOCATION)
                    )
                    last_animation_at_by_station[top_left_alert_station_key] = now

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
