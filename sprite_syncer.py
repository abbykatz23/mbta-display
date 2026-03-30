import base64
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

from settings import settings

SPECIAL_TRAINS_DIR = Path("static/special_trains")
METADATA_PATH = SPECIAL_TRAINS_DIR / "metadata.json"

logger = logging.getLogger(__name__)


def sync_sprites() -> None:
    """Download any newly approved sprites from mbta-server and update metadata."""
    if not settings.mbta_server_url or not settings.pi_api_key:
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
        png_path = SPECIAL_TRAINS_DIR / f"{sprite_id}.png"
        png_bytes = base64.b64decode(sprite["png_base64"])
        png_path.write_bytes(png_bytes)
        metadata[sprite_id] = {
            "birthday": sprite["birthday"],
        }
        logger.info("Synced sprite %s", sprite_id)

    _write_metadata(metadata)
    _write_last_synced(datetime.now(timezone.utc).isoformat())


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
