from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import httpx
import json
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVER_ADDRESS = os.getenv('SERVER_ADDRESS', 'hypixel.net')
MAX_DISPLAYED_PLAYERS = 5

current_data = {
    'address': SERVER_ADDRESS,
    'online': False,
    'players': [],
    'player_count': 0,
    'heads': {}
}

active_queues: set[asyncio.Queue] = set()


def request_heads(players):
    heads = {}
    for player in players:
        uuid = player.get('uuid')
        name = player.get('name')
        if not name:
            continue
        if uuid:
            heads[name] = f'https://mc-heads.net/avatar/{uuid}/24'
        else:
            heads[name] = f'https://mc-heads.net/avatar/{name}/24'
    return heads


_last_broadcast: str = ""


async def broadcast():
    global _last_broadcast
    payload = json.dumps(current_data)
    if payload == _last_broadcast:
        return
    _last_broadcast = payload
    for queue in active_queues:
        await queue.put(payload)


async def fetch_data_loop():
    async with httpx.AsyncClient() as client:
        while True:
            player_count = 0
            try:
                logger.info(f"Fetching data for: {SERVER_ADDRESS}")

                response = await client.get(f'https://api.mcsrvstat.us/3/{SERVER_ADDRESS}')
                stats_dict = response.json()

                reached = stats_dict.get('debug', {}).get('ping', False)

                if reached:
                    online = stats_dict.get('online', False)

                    if online:
                        players_data = stats_dict.get('players', {})
                        player_count = players_data.get('online', 0)
                        players_list = [
                            p for p in players_data.get('list', []) if p.get('name')
                        ][:MAX_DISPLAYED_PLAYERS]

                        current_data['heads'] = {}
                        if players_list:
                            current_data['heads'] = request_heads(players_list)
                            logger.info(f"  Heads: {current_data['heads']}")

                        current_data['players'] = players_list
                        current_data['online'] = True
                        current_data['player_count'] = player_count

                        logger.info(f"Updated current_data with {player_count} players")

                    else:
                        logger.info("SERVER OFFLINE (reached but not accepting connections)")
                        current_data['online'] = False
                        current_data['players'] = []
                        current_data['player_count'] = 0

                else:
                    logger.info("SERVER NOT REACHABLE (does not exist or is not accessible)")
                    current_data['online'] = False
                    current_data['players'] = []
                    current_data['player_count'] = 0

                logger.info(f"Current state — Online: {current_data['online']}, Players: {player_count}")
                await broadcast()

            except Exception as e:
                logger.error(f"ERROR during fetch: {e}", exc_info=True)
                current_data['online'] = False
                current_data['players'] = []
                current_data['heads'] = {}
                current_data['player_count'] = 0
                await broadcast()

            await asyncio.sleep(10)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI server...")
    logger.info(f"Monitoring server: {SERVER_ADDRESS}")
    asyncio.create_task(fetch_data_loop())
    yield


app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/stream")
async def stream():
    queue: asyncio.Queue = asyncio.Queue()
    active_queues.add(queue)

    async def event_generator():
        try:
            yield f"data: {json.dumps(current_data)}\n\n"
            while True:
                payload = await queue.get()
                yield f"data: {payload}\n\n"
        except GeneratorExit:
            pass
        finally:
            active_queues.discard(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", encoding="utf-8") as f:
        return f.read()
