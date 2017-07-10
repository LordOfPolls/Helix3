import asyncio
import discord
from discord.ext import commands

class Fun:
    def __init__(self, bot):
        self.bot = bot
       
    @commands.command(pass_context=True, no_pm=False)
    async def ping(self, ctx):
       await self.bot.say('Pong!')
