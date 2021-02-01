# -*- coding: utf-8 -*-
#------------------------------------------

# Basic Info #
"FetchCog: Cog with commands to fetch episode info and schedule using bot Ritsu#6975"
__author__ = "supershadoe"
__license__ = "Apache v2.0"

#------------------------------------------

# Imports #
from subprocess import CalledProcessError
import datetime
import dateutil.tz
import json
import re

from discord import Embed
from discord.ext import commands
import aiohttp
import asyncio

from ritsu import utils

#------------------------------------------

class FetchCog(commands.Cog, name="Fetch Info"):
    "Has commands which fetch info like schedule and latest episode."
    def __init__(self,bot):
        self.bot = bot

    #------------------------------------------

    @commands.group()
    async def fetch(self, ctx):
        "Group command for multiple stuff like schedule and latest episode"
        if ctx.invoked_subcommand is None:
            help_msg = "No valid subcommand given.\n\nHelp message:\n"
            for c in self.walk_commands():
                if not c.hidden:
                    help_msg += f"`{c.name}`\t{c.help}\n\n"
            return await ctx.send(embed=Embed(title="Error!", description=help_msg, color=0xFF6463))

    #------------------------------------------

    @fetch.command(aliases=('sc',))
    async def schedule(self, ctx):
        "Fetches release schedule of currently running anime from SubsPlease website."
        try:
            schedule = ""
            tz = utils.get_user_info(ctx.author.id).split(',')[2].split('\n')[0]
            for time, anime_s in self.bot.schedule.items():
                for anime in anime_s:
                    schedule += f"{datetime.datetime.utcfromtimestamp(time).replace(tzinfo=dateutil.tz.UTC).astimezone(dateutil.tz.gettz(tz)).strftime('%A %F %H:%M:%S %Z')} {anime}\n"
            return await ctx.send(embed=Embed(title="Schedule", description=schedule, color=0x00FFFF))
        except CalledProcessError:
            if await ctx.invoke(self.bot.get_command("settings")) != "Success!":
                return await ctx.send("User not added in database! Command failed :(")

    #------------------------------------------

    @fetch.command(aliases=("ep",))
    async def episode(self, ctx, *args):
        """Fetches the info of the latest episode of a particular anime.
        Takes two arguments anime name and resolution(both mandatory).
        _Note: The anime name is __case-sensitive__(also the weird symbols are needed(if in name))._
        _Tip: Fetch schedule for the day using the bot and then copy-paste the name._"""
        if not args:
            return await ctx.send(embed=Embed(title="Error!", description="Give the command again with the required **anime name** and **resolution**.", color=0xFF6463))
        args = list(args)
        resolution = args.pop()
        if not re.search("(\d+)p", resolution):
            return await ctx.send(embed=Embed(title="Error!", description="Give the command again with the required **resolution** of anime.", color=0xFF6463))
        ani_name = ' '.join(args)
        try:
            user_info = utils.get_user_info(ctx.author.id).split(',')
            bot_port = user_info[1]
            time_zone = user_info[2].rstrip()
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://arutha.info:{bot_port}/txt") as r:
                    if r.status == 200:
                        try:
                            data = re.findall(f"#(.+) \[(.+)\] \[(.+)\] {re.escape(ani_name)} - (.+) \(({resolution})\)", await r.text()).pop()
                        except IndexError:
                            return await ctx.send(embed=Embed(title="Error!", description="""Required anime with the given resolution **not found**.
                                _Check again if the __case of **every** character__ in the name and the given __resolution__ is valid._""", color=0xFF6463))
                        packno = data[0].split(" ")[0]
                        thumbnail_url, release_date = None, None
                        async with session.get(f"https://subsplease.org/api/?f=search&tz={time_zone}&s={ani_name} - {data[3]}") as picr:
                            if picr.status == 200:
                                json_data = json.loads(await picr.text())[f"{ani_name} - {data[3]}"]
                                thumbnail_url = "https://subsplease.org" + json_data['image_url']
                                release_date = json_data['release_date']
                        msg_to_send = Embed(title="Latest episode", description = f"""
Packinfo
Released by: {data[2]}

Anime name: {ani_name}
Episode: {data[3]}
Resolution: {resolution}
Released on: {release_date}
Pack number: #{packno}
Size: {data[1]}

Type `/msg {utils.Bots(int(bot_port)).name.replace('_','-')}|NEW xdcc send #{packno}` in your IRC client after joining Rizon server.
                        """, color=0xFF00FF)
                        if thumbnail_url is not None:
                            msg_to_send.set_thumbnail(url=thumbnail_url)
                        return await ctx.send(embed=msg_to_send)
                    else:
                        return await ctx.send(embed=Embed(title="Error!", description=f"Couldn't fetch the latest episode :(\nResponse from server: ```{r.status}```", color=0xFF6463))
        except CalledProcessError:
            if await ctx.invoke(self.bot.get_command("settings")) != "Success!":
                return await ctx.send("The required data can't be fetched without first being in the database.")

#------------------------------------------

def setup(bot):
    "Function to add cog to bot"
    bot.add_cog(FetchCog(bot))
