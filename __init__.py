from TailscaleCommands import executeComand
import os


user_home = os.path.expanduser("~")
username = os.path.split(user_home)[-1]

executeComand(f"pkexec tailscale set --operator={username}")