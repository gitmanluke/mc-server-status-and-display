from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import httpx
import requests
import json
import time
import os

SERVER_ADDRESS = os.getenv('SERVER_ADDRESS', '24.60.155.55:25565')  # default fallback

app = FastAPI()

# Initialize current_data with all fields
current_data = {
    'address': SERVER_ADDRESS,
    'online': False,
    'players': [],
    'player_count': 0,
    'heads': {}
}

app.mount("/static", StaticFiles(directory="static"), name="static")


async def request_heads(players):
    heads = {}
    for player in players:
        uuid = player.get('uuid')
        name = player.get('name')
        if uuid and name:
            head_url = f'https://mc-heads.net/avatar/{uuid}/24'
            heads[name] = head_url
            print(f"  - Added head for {name}: {head_url}")
    return heads


async def fetch_data_loop():
    async with httpx.AsyncClient() as client:
        while True:
            try:
                print(f"\n{'='*50}")
                print(f"Fetching data for: {SERVER_ADDRESS}")
                
                # Fixed the f-string formatting
                response = await client.get(f'https://api.mcsrvstat.us/3/{SERVER_ADDRESS}')
                stats_dict = response.json()
                
                # Log the raw response for debugging
                print(f"Raw API Response:")
                print(json.dumps(stats_dict, indent=2))
                
                reached = stats_dict.get('debug', {}).get('ping', False)
                
                if reached:   
                    print("✓ SERVER REACHED")
                    online = stats_dict.get('online', False)
                    
                    if online:
                        print("✓ SERVER ONLINE")
                        players_data = stats_dict.get('players', {})
                        players_list = players_data.get('list', [])
                        player_count = stats_dict.get('players').get('online')
                        
                        print(f"Players found: {len(players_list)}")
                        if players_list:
                            print("Player details:")
                            for player in players_list:
                                print(f"  - {player.get('name')} (UUID: {player.get('uuid')})")
                        
                        # Fetch player heads
                        print("Fetching player heads...")
                        heads = await request_heads(players_list)
                        
                        # Update current_data
                        current_data['players'] = players_list
                        current_data['heads'] = heads
                        current_data['online'] = True
                        current_data['player_count'] = player_count
                        
                        print(f"✓ Updated current_data with {len(players_list)} players")
                        
                    else:
                        print("✗ SERVER OFFLINE (reached but not accepting connections)")
                        current_data['online'] = False
                        current_data['players'] = []
                        current_data['heads'] = {}
                        
                else:
                    print("✗ SERVER NOT REACHABLE (does not exist or is not accessible)")
                    current_data['online'] = False
                    current_data['players'] = []
                    current_data['heads'] = {}
                
                print(f"\nCurrent state:")
                print(f"  Online: {current_data['online']}")
                print(f"  Players: {len(current_data.get('players', []))}")
                print(f"  Heads: {len(current_data.get('heads', {}))}")
                
            except Exception as e:
                print(f"✗ ERROR during fetch: {e}")
                import traceback
                traceback.print_exc()
                
                # Set error state
                current_data['online'] = False
                current_data['players'] = []
                current_data['heads'] = {}
            
            await asyncio.sleep(10)


@app.on_event("startup")
async def startup_event():
    print("Starting FastAPI server...")
    print(f"Monitoring server: {SERVER_ADDRESS}")
    # Start background data fetching
    asyncio.create_task(fetch_data_loop())


@app.get("/data")
async def get_current_data():
    print(f"\n[/data endpoint called] Returning: {current_data}")
    return current_data


@app.get("/", response_class=HTMLResponse)
async def home():
    # Serve your HTML page
    with open("templates/index.html") as f:
        return f.read()