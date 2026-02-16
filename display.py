from pixoo import Pixoo
import time
from PIL import Image

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

    def animate_train_band(self,sprite_path: str, y: int = 20, fps: int = 12, loops: int = 1):
        """
        Animate a small sprite (e.g., 26x5) left-to-right across the Pixoo at a fixed y.
        Clears only the affected band each frame for stability.
        """

        sprite = Image.open(sprite_path).convert("RGBA")
        sw, sh = sprite.size
        display = self.display

        if sh != 5:
            raise ValueError(f"Expected sprite height 5px, got {sh}px")

        dt = 1 / fps

        def clear_band():
            # Clear only the rows y..y+4 to black
            for yy in range(y, y + sh):
                if 0 <= yy < 64:
                    for xx in range(64):
                        display.draw_pixel((xx, yy), (0, 0, 0))

        def draw_sprite_at(x0: int):
            # Clear just the band where the train lives
            clear_band()

            # Draw sprite pixels
            for sy in range(sh):
                dy = y + sy
                if dy < 0 or dy >= 64:
                    continue

                for sx in range(sw):
                    dx = x0 + sx
                    if dx < 0 or dx >= 64:
                        continue

                    r, g, b, a = sprite.getpixel((sx, sy))
                    if a < 10:
                        continue  # transparent

                    display.draw_pixel((dx, dy), (r, g, b))

            self.push_screen()
        # Move fully off-screen left -> fully off-screen right
        start_x = -sw
        end_x = 64

        for _ in range(loops):
            for x in range(start_x, end_x + 1):
                draw_sprite_at(x)
                time.sleep(dt)

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

        self.animate_train_band("red_line.png", y=17, fps=25, loops=2)

        self.display.push()
