# -*- coding: utf-8 -*-
#------------------------------------------

# Basic Info #
"utils: Definition of functions which are used throughout the bot's code"
__author__ = "supershadoe"
__license__ = "Apache v2.0"

#------------------------------------------

# Imports #
from discord.ext import commands
from enum import Enum
from os.path import dirname, isfile
import subprocess

#------------------------------------------

def get_file(filename: str, open_mode: str = 'r', name_only: bool = False):
    "Return a file stream of a file or just the full resolved filename from the database folder"
    if not name_only:
        return open(f"{dirname(__file__)}/../database/{filename}.csv", open_mode)
    else:
        return f"{dirname(__file__)}/../database/{filename}.csv"

#------------------------------------------

def get_user_info(authorid: int):
    "Get user info from the database"
    return str(subprocess.check_output(["grep", "-n", str(authorid), f"{dirname(__file__)}/../database/userinfo.csv"], stderr=subprocess.DEVNULL), "utf-8")

#------------------------------------------

def get_sub_info(searchterm: str):
    "Get subscription info for an animefrom the database"
    return str(subprocess.check_output(["grep", "-n", searchterm, f"{dirname(__file__)}/../database/subsinfo.csv"], stderr=subprocess.DEVNULL), "utf-8")

#------------------------------------------

class Bots(Enum):
    CR_ARUTHA_IPV6 = 1335
    CR_ARUTHA = 1336
    CR_HOLLAND = 1337
    CR_HOLLAND_IPV6 = 1338
    A1080p = 8331
    A720p = 8337
    A480p = 8334
