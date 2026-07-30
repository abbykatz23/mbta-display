# MBTA Pixel Train Display

A 64×64 pixel LED display [Divoom Pixoo64](https://divoom.com/products/pixoo-64?srsltid=AfmBOorv_xBQ_0dPnQDyW66Dh735sF-rbOt_An_Nx16UJzCyesVKCJpG&_su_rec=nfIGcJskwXoMFycteP8mBxweyMospgWDFwB5VIDcbShoT-fjVWok00A1ZcsyKOf0iAJW57Ix-qHVlOIBnV34k_J9bvWbkaKaOZI0G3sjw41lR8VPsXNOUCPNXTu-uIWmYfqBUghqoBBRi0hhG_tLz6FqFXDJv-7GC8cTnBtB2u9iZzmuyldsImzmf611eVrwZ2o_BcmWfd8LDOt4DLEed5sAPMwrSYjzn42OnUOW7CuyJtyHc_COlwYHP-BoBfXiVs6SRluYjEPEykZ4&_su_rec_id=9d75e6d9-109e-4a9b-8065-2b9795ad64fa-1785378986) in my apartment that shows live MBTA
predictions for the stations near me, with a little pixel-art train that animates
across the screen whenever one's arriving at the station.

You can submit a train right now at [makeatrain.pre-idea.com](https://makeatrain.pre-idea.com)
(or [makeatrain.netlify.app](https://makeatrain.netlify.app) in case I don't renew my domain subscription hehe).
DO IT!!! IT'S SO FUN!!! Any time a train goes by, there's a chance it'll be your train, with
better odds during the your birthday week!

This repo is the Raspberry Pi client: it polls the MBTA API and drives the physical
display.

## In Action

Train times auto-update every 20 seconds:

https://github.com/user-attachments/assets/ec3c7edc-39b4-4198-a4df-60cb91891209

An animation of the appropriately-colored T car goes by when it's arrived at my local station.
Left -> right means it's northbound, right -> left means it's southbound.
At the time of taking the below photo, there was a southbound orange line train at Downtown Crossing station.




<img width="3024" height="4032" alt="IMG_7997" src="https://github.com/user-attachments/assets/0084f256-d050-482e-a4dd-33cedf7dafce" />


And extra fun train sprites go by occasionally by chance (or by an admin manually triggering it :D).
Every month gets a special train that has 1/6 odds of appearing every time a train is at the station.
I of course had to get festive for July :)


https://github.com/user-attachments/assets/86fa24f6-b337-49e4-843e-48e608e25749



## How the three repos fit together

- **mbta-display** (this repo) — runs on a Raspberry Pi, polls MBTA predictions, and
  drives the physical Pixoo display.
- [mbta-server](https://github.com/abbykatz23/mbta-server) — serverless API
  (Lambda/API Gateway/S3/DynamoDB) that stores submitted sprites and relays live
  display state.
- [mbta-frontend](https://github.com/abbykatz23/mbta-frontend) — React site where
  people design/submit trains, browse a gallery, and watch a live simulation of the
  physical display in a browser.


https://excalidraw.com/#json=BRuBvz4900FrxCK2AZXIK,rJ98H-aRb1J4b7mux0_sFg


<img width="6406" height="5211" alt="mbta-arch2" src="https://github.com/user-attachments/assets/17f89242-9c3f-46b7-8c7e-11965486e44e" />



## What it does

- Polls the MBTA v3 API every 20s for predictions at the stations on my commute
  (Park St B/C/D/E, Charles/MGH, Bowdoin, Downtown Crossing) and shows minutes until
  I need to leave for each line, with the text brightening as the deadline gets closer.
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


## Running it (requires the Divoom display to see anything interesting!)

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
