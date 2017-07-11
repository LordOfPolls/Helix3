import asyncio
import discord
import timeit
from discord.ext import commands
import code.get as get


class Fun:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context=True)
    async def echo(self, ctx, *args):
        """echos whatever you say"""
        await self.bot.say('{}'.format(' '.join(args)))
        await self.bot.delete_message(ctx.message)
