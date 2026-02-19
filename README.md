# mc-server-status-and-display
Continuously check status of Minecraft server and display info

to use the monitor locally, run this command to start the app on localhost:8000  

``uvicorn app:app --reload``
 
to deploy to raspberry pi, simply clone the repo and run this command from within the main directory [UNTESTED]

``ansible-playbook ansible/playbook.yaml -i "PI_IP," -e "server_address=hypixel.net"``
