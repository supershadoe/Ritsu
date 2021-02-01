# -*- coding: utf-8 -*-
#------------------------------------------

"HelpCog: Cog to hold the commands help and about for discord bot Ritsu#6975"
__author__ = "supershadoe"
__license__ = "Apache v2.0"

#------------------------------------------

# Imports #
from discord import Embed
from discord.ext import commands

#------------------------------------------

class HelpCog(commands.Cog, name="Help"):
    "Commands to help users."
    def __init__(self, bot):
        self.bot = bot

    #------------------------------------------

    @commands.command()
    async def help(self, ctx, *args):
        "Shows a help message"
        bot_pref = self.bot.prefixes.setdefault(ctx.guild.id, '!')
        if not args:
            embed = Embed(title="Bot Commands", description=f"The prefix of the bot on this server is `{bot_pref}`\n\n", color=0xFF00FF)
            embed.set_footer(text=f"For detailed help, give {bot_pref}help (command) (subcommand) without the brackets.")
            for cog in self.bot.cogs:
                cog = self.bot.cogs[cog]
                if 'hidden' in cog.__cog_settings__ and cog.__cog_settings__['hidden']:
                    continue
                prev_one_group = False
                cog_desc = f"> {cog.__doc__}\n"
                for cmd in cog.walk_commands():
                    if not cmd.hidden:
                        if isinstance(cmd, commands.core.Group):
                            cog_desc += f"`{cmd}`**:** "
                        else:
                            if cmd.parent is not None:
                                prev_one_group = True
                            else:
                                if prev_one_group:
                                    prev_one_group = False
                                    cog_desc = cog_desc[:-2] + '\n'
                            cog_desc += f"`{cmd.name}`, "
                cog_desc = cog_desc[:-2]
                embed.add_field(name=cog.__cog_name__, value=cog_desc, inline=False)
            return await ctx.send(embed=embed)
        else:
            if len(args) > 2:
                return await ctx.send(embed=Embed(title="Error!", description=f"Argument overload! Give the command in the form of `{bot_pref}help command subcommand` where command and subcommand are non-mandatory", color=0xFF6463))
            else:
                args = ' '.join(args)
                if (cmd:= self.bot.get_command(args)) is not None:
                    if not cmd.hidden or await self.bot.is_owner(ctx.author):
                        return await ctx.send(embed=Embed(title=f"Help: {cmd.name}", description=f"{cmd.help}", color=0xFF00FF))
                    else:
                        embed = Embed(title="Hidden cmd", description="_Forget this._\nForget that you saw this...\nThe existence of this command is forbidden knowledge!\n**Run while you can!**", color=0x000000)
                        embed.set_thumbnail(url="https://upload.wikimedia.org/wikipedia/commons/c/c6/Hypnotic-spiral.jpg")
                        return await ctx.send(embed=embed)
                else:
                    return await ctx.send(embed=Embed(title="Error!", description=f"{args} is not a valid command!", color=0xFF6463))

    #------------------------------------------

    def about_embed(self, guildid: int, server_intro_msg: bool):
        bot_pref = self.bot.prefixes.setdefault(guildid, '!')
        embed = Embed(title="About this bot", description=f"""
        **{self.bot.user.name}** is a {self.bot.description.split(' ', 1)[1]}

        The prefix of this bot on this server currently is `{bot_pref}`.
        Use `{bot_pref}help` to get the list of commands and help message on how to use them.

        You can invite this bot to other servers using this invite link: [Invite](https://discord.com/api/oauth2/authorize?client_id=776112201734815786&permissions=85056&scope=bot)

        A bot made by **supershadoe**(<@!648000511706005514>).""", color=0xFF00FF)
        if not server_intro_msg:
            embed.description += """
            Copyright (C) 2020 supershadoe
            __License__:
            > Licensed under the Apache License, Version 2.0 (the "License");
            > you may not use this bot except in compliance with the License.
            > You may obtain a copy of the License [here](http://www.apache.org/licenses/LICENSE-2.0).
            > Unless required by applicable law or agreed to in writing, software
            > distributed under the License is distributed on an "AS IS" BASIS,
            > WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
            > See the License for the specific language governing permissions and
            > limitations under the License.
            """
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.get_user(self.bot.user.id).avatar_url)
        return embed

    #------------------------------------------

    @commands.command()
    async def about(self, ctx):
        "Shows an about message."
        return await ctx.send(embed=self.about_embed(ctx.guild.id, False))

#------------------------------------------

def setup(bot):
    "Function to setup cog to add to bot"
    bot.add_cog(HelpCog(bot))
