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

## Troubleshooting

**Logs:**

```bash
journalctl -u mbta-display -f          # live tail
journalctl -u mbta-display -n 100      # last 100 lines
```

**After editing `.env`, restart the service.** `PIXOO_IP_ADDRESS` etc. are only read once at
process startup (`pydantic-settings`), so editing `.env` on a running service does nothing until
you `sudo systemctl restart mbta-display`.

**After a router/network change** (new ISP, new wifi carrier, etc.), both the Pi and the Pixoo
can get reassigned IPs, even if the Pixoo already had a DHCP reservation on the old router. If
logs show something like:

```
HTTPConnectionPool(host='X.X.X.X', port=80): ... Connection refused
```

double check that `PIXOO_IP_ADDRESS` is actually the Pixoo's current IP and not, say, the Pi's
own IP by mistake — run `hostname -I` on the Pi and compare. Find the Pixoo's real IP via the
Divoom app (device settings) or the router's DHCP client list, update `.env`, then restart the
service. Re-adding a DHCP reservation for the Pixoo's MAC on the new router prevents this from
recurring.

**Service is running with no errors, but the Pixoo shows nothing / shows something else:** the
Divoom has multiple "channels" (Clock/Faces, Cloud, Visualizer, Custom) and this app only ever
draws to the Custom channel. The `Display` class forces the device onto Custom once on startup,
so a power cycle self-heals as soon as the service comes back up — you shouldn't need to fix this
by hand after a reboot anymore. This only happens at startup (not on every poll), so you're free
to manually switch the Pixoo to another channel via the Divoom app while the service is running;
it'll just switch back to Custom the next time the service restarts. If it's stuck on the wrong
channel and you don't want to restart the service (e.g. the Pixoo was unreachable at startup),
force it manually:

Check the current channel:

```bash
curl -s -X POST http://<PIXOO_IP>/post -d '{"Command":"Channel/GetIndex"}'
```

Force it back to Custom (index 3):

```bash
curl -s -X POST http://<PIXOO_IP>/post -d '{"Command":"Channel/SetIndex","SelectIndex":3}'
```

If curl can't connect to the Pixoo at all (`Connection refused`, or the source address in
`curl -v` matches the Pi's own IP), that's the stale-IP issue above, not a channel issue — fix
`.env` first.
