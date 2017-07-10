import asyncio
import discord
from discord.ext import commands

class Fun:
    def __init__(self, bot):
        self.bot = bot
        
          @commands.command(pass_context=True, no_pm=True)
    async def ping(message):
          if message.content.startswith('!ping'):
       await client.send_message(message.channel, 'Pong!')
