# -*- coding: utf-8 -*-
#------------------------------------------

# Basic info #
"SettingsCog: Settings cog for discord bot Ritsu#6975"
__author__ = "supershadoe"
__license__ = "Apache v2.0"

#------------------------------------------

# Imports #
from os import system
from zoneinfo import available_timezones
import itertools
import subprocess

from discord.ext import commands
from discord import Embed
from asyncio import TimeoutError

from ritsu import utils

#------------------------------------------

class SettingsCog(commands.Cog, name="Settings"):
    "Has commands related to user settings and server-wide bot settings."
    def __init__(self, bot):
        self.bot = bot

    #------------------------------------------

    @commands.group()
    async def settings(self, ctx):
        "To list or change user settings"
        if ctx.invoked_subcommand is None:
            try:
                userinfo = utils.get_user_info(ctx.author.id).split(',')
                tz = userinfo[2].split('\n')[0]
                msg_to_show = f"""
Settings of {ctx.author.mention}:

Subscribed bot: {utils.Bots(int(userinfo[1])).name.replace('_','-')}|NEW
Timezone: {tz}
                """
                embed=Embed(description=msg_to_show, color=0x00FFFF)
                embed.set_author(name="Settings", icon_url=ctx.author.avatar_url)
                return await ctx.send(embed=embed)
            except subprocess.CalledProcessError:
                qn1 = await ctx.send(embed=Embed(description="⚠️ **User not found in database.**\nDo you want to register your account in the database?\nReact with :thumbsup: to this message **within** __15 seconds__ to start the setup process.", color=0xFF6347))
                authorinfo = (ctx.author.id, ctx.channel.id, ctx.guild.id)

                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check =
                            lambda r,u: (u.id, r.message.id, str(r.emoji)) == (authorinfo[0], qn1.id, "👍"), timeout=15.0)
                except TimeoutError:
                    return await ctx.send("No valid response received. Setup not started.")

                await qn1.delete()
                reply1 = await ctx.invoke(self.bot.get_command('settings bot'), change=False)
                if type(reply1) is not int:
                    return
                reply2 = await ctx.invoke(self.bot.get_command('settings timezone'), change=False)
                if type(reply2) is not str:
                    return
                with utils.get_file("userinfo", "a") as f:
                    f.write(f"{authorinfo[0]},{list(utils.Bots)[reply1-1].value},{reply2}\n")
                    await ctx.send(embed=Embed(title="User set-up", description="User added in database successfully!", color=0x00FFFF))
                    return "Success!"

    #------------------------------------------

    @settings.command()
    async def bot(self, ctx, change=True):
        "To change the bot selected by user during set-up."
        if change:
            try:
                userinfo = utils.get_user_info(ctx.author.id)
                lnno = userinfo.split(':')[0]
                tz = userinfo.split(',')[2].split('\n')[0]
            except subprocess.CalledProcessError:
                return await ctx.invoke(self.bot.get_command("settings"))

        authorinfo = (ctx.author.id, ctx.channel.id, ctx.guild.id)
        embed_words = "Bot change" if change else "User set-up"
        msg_to_show = "Which bot do you want to choose?\n"
        i = 1
        for bot in itertools.islice(utils.Bots,4):
            msg_to_show += f"{i}) {bot.name.replace('_','-')}|NEW\n"
            i+=1
        msg_to_show += """
        Type the number of bot which you want to use.
        Enter the number within 15 seconds.
        """
        qn = await ctx.send(embed=Embed(title=embed_words, description=msg_to_show, color=0x121212))
        try:
            reply = await self.bot.wait_for('message', check =
                    lambda m: (m.author.id, m.channel.id, m.guild.id) == authorinfo
                    and m.content.isdigit(), timeout = 15.0)
        except TimeoutError:
            return await ctx.send(f"No valid response received. {embed_words} aborted :(")

        await qn.delete()
        if not 1<=int(reply.content)<=5:
            return await ctx.send("Number not in required range. Please try again :(")
        else:
            filename = utils.get_file("userinfo", name_only=True)
            if change:
                system(f"sed -i \"{lnno}d\" {filename}")
                with open(filename, "a") as f:
                    reply = int(reply.content)
                    f.write(f"{authorinfo[0]},{list(utils.Bots)[reply-1].value},{tz}\n")
                    return await ctx.send(embed=Embed(title=embed_words, description="Bot changed in database successfully!", color=0x00FFFF))
            else:
                return int(reply.content)

    #------------------------------------------

    @settings.command(alias=('tz',))
    async def timezone(self, ctx, change=True):
        "To change the time zone chosen by user during set-up."
        if change:
            try:
                userinfo = utils.get_user_info(ctx.author.id)
                lnno = userinfo.split(':')[0]
                bot_port = userinfo.split(',')[1]
            except subprocess.CalledProcessError:
                return await ctx.invoke(self.bot.get_command("settings"))
        authorinfo = (ctx.author.id, ctx.channel.id, ctx.guild.id)
        embed_words = "Time zone change" if change else "User set-up"
        timezones = available_timezones()
        msg_to_show = """Select your timezone.

        Type the timezone you want to select in the format of `Zone/Subzone`.
        Refer [this wikipedia page](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones) for help in choosing your timezone.
        _Look at the column TZ database name there._


        You can use [this website](https://ipapi.co/timezone) to get your timezone in that format using your geolocation.
        _Make sure you visit without VPN else the result would be wrong_

        Time zone is case-sensitive.
        Type your choice within 1 minute.
        """
        qn = await ctx.send(embed=Embed(title=embed_words, description=msg_to_show, color=0x121212))
        try:
            reply = await self.bot.wait_for('message', check =
                    lambda m : (m.author.id, m.channel.id, m.guild.id) == authorinfo
                    and m.content in timezones, timeout = 60.0)
        except TimeoutError:
            return await ctx.send(f"No valid response received. {embed_words} aborted :(")

        await qn.delete()
        filename = utils.get_file("userinfo", name_only=True)
        if change:
            system(f"sed -i \"{lnno}d\" {filename}")
            with open(filename, "a") as f:
                f.write(f"{authorinfo[0]},{bot_port},{reply.content}\n")
                return await ctx.send(embed=Embed(title=embed_words, description="Time zone changed in database successfully!", color=0x00FFFF))
        else:
            return reply.content

    #------------------------------------------

    @settings.command()
    async def removemydata(self, ctx):
        "To remove user data from the bot's database"
        try:
            userinfo = utils.get_user_info(ctx.author.id)
            qn1 = await ctx.send(embed=Embed(title="REMOVE DATA", description="**Do you really want to remove your data from the database?**\nReact with :thumbsup: within 15 seconds to remove your data.", color=0xFF0000))
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check =
                        lambda r,u: (u.id, r.message.id, str(r.emoji)) == (int(userinfo.split(',')[0].split(':')[1]), qn1.id, "👍"), timeout=15.0)
            except TimeoutError:
                return await ctx.send("No valid response received. Data removal aborted.")

            await qn1.delete()
            qn2 = await ctx.send(embed=Embed(title="REMOVE DATA", description="**ARE YOU REALLY SURE?**\nReact with :thumbsup: within 15 seconds to remove your data.", color=0xFF0000))
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check =
                        lambda r,u: (u.id, r.message.id, str(r.emoji)) == (int(userinfo.split(',')[0].split(':')[1]), qn2.id, "👍"), timeout=15.0)
            except TimeoutError:
                return await ctx.send("No valid response received. Data removal aborted.")

            await qn2.delete()
            system(f"sed -i \"{userinfo.split(':')[0]}d\" {utils.get_file('userinfo', name_only=True)}")
            return await ctx.send(embed=Embed(title="Data removal", description="Removed your data from bot's database :(", color=0xFF00FF))
        except subprocess.CalledProcessError:
            return await ctx.send(embed=Embed(title="Data removal", description="You aren't in the bot's database in the first place...", color=0xFF6463))

    #------------------------------------------

    @commands.command()
    @commands.has_guild_permissions(administrator=True)
    async def prefix(self, ctx, *args):
        "Changes the prefix of the bot(admin-only command)"
        if not args:
            return await ctx.send(embed=Embed(title="Error!", description="No prefix given to be changed."))
        filename = utils.get_file("prefixes", name_only=True)
        self.bot.prefixes[ctx.guild.id] = args[0]
        try:
            lnno = str(subprocess.check_output(["grep", "-n", str(ctx.guild.id), filename], stderr=subprocess.DEVNULL), "utf-8").split(':')[0]
            system(f"sed -i \"{lnno}d\" {filename}")
        except subprocess.CalledProcessError:
            pass
        with open(filename, "a") as f:
            f.write(f"{ctx.guild.id},{args[0]}\n")
        return await ctx.send(embed=Embed(title="Prefix", description=f"Changed prefix for this server to `{args[0]}`", color=0x00FFFF))

#------------------------------------------

def setup(bot):
    "Function to add cog to bot"
    bot.add_cog(SettingsCog(bot))
