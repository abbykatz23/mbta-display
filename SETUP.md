# Pi Setup

How to get this running on a Raspberry Pi from scratch (e.g. new hardware, or a reinstall).

## 1. Clone and install

```bash
git clone <this repo> ~/mbta-display
cd ~/mbta-display
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

## 2. Create `.env`

Not tracked in git. Create `~/mbta-display/.env` with:

```
MBTA_API_KEY=
PIXOO_IP_ADDRESS=
MBTA_SERVER_URL=
PI_API_KEY=
```

`MBTA_API_KEY` and `PIXOO_IP_ADDRESS` are required. `MBTA_SERVER_URL`/`PI_API_KEY` are only
needed if pushing display state to the remote server (see `mbta-server` repo). Get values from
wherever they were last stored (password manager / previous Pi's `.env`).

Give the Pixoo a DHCP reservation on the router so `PIXOO_IP_ADDRESS` doesn't drift.

## 3. Update commute times

`settings.py` has `COMMUTE_TIMES` hardcoded per station — update these if the walk time from
home to each station has changed (e.g. moved apartments).

## 4. systemd service (auto-start on boot)

Not tracked in git (lives in `/etc/systemd/system/` on the Pi's OS, so it doesn't transfer with
the repo). Create `/etc/systemd/system/mbta-display.service`:

```ini
[Unit]
Description=MBTA Display
After=network.target

[Service]
User=abbykatz
WorkingDirectory=/home/abbykatz/mbta-display
ExecStart=/home/abbykatz/mbta-display/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Adjust `User`/paths if different on the new Pi. Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mbta-display
```

`Restart=always` + `enabled` means it survives crashes and power-cycle reboots with no manual
steps once this is set up.

## Verify

```bash
systemctl status mbta-display
```
