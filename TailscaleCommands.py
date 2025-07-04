import subprocess, os,platform

runCommand = lambda command:executeComand(command)

def executeComand(command):
    
    result = subprocess.run(command.split(), capture_output=True, text=True)

    if result.returncode == 0:
        output = (f"{command} Command successful!")

        if result.stdout:
            output = output +'\n'+ "Output:" +'\n'+ result.stdout
    else:
        executeComand('pkexec '+ command)
        print(f"Command failed with return code {result.returncode}")
        if result.stderr:
            output = "Error:" + result.stderr
    return(output)

def ping_website(target_url, count=4):
    """
    Pings a website using the system's ping command.

    Args:
        target_url (str): The URL or IP address to ping.
        count (int): The number of ping requests to send.
    """
    try:
        if platform.system() == "Windows":
            command = ["ping", "-n", str(count), target_url]
        else:  # Linux/macOS
            command = ["ping", "-c", str(count), target_url]

        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Ping successful for {target_url}:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Ping failed for {target_url}:\n{e.stderr}")
    except FileNotFoundError:
        print("Ping command not found. Ensure it's in your system's PATH.")

ping_website("100.100.100.100", count=2)
#make something to ensure that the state of tailscale with all the infor needed for the callbacks

def stateCallback():
    
    pass

# all of these functions must have call backs to ensure that a reapeat comand is not made
#print(runCommand("tailscale up"))

def executeTailscaleUp():
    
    pass
def executeTailscaleDown():
    
    pass

def executeTailscaleSet():
    
    pass



