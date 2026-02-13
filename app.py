from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import asyncio
import httpx
import requests
import json
import time
import os

SERVER_ADDRESS = os.getenv('SERVER_ADDRESS', 'hypixel.net')  # default fallback

app = FastAPI()
current_data = {}

async def request_heads(players):
    heads = {}
    for player in players:
        uuid = player.get('uuid')
        name = player.get('name')
        if uuid and name:
            head_url = f'https://mc-heads.net/avatar/{uuid}/24'
            heads[name] = head_url
    return heads


async def fetch_data_loop():
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(f'https://api.mcsrvstat.us/3/{SERVER_ADDRESS}')
            stats_dict = response.json()
            reached = stats_dict.get('debug', {}).get('ping', False)

            if (reached):   
                print("SERVER REACHED")
                online = stats_dict.get('online', False)
                if (online):
                    players_data = stats_dict.get('players', {})
                    players_list = players_data.get('list', [])

                    heads = await request_heads(players_list)

                    current_data['players'] = players_list
                    current_data['heads'] = heads
                    current_data['online'] = True
                else:
                    current_data['online'] = False
                    current_data['players'] = []
            else:
                print("SERVER DOES NOT EXIST OR IS NOT ACCESSIBLE")

            await asyncio.sleep(10000)


@app.on_event("startup")
async def startup_event():
    # Start background data fetching
    asyncio.create_task(fetch_data_loop())


@app.get("/data")
async def get_current_data():
    return current_data


@app.get("/", response_class=HTMLResponse)
async def home():
    # Serve your HTML page
    with open("templates/index.html") as f:
        return f.read()