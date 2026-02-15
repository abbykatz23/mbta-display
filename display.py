from pixoo import Pixoo
import time

from settings import settings
from enums import TextColor

PIXOO_IP = settings.pixoo_ip_address


class Display():
    def __init__(self):
        self.display = Pixoo(PIXOO_IP)

    def black_screen(self):
        self.display.fill_rgb(0,0,0)

    def push_screen(self):
        self.display.push()

    def sample_text(self):
        self.display.send_text(
            "hello, Divoom",
            (0, 40),
            (255, 255, 0),
            identifier=4,
            font=3,
            width=64,
            movement_speed=0
        )
    def custom_text_payload(self, payload: dict):
        self.display.send_text(**payload)

    def blink_exclamation(
            self,
            color: tuple[int, int, int],
            location: tuple[int, int] = (2, 17),
            blinks: int = 3,
            on_seconds: float = 0.2,
            off_seconds: float = 0.2,
    ):
        top_left = location
        bottom_right = (location[0] + 2, location[1] + 4)
        for _ in range(blinks):
            self.display.draw_text("!", top_left, color)
            self.display.push()
            time.sleep(on_seconds)
            self.display.draw_filled_rectangle(top_left, bottom_right, (0, 0, 0))
            self.display.push()
            time.sleep(off_seconds)

    def display_train_statuses(
            self,
            b_min_to_nct_1: int,
            b_min_to_nct_2: int,
            c_min_to_nct_1: int,
            c_min_to_nct_2: int,
            d_min_to_nct_1: int,
            d_min_to_nct_2: int,
            e_min_to_nct_1: int,
            e_min_to_nct_2: int,
            north_d_min_to_nct_1: int,
            north_d_min_to_nct_2: int,
            north_e_min_to_nct_1: int,
            north_e_min_to_nct_2: int,
            alewife_min_to_nct_1: int,
            alewife_min_to_nct_2: int,
            ashmont_braintree_min_to_nct_1: int,
            ashmont_braintree_min_to_nct_2: int,
            won_min_to_nct_1: int,
            won_min_to_nct_2: int,
            ol_n_min_to_nct_1: int,
            ol_n_min_to_nct_2: int,
            ol_s_min_to_nct_1: int,
            ol_s_min_to_nct_2: int
    ):
        self.black_screen()

        self.display.draw_text("Union", (0, 0), TextColor.GREEN.value)
        self.display.draw_text("M/Tfts", (23, 0), TextColor.GREEN.value)
        self.display.draw_text("Won", (51, 0), TextColor.BLUE.value)

        self.display.draw_text(f"{north_d_min_to_nct_1 or ''}", (6, 6), TextColor.GREEN.value)
        self.display.draw_text(f"{north_e_min_to_nct_1 or ''}", (30, 6), TextColor.GREEN.value)
        self.display.draw_text(f"{won_min_to_nct_1 or ''}", (53, 6), TextColor.BLUE.value)

        self.display.draw_text(f"{north_d_min_to_nct_2 or ''}", (6, 12), TextColor.GREEN.value)
        self.display.draw_text(f"{north_e_min_to_nct_2 or ''}", (30, 12), TextColor.GREEN.value)
        self.display.draw_text(f"{won_min_to_nct_2 or ''}", (53, 12), TextColor.BLUE.value)

        self.display.draw_text("B", (6, 22), TextColor.GREEN.value)
        self.display.draw_text("C", (22, 22), TextColor.GREEN.value)
        self.display.draw_text("Ale", (34, 22), TextColor.RED.value)
        self.display.draw_text("Oak", (50, 22), TextColor.ORANGE.value)

        self.display.draw_text(f"{b_min_to_nct_1 or ''}", (4, 28), TextColor.GREEN.value)
        self.display.draw_text(f"{c_min_to_nct_1 or ''}", (20, 28), TextColor.GREEN.value)
        self.display.draw_text(f"{alewife_min_to_nct_1 or ''}", (36, 28), TextColor.RED.value)
        self.display.draw_text(f"{ol_n_min_to_nct_1 or ''}", (52, 28), TextColor.ORANGE.value)

        self.display.draw_text(f"{b_min_to_nct_2 or ''}", (4, 34), TextColor.GREEN.value)
        self.display.draw_text(f"{c_min_to_nct_2 or ''}", (20, 34), TextColor.GREEN.value)
        self.display.draw_text(f"{alewife_min_to_nct_2 or ''}", (36, 34), TextColor.RED.value)
        self.display.draw_text(f"{ol_n_min_to_nct_2 or ''}", (52, 34), TextColor.ORANGE.value)

        self.display.draw_text("D", (6, 44), TextColor.GREEN.value)
        self.display.draw_text("E", (22, 44), TextColor.GREEN.value)
        self.display.draw_text("Ash", (34, 44), TextColor.RED.value)
        self.display.draw_text("For", (50, 44), TextColor.ORANGE.value)

        self.display.draw_text(f"{d_min_to_nct_1 or ''}", (4, 50), TextColor.GREEN.value)
        self.display.draw_text(f"{e_min_to_nct_1 or ''}", (20, 50), TextColor.GREEN.value)
        self.display.draw_text(f"{ashmont_braintree_min_to_nct_1 or ''}", (36, 50), TextColor.RED.value)
        self.display.draw_text(f"{ol_s_min_to_nct_1 or ''}", (52, 50), TextColor.ORANGE.value)

        self.display.draw_text(f"{d_min_to_nct_2 or ''}", (4, 56), TextColor.GREEN.value)
        self.display.draw_text(f"{e_min_to_nct_2 or ''}", (20, 56), TextColor.GREEN.value)
        self.display.draw_text(f"{ashmont_braintree_min_to_nct_2 or ''}", (36, 56), TextColor.RED.value)
        self.display.draw_text(f"{ol_s_min_to_nct_2 or ''}", (52, 56), TextColor.ORANGE.value)

        self.display.push()
