import os
path = os.path.expanduser("~/.TailscaleSystemTray")
os.makedirs(path, exist_ok=True)
import json
import subprocess
import sys
from TailscaleCommands import executeComand, get_and_set_state_json, stateCallback, setExitNode
from systray import SystemTray
import logging
from PyQt5.QtWidgets import QApplication


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
    
    logging.basicConfig(
        filename=os.path.join(path, 'main.log'),
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    filename = os.path.join(path, 'State.json')
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

runCommand = lambda command: executeComand(command)
executeComand(f"pkexec tailscale set --operator={os.getlogin()}")

def SetSHHandRoutes():
    logging.debug("Setting SSH and routes")
    try:
        if get_and_set_state_json()["SSH"]:
            runCommand("tailscale set --ssh")
            get_and_set_state_json({"SSH": True})
        else:
            runCommand("tailscale set --ssh=false")
            get_and_set_state_json({"SSH": False})
        
        if get_and_set_state_json()["AcceptRoutes"]:
            runCommand("tailscale set --accept-routes")
            get_and_set_state_json({"AcceptRoutes": True})
        else:
            runCommand("tailscale set --accept-routes=false")
            get_and_set_state_json({"AcceptRoutes": False})
            
        if get_and_set_state_json()["UsingExitNode"]:
            setExitNode(get_and_set_state_json()["UsedExitNode"])
            
        if get_and_set_state_json()["ExitNode"]:
            executeComand("tailscale set --advertise-exit-node")
            get_and_set_state_json({"ExitNode": True})
        else:
            executeComand("tailscale set --advertise-exit-node=false")
            get_and_set_state_json({"ExitNode": False})
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
        get_and_set_state_json({"ExitNodes": exitNodes})
    except Exception as e:
        logging.error(f"Error in indexExitNodes: {str(e)}", exc_info=True)

try:
    with open(os.path.join(os.path.expanduser("~/.TailscaleSystemTray"), 'State.json'), 'r') as file:
        pass
except:
    makeJSON()

indexExitNodes()
SetSHHandRoutes()

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    tray = SystemTray(qt_app,)
    tray.run()