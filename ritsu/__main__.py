#!/usr/bin/env python3

"""The main code for the new Ritsu bot written in hikari"""

from start import start_bot

if __name__ != "__main__":
    raise ImportError("This script isn't intended to be imported!")

bot, activity = start_bot()

bot.run(activity=activity)
