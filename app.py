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


async def fetch_data_loop():
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(f'https://api.mcsrvstat.us/3/{SERVER_ADDRESS}')
            stats_dict = json.loads(response.text)
            reached = stats_dict['debug']['ping']

            if (reached):
                print("SERVER REACHED")
                online = stats_dict['online']
                if (online):
                    current_data['online'] = True
                    if (stats_dict['players']['list'] != None):
                        current_data['players'] = stats_dict['players']['list']
            else:
                print("SERVER DOES NOT EXIST OR IS NOT ACCESSIBLE")

            await asyncio.sleep(10)


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

