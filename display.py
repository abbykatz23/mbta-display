from pixoo import Pixoo
import time
from PIL import Image

from settings import settings
from enums import TextColor, AnimationDirection

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

    def draw_custom_f_glyph(self, location: tuple[int, int], color: tuple[int, int, int]):
        """
        Draw a custom lowercase f shape:
        XXX
        X
        XX
        X
        """
        x, y = location
        f_pixels = (
            (0, 1), (1, 1), (2, 1),
            (0, 2),
            (0, 3), (1, 3),
            (0, 4),
        )
        for dx, dy in f_pixels:
            self.display.draw_pixel((x + dx, y + dy), color)

    def draw_custom_for_label(self, location: tuple[int, int], color: tuple[int, int, int]):
        """Draw "for" with the custom lowercase f shape."""
        x, y = location

        self.draw_custom_f_glyph((x, y), color)

        # Draw the rest of the label with the default font.
        self.display.draw_text("or", (x + 4, y), color)

    def draw_custom_mtfts_label(self, location: tuple[int, int], color: tuple[int, int, int]):
        """
        Draw "m/tfts" with custom slash and lowercase f shapes.

        Slash shape:
          X
         X
         X
        X
        """
        x, y = location

        self.display.draw_text("m", (x, y), color)

        slash_pixels = (
            (2, 1),
            (1, 2),
            (1, 3),
            (0, 4),
        )
        for dx, dy in slash_pixels:
            self.display.draw_pixel((x + 4 + dx, y + dy), color)

        self.display.draw_text("t", (x + 8, y), color)
        self.draw_custom_f_glyph((x + 12, y), color)
        self.display.draw_text("ts", (x + 16, y), color)

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

        self.display.draw_text("union", (0, -1), TextColor.GREEN.value)
        self.draw_custom_mtfts_label((23, -1), TextColor.GREEN.value)
        self.display.draw_text("won", (51, -1), TextColor.BLUE.value)

        self.display.draw_text(f"{north_d_min_to_nct_1 or ''}", (6, 5), TextColor.GREEN.value)
        self.display.draw_text(f"{north_e_min_to_nct_1 or ''}", (30, 5), TextColor.GREEN.value)
        self.display.draw_text(f"{won_min_to_nct_1 or ''}", (53, 5), TextColor.BLUE.value)

        self.display.draw_text(f"{north_d_min_to_nct_2 or ''}", (6, 11), TextColor.GREEN.value)
        self.display.draw_text(f"{north_e_min_to_nct_2 or ''}", (30, 11), TextColor.GREEN.value)
        self.display.draw_text(f"{won_min_to_nct_2 or ''}", (53, 11), TextColor.BLUE.value)

        self.display.draw_text("B", (6, 23), TextColor.GREEN.value)
        self.display.draw_text("C", (22, 23), TextColor.GREEN.value)
        self.display.draw_text("ALE", (34, 23), TextColor.RED.value)
        self.display.draw_text("OAK", (50, 23), TextColor.ORANGE.value)

        self.display.draw_text(f"{b_min_to_nct_1 or ''}", (4, 29), TextColor.GREEN.value)
        self.display.draw_text(f"{c_min_to_nct_1 or ''}", (20, 29), TextColor.GREEN.value)
        self.display.draw_text(f"{alewife_min_to_nct_1 or ''}", (36, 29), TextColor.RED.value)
        self.display.draw_text(f"{ol_n_min_to_nct_1 or ''}", (52, 29), TextColor.ORANGE.value)

        self.display.draw_text(f"{b_min_to_nct_2 or ''}", (4, 35), TextColor.GREEN.value)
        self.display.draw_text(f"{c_min_to_nct_2 or ''}", (20, 35), TextColor.GREEN.value)
        self.display.draw_text(f"{alewife_min_to_nct_2 or ''}", (36, 35), TextColor.RED.value)
        self.display.draw_text(f"{ol_n_min_to_nct_2 or ''}", (52, 35), TextColor.ORANGE.value)

        self.display.draw_text("D", (6, 47), TextColor.GREEN.value)
        self.display.draw_text("E", (22, 47), TextColor.GREEN.value)
        self.display.draw_text("ASH", (34, 47), TextColor.RED.value)
        self.display.draw_text("FOR", (50, 47), TextColor.ORANGE.value)

        self.display.draw_text(f"{d_min_to_nct_1 or ''}", (4, 53), TextColor.GREEN.value)
        self.display.draw_text(f"{e_min_to_nct_1 or ''}", (20, 53), TextColor.GREEN.value)
        self.display.draw_text(f"{ashmont_braintree_min_to_nct_1 or ''}", (36, 53), TextColor.RED.value)
        self.display.draw_text(f"{ol_s_min_to_nct_1 or ''}", (52, 53), TextColor.ORANGE.value)

        self.display.draw_text(f"{d_min_to_nct_2 or ''}", (4, 59), TextColor.GREEN.value)
        self.display.draw_text(f"{e_min_to_nct_2 or ''}", (20, 59), TextColor.GREEN.value)
        self.display.draw_text(f"{ashmont_braintree_min_to_nct_2 or ''}", (36, 59), TextColor.RED.value)
        self.display.draw_text(f"{ol_s_min_to_nct_2 or ''}", (52, 59), TextColor.ORANGE.value)

        self.animate_train_band(
            "red_line.png",
            y=17,
            fps=25,
            loops=1,
            direction=AnimationDirection.RIGHT_TO_LEFT,
        )
        self.animate_train_band(
            "green_line.png",
            y=41,
            fps=25,
            loops=1,
            direction=AnimationDirection.LEFT_TO_RIGHT,
        )

        self.display.push()
