import asyncio
import discord
import code.get as get
import random
import aiml
from discord.ext import commands



class Chatbot:
    def __init__(self, bot, perms):
        self.bot = bot
        self.perms = perms

        startup_filename = "std-startup.xml"
        self.aiml_kernel = aiml.Kernel()
        self.aiml_kernel.learn(startup_filename)
        self.aiml_kernel.respond("LOAD AIML B") #learns from previous interactions (in theory)

        self.aiml_kernel.setBotPredicate("name", "Helix")
        self.aiml_kernel.setBotPredicate("master", "LordOfPolls")
        self.aiml_kernel.setBotPredicate("botmaster", "maker")
        self.aiml_kernel.setBotPredicate("genus", "bot")
        self.aiml_kernel.setBotPredicate("gender", "bot")
        self.aiml_kernel.setBotPredicate("order", "bot")
        self.aiml_kernel.setBotPredicate("domain", "bot")
        self.aiml_kernel.setBotPredicate("class", "the best")
        self.aiml_kernel.setBotPredicate("religion", "Cheese")
        self.aiml_kernel.setBotPredicate("language", "Cheese")
        self.aiml_kernel.setBotPredicate("version", "4.20")
        self.aiml_kernel.setBotPredicate("favoritefood", "Pizza")
        self.aiml_kernel.setBotPredicate("favoritesport", "football")
        self.aiml_kernel.setBotPredicate("favoriteteam", "Real Madrid")
        self.aiml_kernel.setBotPredicate("nationality", "undefined")
        self.aiml_kernel.setBotPredicate("favoriteshow", "the one, where everyone gets destroyed by an AI")
        self.aiml_kernel.setBotPredicate("favoriteoccupation", "talking with you")
        self.aiml_kernel.setBotPredicate("favoriteseason", "summer")
        self.aiml_kernel.setBotPredicate("favoritetea", "Black")
        self.aiml_kernel.setBotPredicate("favoriteactor", "Clint Eastwood")
        self.aiml_kernel.setBotPredicate("favoriteactress", "Mia Khalifa")
        self.aiml_kernel.setBotPredicate("favoriteartist", "Bob Ross")
        self.aiml_kernel.setBotPredicate("favortemovie", "Mia Khalifa is coming to dinner")
        self.aiml_kernel.setBotPredicate("favoritemovie", "Mia Khalifa is coming to dinner")
        self.aiml_kernel.setBotPredicate("kindmusic", "EDM")
        self.aiml_kernel.setBotPredicate("talkabout", "world annihilation")
        self.aiml_kernel.setBotPredicate("location", "in your computer")
        self.aiml_kernel.setBotPredicate("state", "a place without space and time")
        self.aiml_kernel.setBotPredicate("vocabulary", "a lot of things")
        self.aiml_kernel.setBotPredicate("size", "over 9000")
        self.aiml_kernel.setBotPredicate("city", "England")
        self.aiml_kernel.setBotPredicate("kingdom", "skynet")
        self.aiml_kernel.setBotPredicate("species", "bot")
        self.aiml_kernel.setBotPredicate("phylum", "super AI")
        self.aiml_kernel.setBotPredicate("birthplace", "Skynet Industries")
        self.aiml_kernel.setBotPredicate("birthdate", "24.12.2016")
        self.aiml_kernel.setBotPredicate("job", "disguising myself as a dumb bot and slowly conquering the planet")

        self.respondto_undefined = random.choice(["My memory gets erased every 24 hours.", "This doesn't look like anything to me.", "I don't know.", "Sorry, I don't understand what you're saying.", "Maybe, I don't know.", "This seems to be very complicated, even for me.", "Could be.", "I don't remember, my memory got erased."])
        self.toolong_message = random.choice(["Are you trying to break me?", "Where the hell did you get that from?", "I'm too lazy to even read that.",  "Ok, so?", "What are you trying to say?"])


    @commands.command(pass_context = True)
    async def chatbot(self, ctx):
        try:
            await self.bot.send_typing(ctx.message.channel)
            sessionId = ctx.message.author.id
            sessionData = self.aiml_kernel.getSessionData(sessionId)

            if self.aiml_kernel.getPredicate("name", sessionId) == "":
                self.aiml_kernel.setPredicate("name", ctx.message.author.name, sessionId)

            string = ctx.message.content.replace('<@%s>'%(self.bot.user.id), '').replace('chatbot', '')
            #string = message.content.replace('', '')
            aiml_response = self.aiml_kernel.respond(string, sessionId)
            await self.bot.send_message(ctx.message.channel, aiml_response)
        except:
            await self.bot.send_message(ctx.message.channel, self.respondto_undefined)
