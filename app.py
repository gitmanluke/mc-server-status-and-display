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
MOCK_MODE = os.getenv('MOCK_MODE', 'false').lower() == 'true'

MOCK_PLAYERS = [
    {"name": "Notch", "uuid": "069a79f4-44e9-4726-a5be-fca90e38aaf5"},
    {"name": "Dream", "uuid": "ec70bcaf-702f-4bb8-b48d-276fa52a780c"},
    {"name": "Grian", "uuid": "5f8eb73b-25be-4c5a-a50f-d27d65e30ca0"},
    {"name": "Ph1LzA", "uuid": "84555089-add1-49b1-a26d-8021270a40f0"},
    {"name": "xisumavoid", "uuid": "8d86df19-fa5c-4939-ac7c-3b90b2b6abb6"},
]

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
        if uuid and name:
            heads[name] = f'https://mc-heads.net/avatar/{uuid}/24'
        else:
            heads[name] = f'https://mc-heads.net/avatar/%7Buuid%7D/24'
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
    if MOCK_MODE:
        logger.info("MOCK_MODE enabled — serving fake player data")
        current_data['online'] = True
        current_data['players'] = MOCK_PLAYERS
        current_data['player_count'] = len(MOCK_PLAYERS)
        current_data['heads'] = request_heads(MOCK_PLAYERS)
        await broadcast()
        while True:
            await asyncio.sleep(3600)

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
                        players_list = players_data.get('list', [])
                        player_count = players_data.get('online', 0)

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
    with open("templates/index.html") as f:
        return f.read()
