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



    def b_line_from_park_st(self):
        payload = {"text": "B | 15 min",
         "xy": (4, 0),
         'color': (0, 255, 0),
         'identifier': 3,
         'font': 2,
         'width': 58,
         'movement_speed': 50}
        self.display.send_text(**payload)

    def c_line_from_park_st(self):
        payload = {"text": "C | 16 min",
         "xy": (2, 10),
         'color': (0, 255, 0),
         'identifier': 2,
         'font': 2,
         'width': 58,
         'movement_speed': 50}
        self.display.send_text(**payload)

    def d_line_from_park_st(self):
        payload = {"text": "D | 15 min",
         "xy": (2, 20),
         'color': (0, 255, 0),
         'identifier': 1,
         'font': 2,
         'width': 58,
         'movement_speed': 50}
        self.display.send_text(**payload)

    def e_line_from_park_st(self):
        payload = {"text": "E | 9 min",
         "xy": (4, 30),
         'color': (0, 255, 0),
         'identifier': 0,
         'font': 2,
         'width': 58,
         'movement_speed': 50}
        self.display.send_text(**payload)

    def horizontal_line(self):
        for x in range(64):
            self.display.draw_pixel((x, 44), (0, 255, 0))
        self.display.draw_pixel((11, 45), (0, 255, 0))
        self.display.push()

    def smaller(self):
        self.display.draw_text("B |15 min...23", (4, 1), (0, 255, 0))
        self.display.draw_text("C |15 min...23", (4, 7), (0, 255, 0))
        self.display.draw_text("D |19 min...23", (4, 13), (0, 255, 0))
        self.display.draw_text("E |19 min...23", (4, 19), (0, 255, 0))
        self.display.draw_text("D |19 min...23", (4, 25), (0, 255, 0))
        self.display.draw_text("E |19 min...23", (4, 31), (0, 255, 0))
        self.display.draw_text("Alw|19 min...23", (0, 37), (255, 0, 0))
        self.display.draw_text("A/B|19 min...23", (0, 43), (255, 0, 0))
        self.display.draw_text("Won|18 min...23", (0, 49), (0, 0, 255))
        self.display.draw_text("N |19 min...23", (4, 55), (255, 172, 28))
        self.display.draw_text("S |19 min...23", (4, 61), (255, 172, 28))
        self.display.push()