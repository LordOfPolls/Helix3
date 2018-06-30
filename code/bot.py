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
import code.Perms as Perms
import logging
import json
import math
import time
Perms = Perms.Perms

def _setup_logging(log):
    if len(logging.getLogger(__package__).handlers) > 1:
        log.debug("Skipping logger setup, already set up")
        return
    import colorlog
    shandler = logging.StreamHandler(stream=sys.stdout)
    fmt = "%(log_color)s[%(levelname)s] %(name)s: %(message)s"
    date_format = '%Y-%m-%d %H:%M:%S'
    fmt = colorlog.ColoredFormatter(fmt, date_format,
                                  log_colors={'DEBUG': 'cyan', 'INFO': 'reset',
                                              'WARNING': 'bold_yellow', 'ERROR': 'bold_red',
                                              'CRITICAL': 'bold_red'})
    shandler.setFormatter(fmt)
    logging.getLogger(__package__).addHandler(shandler)
    logging.getLogger("FFMPEG").setLevel(logging.ERROR)
    logging.getLogger("player").setLevel(logging.ERROR)
    logging.getLogger("discord.gateway ").setLevel(logging.ERROR)
    logging.getLogger("discord").setLevel(logging.FATAL)
    logging.getLogger(__package__).setLevel(logging.DEBUG)


def getPrefix(bot, message):
    try:
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
    except:
        if message.split(" ")[0][0] == ".":
            return "."
        else:
            return self.bot.user.mention



class Core:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command(pass_context=True, no_pm=False)
    @commands.check(Perms.devOnly)
    async def setpic(self, ctx):
        if ctx.message.attachments:
            pic = ctx.message.attachments[0]['url']
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
        messageX = ctx.message.content.replace(getPrefix(bot, ctx.message), "").lower()
        select = False
        msg = await self.bot.say("Ok :slight_smile:")
        if len(messageX) >= 7:
            select = True
        else:
            log.info("Reloading all cogs")
        if "music" in messageX or not select:
            log.debug("Reloading Music")
            await self.bot.edit_message(msg, "Reloading Music :thinking:")
            self.bot.remove_cog("Music")
            importlib.reload(code.music)
            from code.music import Music
            self.bot.add_cog(Music(bot))
            await self.bot.edit_message(msg, "Reloaded Music :slight_smile:")
        if "mod" in messageX or not select:
            log.debug("Reloading Moderation")
            await self.bot.edit_message(msg, "Reloading Moderation :thinking:")
            self.bot.remove_cog("Moderation")
            importlib.reload(code.moderation)
            from code.moderation import Moderation
            self.bot.add_cog(Moderation(bot))
            await self.bot.edit_message(msg, "Reloaded Moderation :slight_smile:")
        if "fun" in messageX or not select:
            log.debug("Reloading Fun")
            await self.bot.edit_message(msg, "Reloading Fun :thinking:")
            self.bot.remove_cog("Fun")
            importlib.reload(code.fun)
            from code.fun import Fun
            self.bot.add_cog(Fun(bot))
            await self.bot.edit_message(msg, "Reloaded Fun :slight_smile:")
        if "porn" in messageX or not select:
            log.debug("Reloading Porn")
            await self.bot.edit_message(msg, "Reloading Porn :thinking:")
            self.bot.remove_cog("Porn")
            importlib.reload(code.porn)
            from code.porn import Porn
            self.bot.add_cog(Porn(bot))
            await self.bot.edit_message(msg, "Reloaded Porn :slight_smile:")
        if "utilities" in messageX or not select:
            log.debug("Reloading Utilites")
            await self.bot.edit_message(msg, "Reloading Utilities :thinking:")
            self.bot.remove_cog("Utilities")
            importlib.reload(code.utilities)
            from code.utilities import Utilities
            self.bot.add_cog(Utilities(bot))
            await self.bot.edit_message(msg, "Reloaded Utilities :slight_smile:")
        if "chatbot" in messageX or not select:
            log.debug("Reloading Chatbot")
            await self.bot.edit_message(msg, "Reloading Chatbot :thinking:")
            self.bot.remove_cog("Chatbot")
            importlib.reload(code.chatbot)
            from code.chatbot import Chatbot
            self.bot.add_cog(Chatbot(bot))
            await self.bot.edit_message(msg, "Reloaded Chatbot :slight_smile:")            
        await self.bot.edit_message(msg, 'Reload complete :slight_smile:')

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
        try:
            self.bot.remove_cog("Chatbot") # lets the chatbot save its "brain" before shutdown
        except:
            pass
        await self.bot.logout()
        await self.bot.close()
        exit()

    @commands.command(pass_context=True, no_pm=True)
    async def leaderboard(self, ctx):
        # if str(ctx.message.server.id) in open('level_blck.txt').read():
        #     return Response("Leveling has been disabled in this server by your admin")

        with open("data/" + ctx.message.server.id + '/ranking.json', 'r+') as f:
            lvldb = json.load(f)
        data = "["
        for member in ctx.message.server.members:
            try:
                if not member.bot:
                    lvl = int(lvldb[member.id]['Level'])
                    xp = lvldb[member.id]['XP']
                    raw = str({"ID": member.id, "Level": lvl, "XP": xp})
                    raw += ","
                    data += raw
            except:
                pass
        data = data[:-1]
        data += "]"
        data = data
        data = json.loads(data.replace("'", '"'))
        data = sorted(data, key=lambda items: items['Level'], reverse=True)
        msg = "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ **Leaderboard** ✧ﾟ･: *ヽ(◕ヮ◕ヽ)\n\n"
        num = 1
        for item in data:
            if num != 11:
                for member in ctx.message.server.members:
                    if member.id == item['ID']:
                        name = member.display_name
                        msg += "{}. **Name:** {}, **Level:** {}\n".format(str(num), name, str(item['Level']))
                        num += 1

        await self.bot.send_message(ctx.message.channel, msg)

    @commands.command(pass_context=True, np_pm=True)
    async def rank(self, ctx):
        """
        Rank details or options (.help rank for more info)
        Rank enable = enable ranking
        Rank disable = disable ranking
        Ranking is simple, you get XP for messaging. The more you message the higher your level")
        The bigger your message the more XP you earn, however if you spam, you wont earn anything
        """
        message = ctx.message
        channel = message.channel
        author = message.author
        server = message.server
        usage = Perms.adminOnly(ctx)

        msg = ctx.message.content.strip()
        msg = msg.lower()
        prefix = getPrefix(bot, message)
        msg = msg.replace("rank ", "")
        msg = msg.replace(prefix, "")
        if msg == "about" or msg == "help":
            await self.bot.send_message(ctx.message.channel, "Ranking is simple, you get XP for messaging. The more you message the higher your level")
            await self.bot.send_message(ctx.message.channel, "The bigger your message the more XP you earn, however if you spam, you wont earn anything")
            return
        if msg == "enable":
            if usage == True:
                pass
            else:
                await self.bot.send_message(ctx.message.channel, "You need to be server admin to disable commands")
                return
            f = open('level_blck.txt', 'r+')
            filedata = f.read()
            f.close()

            newdata = filedata.replace(server.id, "")

            f = open('level_blck.txt', 'w')
            f.write(newdata)
            f.close()
            await self.bot.send_message(ctx.message.channel, "**Ranking enabled**")
            return
        if msg == "disable":
            if usage == True:
                pass
            else:
                await self.bot.send_message(ctx.message.channel, "You need to be server admin to disable commands")
                return
            try:
                f = open('level_blck.txt', 'a')
            except:
                f = open('level_blck.txt', 'w')
            sid = str(server.id) + " "
            f.write(sid)
            f.close()
            await self.bot.send_message(ctx.message.channel, "**Ranking disabled**")
            return
        else:
            if os.path.isfile('level_blck.txt'):
                if str(server.id) in open('level_blck.txt').read():
                    await self.bot.send_message(ctx.message.channel, "Leveling has been disabled in this server by your admin")
                    return
            with open("data/" + message.server.id + '/ranking.json', 'r+') as f:
                lvldb = json.load(f)

                data = "["
                for member in server.members:
                    try:
                        lvl = int(lvldb[member.id]['Level'])
                        xp = lvldb[member.id]['XP']
                        raw = str({"ID": member.id, "Level": lvl, "XP": xp})
                        raw += ","
                        data += raw
                    except:
                        pass
                data = data[:-1]
                data += "]"
                data = data
                data = json.loads(data.replace("'", '"'))
                data = sorted(data, key=lambda items: items['Level'], reverse=True)
                num = 1
                position = 0
                for item in data:
                    if item['ID'] == author.id:
                        position = num
                    num += 1
                em = discord.Embed(colour=(random.randint(0, 16777215)))
                em.add_field(name="XP", value=str(lvldb[message.author.id]['XP']) + "/" + str(
                    int(lvldb[message.author.id]['Level']) * 40), inline=True)
                em.add_field(name="Level", value=str(lvldb[message.author.id]['Level']), inline=True)
                # try:
                prog_bar_str = ''
                percentage = int(lvldb[message.author.id]['XP']) / (int(lvldb[message.author.id]['Level'])*40)
                progress_bar_length = 10
                for i in range(progress_bar_length):
                    if (percentage < 1 / progress_bar_length * i):
                        prog_bar_str += '□'
                    else:
                        prog_bar_str += '■'
                em.add_field(name="Progress", value=prog_bar_str)
                # except:
                #     pass
                try:
                    if position == 0:
                        pass
                    else:
                        em.add_field(name="Leaderboard Rank", value="#" + str(position), inline=True)
                except:
                    pass
                await self.bot.send_message(channel, embed=em)

import code.music
import code.moderation
import code.fun
import code.porn
import code.utilities
import code.chatbot as chatbot
from code.moderation import Moderation
from code.music import Music
from code.fun import Fun
from code.porn import Porn
from code.utilities import Utilities

log = logging.getLogger(__name__)
bot = commands.Bot(command_prefix=getPrefix, description='Helix3.0', pm_help=True)
global Chatbot
Chatbot = None

def Helix():
    _setup_logging(log)
    log.debug("Loading cogs")
    global Chatbot
    Chatbot = chatbot.Chatbot(bot)
    bot.add_cog(Core(bot))
    bot.add_cog(Music(bot))
    bot.add_cog(Moderation(bot))
    bot.add_cog(Fun(bot))
    bot.add_cog(Porn(bot))
    bot.add_cog(Utilities(bot))
    bot.add_cog(Chatbot)
    log.debug("Cogs loaded")

    if os.path.isfile("data/token.txt"):
        token = open("data/token.txt", "r").read()
    else:
        try:
            os.mkdir("data")
        except:
            pass
        log.error("NO TOKEN Dx")
        token = input("Please input a token: ")
        f = open("data/token.txt", "w")
        f.write(token)
        f.close()
        log.info("New token saved, resuming boot")
    try:
        log.info("Connecting...")
        bot.run(token.replace("\n", ""), reconnect=True, bot=True)
        bot.add_listener(Music.on_voice_state_update, 'on_voice_state_update')
    except discord.errors.LoginFailure:
        log.fatal("Token failed")
        os.unlink("data/token.txt")
    except Exception as e:
        log.fatal("Bot runtime failed")
        log.fatal(e)



async def rankUpdate(message):
    try:
        if message.author == bot.user or message.author == None or message.author.bot:
            return
        # elif str(message.server.id) in open('level_blck.txt').read():
        #     return
    except Exception as e:
        log.error("Error in rankUpdate:\n{}".format(e))
        return

    directory = "data/{}/ranking.json".format(message.server.id)
    if not os.path.exists(directory):
        os.mkdir("data/" +str(message.server.id))
        with open(directory, 'w') as file:
            entry = {message.author.id: {'Rank': 'User', 'XP': '0', 'Level': '1', 'LastMSG': '', 'LastMSGTime':' '}}
            json.dump(entry, file)
            file.seek(0)
            file.write(json.dumps(entry))
            file.truncate()
            return
    # try:
    with open(directory, 'r+') as file:
        lvldata = json.load(file)
        if message.author.id in lvldata:
            score = math.floor(len(message.content.split(' '))/2)
            if score >= 100:
                score = score/2
            try:
                if len(message.attatchments) > 0:
                    score = 10
            except:
                pass
            if lvldata[message.author.id]['LastMSG'] == message.content:
                score = 0
            else:
                lvldata[message.author.id]['LastMSG'] = message.content
            if lvldata[message.author.id]['LastMSGTime'] != ' ':
                diff = int(time.time()) - int(lvldata[message.author.id]['LastMSGTime'])
                if diff < 4:
                    score = 0

            lvldata[message.author.id]['LastMSGTime'] = int(time.time())
            log.debug('Awarding {} points'.format(score))
            lvldata[message.author.id]['XP'] = int(lvldata[message.author.id]['XP']) +score
            if lvldata[message.author.id]['XP'] >= int(lvldata[message.author.id]['Level']) *40:
                lvldata[message.author.id]['Level'] = str(int(lvldata[message.author.id]['Level'])+1)
                lvldata[message.author.id]['XP'] = "0"
                await bot.send_message(message.channel, "Congrats {}, you're level {} now :smile:".format(message.author.mention, lvldata[message.author.id]['Level']))
        else:
            entry = {message.author.id: {'Rank': 'User', 'XP': '0', 'Level': '1', 'LastMSG': '', 'LastMSGTime':' '}}
            lvldata.update(entry)
        file.seek(0)
        file.write(json.dumps(lvldata))
        file.truncate()
    # except Exception as e:
    #     log.error("Error in rankUpdate:\n{}".format(e))





@bot.event
async def on_ready():
    log.info('Logged in as:    {0} (ID: {0.id})'.format(bot.user))
    if len(bot.servers) == 0:
        log.warning("{} is not in any servers\nInvite link: {}".format(bot.user, discord.utils.oauth_url(bot.user.id, permissions=discord.Permissions(70380544), server=None)))
    else:
        string = "Servers:"
        for server in bot.servers:
            string += "\n                 -{}".format(server.name)
        log.info(string)
    bot.loop.create_task(statusCycle(False))
    startStrings = ["Hey! im online", "*yawns* Good Morning :unamused:", "Oh god, am i really that late??? :scream:", "THANK YOU, THANK YOU SO MUCH, DONT SEND ME BACK THERE PLEASE :sob:", "It was so dark... there was nothing to do :worried:", "I was so alone, so cold, so very very cold"]
    #await bot.send_message(discord.Object(456827191838113846), random.choice(startStrings))
    log.info("Ready for user input")

byp = bot
@bot.event
async def on_command(bot, ctx):
    try:
        log.info('{}|{}| "{}"'.format(ctx.message.server.name, ctx.message.author.display_name, ctx.message.content.replace(getPrefix(bot, ctx.message), "")))
        if "help" in ctx.message.content:
            await byp.send_message(ctx.message.channel, ":mailbox_with_mail:")
    except:
        log.info('DM|{}| "{}"'.format(ctx.message.author.display_name, ctx.message.content))


@bot.event
async def on_message(message):
    # level code can be called in here
    if message.author == bot.user:
        return
    try:
        await rankUpdate(message)
    except:
        pass
    if bot.user.mentioned_in(message):
        if len(message.content) == 21 or len(message.content) == 22:
            log.info("{} mentioned me, I guess they want some help".format(message.author.name))
            message.content = ".help" #jankiest way of doing this but it works reliably
            await bot.process_commands(message)
            return
    try:
        await bot.process_commands(message)
    except Exception as e:
        log.error("Error:\n\n", e)
        fmt = 'An error occurred while processing that request: ```py\n{}: {}\n```'
        await bot.send_message(message.channel, fmt.format(type(e).__name__, e))

@bot.event
async def on_server_join(server):
    try:
        log.info("Joined server {}".format(server.name))
        channel = None
        flag = False
        if server.default_channel is None:
            for c in server.channels:
                if c.name == "general" and str(c.type) == "text":
                    channel = c
                    flag = True
                if str(c.type) == "text" and not flag:
                    channel = c

        else:
            channel = server.default_channel

        msg = "Hi there, Im Helix**3.0**. Mention me to see what i can do"
        em = discord.Embed(description=msg, colour=65280)
        em.set_author(name='I just joined :3', icon_url=(bot.user.avatar_url))
        try:
            await bot.send_message(channel, embed=em)
        except:
            await bot.send_message(channel, msg)
        circles = [':white_circle:', ':black_circle:', ':red_circle:', ':large_blue_circle:']

        await bot.send_message(channel, "Give me a second to create some files for your server :thinking:")
        msg = await bot.send_message(channel, ' '.join(circles))
        for x in range(5):
            random.shuffle(circles)
            await bot.edit_message(msg, ' '.join(circles))
            await asyncio.sleep(0.3)
        await bot.edit_message(msg, "Done")

    except Exception as e:
        log.error(e)


@bot.event
async def on_command_error(error, ctx):
    if "not found" in str(error):
        # ignore this, i know its janky but it works blame raptz for making errors stupid
        global Chatbot
        await Chatbot._chatbot(ctx.message)
    elif "check" in str(error):
        await bot.send_message(ctx.message.channel, "{}. Sorry you don't have the permissions to use ``{}``".format(ctx.message.author.mention, ctx.command))
    else:
        log.error(error)
        fmt = 'An error occurred while processing that request: ```py\n{}: {}\n```'
        await bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))

@bot.event
async def on_member_join(ctx):
    member = ctx
    if member.id in str(dev):
        log.info("Dev Join| {} joined {}".format(member.display_name, member.server.name))
        await byp.send_message(member.server, "{}, one of my devs, joined your server".format(member.display_name))
    if member.id in str(staff):
        log.info("Staff Join| {} joined {}".format(member.display_name, member.server.name))
        await byp.send_message(member.server, "{}, one of my staff members, joined your server".format(member.display_name))

async def statusCycle(suspend):
    gameList = ['music somewhere', 'with code', 'something, idk', 'some really messed up stuff', 'with /help', 'with commands', 'porn', 'VIDEO GAMES', 'Overwatch', 'MLG Pro Simulator', 'stuff', 'with too many servers', 'with life of my dev', 'dicks', 'Civ 5', 'Civ 6', 'Besiege', 'with code', 'Mass Effect', 'bangin tunes', 'with children', 'with jews', 'on a new server', '^-^', 'with something', 'the violin', 'For cuddles', 'the harmonica', 'With dicks', 'With a gas chamber', 'Nazi simulator 2K17', 'Rodina', 'Gas bills', 'Memes', 'Darkness', 'With some burnt toast', 'Jepus Crist', 'With my devs nipples', 'SOMeBODY ONCE TOLD ME', 'With Hitlers dick', 'In The Street', 'With Knives', 'ɐᴉlɐɹʇsn∀ uI', 'Shrek Is Love', 'Shrek Is Life', 'Illegal Poker', 'ACROSS THE UNIVERRRRSE', 'Kickball', 'Mah Jam', 'R2-D2 On TV', 'with fire', 'at being a real bot', 'with your fragile little mind']
    num = 0
    while True:
        if not suspend and bot.is_closed == False:
            await bot.change_presence(game=discord.Game(name=gameList[num]))
            num += 1
            if num > len(gameList)-1:
                num = 0
        if suspend:
            log.fatal("wut")
            num = 1
        await asyncio.sleep(8)
        if bot.is_closed:
            break
