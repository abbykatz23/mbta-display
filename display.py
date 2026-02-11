from pixoo import Pixoo

from settings import settings

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
            alewife_mins_to_nct_2: int,
            ashmont_braintree_min_to_nct_1: int,
            ashmont_braintree_min_to_nct_2: int,
            won_min_to_nct_1: int,
            won_min_to_nct_2: int,
            ol_n_min_to_nct_1: int,
            ol_n_min_to_nct_2: int,
            ol_s_min_to_nct_1: int,
            ol_s_min_to_nct_2: int
    ):
        self.black_screen()  # todo: have the westbound gl show the 4 most upcoming trains

        self.display.draw_text(f"Alw|{alewife_min_to_nct_1} min...{alewife_mins_to_nct_2}", (0, 0), (255, 0, 0))
        self.display.draw_text(f"Ash|{ashmont_braintree_min_to_nct_1} min...{ashmont_braintree_min_to_nct_2}", (0, 6), (255, 0, 0))

        self.display.draw_text(f"Won|{won_min_to_nct_1} min...{won_min_to_nct_2}", (0, 13), (0, 0, 255))

        self.display.draw_text(f"Oak|{ol_n_min_to_nct_1} min...{ol_n_min_to_nct_2}", (0, 20), (255, 172, 28))
        self.display.draw_text(f"For|{ol_s_min_to_nct_1} min...{ol_s_min_to_nct_2}", (0, 26), (255, 172, 28))

        self.display.draw_text(f"Uni|{north_d_min_to_nct_1} min...{north_d_min_to_nct_2}", (0, 33), (0, 255, 0))
        self.display.draw_text(f"Med|{north_e_min_to_nct_1} min...{north_e_min_to_nct_2}", (0, 39), (0, 255, 0))

        self.display.draw_text("B   C   D   E", (6, 47), (0, 255, 0))
        # self.display.draw_text(f"{b_min_to_nct_1}  {c_min_to_nct_1}  {d_min_to_nct_1}  {e_min_to_nct_1}",(4, 53), (0, 255, 0))
        # self.display.draw_text(f"{b_min_to_nct_2}  {c_min_to_nct_2}  {d_min_to_nct_2 or ''}  {e_min_to_nct_2 or ''}", (4, 59), (0, 255, 0))

        self.display.draw_text(f"{b_min_to_nct_1 or ''}", (4, 53), (0, 255, 0))
        self.display.draw_text(f"{c_min_to_nct_1 or ''}", (20, 53), (0, 255, 0))
        self.display.draw_text(f"{d_min_to_nct_1 or ''}", (36, 53), (0, 255, 0))
        self.display.draw_text(f"{e_min_to_nct_1 or ''}", (52, 53), (0, 255, 0))

        self.display.draw_text(f"{b_min_to_nct_2 or ''}", (4, 59), (0, 255, 0))
        self.display.draw_text(f"{c_min_to_nct_2 or ''}", (20, 59), (0, 255, 0))
        self.display.draw_text(f"{d_min_to_nct_2 or ''}", (36, 59), (0, 255, 0))
        self.display.draw_text(f"{e_min_to_nct_2 or ''}", (52, 59), (0, 255, 0))

        # self.display.draw_text(f"B |{b_min_to_nct_1} min...{b_min_to_nct_2}", (4, 47), (0, 255, 0))
        # self.display.draw_text(f"C |{c_min_to_nct_1} min...{c_min_to_nct_2}", (4, 53), (0, 255, 0))
        # self.display.draw_text(f"D |{d_min_to_nct_1} min...{d_min_to_nct_2}", (4, 59), (0, 255, 0))
        self.display.push()
