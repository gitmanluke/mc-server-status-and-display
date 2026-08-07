# Minecraft Server Monitor — Implementation Plan

This document describes a set of bug fixes, reliability improvements, and an
architecture change for the mc-server-status-and-display project. Implement
each section in order.

---

## 1. Bug Fixes

### 1.1 `player_count` referenced before assignment

**File:** `app.py`

In `fetch_data_loop`, `player_count` is only assigned inside the `if online:`
branch but is referenced in the `print` statement at the bottom of the `try`
block. If the server is reachable but offline this raises a `NameError`.

**Fix:** Initialize `player_count = 0` at the top of the `while True` loop,
before any branching logic.

### 1.2 Stale `player_count` when server goes offline

**File:** `app.py`

When the server is offline or unreachable, `current_data['player_count']` is
never reset, so old values persist.

**Fix:** In both offline branches (server offline and server not reachable),
explicitly set:

```python
current_data['player_count'] = 0
current_data['players'] = []
```

### 1.3 Stale player heads when players leave

**File:** `app.py`

`current_data['heads']` grows indefinitely and is never cleared when players
log off.

**Fix:** Before calling `request_heads`, reset the heads dict:

```python
current_data['heads'] = {}
```

---

## 2. Design Improvements

### 2.1 Replace deprecated `@app.on_event("startup")`

**File:** `app.py`

FastAPI deprecated `@app.on_event` in favour of the lifespan context manager.

**Fix:** Replace the startup event handler with a lifespan function:

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(fetch_data_loop())
    yield

app = FastAPI(lifespan=lifespan)
```

Remove the old `@app.on_event("startup")` function entirely.

### 2.2 Remove unused `requests` dependency

**File:** `requirements.txt`

`requests` is listed but never imported. `httpx` handles all HTTP calls.

**Fix:** Delete the `requests` line from `requirements.txt`.

### 2.3 Replace `print` statements with `logging`

**File:** `app.py`

Scattered `print` calls are inappropriate for a systemd-managed service.

**Fix:** At the top of `app.py`, add:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

Replace all `print(...)` calls with the appropriate log level:
- Routine status → `logger.info(...)`
- Errors and exceptions → `logger.error(...)`

---

## 3. Architecture Change — Replace UI Polling with Server-Sent Events (SSE)

Currently the frontend calls `GET /data` every 2 seconds regardless of whether
anything has changed. Replace this with SSE so the server pushes updates to the
browser only when the background task detects a change.

### 3.1 Backend — add SSE endpoint

**File:** `app.py`

Add an `asyncio.Queue` that the background fetch loop writes to whenever
`current_data` changes. Add a new `GET /stream` endpoint that streams updates
to connected clients using SSE.

Implementation notes:
- Import `asyncio.Queue` and `StreamingResponse` from fastapi.responses.
- Create a module-level set to track active queues (one per connected client):
  `active_queues: set[asyncio.Queue] = set()`
- After updating `current_data` in `fetch_data_loop`, serialize it to JSON and
  put it on every active queue.
- The `/stream` endpoint should:
  1. Create a new `asyncio.Queue` and add it to `active_queues`.
  2. Send the current state immediately as the first event so the client doesn't
     wait up to 10 seconds for the first update.
  3. `await queue.get()` in a loop, yielding each message formatted as an SSE
     event: `f"data: {payload}\n\n"`.
  4. On disconnect (generator exit / `GeneratorExit`), remove the queue from
     `active_queues`.
- Return a `StreamingResponse` with `media_type="text/event-stream"` and
  headers `Cache-Control: no-cache` and `X-Accel-Buffering: no`.

### 3.2 Frontend — replace `setInterval` fetch with SSE listener

**File:** `templates/index.html`

Remove the `updateDisplay` function and its `setInterval` call entirely.
Replace with an `EventSource` listener:

```javascript
const source = new EventSource('/stream');

source.onmessage = function(event) {
    const data = JSON.parse(event.data);
    // apply the same display update logic that was in updateDisplay()
};

source.onerror = function() {
    document.body.className = 'offline';
    document.getElementById('statusIndicator').textContent = '● Error';
    document.getElementById('playerCount').textContent = 'Players: --';
};
```

The display update logic (setting body class, status indicator, player count,
and player list HTML) should remain identical to what was in `updateDisplay()`,
just moved into the `onmessage` handler.

### 3.3 Remove the now-unused `/data` endpoint

**File:** `app.py`

Once the SSE stream is in place the `GET /data` endpoint is no longer used by
the frontend. Remove it.

---

## 4. Housekeeping

### 4.1 Fix README backtick formatting

**File:** `README.md`

The inline code blocks use double backticks (` `` `) instead of single
backticks. Fix both code spans so they render correctly.

### 4.2 Add comment to `setup-screen.yaml` explaining async task

**File:** `deployment/setup-screen.yaml` (or `setup-screen.yaml` at root)

The `async: 60 / poll: 0` on the LCD driver task means Ansible fires the
script and does not wait for it — intentional because the script reboots the
Pi. Add a comment above the task making this explicit:

```yaml
# The MHS35-show script triggers a reboot, so we run it async and do not poll.
# Ansible will not report success/failure; check the Pi console after reboot.
```