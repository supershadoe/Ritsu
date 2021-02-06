# -*- coding: utf-8 -*-
#------------------------------------------

"AdminCog: Cog to hold dev-only commands for discord bot Ritsu#6975"
__author__ = "supershadoe"
__license__ = "Apache v2.0"

#------------------------------------------

# Imports #
import datetime
import inspect
import platform

from discord import Embed, version_info
from discord.ext import commands
from psutil import Process

#------------------------------------------

class AdminCog(commands.Cog, name="Admin Commands", command_attrs=dict(hidden=True)):
    "Has dev-only(owner-only) commands like eval and shutdown."
    def __init__(self, bot):
        self.bot = bot

    #------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def _load(self, ctx, cog_name):
        "To load a cog while debugging"
        await ctx.send(f"Loading cog **{cog_name}**...")
        return self.bot.load_extension(f"ritsu.cogs.{cog_name}")

    #------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def _unload(self, ctx, cog_name):
        "To unload a cog while debugging"
        await ctx.send(f"Unloading cog **{cog_name}**...")
        return self.bot.unload_extension(f"ritsu.cogs.{cog_name}")

    #------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def _reload(self, ctx, cog_name):
        "To reload a cog while debugging"
        await ctx.send(f"Reloading cog **{cog_name}**...")
        return self.bot.reload_extension(f"ritsu.cogs.{cog_name}")

    #------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def _ping(self, ctx):
        "For just pinging the bot"
        await ctx.send(embed=Embed(title="Ping response", description=f"Pong!\nBot latency is **{int(self.bot.latency*1000)} ms**.", color=0xFF00FF))

    #------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def _stats(self, ctx):
        "Provide stats about the host PC"
        embed = Embed(title="Stats", description=f"Bot name: {self.bot.user}", color=0xFF00FF)
        embed.add_field(name="Linux kernel version", value=f"`{platform.release()}`", inline=False)
        embed.add_field(name="Python version", value=f"`{'.'.join(map(str,platform.sys.version_info[0:3]))}`")
        embed.add_field(name="discord.py version", value=f"`{'.'.join(map(str,version_info[0:3]))}`\n")
        embed.add_field(
                name="Bot uptime",
                value=f"`{str(datetime.datetime.now() - datetime.datetime.fromtimestamp(Process(platform.os.getpid()).create_time()))}`")
        embed.add_field(name="Bot latency", value=f"`{str(int(self.bot.latency*1000))} ms`")
        return await ctx.send(embed=embed)

    #------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def _eval(self, ctx, *args):
        "Eval command: DANGER ZONE!"
        res=eval(' '.join(args))
        if inspect.isawaitable(res):
            output = await res
        else:
            output = res
        return await ctx.send(embed=Embed(title="Python: eval result", description=f"```{output}```", color=0xFF00FF))

    #------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def _shutdown(self, ctx):
        "Shutdown command(owner-only)"
        await ctx.send(embed=Embed(title="Shutting down", description="⏻ Shutting down after command from owner...", color=0xFF0000))
        return await self.bot.logout()

    #------------------------------------------

    @commands.command()
    @commands.is_owner()
    async def _todo(self, ctx):
        "To do command for myself"
        return await ctx.send("https://discord.com/channels/801170087688011828/801174287427174410/805653802308206602")

#------------------------------------------

def setup(bot):
    "Function to setup cog to add to bot"
    bot.add_cog(AdminCog(bot))
