import asyncio
import functools
import logging
import math
import os
import pickle
import pprint
import random
import re
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
import warnings
import discord
import youtube_dl
from PIL import Image
from discord.ext import commands

import code.Perms as Perms
Perms = Perms.Perms
log = logging.getLogger(__name__)
if not discord.opus.is_loaded():
    discord.opus.load_opus('opus')


class Song:
    """Song Data Class
    All the data for the song in question"""
    def __init__(self, url, title, channel, server, author, file=None, thumbnail=None, webURL=None, duration=None,
                 invokeMSG=None, rating=None, is_live=False, id=None, extractor=None, lastnp=None):
        # Song Data -- required
        self.author = author  # The person who requested the song
        self.channel = channel  # The channel it was requested in
        self.server = server  # The server it was requested in
        self.title = title  # The title of the song
        self.url = url  # The url of the video stream

        # Song Data -- Optional
        self.duration = duration  # The duration of the song
        self.extractor = extractor  # The extractor of the video
        self.file = file  # The file of the video, if applicable
        self.id = id  # The id of video, if applicable
        self.invokeMSG = invokeMSG  # The message that invoked the command
        self.is_live = is_live  # Is the video live?
        self.lastNP = lastnp  # The last "now playing" message
        self.rating = rating  # The rating of the video, if applicable
        self.thumbnail = thumbnail  # The videos thumbnail
        self.webpageURL = webURL  # The webpage URL of the video
        self.colour = self.__getColour()  # The accent colour of the embed


    def __getColour(self):
        # getting dominant colors
        urllib.request.urlretrieve(self.thumbnail, "{}thumbnail.png".format(self.server.id))
        image = Image.open("{}thumbnail.png".format(self.server.id))

        image = image.resize((150, 150))
        result = image.convert('P', palette=Image.ADAPTIVE, colors=1)
        result.putalpha(1)
        colors = result.getcolors(150 * 150)
        os.unlink("{}thumbnail.png".format(self.server.id))

        for i, col in colors:
            rgb = col[:3]
            hex = '%02x%02x%02x' % (rgb)
            return discord.Colour(int(hex, 16))  # look, switched to UK english just for you. youre welcome


class VoiceState:
    """The servers voice state"""
    def __init__(self, bot, server=None):
        self.audio_player = bot.loop.create_task(self.audio_player_task())  # The audio player
        self.autoplaylist = open("autoplaylist.txt", "r")  # The autoplaylist, not used yet
        self.bot = bot  # The bot itself
        self.current = None  # The current song
        self.lastaddedmsg = None  # The last "add x song" message
        self.lastnp = None  # The last "now playing" message
        self.opts = {  # Youtube_DL options
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': 'data/audio_cache/%(id)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }
        self.play_next_song = asyncio.Event()  # Take a wild guess
        self.server = server  # The server in quesiton
        self.skipVotes = set()  # A set of users who voted
        self.songs = asyncio.Queue()  # The playlist
        self.voice = None  # Discord.VoiceClient

    def is_playing(self):
        """Is the player active?"""
        if self.voice is None or self.current is None:
            return False  # if there is no voice client, or current song
        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        """The player"""
        return self.current.player

    def skip(self):
        """Skips the current song"""
        self.skipVotes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        """Plays the next song"""
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def serialize(self):
        warnings.warn("Not ready", RuntimeWarning)
        try:
            if len(self.songs._queue) == 0:
                return
            dir = "data/{}".format(self.server.id)
            if not os.path.exists(dir):
                os.mkdir(dir)
            pickle.dump(self.songs._queue, open("data/{}/SerializedPlaylist.txt".format(self.server.id), "wb"))
            log.debug("Successfully serialised queue for {}".format(self.server.id))
        except Exception as e:
            log.error("Failed to serialize queue for {}\n{}: {}".format(self.server.id, type(e).__name__, e))

    async def deserialize(self):
        warnings.warn("Not ready", RuntimeWarning)
        try:
            dir = "data/{}".format(self.server.id)
            if not os.path.exists(dir):
                os.mkdir(dir)
            if os.path.isfile("data/{}/SerializedPlaylist.txt".format(self.server.id)):
                songs = pickle.load(open("data/{}/SerializedPlaylist.txt".format(self.server.id), "rb"))
                for song in songs:
                    await Music(self.bot).addsong(song)
                log.debug("Successfully deserialized queue for {}".format(self.server.id))
        except Exception as e:
            log.error("Failed to deserialized queue for {}\n{}: {}".format(self.server.id, type(e).__name__, e))

    async def audio_player_task(self):
        """The function that handles music playback for the current server
        This basically does all the heavy lifting"""
        while True:
            self.current = await self.songs.get()  # get the next song
            try:
                while self.voice==None:
                    await asyncio.sleep(0.01)
                if self.current.file is None:
                    player = await self.voice.create_ytdl_player(self.current.url, ytdl_options=self.opts,
                                                                 after=self.toggle_next)
                else:
                    player = self.voice.create_ffmpeg_player(self.current.file, after=self.toggle_next)
                self.current.player = player
            except Exception as e:
                fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
                await self.bot.send_message(self.current.channel, fmt.format(type(e).__name__, e))
                log.error("Error in audio_player_task:\n{}".format(fmt.format(type(e).__name__, e)))
                return
            player.start()
            try:
                await self.announceNowPlaying()
            except Exception as e:
                fmt = '{}: {}`'
                log.error("Error in announceNowPlaying:\n{}".format(fmt.format(type(e).__name__, e)))
            await self.play_next_song.wait()
            self.play_next_song.clear()
            # await self.serialize()

    async def announceNowPlaying(self):
        """Announces the current song in chat"""
        song = self.current
        log.debug("Playing {} in {}".format(song.title, song.server))
        # Create an embed for **FANCY** outputs
        em = discord.Embed(description="Playing **{}** from **{}**".format(song.title, song.author),
                           colour=song.colour)
        if song.is_live is None:  # trying to do this with a livestream would be Very bad
            # Make a human readable duration
            sec = int(song.duration)
            mins = sec / 60
            sec -= 60 * mins
            em.add_field(name="Duration:", value=str(time.strftime("%M:%S", time.gmtime(int(song.duration)))),
                         inline=True)
        if song.rating is not None:  # sometimes youtube doesnt give a rating
            # Basically, as far as im aware, a rating is based on the like:dislike ratio of a video
            # im assuming this was left over from when youtube had a 5* rating system
            em.add_field(name="Rating:", value="%.2f" % song.rating, inline=True)
        em.set_footer(text=song.webpageURL)  # maybe they want to see the source of the song
        em.set_image(url=song.thumbnail)  # add a thumbnail

        # Ok so the following code cleans up after the last now playing message
        if self.lastnp is None:  # why do this if its the first one we've ever sent
            self.lastnp = await self.bot.send_message(self.current.channel,
                                                      embed=em)  # send a np message and assign it to the var
        else:
            try:
                data = dict(self.lastnp.embeds[0])  # get the lastnp's embed data
                title = str(data['description']).replace("Playing", "Played").replace("from", "for")
                emB = discord.Embed(description=title, colour=data['color'])
                emB.set_footer(text=str(data['footer']['text']))
                await self.bot.edit_message(self.lastnp, embed=emB)
            except Exception as e:
                log.error(e)
                try:
                    await self.bot.delete_message(self.lastnp)  # if we couldnt edit for whatever reason
                    # just delete it
                except:
                    pass
            self.lastnp = await self.bot.send_message(self.current.channel, embed=em)


class Music:
    """Voice related commands"""
    def __init__(self, bot):
        log.debug("Music Loading...")
        self.bot = bot  # the bot
        self.opts = {  # Youtube_DL options
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'webm',
            'preferredcodec': 'webm',
            'outtmpl': 'data/audio_cache/%(id)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': False,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': False,
            'default_search': 'auto',
            'source_address': '0.0.0.0'
        }
        self.thread_pool = ThreadPoolExecutor(max_workers=2)  # threading stuff. shhhh
        self.voice_states = {}  # all the active voice states

    def __unload(self):
        """Called when the cogs are unloaded"""
        log.debug("Unloading Music...")
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    ### UTIL FUNCTIONS ###
    def get_voice_state(self, server):
        """Gets the current voice state for the specified server"""
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot, server=server)
            self.voice_states[server.id] = state
        return state

    async def create_voice_client(self, channel):
        """Creates a voice client and adds it to the voice state"""
        if self.get_voice_state(channel.server) != None:
            log.warning("Create_voice_client called when voice client already exists")
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    async def addsong(self, songData, ctx=None, playlist=False):
        state = self.get_voice_state(songData.server)
        if not playlist:
            try:
                await self.bot.edit_message(state.lastaddedmsg, 'Added ' + songData.title)
            except:
                state.lastaddedmsg = await self.bot.send_message(songData.channel, 'Added ' + songData.title)
        if songData.duration >= 600 and songData.duration <= 1200:
            log.debug("Downloading {} due to length".format(songData.title))
            await self.bot.edit_message(state.lastaddedmsg, "Downloading {} due to length".format(songData.title))
            if not os.path.exists("data/audio_cache"):
                os.mkdir("data/audio_cache")
            song = [songData.webpageURL]
            await self.download(song)
            songData.file = 'data/audio_cache/{0.id}.webm'.format(songData)
            await self.bot.edit_message(state.lastaddedmsg,  'Added {}'.format(songData.title))

        await state.songs.put(songData)
        # await state.serialize()


    async def async_process_youtube_playlist(self, info, ctx, invokeMSG, **meta):
        data = []  # creating a list simply so i can len() it
        totalSongs = 0   # how many songs are in this playlist
        songsProcessed = 1   # how mnay songs have we processed
        for entry_data in info['entries']:
            totalSongs += 1
            data.append(entry_data)   # so we dont do useless processing
        state = self.get_voice_state(ctx.message.server)  # get the current voice_state
        await self.bot.edit_message(invokeMSG, "Processing {} songs :thinking:".format(totalSongs))
        processedSongs =[]
        for entry_data in data:
            if entry_data:  # is this data even usable?
                baseurl = info['webpage_url'].split('playlist?list=')[0]
                song_url = baseurl + 'watch?v=%s' % entry_data['id']   # get a useful link instead of the stupid playlist link
                data = await self.extract_info(url=song_url, download=False, process=True)   # get the data of this video
                processedSongs.append(await self.parseSong(data, ctx, invokeMSG))   # assign its data to the song class
                try:
                    songsProcessed += 1
                except:
                    pass
                if state.songs.qsize() < 5:
                    # so something plays while they wait
                    await self.addsong(processedSongs[0], playlist=True)
                    processedSongs.remove(processedSongs[0])

        for song in processedSongs:
            await self.addsong(song, playlist=True)
        try:
            await self.bot.edit_message(state.lastaddedmsg, "Added {} songs ^-^".format(totalSongs))
        except:
            pass

    async def async_process_sc_playlist(self, info, ctx, invokeMSG):
        data = []  # creating a list simply so i can len() it
        totalSongs = 0  # how many songs are in this playlist
        songsProcessed = 1  # how mnay songs have we processed
        processedSongs = []
        for entry_data in info['entries']:
            totalSongs += 1
            data.append(entry_data)  # so we dont do useless processing
        state = self.get_voice_state(ctx.message.server)  # get the current voice_state

        for entry_data in info['entries']:
            if entry_data:
                data = await self.extract_info(url=entry_data['url'], download=False, process=True)
                processedSongs.append(Song(url=entry_data['url'], title=data['title'], channel=ctx.message.channel,
                                server=ctx.message.server, author=ctx.message.author, thumbnail=data['thumbnail'],
                                webURL=entry_data['url'], duration=data['duration'], invokeMSG=invokeMSG))

                try:
                    songsProcessed += 1
                except:
                    pass
                if state.songs.qsize() < 5:
                    # so something plays while they wait
                    await self.addsong(processedSongs[0], playlist=True)
                    processedSongs.remove(processedSongs[0])

            for song in processedSongs:
                await self.addsong(song, playlist=True)
            try:
                await self.bot.edit_message(state.lastaddedmsg, "Added {} songs ^-^".format(totalSongs))
            except:
                pass

    async def extract_info(self, *args, **kwargs):
        """
            Runs ytdl.extract_info within a threadpool to avoid blocking the bot's loop
        """
        loop = self.bot.loop  # get the bot's event loop
        ytdl = youtube_dl.YoutubeDL(self.opts)  # get ytdl ready

        # add the ytdl task to the event loop in a seperate thread to avoid blocking
        return await loop.run_in_executor(self.thread_pool, functools.partial(ytdl.extract_info, *args, **kwargs))

    async def download(self, *args, **kwargs):
        loop = self.bot.loop  # get the bot's event loop
        ytdl = youtube_dl.YoutubeDL(self.opts)  # get ytdl ready

        # add the ytdl task to the event loop in a seperate thread to avoid blocking
        return await loop.run_in_executor(self.thread_pool, functools.partial(ytdl.download, *args, **kwargs))

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

    @staticmethod
    async def parseSong(data, ctx, msg):
        """For the sake of better code this is a function. It takes all the data out of youtube_dl's extracted
        info and stores it in the song class"""
        return Song(url=data['url'], title=data['title'], channel=ctx.message.channel,
                    server=ctx.message.server, author=ctx.message.author,
                    thumbnail=data['thumbnail'], webURL=data['webpage_url'], duration=data['duration'],
                    invokeMSG=msg, id=data['id'], rating=data['average_rating'], is_live=data['is_live'],
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
            log.info('Joined "{}"|"{}"'.format(ctx.message.server, summoned_channel.name))
            # await state.deserialize()
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

            if "playlist" in info['extractor'] or "set" in info['extractor']:
                if info['extractor'] == 'youtube:playlist':
                    # try:
                    await self.async_process_youtube_playlist(info=info, channel=ctx.message.channel,
                                                              author=ctx.message.author,
                                                              invokeMSG=state.lastaddedmsg, ytdl=ytdl, ctx=ctx)
                    # except:
                        # await self.bot.send_message(ctx.message.channel, "Sorry, can you send the playlist link instead? :confounded:")
                elif info['extractor'] == 'soundcloud:set':
                    await self.async_process_sc_playlist(info, ctx, state.lastaddedmsg)
            else:
                try:
                    thumbnail = info['thumbnail']
                except:
                    if info['extractor'] == "Newgrounds":
                        thumbnail = "https://goo.gl/bPq9h4"
                    else:
                        thumbnail = "https://png.pngtree.com/element_origin_min_pic/16/07/16/23578a5176bec23.jpg"
                try:
                    rating = info['average_rating']
                except KeyError:
                    rating = None
                try:
                    if info['is_live']:
                        # uh oh we have a live stream
                        await self.bot.edit_message(state.lastaddedmsg, "Sorry live streams dont play properly right now :cry:")
                        return
                except KeyError:
                    pass
                songData = Song(url=info['url'], title=info['title'], channel=ctx.message.channel,
                                server=ctx.message.server, author=ctx.message.author, thumbnail=thumbnail,
                                webURL=info['webpage_url'], duration=info['duration'], invokeMSG=state.lastaddedmsg,
                                rating=rating, id=info['id'])
                await self.addsong(songData, ctx)
                return



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
    async def search(self, ctx):
        """Searches for songs matching your search"""
        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:  # auto spawn if not already in a vc
            success = await ctx.invoke(self.spawn)
            if not success:
                # how on earth did this happen
                return
        replyMSG = await self.bot.send_message(ctx.message.channel, "Searching... :thinking:")
        await self.bot.send_typing(ctx.message.channel)
        search = ctx.message.content.lower()
        search = search.replace(".", "")
        search = search.replace("<@{}>".format(self.bot.user.id), "") # mention
        search = search.replace("<@!{}>".format(self.bot.user.id), "") # mention w/ nickname
        search = search.replace("search", "")
        search = search.strip()
        search = "ytsearch5:" + search
        if search == "":
            await self.bot.edit_message(replyMSG, "Please enter a search query :confused:")
            return
        try:
            info = await self.extract_info(search, download=False, process=True)
        except Exception as e:
            await self.bot.edit_message(replyMSG, "I couldnt find anything due to an error: {}".format(e))
            return

        await self.bot.delete_message(replyMSG)
        replyMSG = await self.bot.send_message(ctx.message.channel, "Found something ^-^")
        for e in info['entries']:
            song = await self.parseSong(e, ctx, state.lastaddedmsg)
            em = discord.Embed(
                description="{}/{}: **{}**".format(info['entries'].index(e) + 1, len(info['entries']), song.title),
                color=song.colour
            )
            if song.is_live is None:
                sec = int(song.duration)
                mins = sec / 60
                sec -= 60 * mins
                em.add_field(name="Duration:", value=str(time.strftime("%M:%S", time.gmtime(int(song.duration)))),
                             inline=True)
            if song.rating is not None:
                em.add_field(name="Rating:", value="%.2f" % song.rating, inline=True)
            em.set_image(url=song.thumbnail)
            em.set_footer(text="y|n|exit")
            await self.bot.edit_message(replyMSG, embed=em)
            reply = None
            reply = await self.bot.wait_for_message(timeout=20, author=ctx.message.author, channel=ctx.message.channel)
            try:
                if not reply:
                    await self.bot.delete_message(replyMSG)
                    await self.bot.send_message(ctx.message.channel, "Why ask for a song if you dont want one :cry:")
                    return
                elif reply.content.lower().startswith('y'):
                    await self.bot.delete_message(replyMSG)
                    await self.bot.delete_message(reply)
                    await self.bot.send_message(ctx.message.channel, "{} searched for {}".format(ctx.message.author.display_name, search.replace("ytsearch5:", "")))
                    await self.addsong(song)
                    return
                elif reply.content.lower().startswith('<@') or reply.content.lower().startswith("."):
                    await self.bot.delete_message(replyMSG)
                    await self.bot.say("Aborting search")
                    return
                elif reply.content.lower().startswith('n'):
                    await self.bot.delete_message(reply)
                elif reply.content.lower().startswith('exit'):
                    await self.bot.delete_message(reply)
                    await self.bot.delete_message(replyMSG)
                    return
            except Exception as e:
                log.error(e)
                await self.bot.delete_message(replyMSG)

        await self.bot.delete_message(replyMSG)
        await self.bot.send_message(ctx.message.channel, "Sorry :cry:")


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
        lines.append("Currently Playing: **{}** added by **{}**\n".format(state.current.title, state.current.author.name))
        for song in songs:
            newline = '`{}.` **{}** added by **{}**'.format(len(lines), song.title, song.author.name).strip()

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
        if Perms.devOnly(ctx):
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
        await state.announceNowPlaying()
