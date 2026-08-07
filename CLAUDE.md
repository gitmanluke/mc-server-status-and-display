# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Minecraft server status dashboard built with FastAPI, designed to run on a Raspberry Pi with a 3.5-inch MHS35 LCD screen in kiosk mode. It polls the public `mcsrvstat.us` API and displays server status, player count, and player avatars.

## Commands

**Run locally:**
```bash
export SERVER_ADDRESS=hypixel.net
uvicorn app:app --reload
# Dashboard at http://localhost:8000
```

**Test API integration:**
```bash
python3 test_polling.py
```

**Deploy to Raspberry Pi:**
```bash
ansible-playbook deployment/playbook.yaml \
  -i "PI_IP," \
  --user PI_USERNAME \
  -e "server_address=SERVER_IP"
```

**Optional — set up MHS35 LCD screen driver:**
```bash
ansible-playbook deployment/setup-screen.yaml -i "PI_IP," --user PI_USERNAME
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

## Architecture

**`app.py`** — FastAPI server with two endpoints (`GET /` and `GET /data`) and a background polling loop. On startup, `fetch_data_loop()` runs every 10 seconds, querying `https://api.mcsrvstat.us/3/{SERVER_ADDRESS}` and fetching player head images from `mc-heads.net`. Results are stored in the `current_data` dict and served via `/data`.

**`templates/index.html`** — Single-page dashboard optimized for 480×320px (small LCD). JavaScript polls `/data` every 2 seconds and updates the DOM. Status background changes color: green (online), red (offline), black (checking).

**`static/minecraft.css`** — Minecraftia font (base64-embedded) and Minecraft chat color palette utility classes.

**`deployment/`** — Ansible playbooks that provision a Raspberry Pi: clones the repo, installs a Python venv, and creates two systemd services — `minecraft-monitor` (uvicorn on port 8000) and `chromium-kiosk` (full-screen Chromium pointing at localhost:8000).

## Key Configuration

- Target server is set via the `SERVER_ADDRESS` environment variable (default: `hypixel.net`).
- The systemd service template injects this at deploy time via Ansible variable `server_address`.
- No database or persistent storage — all state is in-memory.
