import subprocess

runCommand = lambda command:executeComand(command)

def executeComand(command):
    
    result = subprocess.run(command.split(), capture_output=True, text=True)

    if result.returncode == 0:
        output = "Command successful!"

        if result.stdout:
            output = output +'\n'+ "Output:" +'\n'+ result.stdout
    else:
        executeComand('pkexec '+ command)
        print(f"Command failed with return code {result.returncode}")
        if result.stderr:
            output = "Error:" + result.stderr
    return(output)


print(runCommand("tailscale down"))