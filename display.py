from pixoo import Pixoo

from settings import settings

PIXOO_IP = settings.pixoo_ip_address


class Display():
    def __init__(self):
        self.display = Pixoo(PIXOO_IP)

    def _set_channel(self, channel:int = 3):
        self.display.set_channel(channel)

    def black_screen(self):
        self._set_channel()
        self.display.fill_rgb(0,0,0)
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

    def park_street(self):
        payload = {"text": "Park St.",
         "xy": (3, 35),
         'color': (0, 255, 0),
         'identifier': 3,
         'font': 2,
         'width': 58,
         'movement_speed': 0}
        self.display.send_text(**payload)
