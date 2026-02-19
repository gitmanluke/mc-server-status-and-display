from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from mcstatus import JavaServer
import asyncio
import httpx
import requests
import json
import time
import os

SERVER_ADDRESS = os.getenv('SERVER_ADDRESS', 'hypixel.net')  # default fallback

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


# given a list of players, returns a dict with name: head image pairs
async def request_heads(players):
    heads = {}
    for player in players:
        uuid = player.get('uuid')
        name = player.get('name')
        if uuid and name:
            head_url = f'https://mc-heads.net/avatar/{uuid}/24'
            heads[name] = head_url
        else:
            heads[name] = f'https://mc-heads.net/avatar/%7Buuid%7D/24'
    return heads


# requesting data for specified server using mcsrvstat public API
async def fetch_data_loop():
    async with httpx.AsyncClient() as client:
        while True:
            try:
                print(f"Fetching data for: {SERVER_ADDRESS}")
                
                response = await client.get(f'https://api.mcsrvstat.us/3/{SERVER_ADDRESS}')
                stats_dict = response.json()
                
                reached = stats_dict.get('debug', {}).get('ping', False)
                
                if reached:   
                    online = stats_dict.get('online', False)
                    
                    if online:
                        players_data = stats_dict.get('players', {})
                        players_list = players_data.get('list', [])
                        player_count = stats_dict.get('players').get('online')
                        
                        if players_list:
                            heads = await request_heads(players_list)
                            current_data['heads'] = heads
                            print(f"  Heads: {current_data['heads']}")

                        # Update current_data
                        current_data['players'] = players_list
                        current_data['online'] = True
                        current_data['player_count'] = player_count
                        
                        print(f"Updated current_data with {player_count} players")
                        
                    else:
                        print("SERVER OFFLINE (reached but not accepting connections)")
                        current_data['online'] = False
                        current_data['players'] = []
                        
                else:
                    print("SERVER NOT REACHABLE (does not exist or is not accessible)")
                    current_data['online'] = False
                    current_data['players'] = []
                
                print(f"\nCurrent state:")
                print(f"  Online: {current_data['online']}")
                print(f"  Players: {player_count}")
                
            except Exception as e:
                print(f"ERROR during fetch: {e}")
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


# data endpoint used by updateDisplay function in 'index.html'
@app.get("/data")
async def get_current_data():
    print(f"\n[data endpoint called] Returning: {current_data}")
    return current_data


# home page endpoint
@app.get("/", response_class=HTMLResponse)
async def home():
    # Serve your HTML page
    with open("templates/index.html") as f:
        return f.read()