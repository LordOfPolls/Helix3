import asyncio
import discord
import os
import timeit
import json
import aiohttp
import random
from discord.ext import commands
import code.get as get

class Utilities:
    def __init__(self, bot):
        self.bot = bot
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
    async def prefix(self, ctx):
        """Change the bots prefix for your server"""
        message = ctx.message.content.strip()
        message = message.replace("<@{}> ".format(str(self.bot.user.id)), "")
        length = 6 + int(len(await get.Prefix(ctx.message.server)))
        if len(message) == length:
            message = None
        else:
            message = message.split(" ")
            try:
                message = message[1]
            except IndexError:
                message = None
        server = ctx.message.server
        channel = ctx.message.channel

        dir = "data/" + server.id + ".json"
        if not os.path.exists("data"):
            os.mkdir("data")
        if not os.path.isfile(dir):
            with open(dir, 'w') as r:
                entry = {'welcome': channel.id, 'prefix': ".", 'urlblock': 'True', 'mention': 'False',
                         'announcement': 'None', 'modrole': 'None', 'modlog': 'None'}
                json.dump(entry, r)
        else:
            with open(dir, 'r+') as r:
                data = json.load(r)
                try:
                    if message == None:
                        await self.bot.send_message(channel,
                                                    "My current prefix here is ``{}``\n".format(data['prefix']))
                        return
                    data['prefix'] = str(message)
                except:
                    await self.bot.send_message(channel,"My current prefix here is ``{}``\n".format(data['prefix']))
                    return
                r.seek(0)
                r.write(json.dumps(data))
                r.truncate()
        await self.bot.send_message(channel, "Set prefix to ``" + str(message) + "``")

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