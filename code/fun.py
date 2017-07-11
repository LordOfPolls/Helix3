import asyncio
import discord
import timeit
from discord.ext import commands
import code.get as get


class Fun:
    def __init__(self, bot):
        self.bot = bot
       
    @commands.command(pass_context=True, no_pm=False)
    async def ping(self, ctx):
        s = timeit.default_timer()
        await self.bot.send_typing(ctx.message.channel)
        elapsed = timeit.default_timer() - s
        elapsed = elapsed * 1000
        elapsed = "{0:.0f}".format(elapsed)
        msg = await self.bot.say('Pong!')
        await self.bot.edit_message(msg, "Pong!\n\nPing: {}ms".format(str(elapsed)))
