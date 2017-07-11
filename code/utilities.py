import asyncio
import discord
import os
import json
from discord.ext import commands
import code.get as get

class Utilities:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def prefix(self, ctx):
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