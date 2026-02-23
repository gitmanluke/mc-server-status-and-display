# mc-server-status-and-display
Continuously check status of Minecraft server and display info

## Local monitoring
First, set the SERVER_ADDRESS enviornment variable to your desired server address.
### Example: MacOS

`` export SERVER_ADDRESS=hypixel.net ``

Then run this command to start the app on localhost:8000  

``uvicorn app:app --reload``

## Deploy to raspberry Pi
simply clone the repo and run this command from within the main directory
PI_IP: replace with the IP address of your raspberry pi
PI_USERNAME: replace with the username you chose when installing the raspberry pi OS
SERVER_IP: replace with the IP address of the server you intend to monitor

``ansible-playbook deployment/playbook.yaml -i "PI_IP," --user PI_USERNAME -e "server_address=SERVER_IP"``
