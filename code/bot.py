import asyncio
import discord
import importlib
from discord.ext import commands


bot = commands.Bot(command_prefix=commands.when_mentioned_or('.'), description='Helix3.0', pm_help=True)

class Core:
    def __init__(self, bot):
        self.bot = bot

    def devOnly(ctx):
        return ctx.message.author.id in ["174918559539920897", "269543926803726336", "186295030388883456", "220568440161697792", "155347730225561600", "223814431946178560"]

    @commands.command(pass_context=True)
    async def echo(self, ctx, *args):
        """echos whatever you say"""
        await self.bot.say('{}'.format(' '.join(args)))
        await self.bot.delete_message(ctx.message)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(devOnly)
    async def reload(self, ctx):
        """Reloads the bot's cogs"""
        print("Reloading all cogs")
        msg = await self.bot.say('Reloading cogs')

        await self.bot.edit_message(msg, "Reloading Music")
        self.bot.remove_cog("Music")
        importlib.reload(code.music)
        from code.music import Music
        self.bot.add_cog(Music(bot))
        await self.bot.edit_message(msg, "Reloaded Music")

        await self.bot.edit_message(msg, "Reloading Moderation")
        self.bot.remove_cog("Moderation")
        importlib.reload(code.moderation)
        from code.moderation import Moderation
        self.bot.add_cog(Moderation(bot))
        await self.bot.edit_message(msg, "Reloaded Moderation")

        await self.bot.edit_message(msg, "Reloading Fun")
        self.bot.remove_cog("Fun")
        importlib.reload(code.fun)
        from code.fun import Fun
        self.bot.add_cog(Fun(bot))
        await self.bot.edit_message(msg, "Reloaded Fun")

        await self.bot.say('Reload complete')

    @commands.command(pass_context=True)
    @commands.check(devOnly)
    async def shutdown(self, ctx):
        """Shuts down Helix"""
        print("Shutdown command issued")
        await self.bot.send_message(ctx.message.channel, ":wave:")
        self.bot.remove_cog("Music")
        await self.bot.logout()
        exit()

import code.music
import code.moderation
import code.fun
from code.moderation import Moderation
from code.music import Music
from code.fun import Fun

bot.add_cog(Core(bot))
bot.add_cog(Music(bot))
bot.add_cog(Moderation(bot))
bot.add_cog(Fun(bot))

@bot.event
async def on_ready():
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

bot.run('MzMwOTkxOTk3MzI0MDk5NTg0.DEQQbA.d3D1Am_MTPJXcJVBd1iPxI4qpvQ')
