import asyncio
import discord
import timeit
import code.get as get
import urllib
import urllib.request as urllib2
import bs4

from bs4 import BeautifulSoup
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

    @commands.command(pass_context = True)
    async def fakekick(self, ctx):
        """Fake kicks a user"""
        await self.bot.send_typing(ctx.message.channel)
        await self.bot.delete_message(ctx.message)
        user_mentions = list(map(ctx.message.server.get_member, ctx.message.raw_mentions))
        for user in user_mentions:
            await self.bot.say("<@{}>, i kicked <@{}>.".format(ctx.message.author.id, user.id))

    @commands.command(pass_context = True)
    async def dog(self):
        """Sends a dog pic"""
        def findDog():
            page = BeautifulSoup(urllib2.urlopen("https://random.dog/"), "lxml")
            img = page.findAll('img')
            image = str(img)
            image = image.replace('[<img id="dog-img" src="', "")
            image = image.replace('"/>]', "")
            image = "https://random.dog/{}".format(image)

        while "https://random.dog/[]" in image:
            findDog()
                      
        await self.bot.say(image)
