# mc-server-status-and-display
Continuously check status of Minecraft server and display info

## Local monitoring
First, set the SERVER_ADDRESS enviornment variable to your desired server address.
### Example: MacOS

`` export SERVER_ADDRESS=hypixel.net ``

Then run this command to start the app on localhost:8000  

``uvicorn app:app --reload``

## Deploy to raspberry Pi [UNTESTED]
simply clone the repo and run this command from within the main directory

``ansible-playbook ansible/playbook.yaml -i "PI_IP," -e "server_address=hypixel.net"``
