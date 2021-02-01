# -*- coding: utf-8 -*-
#------------------------------------------

"AdminCog: Cog to hold dev-only commands for discord bot Ritsu#6975"
__author__ = "supershadoe"
__license__ = "Apache v2.0"

#------------------------------------------

# Imports #
from discord import Embed
from discord.ext import commands
import inspect

#------------------------------------------

class AdminCog(commands.Cog, name="Admin Commands", command_attrs=dict(hidden=True)):
    "Has dev-only(owner-only) commands like eval and shutdown."
    def __init__(self, bot):
        self.bot = bot
        self.cog_check(commands.is_owner())

    #------------------------------------------

    @commands.command()
    async def _load(self, ctx, cog_name):
        "To load a cog while debugging"
        await ctx.send(f"Loading cog **{cog_name}**...")
        return self.bot.load_extension(f"ritsu.cogs.{cog_name}")

    #------------------------------------------

    @commands.command()
    async def _unload(self, ctx, cog_name):
        "To unload a cog while debugging"
        await ctx.send(f"Unloading cog **{cog_name}**...")
        return self.bot.unload_extension(f"ritsu.cogs.{cog_name}")

    #------------------------------------------

    @commands.command()
    async def _reload(self, ctx, cog_name):
        "To reload a cog while debugging"
        await ctx.send(f"Reloading cog **{cog_name}**...")
        return self.bot.reload_extension(f"ritsu.cogs.{cog_name}")

    #------------------------------------------

    @commands.command()
    async def _ping(self, ctx):
        "For just pinging the bot"
        await ctx.send(embed=Embed(title="Ping response", description=f"Pong!\nBot latency is **{int(self.bot.latency*1000)} ms**.", color=0xFF00FF))

    #------------------------------------------

    @commands.command()
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
    async def _shutdown(self, ctx):
        "Shutdown command(owner-only)"
        await ctx.send(embed=Embed(title="Shutting down", description="⏻ Shutting down after command from owner...", color=0xFF0000))
        return await self.bot.logout()

#------------------------------------------

def setup(bot):
    "Function to setup cog to add to bot"
    bot.add_cog(AdminCog(bot))
