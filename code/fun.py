import asyncio
import discord
from discord.ext import commands

class Fun:
    def __init__(self, bot):
        self.bot = bot
       
    @commands.command(pass_context=True)
    async def panicping(self, ctx, *args):
        """Panic's dead ass ping command"""
        await self.bot.say('Pong')
