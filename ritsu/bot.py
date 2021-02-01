# -*- coding: utf-8 -*-
#------------------------------------------

# Basic info #
"bot.py: Main script for discord bot Ritsu#6975"
__author__ = "supershadoe"
__license__ = "Apache v2.0"

#------------------------------------------

# Imports #
from asyncio import sleep
from discord import Activity, ActivityType, Embed, Status
from discord.ext import commands

from ritsu.utils import get_file

debug_mode=False
if debug_mode:
    import logging
    import traceback
    logging.basicConfig(level=logging.DEBUG)

#------------------------------------------

class BlockDMs(commands.CheckFailure):
    "An empty class to denote command check failure when a command is received from a DM"
    pass

#------------------------------------------

class Ritsu(commands.Bot):
    "Class with event handlers and init function for the bot"
    __slots__ = ('prefixes','subscriptions', 'schedule')
    def __init__(self):
        "Init function"
        # Initializing client #
        super().__init__(
                command_prefix = lambda b,m:
                    b.prefixes.setdefault(m.guild.id, '$') if m.guild is not None else '$',
                help_command = None,
                chunk_guilds_at_startup=False,
                description = "A bot to fetch anime info from IRC bots and also notify users of new episodes.",
                activity=Activity(type=ActivityType.custom, name="Loading!"),
                status=Status.dnd)
        # Set up the prefixes dictionary #
        self.prefixes = self.loop.run_until_complete(self.setup_prefixes())
        # Load all cogs #
        for cog in ('FetchCog', 'SubsCog', 'SettingsCog', 'HelpCog', 'AdminCog'):
            self.load_extension(f'ritsu.cogs.{cog}')
        # Block all DMs bot-wide
        self.add_check(self.block_dms)
        # Add async background loop to change status #
        if not debug_mode:
            self.loop.create_task(self.change_status())

    #------------------------------------------

    async def block_dms(self, ctx):
        "Block all DMs except invite command"
        if ctx.guild is None and not ctx.message.content.startswith("!invite"):
            raise BlockDMs("DMs to this bot are blocked!")
        return True

    #------------------------------------------

    async def on_guild_join(self, guild):
        "Event handler to send an introductory message on joining a server"
        get_file("prefixes", 'a').write(f"{guild.id},$")
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                return await channel.send(embed=self.get_cog("Help").about_embed(guild.id, True))

    #------------------------------------------

    async def on_ready(self):
        "Event handler to be run when the bot gets ready"
        if debug_mode:
            await self.change_presence(activity=Activity(name="with code", type=ActivityType.playing), status=Status.dnd)
            #await self.change_presence(status=Status.invisible)
        await self.get_channel(801174287427174410).send("Logged in!")

    #------------------------------------------

    async def on_command_error(self, ctx, error):
        "Event handler to be run on encountering an error"
        if debug_mode:
            tb='\n'.join(traceback.format_tb(error.__traceback__))
            embed=Embed(title="Oops!", description=f"Error:```py\n{error}``` Error Type:```py\n{type(error)}``` Traceback:```py\n{tb}```", color=0xFF0000)
            embed.set_footer(text="Debug mode is on!")
            return await ctx.send(embed=embed)
        if type(error) is commands.errors.CommandNotFound:
            return
        elif isinstance(error, BlockDMs):
            return await ctx.send(embed=Embed(description="⛔ **DMs are not allowed**\nUse commands in a server where I am in.", color=0xFF0000))

    #------------------------------------------

    async def setup_prefixes(self):
        "Grab all prefixes from prefixes.csv and add to prefixes dict"
        d={}
        for line in get_file("prefixes"):
            if line != "\n":
                line = line.split(',')
                serverid,prefix = line
                prefix = prefix.rstrip()
                d[int(serverid)] = prefix
        return d

    #------------------------------------------

    async def change_status(self):
        "Change bot status every ten seconds(just for fun)"
        await self.wait_until_ready()
        activities=(
                Activity(type=ActivityType.listening, name="commands"),
                Activity(type=ActivityType.watching, name="out for new episodes"))
        while not self.is_closed():
            for activity in activities:
                await self.change_presence(activity=activity)
                await sleep(5)

#------------------------------------------
