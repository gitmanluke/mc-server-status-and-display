# mc-server-status-and-display
 Continuously check status of Minecraft server and display info

to use the monitor locally, run this command to start the app on localhost:8000 after installing the dependencies
''uvicorn app:app --reload''
 
to deploy to raspberry pi, simply clone the repo to your local machine and run this command from within the main directory

'' ansible-playbook deployment/playbook.yaml -i "ANY_PI_IP," --user PI_USERNAME -e "server_address=ANY_SERVER" ''