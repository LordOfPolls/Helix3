import asyncio
import discord
import timeit
import code.get as get
import urllib
import urllib.request as urllib2
import bs4
import aiohttp
import random
import requests
import imgurpython
from bs4 import BeautifulSoup
from discord.ext import commands
from imgurpython import ImgurClient
from code.misc_savage import savage
from code.misc_compliment import compliment
from code.misc_pickup import pickup
from code.misc_shitpost import shitpost
import code.Perms as Perms
Perms = Perms.Perms


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
            if user != self.bot.user:
                mention += "<@{}>  ".format(user.id)
            
        message = (("%s {}").format(mention) % (message))

        await self.bot.say(message)
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context = True)
    async def dog(self):
        """Sends a dog pic"""
        def findDog():
            global pic
            page = BeautifulSoup(urllib2.urlopen("https://random.dog/"), "lxml")
            img = page.findAll('img')
            pic = str(img)
            pic = pic.replace('[<img id="dog-img" src="', "")
            pic = pic.replace('"/>]', "")
            pic = "https://random.dog/{}".format(pic)

        global pic
        findDog()
        while "https://random.dog/[]" in pic:
            findDog()
        em = discord.Embed(colour=0x260068)
        em.set_image(url=pic)
        await self.bot.say(embed=em)

    @commands.command(pass_context=True, hidden=True)
    async def orange(self):
        """"Fuck you orange"""
        await self.bot.say("Orange is an apple")

    @commands.command(pass_context=True)
    async def cat(self):
        """Sends a cat pic"""
        global image
        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            async with session.get('http://aws.random.cat/meow') as r:
                if r.status == 200:
                    js = await r.json()
                    em = discord.Embed(colour=0x260068)
                    em.set_image(url=js['file'])
                    await self.bot.say(embed=em)

    @commands.command(pass_context = True)
    async def meme(self):
        """Sends a meme"""
        client = ImgurClient("clientid", "clientsecret")
        items = client.memes_subgallery()
        item = random.choice(items)     
        await self.bot.say(item.title)
        await self.bot.say(item.link)

    @commands.command(pass_context = True)
    async def compliment(self, ctx):
        """Sends compliments"""
        await self.bot.send_typing(ctx.message.channel)
        message = compliment()
        mention = ""
        user_mentions = list(map(ctx.message.server.get_member, ctx.message.raw_mentions))
        for user in user_mentions:
            mention += "<@{}>  ".format(user.id)
            
        message = (("%s {}").format(mention) % (message))

        await self.bot.say(message)
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context = True)
    async def pickup(self, ctx):
        """Pickup lines"""
        await self.bot.send_typing(ctx.message.channel)
        message = pickup()
        mention = ""
        user_mentions = list(map(ctx.message.server.get_member, ctx.message.raw_mentions))
        for user in user_mentions:
            mention += "<@{}>  ".format(user.id)
            
        message = (("%s {}").format(mention) % (message))

        await self.bot.say(message)
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context = True)
    async def shitpost(self, ctx):
        """Shitposts"""
        await self.bot.send_typing(ctx.message.channel)
        message = shitpost()
        mention = ""
        user_mentions = list(map(ctx.message.server.get_member, ctx.message.raw_mentions))
        for user in user_mentions:
            mention += "<@{}>  ".format(user.id)
            
        message = (("%s {}").format(mention) % (message))

        await self.bot.say(message)
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context = True)
    async def vicky(self, ctx, *args):
        """Victorian insults"""
        await self.bot.send_typing(ctx.message.channel)
        mention = ""
        user_mentions = list(map(ctx.message.server.get_member, ctx.message.raw_mentions))
        for user in user_mentions:
            if user != self.bot.user:
                mention += "<@{}>  ".format(user.id)

        if "326819697381212160" in mention:
            mention.replace("326819697381212160", ctx.message.author.id)

        words1 = ['Artless', 'Bawdy', 'Beslubbering', 'Bootless', 'Churlish', 'Cockered', 'Clouted', 'Craven', 'Currish',
             'Dankish', 'Dissembling', 'Droning', 'Errant', 'Fawning', 'Fobbing', 'Froward', 'Frothy', 'Gleeking',
             'Goatish', 'Gorbellied', 'Impertinent', 'Infectious', 'Jarring', 'Loggerheaded', 'Lumpish', 'Mammering',
             'Mangled', 'Mewling', 'Paunchy', 'Pribbling', 'Puking', 'Puny', 'Quailing', 'Rank', 'Reeky', 'Roguish',
             'Ruttish', 'Saucy', 'Spleeny', 'Spongy', 'Surly', 'Tottering', 'Unmuzzled', 'Vain', 'Venomed',
             'Villainous', 'Warped', 'Wayward', 'Weedy', 'Yeasty','Base-court', 'Bat-fowling', 'Beef-witted', 'Beetle-headed', 'Boil-brained', 'Clapper-clawed','Clay-brained', 'Common-kissing', 'Crook-pated', 'Dismal-dreaming', 'Dizzy-eyed', 'Dog-hearted',
             'Dread-bolted', 'Earth-vexing', 'Elf-skinned', 'Fat-kidneyed', 'Fen-sucked', 'Flap-mouthed', 'Fly-bitten',
             'Folly-fallen', 'Fool-born', 'Full-gorged', 'Guts-griping', 'Half-faced', 'Hasty-witted', 'Hedge-born',
             'Hell-hated', 'Idle-headed', 'Ill-breeding', 'Ill-nurtured', 'Knotty-pated', 'Milk-livered',
             'Motley-minded', 'Onion-eyed', 'Plume-plucked', 'Pottle-deep', 'Pox-marked', 'Reeling-ripe', 'Rough-hewn',
             'Rude-growing', 'Rump-fed', 'Shard-borne', 'Sheep-biting', 'Spur-galled', 'Swag-bellied', 'Tardy-gaited',
             'Tickle-brained', 'Toad-spotted', 'Unchin-snouted', 'Weather-bitten']
        words2 = ['Apple-john', 'Baggage', 'Barnacle', 'Bladder', 'Boar-pig', 'Bugbear', 'Bum-bailey', 'Canker-blossom',
             'Clack-dish', 'Clot-pole', 'Coxcomb', 'Codpiece', 'Death-token', 'Dewberry', 'Flap-dragon', 'Flax-wench',
             'Flirt-gill', 'Foot-licker', 'Fustilarian', 'Giglet', 'Gudgeon', 'Haggard', 'Harpy', 'Hedge-pig',
             'Horn-beast', 'Huggermugger', 'Jolt-head', 'Lewdster', 'Lout', 'Maggot-pie', 'Malt-worm', 'Mammet',
             'Measle', 'Minnow', 'Miscreant', 'Mold-warp', 'Mumble-news', 'Nut-hook', 'Pigeon-egg', 'Pignut', 'Puttock',
             'Pumpion', 'Rats-bane', 'Scut', 'Skains-mate', 'Strumpet', 'Varlot', 'Vassal', 'Whey-face', 'Wagtail']

        adjective1 = random.choice(words1)
        if adjective1.startswith(("A" or "E" or "I" or "O" or "U")):
            article = "an"
        else:
            article = "a"
        adjective2 = random.choice(words1)
        while adjective2 == adjective1:
            adjective2 = random.choice(words1)
        noun = random.choice(words2)
        if mention == "":
            insult = (("Thou art %s %s, %s %s") % (article, adjective1, adjective2, noun))
        else:
            insult = (("%s, thou art %s %s, %s %s") % (mention, article, adjective1, adjective2, noun))
        await self.bot.say(insult)
        
    @commands.command(pass_context = True)   
    async def eightball(self, ctx, message):
        """Magic eightball"""
        channel = ctx.message.channel
        server = ctx.message.server
        await self.bot.send_typing(channel)
        dir = "data/settings/" + ctx.message.server.id + ".json"
        if not os.path.exists("data"):
            os.mkdir("data")
        if not os.path.exists("data/settings"):
            os.mkdir("data/settings")
        if not os.path.isfile(dir):
            prefix = getPrefix(self.bot, ctx.message)
        else:
            with open(dir, 'r') as r:
                data = json.load(r)
                prefix = str(data["prefix"])
        choice = "123"
        choice = random.choice(choice)
        message = ctx.message.content.strip()
        message = message.lower()
        message = message.replace("eightball ", "")
        message = message.replace(prefix, "")
        length = int(len(message))
        if length < 6:
            await self.bot.say("You didn't ask a question")
        else:
            if choice == "1":
                minichoice = random.randint(1, 10)
                if minichoice == 1:
                    await self.bot.send_message(channel, "It is certain")
                if minichoice == 2:
                    await self.bot.send_message(channel, "It is decidedly so")
                if minichoice == 3:
                    await self.bot.send_message(channel, "Without a doubt")
                if minichoice == 4:
                    await self.bot.send_message(channel, "Yes, definitely")
                if minichoice == 5:
                    await self.bot.send_message(channel, "You may rely on it")
                if minichoice == 6:
                    await self.bot.send_message(channel, "As I see it, yes")
                if minichoice == 7:
                    await self.bot.send_message(channel, "Most likely")
                if minichoice == 8:
                    await self.bot.send_message(channel, "Outlook good")
                if minichoice == 9:
                    await self.bot.send_message(channel, "Yes")
                if minichoice == 10:
                    await self.bot.send_message(channel, "Signs point to yes")
            if choice == "2":
                minichoice = random.randint(1, 5)
                if minichoice == 1:
                    await self.bot.send_message(channel, "Reply hazy try again")
                if minichoice == 2:
                    await self.bot.send_message(channel, "Ask again later")
                if minichoice == 3:
                    await self.bot.send_message(channel, "Better not tell you now")
                if minichoice == 4:
                    await self.bot.send_message(channel, "Cannot predict now")
                if minichoice == 5:
                    await self.bot.send_message(channel, "Concentrate and ask again")
            if choice == "3":
                minichoice = random.randint(1, 5)
                if minichoice == 1:
                    await self.bot.send_message(channel, "Don't count on it")
                if minichoice == 2:
                    await self.bot.send_message(channel, "My reply is no")
                if minichoice == 3:
                    await self.bot.send_message(channel, "My sources say no")
                if minichoice == 4:
                    await self.bot.send_message(channel, "Outlook not so good")
                if minichoice == 5:
                    await self.bot.send_message(channel, "Very doubtful")

    @commands.command(pass_context = True)
    async def qr(self, ctx, *args):
        """Converts text to QR code"""
        text = '{}'.format(' '.join(args)) 
        text = str(text)
        text = text.replace(",", "/")
        text = text.replace(" ", "_")
        url = ("https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={}".format(text))
        if text:
            em = discord.Embed(type="rich", colour=0x260068)
            em.set_author(name="QR Code")
            em.set_image(url=url)
            await self.bot.say(embed=em)
            await self.bot.delete_message(ctx.message)
        else:
            await self.bot.say("No text inserted")
            await self.bot.delete_message(ctx.message)

    @commands.command(pass_context = True)
    async def quote(self, ctx):
        """ A random quote"""
        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            async with session.get('https://talaikis.com/api/quotes/random/') as r:
                if r.status == 200:
                    js = await r.json()
                    em = discord.Embed(colour=0x7EC0EE)
                    em.set_author(name=js['quote'])
                    em.set_footer(text=js['author'])
                    await self.bot.say(embed=em)

    @commands.command(pass_context=True)
    async def chuck(self, ctx):
        """Sends a random Chuck Norris joke"""
        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            async with session.get('https://api.chucknorris.io/jokes/random') as r:
                if r.status ==200:
                    js = await r.json()
                    em = discord.Embed(colour=0x7EC0EE)
                    em.set_author(name=js['value'], icon_url=js['icon_url'])
                    await self.bot.say(embed = em)

    @commands.command(pass_context=True)
    async def simpson(self, ctx):
        """Sends a random Simpsons joke"""
        async with aiohttp.ClientSession(loop=self.bot.loop) as session:
            async with session.get('https://thesimpsonsquoteapi.glitch.me/quotes') as r:
                if r.status ==200: 
                    js = await r.json()
                    em = discord.Embed(colour=0x7EC0EE)
                    em.set_author(name=js[0]['quote'])
                    em.set_thumbnail(url=js[0]['image'])
                    em.set_footer(text=js[0]['character'])
                    await self.bot.say(embed = em)