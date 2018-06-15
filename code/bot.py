import asyncio
import discord
import importlib
import os
import json
import random
import sys
import aiohttp
from discord.ext import commands
import pprint

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


class Perms:
    def donatorOnly(ctx):
        if message.ctx.author.id not in []:
            return staffOnly(ctx)  # staff override
        else:
            return True

    def devOnly(ctx):
        return ctx.message.author.id in ["174918559539920897"]

    def staffOnly(ctx):
        return ctx.message.author.id in ["174918559539920897", "26954392680372633"]


class Core:
    def __init__(self, bot, perms):
        self.bot = bot
        self.perms = perms
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command(pass_context=True, no_pm=False)
    async def setpic(self, ctx):
        if ctx.message.attachments:
            pic = ctx.message.attachments[0]['url']
            print(pic)
        else:
            await bot.say("I cant use that :confused:")
            return
        with aiohttp.Timeout(10):
            async with self.session.get(pic) as image:
                image = await image.read()
                await self.bot.edit_profile(avatar=image)

        await bot.say("Done, do i look pretty? :blush:")

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(Perms.devOnly)
    async def reload(self, ctx):
        """Reloads the bot's cogs"""
        await self.bot.change_presence(game=discord.Game(name="new commands"))
        print("Reloading all cogs")
        msg = await self.bot.say('Reloading cogs :thinking')

        await self.bot.edit_message(msg, "Reloading Music :thinking:")
        self.bot.remove_cog("Music")
        importlib.reload(code.music)
        from code.music import Music
        self.bot.add_cog(Music(bot))
        await self.bot.edit_message(msg, "Reloaded Music :slight_smile:")

        await self.bot.edit_message(msg, "Reloading Moderation :thinking:")
        self.bot.remove_cog("Moderation")
        importlib.reload(code.moderation)
        from code.moderation import Moderation
        self.bot.add_cog(Moderation(bot))
        await self.bot.edit_message(msg, "Reloaded Moderation :slight_smile:")

        await self.bot.edit_message(msg, "Reloading Fun :thinking:")
        self.bot.remove_cog("Fun")
        importlib.reload(code.fun)
        from code.fun import Fun
        self.bot.add_cog(Fun(bot))
        await self.bot.edit_message(msg, "Reloaded Fun :slight_smile:")

        await self.bot.edit_message(msg, "Reloading Porn :thinking:")
        self.bot.remove_cog("Porn")
        importlib.reload(code.porn)
        from code.porn import Porn
        self.bot.add_cog(Porn(bot))
        await self.bot.edit_message(msg, "Reloaded Porn :slight_smile:")

        await self.bot.edit_message(msg, "Reloading Utilities :thinking:")
        self.bot.remove_cog("Utilities")
        importlib.reload(code.utilities)
        from code.utilities import Utilities
        self.bot.add_cog(Utilities(bot))
        await self.bot.edit_message(msg, "Reloaded Utilities :slight_smile:")
        await self.bot.edit_message(msg, 'Reload complete :slight_smile:')
        await self.bot.change_presence(game=discord.Game(name="with my thumbs"))

    @commands.command(pass_context=True)
    @commands.check(Perms.devOnly)
    async def shutdown(self, ctx):
        """Shuts down Helix"""
        goodbyeStrings = ["ok :cry:", "please dont make me go back to the darkness :cold_sweat:", "but i dont want to :cry:", "if you say so :unamused:", "please dont, im scared of darkness, dont do this to me :scream:", "dont send me back there, its so cold and dark :sob:"]
        await self.bot.send_message(ctx.message.channel, random.choice(goodbyeStrings))
        try:
            self.bot.remove_cog("Music") # the player HATES this line being called for pretty obvious reasons
        except:
            pass
        await self.bot.logout()
        await self.bot.close()
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


bot = commands.Bot(command_prefix=getPrefix, description='Helix3.0', pm_help=True)
bot.add_cog(Core(bot, Perms))
bot.add_cog(Music(bot, Perms))
bot.add_cog(Moderation(bot, Perms))
bot.add_cog(Fun(bot, Perms))
bot.add_cog(Porn(bot, Perms))
bot.add_cog(Utilities(bot, Perms))
byp = bot

@bot.event
async def on_ready():
    await bot.change_presence(game=discord.Game(name="with my thumbs"))
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))
    if len(bot.servers) == 0:
        print("{} is not in any servers\nInvite link: {}".format(bot.user, discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(70380544), server=None)))
    else:
        print("Servers")
        for server in bot.servers:
            print("    ", server.name)

    startStrings = ["Hey! im online", "*yawns* Good Morning :unamused:", "Oh god, am i really that late??? :scream:", "THANK YOU, THANK YOU SO MUCH, DONT SEND ME BACK THERE PLEASE :sob:", "It was so dark... there was nothing to do :worried:", "I was so alone, so cold, so very very cold"]
    await bot.send_message(discord.Object(456827191838113846), random.choice(startStrings))
    print("Ready for user input")

@bot.event
async def on_command(bot, ctx):
    print("{}|{}|   {}".format(ctx.message.server.name, ctx.message.author.display_name, ctx.message.content))
    if "help" in ctx.message.content:
        await byp.send_message(ctx.message.channel, ":mailbox_with_mail:")

async def on_message(bot, message):
    # level code can be called in here
    if message.author == bot.user:
        return
    await bot.process_commands(message)

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