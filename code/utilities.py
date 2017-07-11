import asyncio
import discord
import os
import timeit
import json
from discord.ext import commands
import code.get as get

class Utilities:
    def __init__(self, bot):
        self.bot = bot

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