import math
import os
import random
import subprocess
import time
import timeit
from subprocess import PIPE
from urllib.parse import parse_qs

import aiohttp
import discord
from discord.ext import commands
from lxml import etree

import code.Perms as Perms
import code.get as get

Perms = Perms.Perms

class Utilities:
    def __init__(self, bot):
        self.bot = bot
        self.bugChannel = discord.Object("457131257898205185")
        self.featureChannel = discord.Object("457131283680591873")

    async def get_google_entries(self, query):
        params = {
            'q': query,
            'safe': 'on'
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64)'
        }

        # list of URLs
        entries = []

        async with aiohttp.get('https://www.google.co.uk/search', params=params, headers=headers) as resp:
            if resp.status != 200:
                raise RuntimeError('Google somehow failed to respond.')

            root = etree.fromstring(await resp.text(), etree.HTMLParser())

            """
            Tree looks like this.. sort of..
            <div class="g">
                ...
                <h3>
                    <a href="/url?q=<url>" ...>title</a>
                </h3>
                ...
                <span class="st">
                    <span class="f">date here</span>
                    summary here, can contain <em>tag</em>
                </span>
            </div>
            """

            search_nodes = root.findall(".//div[@class='g']")
            for node in search_nodes:
                url_node = node.find('.//h3/a')
                if url_node is None:
                    continue

                url = url_node.attrib['href']
                if not url.startswith('/url?'):
                    continue

                url = parse_qs(url[5:])['q'][0]  # get the URL from ?q query string

                # description
                entries.append(url)
                short = node.find(".//span[@class='st']")
                if short is None:
                    entries.append((url, ''))
                else:
                    text = ''.join(short.itertext())
                    entries.append((str(url), str(text.replace('...', ''))))

        return entries

    global startTime
    startTime = time.time()

    @commands.command(pass_context=True, no_pm=False)
    async def id(self, ctx):
        """
        Tells the user their id or the id of another user.
        """
        message = ctx.message
        author = ctx.message.author
        user_mentions = list(map(message.server.get_member, message.raw_mentions))
        if not user_mentions:
            await self.bot.say('your id is `%s`' % author.id)
        else:
            usr = user_mentions[0]
            await self.bot.say("%s's id is `%s`" % (usr.name, usr.id))

    @commands.command(pass_context=True, no_pm=False)
    async def ping(self, ctx):
        """Ping the bot"""
        s = timeit.default_timer()
        await self.bot.send_typing(ctx.message.channel)
        elapsed = timeit.default_timer() - s
        elapsed = elapsed * 1000
        elapsed = "{0:.0f}".format(elapsed)
        msg = await self.bot.say('Pong!')
        await self.bot.edit_message(msg, "Pong!\n\nPing: {}ms".format(str(elapsed)))

    @commands.command(pass_context=True, no_pm=True)
    async def server(self, ctx):
        """Shows the server's information"""
        channel = ctx.message.channel
        author = ctx.message.author
        server = ctx.message.server
        message = ctx.message
        online = str(len([m.status for m in server.members if str(m.status) == "online" or str(m.status) == "idle"]))
        total_users = str(len(server.members))
        text_channels = len([x for x in server.channels if str(x.type) == "text"])
        voice_channels = len(server.channels) - text_channels

        data = "```python\n"
        data += "Name: {}\n".format(server.name)
        data += "ID: {}\n".format(server.id)
        data += "Region: {}\n".format(server.region)
        data += "Users: {}/{}\n".format(online, total_users)
        data += "Text channels: {}\n".format(text_channels)
        data += "Voice channels: {}\n".format(voice_channels)
        data += "Roles: {}\n".format(len(server.roles))
        passed = (message.timestamp - server.created_at).days
        data += "Created: {} ({} days ago)\n".format(server.created_at, passed)
        data += "Owner: {}\n".format(server.owner)
        if server.icon_url != "":
            data += "Icon:"
            data += "```"
            data += server.icon_url
        else:
            data += "```"
        await self.bot.send_message(channel, data)

    @commands.command(pass_context=True, no_pm=True)
    async def urban(self, ctx):
        """Query Urban Dictionary"""
        await self.bot.send_typing(ctx.message.channel)
        prefix = await get.Prefix(ctx.message.server)
        message = ctx.message.content.strip()
        message = message.lower()
        messages = message.replace("urban ", "")
        messages = messages.replace(prefix, "")
        terms = messages
        try:
            async with aiohttp.get(("http://api.urbandictionary.com/v0/define?term=" + terms)) as r:
                if not r.status == 200:
                    await self.bot.say("Unable to connect to Urban Dictionary")
                else:
                    j = await r.json()
                    if j["result_type"] == "no_results":
                        msg = "No results for "
                        msg = msg + terms
                        em = discord.Embed(description=msg, colour=16711680)
                        em.set_author(name='Urban', icon_url="https://pilotmoon.com/popclip/extensions/icon/ud.png")
                        await self.bot.say(embed=em)
                        return
                    elif j["result_type"] == "exact":
                        word = j["list"][0]
                    definerer = (word["definition"])
                    n = ("%s - Urban Dictionary" % word["word"])
                    em = discord.Embed(description=definerer, colour=(random.randint(0, 16777215)))
                    em.set_author(name=n, icon_url="https://pilotmoon.com/popclip/extensions/icon/ud.png")
                    await self.bot.say(embed=em)
        except Exception as e:
            await self.bot.say(("Unable to connect to Urban Dictionary " + str(e)))

    @commands.command(pass_context=True, no_pm=True)
    async def whois(self, ctx):
        """Gets information on a user"""
        message = ctx.message
        channel = ctx.message.channel
        author = ctx.message.author
        server = ctx.message.author
        user_mentions = list(map(message.server.get_member, message.raw_mentions))

        def userinf(user, channel):
            msg = "Information on " + str(user.mention)
            roles = ""
            for role in user.roles:
                if str(role) == "@everyone":
                    pass
                else:
                    roles += str(role) + "\n"
            em = discord.Embed(description=msg, colour=(random.randint(0, 16777215)))
            em.set_author(name=user.display_name, icon_url=(user.avatar_url))
            em.add_field(name="**User name:**", value=str(user.name) , inline=True)
            if not author.name == author.display_name: #so we dont have useless fields sat around
                em.add_field(name="**Nickname:**", value=(str(user.display_name)), inline=True)
            em.add_field(name="**Created on:**", value=str(user.created_at), inline=True)
            em.add_field(name="**ID:**", value=str(user.id), inline=True)
            if not roles == "" or roles == " ":
                em.add_field(name="**Roles**", value=roles, inline=True)
            if user.bot:
                em.add_field(name="**Bot**", value="This user is a bot", inline=False)
            em.set_thumbnail(url=user.avatar_url)
            return em
        try:
            if not user_mentions:
                user = author #allows us to only use this one script, much cleaner and more efficent
                em =userinf(user, channel)
                try:
                    await self.bot.send_message(channel, embed=em)
                except:
                    await self.bot.send_message(channel, "You've disabled my permission to 'embed links'")
            else:
                for user in user_mentions:
                    em = userinf(user, channel)
                    try:
                        await self.bot.send_message(channel, embed=em)
                    except:
                        await self.bot.send_message(channel, "You've disabled my permission to 'embed links'")
        except:
            pass

    @commands.command(pass_context=True, no_pm=False)
    async def google(self, ctx):
        """Searches google and gives you top result."""
        server = ctx.message.server
        channel = ctx.message.channel
        prefix = await get.Prefix(server)
        message = ctx.message.content.strip()
        message = message.lower()
        message = message.replace("google ", "")
        message = message.replace(prefix, "")
        query = message
        try:
            entries = await self.get_google_entries(query)
        except RuntimeError as e:
            await self.bot.say(str(e))
        else:
            next_two = entries[3:5]
            if next_two:
                formatted = "\n"
                for item in next_two:
                    item = str(item)
                    formatted += "{}\n".format(item.replace("(","").replace("'", "").replace("\\n", "")[:-5] + "...")
                msg = formatted
            else:
                try:
                    msg = entries[0]
                except IndexError:
                    msg = "No results"
                    em = discord.Embed(description=msg, colour=16711680)
                    em.set_author(name='Google:',
                                  icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/2000px-Google_%22G%22_Logo.svg.png")
                    await self.bot.send_message(channel, embed=em)
                    return
            em = discord.Embed(description=msg, colour=(random.randint(0, 16777215)))
            em.set_author(name='Google:',
                          icon_url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/2000px-Google_%22G%22_Logo.svg.png")
            await self.bot.send_message(channel, embed=em)

    @commands.command(pass_context = True)
    async def join(self, ctx):
        """Invite links for the bot"""
        message = ctx.message
        author = message.author
        em = discord.Embed(title="Info", colour=(random.randint(0, 16777215)))
        em.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url)
        invite = "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=1312156871".format(self.bot.user.id)
        em.add_field(name="Add Helix", value=invite)
        em.add_field(name="Join the server", value="https://discord.gg/ZYVNxwh")
        await self.bot.say(embed=em)

    @commands.command(pass_context = True)
    async def info(self,ctx):
        """Info on the bot"""
        await self.bot.send_typing(ctx.message.channel)
        global startTime
        try:
            version = os.popen(r'git show -s HEAD --format="%cr|%s|%h"')
            version = version.read()
            version = version.split('|')
            version = str(version[2])
            version = version.strip()
            gversion = True
        except:
            gversion = False
        if version == "" or version == None:
            gversion = False
        users = len(set(self.bot.get_all_members()))
        online = sum(1 for m in (set(self.bot.get_all_members())) if m.status != discord.Status.offline)
        servercount = str(len(self.bot.servers))
        uptime = time.time() - startTime
        uptime = math.floor(uptime)
        seconds = uptime % 60
        minutes = math.floor((uptime - seconds) / 60)
        hours = math.floor(minutes / 60)
        try:
            minutes = minutes % hours

            days = math.floor(hours / 24)
            hours = hours % days
        except:
            days = 0
        uptime = "Days: {} , Hours: {} , Minutes: {} , Seconds: {}".format(days, hours, minutes, seconds)
        uptime = uptime.replace(".0", "")
        em = discord.Embed(title="Helix Info", colour=(random.randint(0, 16777215)))
        em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url)
        em.add_field(name="Version", value=version, inline=True)
        em.add_field(name="Users", value=users, inline=True)
        em.add_field(name="Online Users", value=online, inline=True)
        em.add_field(name="Servers", value=servercount)
        em.add_field(name="Bot Uptime", value=uptime)
        try:
            await self.bot.say(embed=em)
        except:
            await self.bot.say("I need the 'embed links' permission.")

    @commands.command(pass_context = True)
    async def donate(self, ctx):
        await self.bot.say("Disabled")
        return
        await self.bot.send_typing(ctx.message.channel)
        message = "Thanks for considering donating to us, it means a lot. The servers Helix use are expensive and we need all the money we can get."
        patreon = "https://www.patreon.com/HelixBot"
        em = discord.Embed(title="Donate", colour=(random.randint(0, 16777215)))
        em.set_author(name=self.bot.user.display_name, icon_url=self.bot.user.avatar_url)
        em.add_field(name="Patreon", value=patreon)
        try:
            await self.bot.say(embed=em)
        except:
            await self.bot.say("I need the 'embed links' permission")
        author = ctx.message.author
        await self.bot.send_message(author, message)

    @commands.command(pass_context = True)
    async def updatelog(self, ctx):
        """The bots update log"""
        await self.bot.say("Disabled")
        return
        channel = ctx.message.channel
        command = 'git log --name-status HEAD^..HEAD'
        pipe = subprocess.Popen(command, stdout=PIPE, shell=True)
        text = pipe.communicate()[0]
        text = str(text, 'utf8')
        text = text.replace("commit", "Commit ID:")
        go = True
        char = 0
        while go == True:
            if text[char] != "<":
                char += 1
            else:
                opening = char
                go = False
        go = True
        char = 0
        while go == True:
            if text[char] != ">":
                char += 1
            else:
                closing = char
                go = False
        char = opening
        email = ""
        while char <= closing:
            email = email + text[char]
            char += 1            

        text = text.replace(email, "")
        em = discord.Embed(title="", colour=(random.randint(0, 16777215)))
        em.add_field(name="Latest Update", value=text)
        await self.bot.send_message(channel, embed=em)
