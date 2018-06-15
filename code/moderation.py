import asyncio
import discord
from discord.ext import commands
import code.get as get
import time


class Moderation:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    async def clean(self, ctx):
        """Cleans up all the bot messages"""
        channel = ctx.message.channel
        author = ctx.message.author
        server = ctx.message.server
        message = ctx.message
        prefix = "."

        search_range = 1000
        delete_invokes = True
        delete_all = channel.permissions_for(
            author).manage_messages or "174918559539920897" == author.id

        def is_possible_command_invoke(entry, prefix):
            if entry.content.startswith(prefix):
                return True
            else:
                return False

        def check(message):
            if is_possible_command_invoke(message, prefix) and delete_invokes:
                return delete_all or message.author == author
            return message.author == self.bot.user

        await self.bot.delete_message(ctx.message)
        if channel.permissions_for(server.me).manage_messages:
            deleted = await self.bot.purge_from(channel, check=check, limit=search_range,
                                            before=message)
            await self.bot.say('<@{}>, I cleaned up {} message{}.'.format(author.id, len(deleted), 's' * bool(deleted)))

    @commands.command(pass_context=True, no_pm=True)
    async def apocalypse(self, ctx):
        """Cleans the entire channel"""
        author = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server
        try:
            perms = author.permissions_in(channel)
            for role in author.roles:
                try:
                    if perms.administrator:
                        usage = True
                    else:
                        usage = False
                except:
                    await self.bot.send_message(channel, "Failed to find administrator role")
                    await self.bot.send_message(channel, perms)
        except:
            pass
        if author.id == "174918559539920897":
            usage = True
        if usage == True:
            await self.bot.send_message(channel, "**PURGING**")
            time.sleep(1)
            try:
                await self.bot.purge_from(channel, limit=99999999999999)
            except:
                message = await self.bot.send_message(channel, "Discord attempting to block purge")
                await asyncio.sleep(2)
                await self.send_message(channel, "**OVERRIDING**")
                search_range = 99999999999999
                async for entry in self.bot.logs_from(channel, search_range):
                    await self.bot.delete_message(entry)
            await self.bot.send_message(channel, ":fire:**CHAT PURGED**:fire:")
        else:
            return Response("Fuck off")

    @commands.command(pass_context=True, no_pm=True)
    async def kick(self, ctx, message):
        """Kickes a mentioned user"""
        user_mentions = list(map(ctx.message.server.get_member, ctx.message.raw_mentions))
        for user in user_mentions:
            await self.bot.kick(user)
            await self.bot.say("<@{}>, i kicked <@{}>.".format(ctx.message.author.id, user.id))

    @commands.command(pass_context=True, no_pm=True)
    async def ban(self, ctx, message):
        """Bans a mentioned user"""
        user_mentions = list(map(ctx.message.server.get_member, ctx.message.raw_mentions))
        for user in user_mentions:
            await self.bot.ban(user)
            await self.bot.say("<@{}>, I banned <@{}>.".format(ctx.message.author.id, user.id))
