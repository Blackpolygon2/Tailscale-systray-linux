from TailscaleCommands import executeComand,Use_json,stateCallback,setExitNode
import os, json, subprocess,time
from systray import systemtray


user_home = os.path.expanduser("~")
username = os.path.split(user_home)[-1]
def makeJSON():
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
        
        
runCommand = lambda command:executeComand(command)        
executeComand(f"pkexec tailscale set --operator={os.getlogin()}")
def SetSHHandRoutes():
    if Use_json()["SSH"]:
        runCommand("tailscale set --ssh")
        Use_json({"SSH":True})
    else:
        runCommand("tailscale set --ssh=false")
        Use_json({"SSH":False})

    
    if Use_json()["AcceptRoutes"]:
        runCommand("tailscale set --accept-routes")
        Use_json({"AcceptRoutes":True})
    else:
        runCommand("tailscale set --accept-routes=false")
        Use_json({"AcceptRoutes":False})
        
    if Use_json()["UsingExitNode"]:
        setExitNode(Use_json()["UsedExitNode"])
        
    if Use_json()["ExitNode"]:
        executeComand("tailscale set --advertise-exit-node")
        Use_json({"ExitNode":True})
    else:
        executeComand("tailscale set --advertise-exit-node=false")
        Use_json({"ExitNode":False})


def indexExitNodes():
    exitnodes = subprocess.run("tailscale exit-node list".split(), capture_output=True, text=True).stdout.split("\n")
    exitNodes = {"None":""}
    for exitnode in exitnodes:
        if "100" in exitnode:
            exitNodes[exitnode.split()[1]]=exitnode.split()[0]
    Use_json({"ExitNodes":exitNodes})
    
try:
    with open('State.json', 'r') as file:
        pass
except:
    makeJSON()

indexExitNodes()
SetSHHandRoutes()

if __name__ == "__main__":
    
    
    # Create an instance of your tray app
    tray_app = systemtray()
    
    # Run the tray icon in a separate thread
    tray_app.run_in_thread()
    
    
    
    
    # The program will wait here until the user quits via the tray's 'Quit' button
    try:
        tray_app.shutdown_event.wait()
    except KeyboardInterrupt:
        # This allows you to stop the main program with Ctrl+C
        print("\nCtrl+C detected, shutting down...")
        tray_app.icon.stop()

    