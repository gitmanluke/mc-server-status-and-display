import requests
import json
import time
from mcstatus import JavaServer

response = requests.get("https://api.mcsrvstat.us/3/hypixel.net")

data = response.json()

print(data.keys())
print(data.get('online'))