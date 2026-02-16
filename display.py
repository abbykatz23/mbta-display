from pixoo import Pixoo
import time
from PIL import Image

from settings import settings
from enums import TextColor, AnimationDirection

PIXOO_IP = settings.pixoo_ip_address


class Display():
    TOP_LEFT_ALERT_LOCATION = (2, 17)
    BOTTOM_RIGHT_ALERT_LOCATION = (61, 39)

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

    def draw_station_label(self, text: str, location: tuple[int, int], color: tuple[int, int, int]):
        """
        Draw a station label, patching custom glyphs where needed.

        Custom lowercase f:
        XXX
        X
        XX
        X

        Custom slash:
          X
         X
         X
        X

        Custom lowercase o / uppercase O:
        fill top-left and bottom-right corners.
        """
        x, y = location
        self.display.draw_text(text, (x, y), color)

        def draw_pixel_if_on_display(px: int, py: int, rgb: tuple[int, int, int]):
            if 0 <= px < 64 and 0 <= py < 64:
                self.display.draw_pixel((px, py), rgb)

        for idx, char in enumerate(text):
            if char not in ("f", "/", "o", "O", "D", "u", "U"):
                continue

            glyph_x = x + (idx * 4)

            # Clear glyph cell before drawing custom pixels.
            for dy in range(5):
                for dx in range(3):
                    draw_pixel_if_on_display(glyph_x + dx, y + dy, (0, 0, 0))

            if char == "f":
                glyph_pixels = (
                    (0, 1), (1, 1), (2, 1),
                    (0, 2),
                    (0, 3), (1, 3),
                    (0, 4),
                )
            elif char == "/":
                glyph_pixels = (
                    (2, 1),
                    (1, 2),
                    (1, 3),
                    (0, 4),
                )
            elif char == "o":
                glyph_pixels = (
                    (0, 1), (1, 1), (2, 1),
                    (0, 2), (2, 2),
                    (0, 3), (2, 3),
                    (0, 4), (1, 4), (2, 4),
                )
            elif char == "D":
                glyph_pixels = (
                    (0, 0), (1, 0),
                    (0, 1), (2, 1),
                    (0, 2), (2, 2),
                    (0, 3), (2, 3),
                    (0, 4), (1, 4),
                )
            elif char == "u":
                glyph_pixels = (
                    (0, 1), (2, 1),
                    (0, 2), (2, 2),
                    (0, 3), (2, 3),
                    (0, 4), (1, 4), (2, 4),
                )
            elif char == "U":
                glyph_pixels = (
                    (0, 0), (2, 0),
                    (0, 1), (2, 1),
                    (0, 2), (2, 2),
                    (0, 3), (2, 3),
                    (0, 4), (1, 4), (2, 4),
                )
            else:  # 'O'
                glyph_pixels = (
                    (0, 0), (1, 0), (2, 0),
                    (0, 1), (2, 1),
                    (0, 2), (2, 2),
                    (0, 3), (2, 3),
                    (0, 4), (1, 4), (2, 4),
                )

            for dx, dy in glyph_pixels:
                draw_pixel_if_on_display(glyph_x + dx, y + dy, color)

    def animate_train_band(
            self,
            sprite_path: str,
            y: int = 20,
            fps: int = 12,
            loops: int = 1,
            direction: AnimationDirection = AnimationDirection.LEFT_TO_RIGHT,
    ):
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
        if direction == AnimationDirection.LEFT_TO_RIGHT:
            # Move fully off-screen left -> fully off-screen right
            x_positions = range(-sw, 65)
        elif direction == AnimationDirection.RIGHT_TO_LEFT:
            # Move fully off-screen right -> fully off-screen left
            x_positions = range(64, -sw - 1, -1)
        else:
            raise ValueError(
                f"Invalid direction '{direction}'. Expected an AnimationDirection enum value."
            )

        for _ in range(loops):
            for x in x_positions:
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

    def blink_and_animate_arrival(
            self,
            color: tuple[int, int, int],
            location: tuple[int, int],
            fps: int = 25,
            loops: int = 1,
    ):
        sprite_path_by_color = {
            TextColor.RED.value: "red_line.png",
            TextColor.ORANGE.value: "orange_line.png",
            TextColor.GREEN.value: "green_line.png",
            TextColor.BLUE.value: "blue_line.png",
        }

        sprite_path = sprite_path_by_color.get(color)
        if not sprite_path:
            return

        self.blink_exclamation(color, location=location)

        if location == self.BOTTOM_RIGHT_ALERT_LOCATION:
            y = 41
            direction = AnimationDirection.RIGHT_TO_LEFT
        else:
            y = 17
            direction = AnimationDirection.LEFT_TO_RIGHT

        self.animate_train_band(
            sprite_path,
            y=y,
            fps=fps,
            loops=loops,
            direction=direction,
        )

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

        self.draw_station_label("union", (0, -1), TextColor.GREEN.value)
        self.draw_station_label("m/tfts", (23, -1), TextColor.GREEN.value)
        self.draw_station_label("won", (51, -1), TextColor.BLUE.value)

        self.display.draw_text(f"{north_d_min_to_nct_1 or ''}", (6, 5), TextColor.GREEN.value)
        self.display.draw_text(f"{north_e_min_to_nct_1 or ''}", (30, 5), TextColor.GREEN.value)
        self.display.draw_text(f"{won_min_to_nct_1 or ''}", (53, 5), TextColor.BLUE.value)

        self.display.draw_text(f"{north_d_min_to_nct_2 or ''}", (6, 11), TextColor.GREEN.value)
        self.display.draw_text(f"{north_e_min_to_nct_2 or ''}", (30, 11), TextColor.GREEN.value)
        self.display.draw_text(f"{won_min_to_nct_2 or ''}", (53, 11), TextColor.BLUE.value)

        self.draw_station_label("B", (6, 23), TextColor.GREEN.value)
        self.draw_station_label("C", (22, 23), TextColor.GREEN.value)
        self.draw_station_label("ALE", (34, 23), TextColor.RED.value)
        self.draw_station_label("OAK", (50, 23), TextColor.ORANGE.value)

        self.display.draw_text(f"{b_min_to_nct_1 or ''}", (4, 29), TextColor.GREEN.value)
        self.display.draw_text(f"{c_min_to_nct_1 or ''}", (20, 29), TextColor.GREEN.value)
        self.display.draw_text(f"{alewife_min_to_nct_1 or ''}", (36, 29), TextColor.RED.value)
        self.display.draw_text(f"{ol_n_min_to_nct_1 or ''}", (52, 29), TextColor.ORANGE.value)

        self.display.draw_text(f"{b_min_to_nct_2 or ''}", (4, 35), TextColor.GREEN.value)
        self.display.draw_text(f"{c_min_to_nct_2 or ''}", (20, 35), TextColor.GREEN.value)
        self.display.draw_text(f"{alewife_min_to_nct_2 or ''}", (36, 35), TextColor.RED.value)
        self.display.draw_text(f"{ol_n_min_to_nct_2 or ''}", (52, 35), TextColor.ORANGE.value)

        self.draw_station_label("D", (6, 47), TextColor.GREEN.value)
        self.draw_station_label("E", (22, 47), TextColor.GREEN.value)
        self.draw_station_label("ASH", (34, 47), TextColor.RED.value)
        self.draw_station_label("FOR", (50, 47), TextColor.ORANGE.value)

        self.display.draw_text(f"{d_min_to_nct_1 or ''}", (4, 53), TextColor.GREEN.value)
        self.display.draw_text(f"{e_min_to_nct_1 or ''}", (20, 53), TextColor.GREEN.value)
        self.display.draw_text(f"{ashmont_braintree_min_to_nct_1 or ''}", (36, 53), TextColor.RED.value)
        self.display.draw_text(f"{ol_s_min_to_nct_1 or ''}", (52, 53), TextColor.ORANGE.value)

        self.display.draw_text(f"{d_min_to_nct_2 or ''}", (4, 59), TextColor.GREEN.value)
        self.display.draw_text(f"{e_min_to_nct_2 or ''}", (20, 59), TextColor.GREEN.value)
        self.display.draw_text(f"{ashmont_braintree_min_to_nct_2 or ''}", (36, 59), TextColor.RED.value)
        self.display.draw_text(f"{ol_s_min_to_nct_2 or ''}", (52, 59), TextColor.ORANGE.value)

        self.display.push()
