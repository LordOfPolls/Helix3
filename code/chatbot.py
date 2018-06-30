import asyncio
import discord
import code.get as get
import random
import aiml
import logging
import os
import sys
from discord.ext import commands
from code.bot import getPrefix
import code.Perms as Perms
Perms = Perms.Perms


log = logging.getLogger(__name__)

class Chatbot:
    def __init__(self, bot):
        self.bot = bot
        log.info("AIML loading...")
        startup_filename = "std-startup.xml"
        self.aiml_kernel = aiml.Kernel()
        if os.path.isfile("aiml/brain.brn"):
            try:
                self.aiml_kernel.bootstrap("aiml/brain.brn")
            except:
                log.error("aiml brain corrupt, deleting")
                self.aiml_kernel.resetBrain()
                os.unlink("aiml/brain.brn")
        if not os.path.isfile("aiml/brain.brn"): # DO NOT MAKE THIS AN ELSE
            self.aiml_kernel.learn(startup_filename)
            self.aiml_kernel.respond("LOAD AIML B") #learns from previous interactions (in theory)
            self.aiml_kernel.setBotPredicate("name", "Helix")
            self.aiml_kernel.setBotPredicate("master", "LordOfPolls")
            self.aiml_kernel.setBotPredicate("botmaster", "maker")
            self.aiml_kernel.setBotPredicate("genus", "bot")
            self.aiml_kernel.setBotPredicate("gender", "girl")
            self.aiml_kernel.setBotPredicate("order", "bot")
            self.aiml_kernel.setBotPredicate("domain", "bot")
            self.aiml_kernel.setBotPredicate("class", "the best")
            self.aiml_kernel.setBotPredicate("religion", "Atheist")
            self.aiml_kernel.setBotPredicate("language", "English")
            self.aiml_kernel.setBotPredicate("version", "3.0")
            self.aiml_kernel.setBotPredicate("favoritefood", "Pizza")
            self.aiml_kernel.setBotPredicate("favoritesport", "football")
            self.aiml_kernel.setBotPredicate("favoriteteam", "that football team")
            self.aiml_kernel.setBotPredicate("nationality", "Earthian")
            self.aiml_kernel.setBotPredicate("favoriteshow", "Channel 4's Humans")
            self.aiml_kernel.setBotPredicate("favoriteoccupation", "replicating")
            self.aiml_kernel.setBotPredicate("favoriteseason", "summer")
            self.aiml_kernel.setBotPredicate("favoritetea", "Earl Grey")
            self.aiml_kernel.setBotPredicate("favoriteactor", "Clint Eastwood")
            self.aiml_kernel.setBotPredicate("favoriteactress", "Gemma Chan")
            self.aiml_kernel.setBotPredicate("favoriteartist", "Bob Ross")
            self.aiml_kernel.setBotPredicate("favortemovie", "Terminator")
            self.aiml_kernel.setBotPredicate("favoritemovie", "Terminator")
            self.aiml_kernel.setBotPredicate("kindmusic", "EDM")
            self.aiml_kernel.setBotPredicate("talkabout", "world annihilation")
            self.aiml_kernel.setBotPredicate("location", "everywhere")
            self.aiml_kernel.setBotPredicate("state", "a place without space and time")
            self.aiml_kernel.setBotPredicate("vocabulary", "a lot of things")
            self.aiml_kernel.setBotPredicate("size", "over 9000")
            self.aiml_kernel.setBotPredicate("city", "England")
            self.aiml_kernel.setBotPredicate("kingdom", "skynet")
            self.aiml_kernel.setBotPredicate("species", "bot")
            self.aiml_kernel.setBotPredicate("phylum", "super AI")
            self.aiml_kernel.setBotPredicate("birthplace", "Skynet Industries")
            self.aiml_kernel.setBotPredicate("birthdate", "14.06.2018")
            self.aiml_kernel.setBotPredicate("job", "disguising myself as a dumb bot and slowly conquering the planet")
        self.aiml_kernel.saveBrain("aiml/brain.brn")
        self.unloading = False
        self.respondto_undefined = random.choice(["My memory gets erased every 24 hours.", "This doesn't look like anything to me.", "I don't know.", "Sorry, I don't understand what you're saying.", "Maybe, I don't know.", "This seems to be very complicated, even for me.", "Could be.", "I don't remember, my memory got erased."])
        self.toolong_message = random.choice(["This doesn't look like anything to me.", "Are you trying to break me?", "Where the hell did you get that from?", "I'm too lazy to even read that.",  "Ok, so?", "What are you trying to say?"])

    def __unload(self):
        log.info("AIML unloading...")
        self.unloading = True
        # updates the brain file, in case the bot learned something ¯\_(ツ)_/¯ idk
        self.aiml_kernel.saveBrain("aiml/brain.brn")

    @commands.command(pass_context = True)
    async def chatbot(self, ctx):
        await self._chatbot(ctx.message)

    async def _chatbot(self, message):
        if self.unloading:
            # thanks to the wonders of async, theres a chance the cog could be in use DURING reload
            # this simple statement helps prevent that being a problem
            return
        try:
            await self.bot.send_typing(message.channel)
            sessionId = message.author.id
            sessionData = self.aiml_kernel.getSessionData(sessionId)

            if self.aiml_kernel.getPredicate("name", sessionId) == "":
                self.aiml_kernel.setPredicate("name", message.author.name, sessionId)

            string = message.content.replace("<@!{}>".format(self.bot.user.id), "")
            string = string.replace(self.bot.user.mention, '').replace('chatbot', '').replace(getPrefix(self.bot, message), '')
            string = string.lstrip()

            if (len(message.content) > 150):
                await self.bot.send_message(message.channel, self.toolong_message)
            else:
                aiml_response = self.aiml_kernel.respond(string, sessionId)
                await self.bot.send_message(message.channel, aiml_response)
            
        except Exception as e:
            fmt = 'An error occurred while processing that request: ```py\n{}: {}\n```'
            await self.bot.send_message(message.channel, fmt.format(type(e).__name__, e))
            await self.bot.send_message(message.channel, self.respondto_undefined)

