# -*- coding: utf-8 -*-
#------------------------------------------

# Basic Info #
"""
SubsCog:
Cog to hold commands which are used for subscribing to anime to get a DM when a
new episode gets released.
(and related commands)
"""
__author__ = "supershadoe"
__license__ = "Apache v2.0"

#------------------------------------------

# Imports #
from os import system
from subprocess import CalledProcessError
import datetime
import dateutil.tz
import itertools
import json
import re

from discord import Embed, ClientException
from discord.ext import commands, tasks
import asyncio
import aiohttp

from ritsu import utils

#------------------------------------------

class SubsCog(commands.Cog, name="Subscription"):
    "Has commands which help in subscribing to anime to get a DM when a new episode gets released."
    def __init__(self, bot):
        self.bot = bot
        self.subsfile = utils.get_file("subsinfo", name_only=True)
        try:
            self.bot.subscriptions = self.bot.loop.run_until_complete(self.setup_subs())
        except (RuntimeError, RuntimeWarning):
            # Adding this as it causes problems while reloading cog
            pass
        self.schedule_check_loop.start()
        self.sub_loop.start()

    #------------------------------------------

    def __unload(self):
        self.schedule_check_loop.cancel()
        self.sub_loop.cancel()

    #------------------------------------------

    @commands.group()
    async def sub(self, ctx):
        "Group command for subscription related stuff."
        if ctx.invoked_subcommand is None:
            help_msg = "No valid subcommand given.\n\nHelp message:\n"
            for c in self.walk_commands():
                if not c.hidden:
                    help_msg += f"`{c.name}`\t{c.help}\n\n"
            return await ctx.send(embed=Embed(title="Error!", description=help_msg, color=0xFF6463))

    #------------------------------------------

    @sub.command()
    async def add(self, ctx, *args):
        "To subscribe to an anime to get DM notifications when a new episode gets released."
        try:
            utils.get_user_info(ctx.author.id)
        except CalledProcessError:
            if await ctx.invoke(self.bot.get_command("settings")) != "Success!":
                return await ctx.send("User not added in database. Subscription addition aborted :(")

        if not args:
            return await ctx.send(embed=Embed(title="Error!", description="Give the command again with the required **anime name** and **resolution** of anime.", color=0xFF6463))
        args = list(args)
        res = args.pop()
        if not re.search("(\d+)p", res):
            return await ctx.send(embed=Embed(title="Error!", description="Give the command again with the required **resolution** of anime.", color=0xFF6463))
        args = ' '.join(args)
        if args not in self.bot.subscriptions:
            with open(self.subsfile, "a") as f:
                f.write(f"{args},{ctx.author.id}:{res}\n")
            self.bot.subscriptions[args] = [(ctx.author.id,res)]
        else:
            if any(ctx.author.id not in i for i in self.bot.subscriptions[args]):
                sub_info = utils.get_sub_info(args)
                system(f"sed -i \"{sub_info.split(':')[0]}d\" {self.subsfile}")
                with open(self.subsfile, "a") as f:
                    f.write(f"{(sub_info.split(':',1)[1].lstrip()).rstrip()},{ctx.author.id}:{res}\n")
                self.bot.subscriptions[args].append((ctx.author.id,res))
            else:
                return await ctx.send(embed=Embed(title="Already subscribed!", description = "You are already subscribed to this anime!", color=0xFF6463))
        return await ctx.send(embed=Embed(title="Subscribed!", description = "Your subscription has been added!", color=0x00FFFF))

    #------------------------------------------

    @sub.command()
    async def list(self, ctx, remove: bool = False):
        "Shows a list of anime which the user has subscribed to."
        l = {}
        for i in self.bot.subscriptions.items():
            for j in i[1]:
                if ctx.author.id == j[0]:
                    l[i[0]] = j[1]
        l_keys = tuple(l.keys())
        if len(l) != 0:
            return (await ctx.send(embed=Embed(title=f"{ctx.author.name}'s Sub List", description='\n'.join(itertools.islice((f"<{i+1}> {l_keys[i]}" for i in itertools.count()), len(l_keys))), color=0x00FFFF)), l)
        else:
            if remove:
                return None
            else:
                return (await ctx.send(embed=Embed(title=f"{ctx.author.name}'s Sub List", description="You aren't subscribed to any anime!", color=0xFF6463)), None)

    #------------------------------------------

    @sub.command()
    async def remove(self, ctx):
        "Removes an anime subscription."
        authorinfo = (ctx.author.id, ctx.channel.id, ctx.guild.id)
        sublist = await ctx.invoke(self.bot.get_command("sub list"), remove=True)
        if not isinstance(sublist, tuple) and sublist is None:
            return await ctx.send(embed=Embed(title="Remove subscription", description="You aren't subscribed to any anime!", color=0xFF6463))
        qn = await ctx.send("Remove subscription by typing the name of any of those anime in that list(case-sensitive) within a minute.")
        try:
            reply = await self.bot.wait_for('message', check = lambda m: (m.author.id, m.channel.id, m.guild.id) == authorinfo and m.content in sublist[1], timeout = 60.0)
        except asyncio.TimeoutError:
            return await ctx.send(f"No valid response received. Subscription removal stopped.")

        await qn.delete()
        await sublist[0].delete()
        sublist = sublist[1]
        filename = utils.get_file("subsinfo", name_only=True)
        to_split_term = str(authorinfo[0]) + ':' + sublist[reply.content]
        line_in_subs_file = utils.get_sub_info(reply.content).split(to_split_term, 1)
        if line_in_subs_file[1] != "\n":
            print(line_in_subs_file := line_in_subs_file[0] + line_in_subs_file[1].split(',',1)[1])
            lnno, line = line_in_subs_file.split(':', 1)
            system(f"sed -i \"{lnno}d\" {filename}")
            with open(filename, "a") as f:
                f.write(line)
            self.bot.subscriptions[reply.content].remove((authorinfo[0], sublist[reply.content]))
        else:
            lnno = line_in_subs_file[0].split(':',1)[0]
            print(lnno)
            system(f"sed -i \"{lnno}d\" {filename}")
            del self.bot.subscriptions[reply.content]
        return await ctx.send(embed=Embed(title="Remove subscription", description="Subscription removed!", color=0x00FFFF))

    #------------------------------------------

    @tasks.loop(minutes=1, reconnect=True)
    async def sub_loop(self):
        "Async task to notify user at the time mentioned on schedule"
        if self.bot.is_ready():
            t = datetime.datetime.utcnow()
            present_time = t.replace(t.year, t.month, t.day, t.hour, t.minute, 0, 0, tzinfo=dateutil.tz.UTC).timestamp()
            del t
            if present_time in self.bot.schedule:
                for anime in self.bot.schedule[present_time]:
                    if anime in self.bot.subscriptions:
                        ani_data = {}
                        async with aiohttp.ClientSession() as session:
                            async with session.get(f"http://arutha.info:1337/txt") as r:
                                if r.status == 200:
                                    data = re.findall(f"#(.+) \[(.+)\] \[(.+)\] {re.escape(anime)} - (.+) \((.+)\)", await r.text())
                                    ani_data['thumbnail_url'], ani_data['release_date'] = None, None
                                    async with session.get(f"https://subsplease.org/api/?f=search&tz=UTC&s={anime} - {data[-1][3]}") as picr:
                                        if picr.status == 200:
                                            json_data = json.loads(await picr.text())[f"{anime} - {data[-1][3]}"]
                                            ani_data['thumbnail_url'] = "https://subsplease.org" + json_data['image_url']
                                            ani_data['release_date'] = json_data['release_date']
                                    for pack in data[-3:]:
                                        pack = list(pack)
                                        res = pack.pop()
                                        ani_data[res] = pack
                                    del data
                        for userdata in self.bot.subscriptions[anime]:
                            user_info = utils.get_user_info(userdata[0]).split(',')
                            bot_port = user_info[1]
                            time_zone = user_info[2].rstrip()
                            pack = ani_data[userdata[1]]
                            packno = pack[0].split(" ")[0]
                            if ani_data['release_date'] is not None:
                                release_date = ani_data['release_date']
                            else:
                                release_date = "Unknown"
                            msg_to_send = Embed(title=":tv: New episode!", description = f"""
New episode of **{anime}** has been released(Probably)!

__Packinfo__:
(of latest episode)
Released by: {pack[2]}
Episode: {pack[3]}
Resolution: {userdata[1]}
Released on: {release_date}
Pack number: #{packno}
Size: {pack[1]}

Type `/msg {utils.Bots(int(bot_port)).name.replace('_','-')}|NEW xdcc send #{packno}` in your IRC client after joining Rizon server.
                            """, color=0xFF00FF)
                            msg_to_send.set_footer(text="Note: The episode may not have been released due to some issues.")
                            if ani_data['thumbnail_url'] is not None:
                                msg_to_send.set_thumbnail(url=ani_data['thumbnail_url'])
                            try:
                                await (await self.bot.fetch_user(userdata[0])).send(embed=msg_to_send)
                            except ClientException:
                                pass

    #------------------------------------------

    @tasks.loop(hours=1, reconnect=True)
    async def schedule_check_loop(self):
        "Async task to refresh the schedule cache of the bot every hour"
        utctime = datetime.datetime.utcnow()
        this_week = itertools.islice(
                (i for i in itertools.islice(
                    (utctime.date() + datetime.timedelta(days=i) for i in itertools.count()), 7)), 7)
        d = {}
        async with aiohttp.ClientSession() as session:
            async with session.get("https://subsplease.org/api/?f=schedule&tz=UTC") as r:
                if r.status == 200:
                    data = json.loads(await r.text())['schedule']
                    for date in tuple(this_week):
                        for anime in data[date.strftime('%A')]:
                            time = int(datetime.datetime.combine(date, (datetime.datetime.strptime(anime['time'], "%H:%M") + datetime.timedelta(minutes=10)).time()).replace(tzinfo=dateutil.tz.UTC).timestamp())
                            if time in d:
                                d[time].append(anime['title'])
                            else:
                                d[time] = [anime['title']]
        self.bot.schedule = d

    #------------------------------------------

    async def setup_subs(self):
        "Grab all subscriptions data from subinfo.csv and add to subscriptions dict"
        d={}
        for line in open(self.subsfile):
            if line !=  "\n":
                line = line.split(',',1)
                anime, subscribers = line
                d[anime] = [(int(i.split(':')[0]),i.split(':')[1]) for i in (subscribers.rstrip()).split(',')]
        return d

#------------------------------------------
def setup(bot):
    "Function to add the cog to the bot"
    bot.add_cog(SubsCog(bot))
