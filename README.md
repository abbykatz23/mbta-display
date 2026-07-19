# MBTA Pixel Train Display

A 64×64 pixel LED display (Divoom Pixoo64) in my apartment that shows live MBTA
predictions for the stations near me, with a little pixel-art train that animates
across the screen whenever one's arriving. Friends can design and submit their own
train car from a website — submissions get worked into the animation rotation, with
better odds during the submitter's birthday week.

This repo is the Raspberry Pi client: it polls the MBTA API and drives the physical
display.

## How the three repos fit together

- **mbta-display** (this repo) — runs on a Raspberry Pi, polls MBTA predictions, and
  drives the physical Pixoo display.
- [mbta-server](https://github.com/abbykatz23/mbta-server) — serverless API
  (Lambda/API Gateway/S3/DynamoDB) that stores submitted sprites and relays live
  display state.
- [mbta-frontend](https://github.com/abbykatz23/mbta-frontend) — React site where
  people design/submit trains, browse a gallery, and watch a live simulation of the
  physical display in a browser.

```
MBTA v3 API ──▶ mbta-display (Pi) ──▶ mbta-server (Lambda/DynamoDB/S3) ──▶ mbta-frontend
                     │                        ▲
                     ▼                        │
              Pixoo LED display      submitted sprites, live state
```

## What it does

- Polls the MBTA v3 API every 20s for predictions at the stations on my commute
  (Park St B/C/D/E, Charles/MGH, Bowdoin, Downtown Crossing) and shows minutes until
  I need to leave for each line, dimming the text as the deadline gets closer.
- Animates a small pixel train across the display when a train is currently
  arriving, color-coded by line, with a cooldown so the same arrival doesn't
  re-trigger the animation repeatedly.
- Every 5 minutes, syncs newly approved sprite submissions from `mbta-server` and
  assembles them into multi-car trains for the animation rotation, including
  birthday-week and birthday-month odds boosts for the submitter's own sprite.
- Pushes its current state to `mbta-server` on every poll cycle so `mbta-frontend`
  can render a live simulation of the display for anyone browsing the site.

## Stack

Python 3.12, `asyncio`, [`pixoo`](https://pypi.org/project/pixoo/) (Divoom Pixoo64
SDK), Pillow, Pydantic/`pydantic-settings`.

## Running it

```bash
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

Create `.env` (not tracked in git):

```
MBTA_API_KEY=
PIXOO_IP_ADDRESS=
MBTA_SERVER_URL=
PI_API_KEY=
```

`MBTA_API_KEY` and `PIXOO_IP_ADDRESS` are required; the server variables are only
needed to sync submitted sprites and push live state.

```bash
python main.py
```

Commute walk times live in `COMMUTE_TIMES` in `settings.py` — update these if the
walk from home to each station changes (e.g. after a move).

For full Raspberry Pi provisioning (systemd service, fresh-hardware setup), see
[SETUP.md](SETUP.md).

## License

MIT — see [LICENSE](LICENSE).
