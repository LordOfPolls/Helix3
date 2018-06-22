import asyncio
import functools
import logging
import math
import pprint
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor

import discord
import youtube_dl
from discord.ext import commands

# loads the bot's logging stuff
log = logging.getLogger(__name__)
if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')


class Song:
    """Song Data class
    Holds all the data for the selected song, including where it was requested"""
    def __init__(self, url, title, channel, server, author,
                 file=None, thumbnail=None, player=None, webURL=None, length=None, msg=None,
                 rating=None, is_live=None, id=None, extractor=None, np=None):
        ### Song data ###
        self.url = url  # url of the video itself (used by player)
        self.webURL = webURL  # url of the youtube page (used by everything else)
        self.length = length  # length of the video
        self.title = title  # title of the video
        self.thumbnail = thumbnail  # thumbnail of the video
        self.file = file  # cache file, not used rn
        self.rating = rating # rating out of 5 of the video based on like:dislike
        self.is_live = is_live # is this a live stream?
        self.id = id # The video ID
        self.source = extractor # where is this video from

        ### Discord Data ###
        self.channel = channel  # channel command was used in
        self.server = server  # server command was used in
        self.invoker = author  # person who asked for the song
        self.player = player  # the audio player itself (the thing that streams music from youtube to discord)
        self.npmessage = msg  # The last added message, used by playlists
        self.lastnp = np  # the last now playing message


class VoiceState:
    """The servers voice state
    Handles the player and the now playing announcements """
    def __init__(self, bot):
        self.current = None  # The current playing song (Class Song)
        self.voice = None  # Discord.VoiceClient
        self.bot = bot  # The bot itself
        self.server = None  # What server this state is for
        self.play_next_song = asyncio.Event()  # take a wild guess
        self.songs = asyncio.Queue()  # The playlist for said server
        self.skip_votes = set()  # A set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())   # The audio player
        self.autoplaylist = open("autoplaylist.txt", "r")   # Unused, ignore me for now ;)
        self.opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }  # yrdl's options
        self.lastnp = None  # The last now playing message
        self.lastaddedmsg = None # The last added message

    def is_playing(self):
        """Is the player active?"""
        if self.voice is None or self.current is None:
            return False  # if there is no voice channel, or no current song

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        """The player"""
        return self.current.player

    def skip(self):
        """Skips the current song"""
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        """Plays the next song"""
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        """The function that handles music playback for the current server
        This basically does all the heavy lifting"""
        while True:
            self.play_next_song.clear()  # each loop, clean up after the last loop
            self.current = await self.songs.get()  # get the current song
            try:
                # Try and create a player
                player = await self.voice.create_ytdl_player(self.current.url, ytdl_options=self.opts,
                                                           after=self.toggle_next)
                self.current.player = player
            except Exception as e:
                fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                await self.bot.send_message(self.current.channel, fmt.format(type(e).__name__, e))
                log.error("Error in addsong:\n{}".format(fmt.format(type(e).__name__, e)))
                return
            player.start()  # start playback
            try:
                await self.announceNowPlaying()  # Try and announce the new song
            except Exception as e:
                log.error(e)
            await self.play_next_song.wait()  # Wait for the next song to be ready

    async def announceNowPlaying(self):
        """Announces the current song in chat"""
        song = self.current
        log.debug("Playing {} in {}".format(song.title, song.server))
        # Create an embed for **FANCY** outputs
        em = discord.Embed(description="Playing **{}** from **{}**".format(song.title, song.invoker),
                           colour=(random.randint(0, 16777215)))
        if song.is_live is None:  # trying to do this with a livestream would be Very bad
            # Make a human readable duration
            sec = int(song.length)
            mins = sec / 60
            sec -= 60 * mins
            em.add_field(name="Duration:", value=str(time.strftime("%M:%S", time.gmtime(int(song.length)))), inline=True)
        if song.rating is not None:  # sometimes youtube doesnt give a rating
            # Basically, as far as im aware, a rating is based on the like:dislike ratio of a video
            # im assuming this was left over from when youtube had a 5* rating system
            em.add_field(name="Rating:", value="%.2f" %song.rating, inline=True)
        em.set_footer(text=song.webURL)  # maybe they want to see the source of the song
        em.set_image(url=song.thumbnail)   # add a thumbnail

        # Ok so the following code cleans up after the last now playing message
        if self.lastnp is None:   # why do this if its the first one we've ever sent
            self.lastnp = await self.bot.send_message(self.current.channel, embed=em)  # send a np message and assign it to the var
        else:
            try:
                data = dict(self.lastnp.embeds[0])   # get the lastnp's embed data
                title = str(data['description']).replace("Playing", "Played").replace("from", "for")
                emB = discord.Embed(description=title, colour=data['color'])
                emB.set_footer(text=str(data['footer']['text']))
                await self.bot.edit_message(self.lastnp, embed=emB)
            except Exception as e:
                log.error(e)
                try:
                    await self.bot.delete_message(self.lastnp)  # if we couldnt edit for whatever reason
                    #just delete it
                except:
                    pass
            self.lastnp = await self.bot.send_message(self.current.channel, embed=em)

class Music:
    """Voice related commands.
    Works in multiple servers at once.
    """
    def __init__(self, bot, perms):
        self.bot = bot  # the bot
        self.voice_states = {}  # all the active voice states
        self.perms = perms  # deprecated. do an ignore
        self.opts = {
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }  # ytdl options
        self.thread_pool = ThreadPoolExecutor(max_workers=2)  # threading stuff. shhhh

    def __unload(self):
        """Called when the cog is unloaded"""
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    #### UTIL FUNCTIONS ####

    def get_voice_state(self, server):
        """"Gets the current voice state for a specified server"""
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    async def addsong(self, songData, ctx=None, playlist=False, totalSongs=None, songsProcessed=None):
        state = self.get_voice_state(songData.server)
        # await self.create_voice_client(ctx.message.author.voice_channel)
        try:
            if totalSongs:
                await self.bot.edit_message(state.lastaddedmsg, '{}/{}\nAdded {}'.format(songsProcessed, totalSongs, songData.title))
            else:
                await self.bot.edit_message(state.lastaddedmsg, 'Added ' + songData.title)
        except Exception as e:
            log.error(e)
            state.lastaddedmsg = await self.bot.send_message(songData.channel, 'Added ' + songData.title)
        await state.songs.put(songData)

    async def async_process_youtube_playlist(self, info, ctx, msg, **meta):
        """
            Processes youtube playlists links from `playlist_url` in a questionable, async fashion.
            :param playlist_url: The playlist url to be cut into individual urls and added to the playlist
            :param meta: Any additional metadata to add to the playlist entry
            :param ytdl: Youtube_dl object created in .play
            :param ctx: context
        """
        data = []  # creating a list simply so i can len() it
        totalSongs = 0   # how many songs are in this playlist
        songsProcessed = 1   # how mnay songs have we processed
        for entry_data in info['entries']:
            totalSongs += 1
            data.append(entry_data)   # so we dont do useless processing
        state = self.get_voice_state(ctx.message.server)  # get the current voice_state
        await self.bot.edit_message(msg, "Processing {} songs :thinking:".format(totalSongs))
        for entry_data in data:
            if entry_data:  # is this data even usable?
                baseurl = info['webpage_url'].split('playlist?list=')[0]
                song_url = baseurl + 'watch?v=%s' % entry_data['id']   # get a useful link instead of the stupid playlist link
                data = await self.extract_info(url=song_url, download=False, process=True)   # get the data of this video
                song = await self.parseSong(data, ctx, msg)   # assign its data to the song class
                await self.addsong(song, ctx, playlist=True, totalSongs=totalSongs, songsProcessed=songsProcessed)  # add it
                songsProcessed += 1
        try:
            await self.bot.edit_message(state.lastaddedmsg, "Added {} songs ^-^".format(totalSongs))
        except:
            pass

    async def async_process_sc_playlist(self, info, ctx, msg):
        """
            Processes soundcloud set and bancdamp album links from `playlist_url` in a questionable, async fashion.
            :param playlist_url: The playlist url to be cut into individual urls and added to the playlist
            :param meta: Any additional metadata to add to the playlist entry
        """
        for entry_data in info['entries']:
            if entry_data:
                data = await self.extract_info(url=entry_data['url'], download=False, process=True)
                songData = Song(url=entry_data['url'], title=data['title'], channel=ctx.message.channel,
                                server=ctx.message.server, author=ctx.message.author, thumbnail=data['thumbnail'],
                                webURL=entry_data['url'], length=data['duration'], msg=msg)

                try:
                    self.addsong(songData)
                except Exception as e:
                    log.error("Error adding entry {}".format(entry_data['id']), exc_info=e)

    async def extract_info(self, *args, **kwargs):
        """
            Runs ytdl.extract_info within a threadpool to avoid blocking the bot's loop
        """
        loop = self.bot.loop  # get the bot's event loop
        ytdl = youtube_dl.YoutubeDL(self.opts)  # get ytdl ready

        # add the ytdl task to the event loop in a seperate thread to avoid blocking
        return await loop.run_in_executor(self.thread_pool, functools.partial(ytdl.extract_info, *args, **kwargs))

    @staticmethod
    async def parseSong(data, ctx, msg):
        """For the sake of better code this is a function. It takes all the data out of youtube_dl's extracted
        info and stores it in the song class"""
        return Song(url=data['url'], title=data['title'], channel=ctx.message.channel,
                   server=ctx.message.server, author=ctx.message.author,
                   thumbnail=data['thumbnail'], webURL=data['webpage_url'], length=data['duration'],
                   msg=msg, id=data['id'], rating=data['average_rating'], is_live=data['is_live'],
                   extractor=data['extractor'])

    #### COMMANDS ###

    @commands.command(pass_context=True, no_pm=True)
    async def spawn(self, ctx):
        """Summons the bot to join your voice channel."""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:  # is the user even in a channel?
            await self.bot.say('You are not in a voice channel.')
            return False
        msg = await self.bot.say('Joining... ``{}``'.format(summoned_channel.name))  # UI
        state = self.get_voice_state(ctx.message.server)  # get the current voice_state
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)  # join the vc
            await self.bot.edit_message(msg, 'Joined... ``{}``'.format(summoned_channel.name))
            log.info('Joined "{}"|"{}"'.format(ctx.message.server, summoned_channel))
        else:
            await state.voice.move_to(summoned_channel)  # move to the new vc if we were already in another
            await self.bot.edit_message(msg, 'Moved to... ``{}``'.format(summoned_channel.name))
            log.info('{} moved me to {}'.format(ctx.message.author, summoned_channel.name))

        return True

    @commands.command(pass_context=True, no_pm=True)
    async def play(self, ctx, *, song:str):
        """Plays a song.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.server)
        ytdl = youtube_dl.YoutubeDL(self.opts)

        if state.voice is None:  # auto spawn if not already in a vc
            success = await ctx.invoke(self.spawn)
            if not success:
                # how on earth did this happen
                return

        state.lastaddedmsg = await self.bot.say("Processing... :confused:")
        regex = re.compile(
            r'^(?:http|ftp)s?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
            r'(?:/?|[/?]\S+)$)', re.IGNORECASE)
        # that magical RE statement is used to check if there is a URL in this link without any real processing
        if not re.match(regex, ctx.message.content.split(" ")[1]):
            # if there is no url
            info = await self.extract_info(url=song, download=False, process=True) # search youtube for the query and add it
            for item in info['entries']:
                song = await self.parseSong(item, ctx, state.lastaddedmsg)
                await self.addsong(song, ctx)
        else:
            song = ctx.message.content.split(" ")[1]  # get the value after the command
            info = await self.extract_info(url=song, download=False, process=False)
            log.debug('Processing {}'.format(info['title']))

            # find the appropriate way to handle the link, be it a youtube video, soundcloud song or playlist
            if info['extractor'] == 'youtube:playlist':
                await self.async_process_youtube_playlist(info=info, channel=ctx.message.channel, author=ctx.message.author, msg=state.lastaddedmsg, ytdl=ytdl, ctx=ctx)
            elif info['extractor'] == 'soundcloud:set':
                await self.async_process_sc_playlist(info, ctx, state.lastaddedmsg)
            elif info['extractor'] == 'soundcloud':
                songData = Song(url=info['url'], title=info['title'], channel=ctx.message.channel,
                                server=ctx.message.server, author=ctx.message.author, thumbnail=info['thumbnail'],
                                webURL=info['webpage_url'], length=info['duration'], msg=state.lastaddedmsg)
                await self.addsong(songData, ctx)
            elif info['extractor'] == 'youtube':
                if info['is_live']:
                    # uh oh we have a live stream
                    await self.bot.edit_message(state.lastaddedmsg, "Sorry live streams dont play properly right now :cry:")
                    return
                else:
                    songData = Song(url=info['url'], title=info['title'], channel=ctx.message.channel,
                                    server=ctx.message.server, author=ctx.message.author, thumbnail=info['thumbnail'],
                                    webURL=info['webpage_url'], length=info['duration'], msg=state.lastaddedmsg)
                await self.addsong(songData, ctx)
            else:
                await self.bot.edit_message(state.lastaddedmsg, "Sorry, i cant play that yet :cry:")

    @commands.command(pass_context=True, no_pm=True)
    async def volume(self, ctx):
        """Sets the volume of the currently playing song."""
        state = self.get_voice_state(ctx.message.server)
        player = state.player

        value = ctx.message.content.strip()
        value = value.split(" ")
        if len(value) == 1:
            await self.bot.say("Im playing at ``{:.0%}`` volume".format(player.volume))
        else:

            try:
                value = int(value[1])
            except:

                # if value[0][0] in '+-':
                #     new_volume = value[0]
                #     new_volume += (player.volume * 100)
                #     if 0 < new_volume <= 100:
                #         player.volume = new_volume / 100.0
                # else:
                await self.bot.say("Thats not a number now is it, {}".format(ctx.message.author.display_name))
                return
            if value > 100:
                await self.bot.say("no")
                return
            if state.is_playing():

                player.volume = value / 100
                await self.bot.say('Set the volume to {:.0%}'.format(player.volume))

    @commands.command(pass_context=True, no_pm=True)
    async def pause(self, ctx):
        """Pauses the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.pause()
            await self.bot.say(":pause_button: ")
        else:
            await self.bot.say("But im not playing anything Dx")

    @commands.command(pass_context=True, no_pm=True)
    async def resume(self, ctx):
        """Resumes the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()
            await self.bot.say(":arrow_forward:")
        else:
            await self.bot.say("But im not playing anything Dx")

    @commands.command(pass_context=True, no_pm=True)
    async def stop(self, ctx):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()
            state.songs._queue.clear()
            state.songs._finished.set()
            state.songs._unfinished_tasks =0
            await self.bot.say(":stop_button:")

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

    @commands.command(pass_context=True, no_pm=True)
    async def clear(self, ctx):
        """Clears the current playlist"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            if not state.songs.empty():
                state.songs._queue.clear()
                await self.bot.send_message(ctx.message.channel, ":thumbsup:")
            else:
                await self.bot.send_message(ctx.message.channel, "There are no songs to clear :confused:")
        else:
            await self.bot.send_message(ctx.message.channel, "But im not playing anything :confused:")


    @commands.command(pass_context=True, no_pm=True)
    async def playlist(self, ctx):
        """Lists the current playlist"""
        unlisted = 0
        discord_char_limit = 2000
        state = self.get_voice_state(ctx.message.server)
        queue = state.songs
        songs = list(queue._queue)
        andmoretext = '*... and xxxxxxxxxx more*'
        await self.bot.send_message(ctx.message.channel, "There are {} songs in the queue".format(len(songs)))
        lines = []
        lines.append("Currently Playing: **{}** added by **{}**\n".format(state.current.title, state.current.invoker.name))
        for song in songs:
            newline = '`{}.` **{}** added by **{}**'.format(len(lines), song.title, song.invoker.name).strip()

            linesSum = sum(len(x) + 4 for x in lines)  # +3 is for newline chars
            if linesSum + len(newline) + len(andmoretext) > discord_char_limit:
                if linesSum + len(andmoretext):
                    unlisted += 1
            else:
                lines.append(newline)
        if unlisted != 0:
            lines.append(andmoretext.replace("xxxxxxxxxx", str(unlisted)))
        message = str('\n'.join(lines))
        em = discord.Embed(description=message, colour=(random.randint(0, 16777215)))
        em.set_author(name='Playlist:',
                      icon_url=self.bot.user.avatar_url)
        await self.bot.send_message(ctx.message.channel, embed=em)

    @commands.command(pass_context=True, no_pm=True)
    async def skip(self, ctx):
        """Vote to skip a song. The song requester can automatically skip.
        skip votes are needed for the song to be skipped.
        """
        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('But im not playing anything ;-;')
            return
        voter = ctx.message.author
        if voter.id in ['174918559539920897']: # placeholder dev override until perms system finished
            await self.bot.say('``Dev Override``:track_next:')
            state.skip()
        elif voter == state.current.invoker:
            await self.bot.say(':track_next:')
            state.skip()
        elif voter.id not in state.skip_votes:
            numInChannel = sum(1 for m in state.voice.channel.voice_members if not(
                m.deaf or m.self_deaf or m.bot
            ))
            required_votes = math.floor(0.5 * numInChannel)
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= required_votes:
                await self.bot.say(':track_next:')
                state.skip()
            else:
                await self.bot.say('Skip vote: [{}/{}]'.format(total_votes, required_votes))
        else:
            await self.bot.say('Now now, you cant vote twice :P')

    @commands.command(pass_context=True, no_pm=True)
    async def np(self, ctx):
        """Shows info about the currently played song."""
        state = self.get_voice_state(ctx.message.server)
        song = state.current
        if state.current is None:
            await self.bot.say('Not playing anything.')
        else:
            thumbnail = state.player.url
            thumbnail = thumbnail.replace("www.", "")
            thumbnail = thumbnail.replace("https://youtube.com/watch?v=", "http://img.youtube.com/vi/")
            thumbnail = thumbnail + "/mqdefault.jpg"
            em = discord.Embed(description="**"+state.current.title+"**",
                               colour=(random.randint(0, 16777215)))
            em.set_footer(text=song.webURL)
            em.set_image(url=song.thumbnail)
            await self.bot.send_message(ctx.message.channel, embed=em)

    async def on_voice_state_update(self, before, after):
        """Event to handle voice changes"""
        if after is None:
            return
        if after.server.id not in self.voice_states:
            return
        state = self.get_voice_state(after.server)
        if not state.is_playing():
            return
        if before.mute != after.mute:
            if after.mute and state.is_playing:
                log.debug("I was muted in {}".format(after.server.name))
                state.player.pause()
                await self.bot.send_message(state.current.channel, "... Whyd you mute me :cry:")
            elif not after.mute and state.is_playing:
                log.debug("I was unmuted in {}".format(after.server.name))
                state.player.resume()
                await self.bot.send_message(state.current.channel, "YAY! i can sing again :notes:")
        try:
            membersInChannel = sum(1 for m in state.voice.channel.voice_members if not(
                m.deaf or m.self_deaf or m.bot))
        except:
            return
        if membersInChannel == 0 and state.is_playing:
            log.debug("Bot alone in {}, pausing".format(state.current.server))
            await self.bot.send_message(state.current.channel, "Im all alone, with noone here besiiiiide me")
            state.player.pause()
        if membersInChannel >= 1 and state.is_playing:
            await asyncio.sleep(2) # gives the user time to join
            state.player.resume()






