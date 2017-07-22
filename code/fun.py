import asyncio
import discord
import timeit
import code.get as get

from discord.ext import commands
from code.savage import savage



class Fun:
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(pass_context=True)
    async def echo(self, ctx, *args):
        """echos whatever you say"""
        await self.bot.say('{}'.format(' '.join(args)))
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context = True)
    async def savage(self, ctx):
        """Savage insults"""
        await self.bot.send_typing(ctx.message.channel)
        message = savage()
        mention = ""
        user_mentions = list(map(ctx.message.server.get_member, ctx.message.raw_mentions))
        for user in user_mentions:
            mention += "<@{}>  ".format(user.id)
            
        message = (("%s {}").format(mention) % (message))

        await self.bot.say(message)
        await self.bot.delete_message(ctx.message)