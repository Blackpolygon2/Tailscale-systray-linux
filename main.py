import os
import json
import subprocess
import sys
from TailscaleCommands import executeComand, Use_json, stateCallback, setExitNode
from systray import SystemTray
import logging
from PyQt5.QtWidgets import QApplication

logging.basicConfig(
    filename='main.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

user_home = os.path.expanduser("~")
username = os.path.split(user_home)[-1]

def makeJSON():
    logging.debug("Creating State.json")
    data = {
        "SSH": False,
        "ExitNode": False,
        "AcceptRoutes": False,
        "UsingExitNode": False,
        "UsedExitNode": "",
        "ExitNodes": {},
    }
    filename = 'State.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

runCommand = lambda command: executeComand(command)
executeComand(f"pkexec tailscale set --operator={os.getlogin()}")

def SetSHHandRoutes():
    logging.debug("Setting SSH and routes")
    try:
        if Use_json()["SSH"]:
            runCommand("tailscale set --ssh")
            Use_json({"SSH": True})
        else:
            runCommand("tailscale set --ssh=false")
            Use_json({"SSH": False})
        
        if Use_json()["AcceptRoutes"]:
            runCommand("tailscale set --accept-routes")
            Use_json({"AcceptRoutes": True})
        else:
            runCommand("tailscale set --accept-routes=false")
            Use_json({"AcceptRoutes": False})
            
        if Use_json()["UsingExitNode"]:
            setExitNode(Use_json()["UsedExitNode"])
            
        if Use_json()["ExitNode"]:
            executeComand("tailscale set --advertise-exit-node")
            Use_json({"ExitNode": True})
        else:
            executeComand("tailscale set --advertise-exit-node=false")
            Use_json({"ExitNode": False})
    except Exception as e:
        logging.error(f"Error in SetSHHandRoutes: {str(e)}", exc_info=True)

def indexExitNodes():
    logging.debug("Indexing exit nodes")
    try:
        exitnodes = subprocess.run("tailscale exit-node list".split(), capture_output=True, text=True).stdout.split("\n")
        exitNodes = {"None": ""}
        for exitnode in exitnodes:
            if "100" in exitnode:
                exitNodes[exitnode.split()[1]] = exitnode.split()[0]
        Use_json({"ExitNodes": exitNodes})
    except Exception as e:
        logging.error(f"Error in indexExitNodes: {str(e)}", exc_info=True)

try:
    with open('State.json', 'r') as file:
        pass
except:
    makeJSON()

indexExitNodes()
SetSHHandRoutes()

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    tray = SystemTray(qt_app,)
    tray.run()