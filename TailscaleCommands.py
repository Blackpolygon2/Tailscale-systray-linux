import subprocess
import os
import platform
import json
import shlex


def runCommand(command): return executeComand(command)


def executeComand(command, use_sudo=False):

    try:
        if use_sudo:
            command = "pkexec " + command

        result = subprocess.run(shlex.split(
            command), capture_output=True, text=True, check=True)
        print(f" Command '{command}' successful!")
        return result.stdout

    except FileNotFoundError:
        print(
            f" Error: Command not found. Is '{shlex.split(command)[0]}' installed and in your PATH?")
        return None

    except subprocess.CalledProcessError as e:
        print(f" Command '{command}' failed with return code {e.returncode}.")
        if e.stderr:
            print(f"Error details:\n{e.stderr}")

        if not use_sudo:
            print("Retrying with pkexec (sudo)...")
            return executeComand(command, use_sudo=True)

        return None


def Use_json(*DictItemValue: dict):
    with open('State.json', 'r') as file:
        data = json.load(file)

    for DictItemValue in DictItemValue:
        # i am so sorry i dont know any other way (;_;)
        data[list(DictItemValue.keys())[0]] = list(DictItemValue.values())[0]
        print(data)
        with open('State.json', 'w') as file:
            json.dump(data, file, indent=4)

    # print(DictItemValue)

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
        else:  # Linux/macOS
            command = ["ping", "-c", str(count), target_url]

        result = subprocess.run(
            command, capture_output=True, text=True, check=True)
        # print(f"Ping successful for {target_url}:\n{result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        # print(f"Ping failed for {target_url}:\n{e.stderr}")
        return False
    except FileNotFoundError:
        print("Ping command not found. Ensure it's in your system's PATH.")

# make something to ensure that the state of tailscale with all the infor needed for the callbacks


def stateCallback(itemRequested=""):
    if "exit" in GetTailwindStatus():
        Use_json({"ExitNode": True})

    match itemRequested:
        case "onOff":
            return pingWebsite("100.100.100.100", count=2)
        case 'exitNode':
            return Use_json()["ExitNode"]
        case 'ssh':
            return Use_json()["SSH"]

        case 'AcceptRoutes':
            return Use_json()["AcceptRoutes"]
        case "t":
            pass
        case _:
            print('pls correct input or no input used but stateCallback was called  ')
    pass

# all of these functions must have call backs to ensure that a reapeat comand is not made
# print(runCommand("tailscale up"))


def toggleTailscaleOnOff():
    if stateCallback('onOff'):
        runCommand("tailscale down")
    else:
        runCommand("tailscale up")


def executeTailscaleSetToggle(ItemToBeSet: str):
    """
    Toggles Tailscale settings like SSH, advertising an exit node, or accepting routes.
    It reads the current state and performs the opposite action.
    """
    match ItemToBeSet:
        case "exitNode":
            is_exit_node_on = Use_json('exitNode')
            if is_exit_node_on:
                print("🏁 Exit Node advertising is ON, turning it OFF...")
                executeComand("tailscale set --advertise-exit-node=false")
                Use_json({"ExitNode": False})
            else:
                print("🏁 Exit Node advertising is OFF, turning it ON...")
                executeComand("tailscale set --advertise-exit-node")
                Use_json({"ExitNode": True})

        case "ssh":
            is_ssh_on = Use_json('ssh')
            if is_ssh_on:
                print("🔒 SSH is ON, turning it OFF...")
                executeComand("tailscale set --ssh=false")
                Use_json({"SSH": False})
            else:
                print("🔒 SSH is OFF, turning it ON...")
                executeComand("tailscale set --ssh")
                Use_json({"SSH": True})

        case "acceptRoutes":
            are_routes_accepted = Use_json('AcceptRoutes')
            if are_routes_accepted:
                print("🗺️ Accepting routes is ON, turning it OFF...")
                executeComand("tailscale set --accept-routes=false")
                Use_json({"AcceptRoutes": False})
            else:
                print("🗺️ Accepting routes is OFF, turning it ON...")
                executeComand("tailscale set --accept-routes")
                Use_json({"AcceptRoutes": True})

        case _:
            print(
                f"Error: Unknown setting '{ItemToBeSet}'. Please use 'exitNode', 'ssh', or 'acceptRoutes'.")


def setExitNode(Nodeip: str):

    if stateCallback('exitNode'):
        runCommand("tailscale set --advertise-exit-node=false")
    if Nodeip != "off":
        stateCallback("t")
        runCommand(f"tailscale set --exit-node {Nodeip}")
        Use_json({"UsingExitNode": True})
    else:
        runCommand(f"tailscale set --exit-node")
        Use_json({"UsingExitNode": False})


# print(Use_json()["SSH"])
# Use_json({"SSH":True})
