import asyncio
import discord
from discord.ext import commands

class Fun:
    def __init__(self, bot):
        self.bot = bot
        
 @commands.command(pass_context=True, no_pm=True)
 async def ping(message):
     if message.content.startswith('!ping'):
         return await my_bot.say("Hello, world!")

