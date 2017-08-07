import asyncio
import discord
import importlib
import os
import json
from discord.ext import commands

def getPrefix(bot, message):
    dir = "data/" + message.server.id + ".json"
    if not os.path.exists("data"):
        os.mkdir("data")
    if not os.path.isfile(dir):
        prefix = "."
    else:
        with open(dir, 'r') as r:
            data = json.load(r)
            prefix = str(data["prefix"])
    if not prefix in message.content:
        if "<@{}>".format(bot.user.id) in message.content:
            prefix = "<@{}> ".format(bot.user.id)
    return prefix

class Core:
    def __init__(self, bot):
        self.bot = bot

    def devOnly(ctx):
        return ctx.message.author.id in ["174918559539920897", "269543926803726336", "186295030388883456", "220568440161697792", "155347730225561600", "223814431946178560"]

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(devOnly)
    async def reload(self, ctx):
        """Reloads the bot's cogs"""
        print("Reloading all cogs")
        msg = await self.bot.say('Reloading cogs')

        await self.bot.edit_message(msg, "Reloading Music")
        self.bot.remove_cog("Music")
        importlib.reload(code.music)
        from code.music import Music
        self.bot.add_cog(Music(bot))
        await self.bot.edit_message(msg, "Reloaded Music")

        await self.bot.edit_message(msg, "Reloading Moderation")
        self.bot.remove_cog("Moderation")
        importlib.reload(code.moderation)
        from code.moderation import Moderation
        self.bot.add_cog(Moderation(bot))
        await self.bot.edit_message(msg, "Reloaded Moderation")

        await self.bot.edit_message(msg, "Reloading Fun")
        self.bot.remove_cog("Fun")
        importlib.reload(code.fun)
        from code.fun import Fun
        self.bot.add_cog(Fun(bot))
        await self.bot.edit_message(msg, "Reloaded Fun")

        await self.bot.edit_message(msg, "Reloading Porn")
        self.bot.remove_cog("Porn")
        importlib.reload(code.porn)
        from code.porn import Porn
        self.bot.add_cog(Porn(bot))
        await self.bot.edit_message(msg, "Reloaded Porn")

        await self.bot.edit_message(msg, "Reloading Utilities")
        self.bot.remove_cog("Utilities")
        importlib.reload(code.utilities)
        from code.utilities import Utilities
        self.bot.add_cog(Utilities(bot))
        await self.bot.edit_message(msg, "Reloaded Utilities")

        await self.bot.say('Reload complete')

    @commands.command(pass_context=True)
    @commands.check(devOnly)
    async def shutdown(self, ctx):
        """Shuts down Helix"""
        print("Shutdown command issued")
        await self.bot.send_message(ctx.message.channel, ":wave:")
        self.bot.remove_cog("Music")
        await self.bot.logout()
        exit()

import code.music
import code.moderation
import code.fun
import code.porn
import code.utilities
from code.moderation import Moderation
from code.music import Music
from code.fun import Fun
from code.porn import Porn
from code.utilities import Utilities

global bot
bot = commands.Bot(command_prefix=getPrefix, description='Helix3.0', pm_help=True)
bot.add_cog(Core(bot))
bot.add_cog(Music(bot))
bot.add_cog(Moderation(bot))
bot.add_cog(Fun(bot))
bot.add_cog(Porn(bot))
bot.add_cog(Utilities(bot))
global byp
global staff
global dev
global donator
byp = bot
staff = [174918559539920897, 155347730225561600, 269543926803726336, 186295030388883456, 220568440161697792, 266282285861437441, 273724497150869514, 239591008982007808]
dev = [174918559539920897, 220568440161697792, 196638626925248513, 223814431946178560, 245994206965792780]
donator = [266282285861437441, 222723232694796291]

@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

@bot.event
async def on_command(bot, ctx):
    print("{}|{}|   {}".format(ctx.message.server.name, ctx.message.author.display_name, ctx.message.content))
    if "help" in ctx.message.content:
        await byp.send_message(ctx.message.channel, ":mailbox_with_mail:")

@bot.event
async def on_member_join(ctx):
    member = ctx
    if member.id in str(dev):
        print("Dev Join| {} joined {}".format(member.display_name, member.server.name))
        await byp.send_message(member.server, "{}, one of my devs, joined your server".format(member.display_name))
    if member.id in str(staff):
        print("Staff Join| {} joined {}".format(member.display_name, member.server.name))
        await byp.send_message(member.server, "{}, one of my staff members, joined your server".format(member.display_name))

def Helix():
    if os.path.isfile("data/token.txt"):
        token = open("data/token.txt", "r").read()
    else:
        try:
            os.mkdir("data")
        except:
            pass
        print("NO TOKEN Dx")
        token = input("Please input a token: ")
        f = open("data/token.txt", "w")
        f.write(token)
        f.close()
        print("New token saved, resuming boot")
    try:
        bot.run(token.replace("\n", ""))
    except discord.errors.LoginFailure:
        print("Token failed")
        os.unlink("data/token.txt")