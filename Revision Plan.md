# Minecraft Server Monitor — Static Site Revision Plan

## What This Branch Is

This is the `static-site` branch. Its goal is a fully static version of the Minecraft Server Monitor: no Python backend, no FastAPI, no SSE. Just HTML, CSS, and JavaScript deployed to Render's free static site tier.

The `main` branch keeps the FastAPI app intact for Raspberry Pi kiosk deployment. Do not merge static-site work back to main and do not touch `app.py` or the deployment playbooks from this branch.

## What the App Does

A browser-based tool that lets any Minecraft player monitor the status of their server in real time. The user enters a server address, and the app shows:

- Online / offline status (green / red background)
- Current player count
- List of online players with their Minecraft skin head avatars

Data comes from the public mcsrvstat.us API (v3): `https://api.mcsrvstat.us/3/{server_address}`. It supports browser requests directly — no backend proxy needed.

## Architecture for This Branch

Everything runs in the browser. No server process.

- **Landing / input view:** A form where the user types in a Minecraft server address and hits Go.
- **Monitor view:** After submission, the page switches to the status display. JavaScript polls the mcsrvstat.us API every 10 seconds using `setInterval`. No SSE.
- **Responsive layout:** The fixed 480x320 Pi layout is gone. This needs to look good on desktop and mobile.
- **Single-page:** One HTML file is fine. The "view switch" between input and monitor can be a show/hide on two divs.

## Current Files to Carry Over or Adapt

- `static/minecraft.css` — Minecraftia font and base styles. Keep and adapt for responsive layout.
- `templates/index.html` — Reference for existing UI logic and the SSE data-handling JS. The `setInterval` polling replaces the `EventSource` code.

## Key Decisions Already Made

- mcsrvstat.us v3 API field to check reachability: `data.debug.ping` (boolean). If false, server is unreachable. If true, check `data.online`.
- Player head avatars come from mc-heads.net: `https://mc-heads.net/avatar/{uuid}/24`.
- The per-player UUID is in `data.players.list[].uuid`.

## Deployment Target

Render static site (free tier). Build command: none (pure static). Publish directory: the repo root or a `/dist` folder if one is created. No server-side rendering, no build step required unless one is added later.

## Things to Keep Clean

- No backend files on this branch (no `app.py`, no `requirements.txt` changes).
- Keep the existing `deployment/` folder untouched — it belongs to the Pi path on main.
- The untracked file `minecraft_server_status.py` in the repo root is unrelated scratch — leave it alone.
