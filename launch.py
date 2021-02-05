#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#------------------------------------------

"Script for starting discord bot Ritsu#6975"
__author__ = "supershadoe"
__license__ = "Apache v2.0"

#------------------------------------------

# Imports #
import os
import subprocess
import sys

try:
    from ritsu.config import bot_token
except ModuleNotFoundError:
    print("""[0;1;31mConfig file missing![0m

Create a [1mconfig.py[0m inside [1mritsu[0m subdirectory and add a [1mbot_token[0m variable
with the token as the value(as a string).""")
    exit(1)
except ImportError:
    print("""[0;1;31mBot token missing![0m

Add a [1mbot_token[0m variable in the [1mconfig.py[0m file!""")
    exit(1)

try:
    from ritsu.bot import Ritsu
except (ImportError, ModuleNotFoundError) as err:
    print(f"[0;1;31mMissing module: {err}[0m")

#------------------------------------------

req_reinst = False

if not sys.version_info >= (3, 8):
    print("[0;1;31mError: Python version less than minimum requirement.\nRitsu bot runs on Python 3.8!+[0m")
    exit(22)

def inst_req():
    "To try to install pip requirements if startup fails due to a missing module."
    global req_reinst
    print("Attempting to install missing modules...")
    try:
        subprocess.run(['pip', 'install', '-Ur', 'requirements.txt'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        req_reinst = True
    except (OSError, subprocess.CalledProcessError) as err:
        print("[0;1;31mRequirements install failed![0m")
        print(err)
        exit(1)

def reimport_bot():
    "To reimport the bot class after reinstalling all requirements."
    try:
        from ritsu.bot import Ritsu
        return Ritsu()
    except (ImportError, ModuleNotFoundError) as err:
        print("Installing requirements didn't fix the issue... Try fixing the error on your own or contact the developer")
        print(err)
        exit(1)

def __main__():
    "Core function of bot"
    try:
        if req_reinst:
            ritsu = reimport_bot()
        else:
            ritsu = Ritsu()
        ritsu.run(bot_token, reconnect=True)
    except (ImportError, ModuleNotFoundError, NameError):
        inst_req()
        __main__()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    __main__()

#------------------------------------------
