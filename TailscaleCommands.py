import subprocess
import platform
import json
import shlex
from typing import Literal
from notifypy import Notify
import logging



logging.basicConfig(
    filename='functions.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)



def runCommand(command): return executeComand(command)


def executeComand(command, use_sudo=False):

    try:
        if use_sudo:
            command = "pkexec " + command

        result = subprocess.run(shlex.split(
            command), capture_output=True, text=True, check=True)
        logging.debug(f" Command '{command}' successful!")
        return result.stdout

    except FileNotFoundError:
        logging.error(
            f" Error: Command not found. Is '{shlex.split(command)[0]}' installed and in your PATH?")
        return None

    except subprocess.CalledProcessError as e:
        logging.error(f" Command '{command}' failed with return code {e.returncode}.")
        if e.stderr:
            logging.error(f"Error details:\n{e.stderr}")

        if not use_sudo:
            logging.error("Retrying with pkexec (sudo)...")
            return executeComand(command, use_sudo=True)

        return None


def Use_json(*DictItemValue: dict):
    with open('State.json', 'r') as file:
        data = json.load(file)

    for DictItemValue in DictItemValue:
        data[list(DictItemValue.keys())[0]] = list(DictItemValue.values())[0]
        
        with open('State.json', 'w') as file:
            json.dump(data, file, indent=4)


    return (data)


def GetTailwindStatus():
    result = subprocess.run("tailscale status".split(),
                            capture_output=True, text=True)

    lines = result.stdout.splitlines()
    ip = subprocess.run("tailscale ip -4".split(),
                        capture_output=True, text=True).stdout

    for line in lines:

        if ip.strip() in line:
            return (line.strip())

 
def pingWebsite(target_url, count=4):
    try:
        if platform.system() == "Windows":
            command = ["ping", "-n", str(count), target_url]
        else:  
            command = ["ping", "-c", str(count), target_url]

        result = subprocess.run(
            command, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False
    except FileNotFoundError:
        logging.error("Ping command not found. Ensure it's in your system's PATH.")


stateCallbackOptions = Literal["onOff","exitNode", "ssh", "AcceptRoutes", "t"]
def stateCallback(itemRequested: stateCallbackOptions=""):
    status_line = GetTailwindStatus()
    if status_line:
        if "exit" in status_line:
            Use_json({"ExitNode": True})
        else:
            Use_json({"ExitNode": False})
    else:
        Use_json({"ExitNode": False})
        
    match itemRequested:
        case "onOff":
            return pingWebsite("100.100.100.100", count=2)
        case 'exitNode':
            return Use_json()["ExitNode"]
        case 'ssh':
            return Use_json()["SSH"]

        case 'AcceptRoutes':
            return Use_json()["AcceptRoutes"]
        case "test":
            pass
        case _:
            logging.debug('pls correct input or no input used but stateCallback was called  ')
    pass




def toggleTailscaleOnOff():
    if stateCallback('onOff'):
        runCommand("tailscale down")
    else:
        runCommand("tailscale up")


def executeTailscaleSetToggle(ItemToBeSet: str):
    
    match ItemToBeSet:
        case "exitNode":
            is_exit_node_on = Use_json()['ExitNode']
            if is_exit_node_on:
                logging.debug(" Exit Node advertising is ON, turning it OFF...")
                executeComand("tailscale set --advertise-exit-node=false")
                Use_json({"ExitNode": False})
            else:
                setExitNode("off")
                logging.debug(" Exit Node advertising is OFF, turning it ON...")
                executeComand("tailscale set --advertise-exit-node")
                
                Use_json({"ExitNode": True})

        case "ssh":
            is_ssh_on = Use_json()['SSH']
            if is_ssh_on:
                logging.debug(" SSH is ON, turning it OFF...")
                executeComand("tailscale set --ssh=false")
                Use_json({"SSH": False})
            else:
                logging.debug(" SSH is OFF, turning it ON...")
                executeComand("tailscale set --ssh")
                Use_json({"SSH": True})

        case "acceptRoutes":
            are_routes_accepted = Use_json()['AcceptRoutes']
            if are_routes_accepted:
                logging.debug(" Accepting routes is ON, turning it OFF...")
                executeComand("tailscale set --accept-routes=false")
                Use_json({"AcceptRoutes": False})
            else:
                logging.debug(" Accepting routes is OFF, turning it ON...")
                executeComand("tailscale set --accept-routes")
                Use_json({"AcceptRoutes": True})
        case "onOff":
            toggleTailscaleOnOff()
        case _:
            logging.error(
                f"Error: Unknown setting '{ItemToBeSet}'. Please use 'exitNode', 'ssh', or 'acceptRoutes'.")


def setExitNode(NodeName: str= "off"):

    if stateCallback('exitNode'):
        runCommand("tailscale set --advertise-exit-node=false")
    if NodeName != "off":
        #turning on exit node
        stateCallback("test")
        all_nodes = Use_json()["ExitNodes"]
        try:
            target_node_ip = all_nodes[NodeName]
            runCommand(f"tailscale set --exit-node {target_node_ip}")
            Use_json({"UsedExitNode": NodeName})
            Use_json({"UsingExitNode": True})
            Use_json({"ExitNode": False})
        except:
            setExitNode("off")
            logging.error(f"Exit node not found")
        
        
        
    else:
        runCommand(f"tailscale set --exit-node=")
        Use_json({"UsedExitNode": "None"})
        Use_json({"UsingExitNode": False})

def send_notification(message: str):
    if message:        
        notification = Notify()
        notification.title = "Tailscale Tray"
        notification.application_name = "Tailscale Tray"
        notification.message = message
        notification.icon = "logo.png"
        notification.send()

