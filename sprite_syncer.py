import base64
import io
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from PIL import Image

from settings import settings

_UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

SPECIAL_TRAINS_DIR = Path("static/special_trains")
METADATA_PATH = SPECIAL_TRAINS_DIR / "metadata.json"

logger = logging.getLogger(__name__)


def sync_sprites() -> None:
    """Download any newly approved sprites from mbta-server and update metadata."""
    if not settings.mbta_server_url or not settings.pi_api_key:
        logger.info("Sprite syncing is disabled (mbta_server_url or pi_api_key not set)")
        return

    SPECIAL_TRAINS_DIR.mkdir(parents=True, exist_ok=True)

    last_synced = _read_last_synced()
    params = {}
    if last_synced:
        params["since"] = last_synced

    try:
        response = requests.get(
            f"{settings.mbta_server_url}/sprites",
            headers={"X-API-Key": settings.pi_api_key},
            params=params,
            timeout=10,
        )
        response.raise_for_status()
    except Exception as e:
        logger.warning("Sprite sync failed: %s", e)
        return

    sprites = response.json()
    if not sprites:
        return

    metadata = _read_metadata()
    for sprite in sprites:
        sprite_id = sprite["id"]
        if not _UUID_RE.match(sprite_id):
            logger.warning("Skipping sprite with invalid id: %r", sprite_id)
            continue
        png_path = SPECIAL_TRAINS_DIR / f"{sprite_id}.png"
        png_bytes = base64.b64decode(sprite["png_base64"])
        car = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
        multi = _build_multi_car_sprite(car)
        buf = io.BytesIO()
        multi.save(buf, format="PNG")
        png_path.write_bytes(buf.getvalue())
        metadata[sprite_id] = {
            "birthday": sprite["birthday"],
            "flip_rtl": sprite.get("flip_rtl", True),
        }
        _append_to_priority_queue(sprite_id)
        logger.info("Synced sprite %s", sprite_id)

    _write_metadata(metadata)
    _write_last_synced(datetime.now(timezone.utc).isoformat())
    _process_queue()


def _build_multi_car_sprite(car: Image.Image) -> Image.Image:
    LINK_ROW = 3
    LINK_COLOR = (70, 70, 70, 255)

    w, h = car.size
    car_count = 5 if w < 10 else 3
    gap_count = car_count - 1
    total_width = car_count * w + gap_count
    assembled = Image.new("RGBA", (total_width, h), (0, 0, 0, 0))
    for i in range(car_count):
        assembled.paste(car, (i * (w + 1), 0))

    gap_columns = tuple(i * (w + 1) + w for i in range(gap_count))
    for link_x in gap_columns:
        assembled.putpixel((link_x, LINK_ROW), LINK_COLOR)

        col = link_x - 1
        while col >= 0:
            _, _, _, a = assembled.getpixel((col, LINK_ROW))
            if a >= 10:
                break
            assembled.putpixel((col, LINK_ROW), LINK_COLOR)
            col -= 1

        col = link_x + 1
        while col < total_width:
            _, _, _, a = assembled.getpixel((col, LINK_ROW))
            if a >= 10:
                break
            assembled.putpixel((col, LINK_ROW), LINK_COLOR)
            col += 1

    return assembled


def _process_queue() -> None:
    if not settings.mbta_server_url or not settings.pi_api_key:
        return
    try:
        response = requests.post(
            f"{settings.mbta_server_url}/queued/consume",
            headers={"X-API-Key": settings.pi_api_key},
            timeout=10,
        )
        response.raise_for_status()
    except Exception as e:
        logger.warning("Queue check failed: %s", e)
        return
    for sprite_id in response.json().get("ids", []):
        if not _UUID_RE.match(sprite_id):
            logger.warning("Skipping queued sprite with invalid id: %r", sprite_id)
            continue
        if (SPECIAL_TRAINS_DIR / f"{sprite_id}.png").exists():
            _append_to_priority_queue(sprite_id)
            logger.info("Priority queued sprite %s", sprite_id)


def _append_to_priority_queue(sprite_id: str) -> None:
    queue_path = SPECIAL_TRAINS_DIR / "priority_queue.json"
    queue = []
    if queue_path.exists():
        try:
            queue = json.loads(queue_path.read_text())
        except Exception as e:
            logger.warning("Could not parse priority_queue.json: %s", e)
            queue = []
    if sprite_id not in queue:
        queue.append(sprite_id)
    queue_path.write_text(json.dumps(queue))


def _read_metadata() -> dict:
    if METADATA_PATH.exists():
        try:
            return json.loads(METADATA_PATH.read_text())
        except Exception:
            pass
    return {}


def _write_metadata(metadata: dict) -> None:
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))


def _read_last_synced() -> str:
    last_synced_path = SPECIAL_TRAINS_DIR / ".last_synced"
    if last_synced_path.exists():
        return last_synced_path.read_text().strip()
    return ""


def _write_last_synced(ts: str) -> None:
    (SPECIAL_TRAINS_DIR / ".last_synced").write_text(ts)
