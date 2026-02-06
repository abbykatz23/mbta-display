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
            alewife_min_1: int,
            alewife_min_2: int,
            ashmont_braintree_min_1: int,
            ashmont_braintree_min_2: int,
    ):
        self.black_screen()
        self.display.draw_text("B |15 min...23", (4, 1), (0, 255, 0))
        self.display.draw_text("C |15 min...23", (4, 7), (0, 255, 0))
        self.display.draw_text("D^|19 min...23", (4, 13), (0, 255, 0))
        self.display.draw_text("E^|19 min...23", (4, 19), (0, 255, 0))
        self.display.draw_text(f"Alw|{alewife_min_1} min...{alewife_min_2}", (0, 25), (255, 0, 0))
        self.display.draw_text(f"A/B|{ashmont_braintree_min_1} min...{ashmont_braintree_min_2}", (0, 31), (255, 0, 0))
        self.display.draw_text("Won|18 min...23", (0, 37), (0, 0, 255))
        self.display.draw_text("N |19 min...23", (4, 43), (255, 172, 28))
        self.display.draw_text("S |19 min...23", (4, 50), (255, 172, 28))
        self.display.push()