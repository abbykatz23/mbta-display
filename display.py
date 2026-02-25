from pixoo import Pixoo
import random
import time
from pathlib import Path
from PIL import Image

from settings import settings
from enums import TextColor, AnimationDirection

PIXOO_IP = settings.pixoo_ip_address


class Display():
    TOP_LEFT_ALERT_LOCATION = (1, 17)
    BOTTOM_RIGHT_ALERT_LOCATION = (61, 41)
    BODY_BG_FACTOR = 0.16
    HEADER_BG_FACTOR = 0.24
    HEADER_GREEN_BLUE_BG_FACTOR = 0.28
    MAX_DIM_MINUTES = 10
    MIN_TEXT_BRIGHTNESS_FACTOR = 0.42
    SPRITE_DIRECTORY = Path("static")
    ROOMMATES_SPRITE_PATH = SPRITE_DIRECTORY / "roommates.png"
    ROOMMATES_SPRITE_CHANCE_DENOMINATOR = 100
    COLOR_NAME_BY_VALUE = {
        TextColor.RED.value: "red",
        TextColor.ORANGE.value: "orange",
        TextColor.GREEN.value: "green",
        TextColor.BLUE.value: "blue",
    }

    def __init__(self):
        self.display = Pixoo(PIXOO_IP)
        self.static_layout_drawn = False
        self._sprite_path_by_color_set: dict[frozenset[str], str] | None = None

    def black_screen(self):
        self.display.fill_rgb(0,0,0)
        self.static_layout_drawn = False

    def draw_layout_background(self):
        # Dark tinted zone colors.
        dark_green = tuple(int(channel * self.BODY_BG_FACTOR) for channel in TextColor.GREEN.value)
        dark_red = tuple(int(channel * self.BODY_BG_FACTOR) for channel in TextColor.RED.value)
        dark_orange = tuple(int(channel * self.BODY_BG_FACTOR) for channel in TextColor.ORANGE.value)
        dark_blue = tuple(int(channel * self.BODY_BG_FACTOR) for channel in TextColor.BLUE.value)
        light_green = tuple(int(channel * self.HEADER_GREEN_BLUE_BG_FACTOR) for channel in TextColor.GREEN.value)
        light_red = tuple(int(channel * self.HEADER_BG_FACTOR) for channel in TextColor.RED.value)
        light_orange = tuple(int(channel * self.HEADER_BG_FACTOR) for channel in TextColor.ORANGE.value)
        light_blue = tuple(int(channel * self.HEADER_GREEN_BLUE_BG_FACTOR) for channel in TextColor.BLUE.value)

        # Top section: green on left/middle, blue on right for Wonderland.
        self.display.draw_filled_rectangle((0, 0), (48, 16), dark_green)
        self.display.draw_filled_rectangle((49, 0), (63, 16), dark_blue)

        # Middle/bottom sections by line family columns.
        self.display.draw_filled_rectangle((0, 22), (31, 63), dark_green)
        self.display.draw_filled_rectangle((32, 22), (47, 63), dark_red)
        self.display.draw_filled_rectangle((48, 22), (63, 63), dark_orange)

        # Entire header bands (and one row above/below) are lighter.
        # Top headers at y=-1 => visible rows 0..3, plus one below => 0..4.
        self.display.draw_filled_rectangle((0, 0), (48, 4), light_green)
        self.display.draw_filled_rectangle((49, 0), (63, 4), light_blue)
        # Middle headers at y=23 => rows 23..27, plus one above/below => 22..28.
        self.display.draw_filled_rectangle((0, 22), (31, 28), light_green)
        self.display.draw_filled_rectangle((32, 22), (47, 28), light_red)
        self.display.draw_filled_rectangle((48, 22), (63, 28), light_orange)
        # Bottom headers at y=47 => rows 47..51, plus one above/below => 46..52.
        self.display.draw_filled_rectangle((0, 46), (31, 52), light_green)
        self.display.draw_filled_rectangle((32, 46), (47, 52), light_red)
        self.display.draw_filled_rectangle((48, 46), (63, 52), light_orange)

        # Train lanes stay black.
        self.display.draw_filled_rectangle((0, 17), (63, 21), (0, 0, 0))
        self.display.draw_filled_rectangle((0, 41), (63, 45), (0, 0, 0))

    def push_screen(self):
        self.display.push()

    def _scaled_color(self, color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
        return tuple(int(channel * factor) for channel in color)

    def _layout_color_at(self, x: int, y: int) -> tuple[int, int, int]:
        dark_green = self._scaled_color(TextColor.GREEN.value, self.BODY_BG_FACTOR)
        dark_red = self._scaled_color(TextColor.RED.value, self.BODY_BG_FACTOR)
        dark_orange = self._scaled_color(TextColor.ORANGE.value, self.BODY_BG_FACTOR)
        dark_blue = self._scaled_color(TextColor.BLUE.value, self.BODY_BG_FACTOR)
        light_green = self._scaled_color(TextColor.GREEN.value, self.HEADER_GREEN_BLUE_BG_FACTOR)
        light_red = self._scaled_color(TextColor.RED.value, self.HEADER_BG_FACTOR)
        light_orange = self._scaled_color(TextColor.ORANGE.value, self.HEADER_BG_FACTOR)
        light_blue = self._scaled_color(TextColor.BLUE.value, self.HEADER_GREEN_BLUE_BG_FACTOR)

        # Train lanes are always black.
        if 17 <= y <= 21 or 41 <= y <= 45:
            return (0, 0, 0)

        # Header bands.
        if 0 <= y <= 4:
            return light_blue if x >= 49 else light_green
        if 22 <= y <= 28 or 46 <= y <= 52:
            if x <= 31:
                return light_green
            if x <= 47:
                return light_red
            return light_orange

        # Body zones.
        if 0 <= y <= 16:
            return dark_blue if x >= 49 else dark_green
        if 22 <= y <= 63:
            if x <= 31:
                return dark_green
            if x <= 47:
                return dark_red
            return dark_orange

        return (0, 0, 0)

    def _clear_dynamic_text_cell(self, location: tuple[int, int], max_chars: int = 3):
        x, y = location
        bg = self._layout_color_at(x, y)
        width = max(1, (max_chars * 4) - 1)
        self.display.draw_filled_rectangle(
            (x, y),
            (min(63, x + width - 1), min(63, y + 4)),
            bg,
        )

    def _draw_dynamic_value(self, value: int | None, location: tuple[int, int], color: tuple[int, int, int]):
        self._clear_dynamic_text_cell(location)
        text = "" if value is None else str(value)
        draw_color = color
        if value is not None:
            clamped_minutes = max(0, min(self.MAX_DIM_MINUTES, value))
            brightness_factor = 1 - (
                (clamped_minutes / self.MAX_DIM_MINUTES)
                * (1 - self.MIN_TEXT_BRIGHTNESS_FACTOR)
            )
            draw_color = tuple(
                max(0, min(255, int(channel * brightness_factor)))
                for channel in color
            )
        x, y = location
        if len(text) == 1:
            x += 2
        self.display.draw_text(text, (x, y), draw_color)

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

    def draw_station_label(
            self,
            text: str,
            location: tuple[int, int],
            color: tuple[int, int, int],
            glyph_clear_color: tuple[int, int, int] = (0, 0, 0),
    ):
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
                    draw_pixel_if_on_display(glyph_x + dx, y + dy, glyph_clear_color)

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

    def draw_station_header(self, text: str, location: tuple[int, int], color: tuple[int, int, int]):
        x, y = location
        # Approximate width in the 3x5 font with 1px spacing.
        width = max(1, (len(text) * 4) - 1)
        top = max(0, y)
        bottom = min(63, top + 4)
        right = min(63, x + width - 1)

        # Very dark proportional tint of the text color.
        bg_factor = (
            self.HEADER_GREEN_BLUE_BG_FACTOR
            if color in (TextColor.GREEN.value, TextColor.BLUE.value)
            else self.HEADER_BG_FACTOR
        )
        bg = tuple(max(0, min(255, int(channel * bg_factor))) for channel in color)
        self.display.draw_filled_rectangle((x, top), (right, bottom), bg)
        self.draw_station_label(text, location, color, glyph_clear_color=bg)

    def draw_static_layout(self):
        self.draw_layout_background()

        self.draw_station_header("union", (0, -1), TextColor.GREEN.value)
        self.draw_station_header("m/tfts", (23, -1), TextColor.GREEN.value)
        self.draw_station_header("won", (51, -1), TextColor.BLUE.value)

        self.draw_station_header("B", (6, 23), TextColor.GREEN.value)
        self.draw_station_header("C", (22, 23), TextColor.GREEN.value)
        self.draw_station_header("ALE", (34, 23), TextColor.RED.value)
        self.draw_station_header("OAK", (50, 23), TextColor.ORANGE.value)

        self.draw_station_header("D", (6, 47), TextColor.GREEN.value)
        self.draw_station_header("E", (22, 47), TextColor.GREEN.value)
        self.draw_station_header("ASH", (34, 47), TextColor.RED.value)
        self.draw_station_header("FOR", (50, 47), TextColor.ORANGE.value)

        self.push_screen()
        self.static_layout_drawn = True

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
            fps: int = 35,
            loops: int = 1,
    ):
        self.blink_and_animate_arrivals(
            arrivals=[(color, location)],
            fps=fps,
            loops=loops,
        )

    def blink_and_animate_arrivals(
            self,
            arrivals: list[tuple[tuple[int, int, int], tuple[int, int]]],
            fps: int = 35,
            loops: int = 1,
    ):
        if not arrivals:
            return

        colors_by_location: dict[tuple[int, int], set[tuple[int, int, int]]] = {}
        for color, location in arrivals:
            colors_by_location.setdefault(location, set()).add(color)

        valid_arrivals: list[dict] = []
        for location, colors in colors_by_location.items():
            sprite_path = self._resolve_sprite_path(colors)
            if not sprite_path:
                continue
            sprite_path = self._maybe_override_with_roommates_sprite(sprite_path)

            if location == self.BOTTOM_RIGHT_ALERT_LOCATION:
                y = 41
                direction = AnimationDirection.RIGHT_TO_LEFT
            else:
                y = 17
                direction = AnimationDirection.LEFT_TO_RIGHT

            sprite = Image.open(sprite_path).convert("RGBA")
            sw, sh = sprite.size
            if sh != 5:
                raise ValueError(f"Expected sprite height 5px, got {sh}px")
            opaque_pixels: list[tuple[int, int, tuple[int, int, int]]] = []
            for sy in range(sh):
                for sx in range(sw):
                    r, g, b, a = sprite.getpixel((sx, sy))
                    if a < 10:
                        continue
                    opaque_pixels.append((sx, sy, (r, g, b)))

            valid_arrivals.append(
                {
                    "colors": self._ordered_colors(colors),
                    "location": location,
                    "sw": sw,
                    "y": y,
                    "opaque_pixels": opaque_pixels,
                    "positions": (
                        list(range(-sw, 65))
                        if direction == AnimationDirection.LEFT_TO_RIGHT
                        else list(range(64, -sw - 1, -1))
                    ),
                }
            )

        if not valid_arrivals:
            return

        # Blink all alerts together.
        for _ in range(3):
            for arrival in valid_arrivals:
                self._draw_alert_exclamation(arrival["location"], arrival["colors"])
            self.push_screen()
            time.sleep(0.12)

            for arrival in valid_arrivals:
                x, y = arrival["location"]
                self.display.draw_filled_rectangle((x, y), (x + 2, y + 4), (0, 0, 0))
            self.push_screen()
            time.sleep(0.12)

        dt = 1 / fps
        total_frames = max(len(arrival["positions"]) for arrival in valid_arrivals)
        lanes = {arrival["y"] for arrival in valid_arrivals}

        for _ in range(loops):
            next_frame_at = time.perf_counter()
            for frame_idx in range(total_frames):
                # Clear each active train lane once per frame.
                for lane_y in lanes:
                    for yy in range(lane_y, lane_y + 5):
                        if 0 <= yy < 64:
                            for xx in range(64):
                                self.display.draw_pixel((xx, yy), (0, 0, 0))

                # Draw each train at its current frame position.
                for arrival in valid_arrivals:
                    if frame_idx >= len(arrival["positions"]):
                        continue
                    x0 = arrival["positions"][frame_idx]
                    lane_y = arrival["y"]

                    for sx, sy, color in arrival["opaque_pixels"]:
                        dy = lane_y + sy
                        if dy < 0 or dy >= 64:
                            continue
                        dx = x0 + sx
                        if dx < 0 or dx >= 64:
                            continue
                        self.display.draw_pixel((dx, dy), color)

                self.push_screen()
                next_frame_at += dt
                sleep_for = next_frame_at - time.perf_counter()
                if sleep_for > 0:
                    time.sleep(sleep_for)
                else:
                    next_frame_at = time.perf_counter()

    def _load_sprite_paths_by_color_set(self) -> dict[frozenset[str], str]:
        if self._sprite_path_by_color_set is not None:
            return self._sprite_path_by_color_set

        sprite_paths: dict[frozenset[str], str] = {}
        valid_color_names = set(self.COLOR_NAME_BY_VALUE.values())

        for path in self.SPRITE_DIRECTORY.glob("*.png"):
            parts = path.stem.lower().split("_")
            if not parts:
                continue
            if any(part not in valid_color_names for part in parts):
                continue
            sprite_paths[frozenset(parts)] = str(path)

        self._sprite_path_by_color_set = sprite_paths
        return sprite_paths

    def _resolve_sprite_path(self, colors: set[tuple[int, int, int]]) -> str | None:
        color_names = frozenset(
            self.COLOR_NAME_BY_VALUE[color]
            for color in colors
            if color in self.COLOR_NAME_BY_VALUE
        )
        if not color_names:
            return None

        sprites = self._load_sprite_paths_by_color_set()
        if color_names in sprites:
            return sprites[color_names]

        if len(color_names) == 1:
            color_name = next(iter(color_names))
            return str(self.SPRITE_DIRECTORY / f"{color_name}.png")

        return None

    def _ordered_colors(
            self,
            colors: set[tuple[int, int, int]],
    ) -> list[tuple[int, int, int]]:
        ordered_colors = sorted(
            colors,
            key=lambda color: self.COLOR_NAME_BY_VALUE.get(color, "zzzz"),
        )
        return ordered_colors or [TextColor.GREEN.value]

    def _draw_alert_exclamation(
            self,
            location: tuple[int, int],
            colors: list[tuple[int, int, int]],
    ):
        if len(colors) <= 1:
            self.display.draw_text("!", location, colors[0])
            return

        # 3x5 exclamation in the same alert cell used by draw_text.
        line_pixels = ((1, 0), (1, 1), (1, 2))
        dot_pixel = (1, 4)
        x0, y0 = location
        if len(colors) == 2:
            dot_color, line_color = colors[0], colors[1]
            for dx, dy in line_pixels:
                self.display.draw_pixel((x0 + dx, y0 + dy), line_color)
            self.display.draw_pixel((x0 + dot_pixel[0], y0 + dot_pixel[1]), dot_color)
            return

        exclamation_pixels = (*line_pixels, dot_pixel)
        for pixel_idx, (dx, dy) in enumerate(exclamation_pixels):
            color = colors[pixel_idx % len(colors)]
            self.display.draw_pixel((x0 + dx, y0 + dy), color)

    def _maybe_override_with_roommates_sprite(self, sprite_path: str) -> str:
        if not self.ROOMMATES_SPRITE_PATH.exists():
            return sprite_path
        if random.randrange(self.ROOMMATES_SPRITE_CHANCE_DENOMINATOR) == 0:
            return str(self.ROOMMATES_SPRITE_PATH)
        return sprite_path

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
        if not self.static_layout_drawn:
            self.draw_static_layout()

        self._draw_dynamic_value(north_d_min_to_nct_1, (6, 5), TextColor.GREEN.value)
        self._draw_dynamic_value(north_e_min_to_nct_1, (30, 5), TextColor.GREEN.value)
        self._draw_dynamic_value(won_min_to_nct_1, (53, 5), TextColor.BLUE.value)

        self._draw_dynamic_value(north_d_min_to_nct_2, (6, 11), TextColor.GREEN.value)
        self._draw_dynamic_value(north_e_min_to_nct_2, (30, 11), TextColor.GREEN.value)
        self._draw_dynamic_value(won_min_to_nct_2, (53, 11), TextColor.BLUE.value)

        self._draw_dynamic_value(b_min_to_nct_1, (4, 29), TextColor.GREEN.value)
        self._draw_dynamic_value(c_min_to_nct_1, (20, 29), TextColor.GREEN.value)
        self._draw_dynamic_value(alewife_min_to_nct_1, (36, 29), TextColor.RED.value)
        self._draw_dynamic_value(ol_n_min_to_nct_1, (52, 29), TextColor.ORANGE.value)

        self._draw_dynamic_value(b_min_to_nct_2, (4, 35), TextColor.GREEN.value)
        self._draw_dynamic_value(c_min_to_nct_2, (20, 35), TextColor.GREEN.value)
        self._draw_dynamic_value(alewife_min_to_nct_2, (36, 35), TextColor.RED.value)
        self._draw_dynamic_value(ol_n_min_to_nct_2, (52, 35), TextColor.ORANGE.value)

        self._draw_dynamic_value(d_min_to_nct_1, (4, 53), TextColor.GREEN.value)
        self._draw_dynamic_value(e_min_to_nct_1, (20, 53), TextColor.GREEN.value)
        self._draw_dynamic_value(ashmont_braintree_min_to_nct_1, (36, 53), TextColor.RED.value)
        self._draw_dynamic_value(ol_s_min_to_nct_1, (52, 53), TextColor.ORANGE.value)

        self._draw_dynamic_value(d_min_to_nct_2, (4, 59), TextColor.GREEN.value)
        self._draw_dynamic_value(e_min_to_nct_2, (20, 59), TextColor.GREEN.value)
        self._draw_dynamic_value(ashmont_braintree_min_to_nct_2, (36, 59), TextColor.RED.value)
        self._draw_dynamic_value(ol_s_min_to_nct_2, (52, 59), TextColor.ORANGE.value)

        self.display.push()
