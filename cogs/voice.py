#===============================================================================
# Voice v1.6.4
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 20 Mar 2025 - v1.6.4; Made strings with escape characters raw strings. -YY
# 17 Dec 2024 - v1.6.3; Removed hardcoded "Musa" reading due to Google API
#               update. -YY
# 04 Apr 2024 - v1.6.2; Hardcoded "Neon | Monochrome" to be read as "Neon" until
#               I perform the name customization rework. Also coded !bind TTS to
#               ignore backquotes from code blocks. -YY
# 27 Jul 2023 - v1.6.1; Made loop feature announce whether it was toggled ON or
#               OFF. Now removing songs after playback instead of at the start
#               in order to include currently playing song when enabling loop.
#               Note: Moving entries to the end of queue to form a "loop" still
#               causes undesired behaviour as something may get queued after the
#               first song of a playlist ended, appending it in the middle of
#               the 2nd iteration of that playlist. Queue rework is needed. -YY
# 06 Jul 2023 - v1.6.0; Added loop feature. Currently only loops if toggled
#               before starting the song, instead of before ending it. -YY
# 05 Jul 2023 - v1.5.6; Updated to yt-dlp. This fixes the latest YouTube update
#               incompatability and allows for some age-restricted videos. -YY
# 02 Mar 2023 - v1.5.5; Workaround for yt-dl main branch not working. -YY
# 06 Nov 2022 - v1.5.4; Reads Ylva and Anoeskas correctly and ignores ID numbers
#               in custom emoji and replaces ID numbers in mentions. -YY
# 01 Nov 2022 - v1.5.3; Reads Jamy and Musa correctly now. -YY
# 23 Oct 2022 - v1.5.2; Reads :3 as catface and ignores links during Bind. -YY
# 22 Oct 2022 - v1.5.1; Reads nickname instead of username and ignores any bot
#               messages. -YY
# 21 Oct 2022 - v1.5.0; Say command: Now supports messages over 200 characters
#               by splitting TTS queries at logical points in the sentence.
#               Added Bind command to bind Say to all messages in a channel
#               until Unbind command is used. -YY
# 06 Oct 2022 - v1.4.0; Added Spotify "support" by looking up songs on YouTube.
#               Added shuffle feature. -YY
# 16 Apr 2022 - v1.3.0; Say command: Added error message for messages over 200
#               characters. -YY
# 13 Sep 2021 - v1.2.0; Added concurrent multi-server support. -YY
# 01 Sep 2021 - v1.1.0; Added non-Youtube play support. -YY
# 06 Jul 2021 - v1.0.0; Finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Split file into multiple to make reloading specific features easier. -YY
# - Paired quote marks without pair break Discord commands, so phrases like
#   "!say it’s" don't work properly. I think this is a Discord API limitation
#   and not something I can fix. -YY
# - Hardcode TTS: "cya". -YY
# - Add Bandcamp playlist compatability. -YY
# - Disconnection Listener isn't working. -YY
# - Do we need a separate check for an admin moving MUSA between channels? -YY
# - Would love to have an error message for video fetching errors that currently
#   pass silently. Requires queue rework. -YY
# - Include currently playing video in new loop feature. -YY
# - Give more feedback for current state of new loop feature. -YY
# - Add more TTS voices. -YY
# - Rework queue. Add extra information to each queue element.
#   Track who queued something, and in what channel.
#   Allow users to view queue at any time.
#   Don't remove queue elements at start of playback, do it at the end instead,
#   to allow looping and timemark interruptions.
#   Add playback starting timemark for interruptions and timeskips. -YY
# - Allow users to play videos from a certain timemark. -YY
# - Allow text-to-speech to interrupt videos and then resume videos. -YY
# - Allow users to save their own playlists for future playback. -YY
# - Expand TTS binding: personal bind in addition to channel-wide bind.
#   Add whitelist and blacklist of specific users to bind.
#   Allow messages prefixed with specific characters to be ignored.
#   Allow users to customize what their name is read as, which takes priority
#   over their display name if set. -YY
# - Allow users to browse to subsequent query results when searching for a
#   YouTube video without link, which interrupts/removes the original query
#   result in favour of the next one. -YY
# - Maybe add a !prev command to go to previous songs? Would have to keep things
#   in the queue for that. -YY
# - Fix random connectino hiccup instant disconnect/reconnect which fucks with
#   active playback. -YY
# - Add an Embed interface with new queued videos which also details the current
#   state of volume, loop, queue size, etc. -YY
# - Replace YT Playlist compatability with yt-dlp's playlist -g function. -YY
# - Investigate under which conditions VoiceChannels are removed from the list,
#   maybe they're automatically deleted under some conditions such that
#   list.remove(x) isn't needed? -YY
# - Add a check for when Musa is in only one voice chat to make sure users are
#   not unwittingly queuing up songs in a server they're not in nor can see. -YY
# - Better feedback for errors, e.g. HTTP 403 codes. -YY
#===============================================================================
# Description
# ..............................................................................
# voice.py lets users play audio and video files in a Discord voice chat they're
# in, with support for YouTube playlists, text-to-speech, and volume changing.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands, tasks

from cogs.video import search_video
from common.prefix import get_prefix_of_guild

import random
import math
import os
import subprocess
import urllib.parse, urllib.request
import re
import datetime
import nacl

class ActiveVoiceChannel:
    def __init__(self, parent, vc, vc_client):
        self.parent = parent
        self.vc = vc
        self.vc_client = vc_client
        self.queue = []
        self.volume = 100.0
        self.bound_text_channels = []
        self.loop = False
        self.channel_timer.start()

    #Volume inactivity timer.
    @tasks.loop(hours=1.0, count=2)
    async def volume_timer(self):
        if self.volume_timer.current_loop != 0:
            self.volume = 100.0

    #Channel connection inactivity timer.
    @tasks.loop(hours=2.0, count=2)
    async def channel_timer(self):
        try:
            if self.channel_timer.current_loop != 0:
                if self.vc_client.is_playing() or len(self.queue) > 0:
                    self.channel_timer.restart()
                    return
                await self.vc_client.disconnect()
                self.parent.remove_active_channel(self)
        except Exception as e:
            print(e) #Whatever!!!!!!!!

    #Handle clearing variables and stopping timers on disconnect.
    def clear_on_disconnect(self):
        self.volume_timer.stop()
        self.channel_timer.stop()
        self.parent.remove_active_channel(self)

    #Supposed to handle getting force-disconnected but doesn't even sense the on_voice_state_update trigger
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print("! - State Update Detected")
        if self.parent.client.user.id == member.id and after.channel == None:
            self.clear_on_disconnect()
            print("Force-disconnected.")

    def play_audio(self, audio):
        self.vc_client.play(discord.FFmpegPCMAudio(audio, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn"), after=lambda e: self.after_play())

    def after_play(self):
        url = self.queue.pop(0)
        if self.loop and not url.startswith("http://translate.google.com/translate_tts?client=tw-ob&tl=en&q="):
            self.queue.append(url)
        self.play_queue()

    def play_queue(self):
        try:
            if self.volume_timer.is_running():
                self.volume_timer.restart()
            if self.channel_timer.is_running():
                self.channel_timer.restart()
            if len(self.queue) <= 0:
                return
            url = self.queue[0]
            if url.startswith("http://translate.google.com/translate_tts?client=tw-ob&tl=en&q="):
                self.play_audio(url)
            else:
                if url.startswith("https://open.spotify.com/track/"):
                    try:
                        title_desc = self.get_spotify_title_and_desc_from_track(url)
                        url = search_video(title_desc)
                    except Exception as e:
                        print(e)
                        self.play_queue()
                command = ["yt-dlp", "-g", "-x", f"{url}"]
                p = subprocess.Popen(command, stdout=subprocess.PIPE)
                text = p.stdout.read().splitlines()
                p.wait()
                if len(text) != 0:
                    audio = text[-1]
                    self.play_audio(audio)
                    self.vc_client.source = discord.PCMVolumeTransformer(self.vc_client.source, volume=self.volume/250)
        except Exception as e:
            print(e)

    def queue_audio(self, source):
        self.queue.append(source)
        if self.vc_client.is_playing() == False:
            self.play_queue()

    def get_spotify_title_and_desc_from_track(self, url):
        page_content = urllib.request.urlopen(url).read().decode()
        title_start = re.search('<meta property="og:title" content="', page_content)
        desc_start = re.search('<meta property="og:description" content="', page_content)
        if title_start == None or desc_start == None:
            raise RuntimeError("Spotify data could not be parsed.")
        title_start = title_start.span()[1]
        title_end = title_start + page_content[title_start:].find('"/>')
        title = page_content[title_start:title_end]
        desc_start = desc_start.span()[1]
        desc_end = desc_start + page_content[desc_start:].find('"/>')
        desc = page_content[desc_start:desc_end]
        return f"{title} {desc}"

    def get_spotify_tracks_from_playlist(self, url):
        page_content = urllib.request.urlopen(url).read().decode()
        playlist = re.findall(r"https://open\.spotify\.com/track/.{22}", page_content)
        if len(playlist) < 60:
            half = math.floor(len(playlist)/2)
            playlist = playlist[half:]
        else:
            playlist = playlist[30:]
        return playlist

    def split_text_at_symbol(self, text_list, index, symbol):
        texts = []
        for text in text_list[:index]:
            texts.append(text)
        splits = text_list[index].split(symbol)
        for split in splits:
            texts.append(split)
        for text in text_list[index+1:]:
            texts.append(text)
        return texts

    def split_text_at_space_before_nth_character(self, text_list, index, n):
        texts = []
        for text in text_list[:index]:
            texts.append(text)
        words = text_list[index].split(" ")
        sentences = []
        sentence = ""
        space = 0
        for word in words:
            if len(sentence)+space+len(word) > n and sentence != "":
                sentences.append(sentence)
                sentence = ""
                space = 0
            if space == 1:
                sentence += " "
            else:
                space = 1
            sentence += word
        sentences.append(sentence)
        for sentence in sentences:
            texts.append(sentence)
        for text in text_list[index+1:]:
            texts.append(text)
        return texts

    def split_text_at_nth_character(self, text_list, index, n):
        texts = []
        for text in text_list[:index]:
            texts.append(text)
        text = text_list[index]
        for i in range(0, len(text), n):
            if i+n > len(text):
                texts.append(text[i:len(text)])
            else:
                texts.append(text[i:i+n])
        for text in text_list[index+1:]:
            texts.append(text)
        return texts

    def match_word(self, word, full_text):
        #Returns a Match object of the first occurrence of a word, with surrounding whitespace or punctuation, or None
        return re.search(f"(^{word}$)|(^{word}[.,!?\\s])|([.,!?\\s]{word}$)|([.,!?\\s]{word}[.,!?\\s])", full_text)

    def hardcode_readings(self, full_text):
        full_text = full_text.lower()
        replacements = [(":3", "🐱"), ("jamy", "jami"), ("ylva", "yulva"), ("anoeskas", "anooskas"), ("ona", "ohna"), ("neon \\| monochrome", "neon")]
        for replacement in replacements:
            old, new = replacement
            match = self.match_word(old, full_text)
            while match != None:
                fix = re.sub(old, new, match.group())
                start, end = match.span()
                full_text = full_text[:start] + fix + full_text[end:]
                match = self.match_word(old, full_text)
        return full_text

    def detect_custom_emoji(self, full_text):
        #Returns a Match object of the first occurrence of any custom emoji, or None
        return re.search(r"<a?:\w+:\d+>", full_text)

    def remove_custom_emoji_id_numbers(self, full_text):
        #Removes ID numbers from custom emoji
        match = self.detect_custom_emoji(full_text)
        while match != None:
            fix = re.sub(r"<a?:", "", match.group())
            fix = re.sub(r":\d+>", "", fix)
            start, end = match.span()
            full_text = full_text[:start] + fix + full_text[end:]
            match = self.detect_custom_emoji(full_text)
        return full_text

    def detect_member_mention(self, full_text):
        #Returns a Match object of the first occurrence of a guild member mention, or None
        return re.search(r"<@\d+>", full_text)

    def replace_member_mention_id_numbers(self, full_text):
        #Replaces ID numbers from mentions with the target members' nicknames
        match = self.detect_member_mention(full_text)
        while match != None:
            fix = re.sub("<", "", match.group())
            fix = re.sub(">", "", fix)
            mention_id_match = re.search(r"\d+", match.group())
            if mention_id_match != None:
                mention_id = int(mention_id_match.group())
                mention_member = self.vc.guild.get_member(mention_id)
                if mention_member != None:
                    mention_name = mention_member.display_name
                    fix = re.sub(r"\d+", mention_name, fix)
            start, end = match.span()
            full_text = full_text[:start] + fix + full_text[end:]
            match = self.detect_member_mention(full_text)
        return full_text

    def detect_role_mention(self, full_text):
        #Returns a Match object of the first occurrence of a role mention, or None
        return re.search(r"<@&\d+>", full_text)

    def replace_role_mention_id_numbers(self, full_text):
        #Replaces ID numbers from mentions with the target roles' names
        match = self.detect_role_mention(full_text)
        while match != None:
            fix = re.sub("<@&", "@", match.group())
            fix = re.sub(">", "", fix)
            role_id_match = re.search(r"\d+", match.group())
            if role_id_match != None:
                role_id = int(role_id_match.group())
                role = self.vc.guild.get_role(role_id)
                if role != None:
                    role_name = role.name
                    fix = re.sub(r"\d+", role_name, fix)
            start, end = match.span()
            full_text = full_text[:start] + fix + full_text[end:]
            match = self.detect_role_mention(full_text)
        return full_text

    def remove_id_numbers(self, full_text):
        #Removes ID numbers from custom emoji and mentions
        full_text = self.remove_custom_emoji_id_numbers(full_text)
        full_text = self.replace_member_mention_id_numbers(full_text)
        full_text = self.replace_role_mention_id_numbers(full_text)
        return full_text

    def split_text_at_logical_position(self, full_text, max_chars):
        texts = [full_text]
        index = 0
        while index < len(texts):
            if len(texts[index]) <= 200:
                index += 1
                continue
            for symbol in [".", "!", ":", ";", "?", ","]:
                texts = self.split_text_at_symbol(texts, index, symbol)
                if len(texts[index]) <= 200:
                    break
            if len(texts[index]) > 200:
                texts = self.split_text_at_space_before_nth_character(texts, index, 200)
            if len(texts[index]) > 200:
                texts = self.split_text_at_nth_character(texts, index, 200)
            index += 1
        return texts

    def get_tts_links(self, full_text):
        full_text = self.hardcode_readings(full_text)
        full_text = self.remove_id_numbers(full_text)
        texts = self.split_text_at_logical_position(full_text, 200)
        sources = []
        for text in texts:
            text = urllib.parse.urlencode({"q": text})
            source = f"http://translate.google.com/translate_tts?client=tw-ob&tl=en&{text}"
            sources.append(source)
        return sources

    async def play(self, ctx, query):
        if len(query) <= 0:
            await ctx.channel.send("You gotta provide a url, like `!play URL`, or search prompt, like `!play SEARCH PROMPT`.")
            return
        url = ""
        #Link handling
        if len(query) == 1 and (query[0].count("http://") > 0 or query[0].count("https://") > 0):
            #YouTube handling
            if query[0].count("youtube.com/") > 0 or query[0].count("youtu.be/") > 0:
                #YouTube playlist handling
                if query[0].count("list=") > 0 and query[0].count("watch?v=") == 0:
                    page_content = urllib.request.urlopen(query[0])
                    playlist = re.findall(r"/watch\?v=(.{11})", page_content.read().decode())
                    if len(playlist) <= 0:
                        await ctx.channel.send("No videos found.")
                        return
                    for video_code in playlist:
                        url = f"http://www.youtube.com/watch?v={video_code}"
                        self.queue_audio(url)
                    for _ in range(3):
                        del self.queue[-1]
                    await ctx.channel.send("Queued YouTube playlist.")
                #YouTube single video handling
                else:
                    url = query[0]
                    if self.vc_client.is_playing() == True or len(self.queue) > 0:
                        await ctx.message.add_reaction("⏳")
                    else:
                        await ctx.message.add_reaction("👍")
                    self.queue_audio(url)
            #Spotify handling
            elif query[0].count("spotify.com/") > 0:
                #Spotify single song handling
                if query[0].count("track/") > 0:
                    try:
                        title_desc = self.get_spotify_title_and_desc_from_track(query[0])
                        url = search_video(title_desc)
                        self.queue_audio(url)
                        if self.vc_client.is_playing() == True or len(self.queue) > 0:
                            await ctx.channel.send(f"Queued {url}")
                        else:
                            await ctx.channel.send(f"Playing {url}")
                    except Exception as e:
                        await ctx.channel.send(str(e))
                #Spotify playlist handling
                elif query[0].count("playlist/") > 0:
                    tracks = self.get_spotify_tracks_from_playlist(query[0])
                    for track in tracks:
                        self.queue_audio(track)
                    await ctx.channel.send("Queued Spotify playlist.")
            #Any link other than YouTube or Spotify handling
            else:
                url = query[0]
                if self.vc_client.is_playing() == True or len(self.queue) > 0:
                    await ctx.message.add_reaction("⏳")
                else:
                    await ctx.message.add_reaction("👍")
                self.queue_audio(url)
        #Search handling
        else:
            url = ""
            try:
                url = search_video(query)
            except Exception as e:
                await ctx.channel.send(str(e))
                return
            if self.vc_client.is_playing() == True or len(self.queue) > 0:
                await ctx.channel.send(f"Queued {url}")
            else:
                await ctx.channel.send(f"Playing {url}")
            self.queue_audio(url)
        print(f"{datetime.datetime.now()} - Audio in {self.vc.guild.name} queued for {query} by {ctx.author.name}")

    async def vol(self, ctx, vol):
        if vol == None:
            await ctx.channel.send(f"Current volume is {self.volume}%.")
            return
        if vol.isdigit() == False or float(vol) < 0.0:
            await ctx.channel.send("You gotta provide a volume above 0, like `!vol 100`.")
            return
        if float(vol) < 500.0:
            self.volume = float(vol)
        else:
            self.volume = 500.0
        if self.vc_client.is_playing() == True:
            self.vc_client.source.volume = self.volume / 250.0
        if self.volume_timer.is_running():
            self.volume_timer.restart()
        else:
            self.volume_timer.start()
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        await ctx.message.add_reaction("👍")
        print(f"{datetime.datetime.now()} - Volume in {self.vc.guild.name} changed to {self.volume}% by {ctx.author.name}.")

    async def toggle_loop(self, ctx):
        self.loop = not self.loop
        if self.volume_timer.is_running():
            self.volume_timer.restart()
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        if self.loop:
            await ctx.channel.send("Loop enabled.")
        else:
            await ctx.channel.send("Loop disabled.")
        print(f"{datetime.datetime.now()} - Loop toggled in {self.vc.guild.name} by {ctx.author.name}.")

    async def say(self, ctx, query):
        if len(query) <= 0:
            await ctx.channel.send("You gotta provide something to say, like `!say SOMETHING`.")
            return
        text = " ".join(query)
        sources = self.get_tts_links(text)
        if self.vc_client.is_playing() == True or len(self.queue) > 0:
            await ctx.message.add_reaction("⏳")
        else:
            await ctx.message.add_reaction("👍")
        for source in sources:
            self.queue_audio(source)
        print(f"{datetime.datetime.now()} - Text-to-speech in {self.vc.guild.name} queued for {query} by {ctx.author.name}")

    async def bound_say(self, message):
        #Ignore certain messages
        if message.author.bot or message.guild == None: #Ignore own messages and DMs
            return
        prefixes = get_prefix_of_guild(message.guild) #Don't say commands
        for prefix in prefixes:
            if message.content.startswith(prefix):
                return
        msg = re.sub(r"(https?://\S+)", "", message.content).strip() #Ignore links, get message content
        msg = re.sub("`", "", msg).strip() #Remove backquotes from codeblocks
        channel = message.channel.id
        if channel not in self.bound_text_channels or len(msg) <= 0: #Ignore outside bound channel, ignore empty messages
            return
        #Get message author name
        author = message.author.display_name
        #Submit text-to-speech
        msg = f"{author} says. {msg}"
        sources = self.get_tts_links(msg)
        for source in sources:
            self.queue_audio(source)
        print(f"{datetime.datetime.now()} - Bound text-to-speech in {self.vc.guild.name} queued for {msg} by {ctx.author.name}")

    async def bind(self, ctx):
        channel = ctx.channel.id
        if channel not in self.bound_text_channels:
            self.bound_text_channels.append(channel)
            await ctx.message.add_reaction("👍")
        else:
            await ctx.channel.send("Already bound to this channel. If you want to unbind the channel, use `!unbind`.")
            return
        print(f"{datetime.datetime.now()} - Bind channel {ctx.channel.name} in {self.vc.guild.name} by {ctx.author.name}")

    async def unbind(self, ctx):
        channel = ctx.channel.id
        if channel in self.bound_text_channels:
            self.bound_text_channels.remove(channel)
            await ctx.message.add_reaction("👍")
        else:
            await ctx.channel.send("I don't think I'm bound to this channel.")
            return
        print(f"{datetime.datetime.now()} - Unbind channel {ctx.channel.name} in {self.vc.guild.name} by {ctx.author.name}")

    async def skip(self, ctx, amount):
        if self.vc_client.is_playing() == True:
            if amount != None and amount.isdigit() == True and int(amount) > 1:
                for _ in range(int(amount)-1):
                    if len(self.queue) == 0:
                        return
                    url = self.queue.pop(0)
                    if self.loop and not url.startswith("http://translate.google.com/translate_tts?client=tw-ob&tl=en&q="):
                        self.queue.append(url)
            self.vc_client.stop()
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        await ctx.message.add_reaction("👍")
        print(f"{datetime.datetime.now()} - Skip in {self.vc.guild.name} by {ctx.author.name}")

    async def stop(self, ctx):
        if self.vc_client.is_playing() == True:
            self.queue = []
            self.vc_client.stop()
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        await ctx.message.add_reaction("👍")
        print(f"{datetime.datetime.now()} - Stop in {self.vc.guild.name} by {ctx.author.name}")

    async def pause(self, ctx):
        if self.vc_client.is_playing() == True:
            self.vc_client.pause()
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        await ctx.message.add_reaction("👍")
        print(f"{datetime.datetime.now()} - Pause in {self.vc.guild.name} by {ctx.author.name}")

    async def resume(self, ctx):
        if self.vc_client.is_paused() == True:
            self.vc_client.resume()
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        await ctx.message.add_reaction("👍")
        print(f"{datetime.datetime.now()} - Resume in {self.vc.guild.name} by {ctx.author.name}")

    async def shuffle(self, ctx):
        random.shuffle(self.queue)
        await ctx.message.add_reaction("👍")
        print(f"{datetime.datetime.now()} - Queue shuffled in {self.vc.guild.name} by {ctx.author.name}")

#Cog Setup
class VoiceCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.active_channels = []

    @commands.Cog.listener()
    async def on_ready(self):
        print("Voice cog loaded.")

    #Join a voice channel
    async def join_voice_chat(self, ctx):
        if ctx.guild == None:
            await ctx.channel.send("I cannot join you in a voice channel through DMs.")
            return
        voice = ctx.message.author.voice
        if voice == None:
            await ctx.channel.send("I cannot join you in a voice channel in this server when you aren't in one.")
            return
        for active_vc in self.active_channels:
            if active_vc.vc.guild == ctx.guild:
                await active_vc.vc_client.disconnect()
                active_vc.clear_on_disconnect()
                break
        vc_client = await voice.channel.connect()
        vc = ActiveVoiceChannel(self, voice.channel, vc_client)
        self.active_channels.append(vc)

    #Leave a voice channel
    async def leave_voice_chat(self, ctx):
        for active_vc in self.active_channels:
            if active_vc.vc.guild == ctx.guild:
                await active_vc.vc_client.disconnect()
                active_vc.clear_on_disconnect()
                return

    #Remove an entry from the active voice channels array
    def remove_active_channel(self, vc):
        if vc in self.active_channels:
            self.active_channels.remove(vc)

    #Connect to voice channel
    @commands.command(aliases=["join", "voice", "vc", "voicechannel", "voicechat", "voice_channel", "voice_chat"], case_insensitive=True, invoke_without_command=True)
    async def connect(self, ctx):
        try:
            await self.join_voice_chat(ctx)
        except Exception as e:
            print(e)

    #Disconnect from voice channel
    @commands.command(aliases=["leave", "quit"], case_insensitive=True, invoke_without_command=True)
    async def disconnect(self, ctx):
        try:
            await self.leave_voice_chat(ctx)
        except Exception as e:
            print(e)

    #Play audio
    @commands.command(aliases=["p", "queue"], case_insensitive=True, invoke_without_command=True)
    async def play(self, ctx, *query):
        try:
            if ctx.guild != None:
                if ctx.guild not in [active_vc.vc.guild for active_vc in self.active_channels]:
                    await self.join_voice_chat(ctx)
                for active_vc in self.active_channels:
                    if active_vc.vc.guild == ctx.guild:
                        await active_vc.play(ctx, query)
                        return
            if len(self.active_channels) == 1:
                await self.active_channels[0].play(ctx, query)
                return
            if ctx.guild == None:
                await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")
        except Exception as e:
            print(e)

    #Change the volume.
    @commands.command(aliases=["vol"], case_insensitive=True, invoke_without_command=True)
    async def volume(self, ctx, vol=None):
        try:
            if ctx.guild != None:
                for active_vc in self.active_channels:
                    if active_vc.vc.guild == ctx.guild:
                        await active_vc.vol(ctx, vol)
                        return
                await ctx.channel.send("I don't think I'm in a voice channel here, but volume should be at 100.0% when I join a channel.")
                return
            if len(self.active_channels) == 1:
                await self.active_channels[0].vol(ctx, vol)
                return
            if len(self.active_channels) == 0:
                await ctx.channel.send("I'm not in any voice channels, but volume should be at 100.0% when I join a channel.")
                return
            if ctx.guild == None:
                await ctx.channel.send("Sorry, I'm connected to multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")
        except Exception as e:
            print(e)

    #Say something in voice chat with Google Translate API
    @commands.command(aliases=["speak"], case_insensitive=True, invoke_without_command=True)
    async def say(self, ctx, *query):
        try:
            if ctx.guild != None:
                if ctx.guild not in [active_vc.vc.guild for active_vc in self.active_channels]:
                    await self.join_voice_chat(ctx)
                for active_vc in self.active_channels:
                    if active_vc.vc.guild == ctx.guild:
                        await active_vc.say(ctx, query)
                        return
            if len(self.active_channels) == 1:
                await self.active_channels[0].say(ctx, query)
                return
            if ctx.guild == None:
                await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")
        except Exception as e:
            print(e)

    #Skip the current song
    @commands.command(aliases=["next"], case_insensitive=True, invoke_without_command=True)
    async def skip(self, ctx, amount=None):
        try:
            if ctx.guild != None:
                for active_vc in self.active_channels:
                    if active_vc.vc.guild == ctx.guild:
                        await active_vc.skip(ctx, amount)
                        return
                await ctx.channel.send("I don't think I'm playing anything here.")
                return
            if len(self.active_channels) == 1:
                await self.active_channels[0].skip(ctx, amount)
                return
            if ctx.guild == None:
                await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")
        except Exception as e:
            print(e)

    #Stop playing audio in voice chat
    @commands.command(aliases=["silence", "quiet", "shutup", "shut_up", "shut"], case_insensitive=True, invoke_without_command=True)
    async def stop(self, ctx):
        try:
            if ctx.guild != None:
                for active_vc in self.active_channels:
                    if active_vc.vc.guild == ctx.guild:
                        await active_vc.stop(ctx)
                        return
                await ctx.channel.send("I don't think I'm playing anything here.")
                return
            if len(self.active_channels) == 1:
                await self.active_channels[0].stop(ctx)
                return
            if ctx.guild == None:
                await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")
        except Exception as e:
            print(e)

    #Pause audio playing in voice chat
    @commands.command(aliases=[], case_insensitive=True, invoke_without_command=True)
    async def pause(self, ctx):
        try:
            if ctx.guild != None:
                for active_vc in self.active_channels:
                    if active_vc.vc.guild == ctx.guild:
                        await active_vc.pause(ctx)
                        return
                await ctx.channel.send("I don't think I'm playing anything here.")
                return
            if len(self.active_channels) == 1:
                await self.active_channels[0].pause(ctx)
                return
            if ctx.guild == None:
                await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")
        except Exception as e:
            print(e)

    #Resume paused audio in voice chat
    @commands.command(aliases=["unpause"], case_insensitive=True, invoke_without_command=True)
    async def resume(self, ctx):
        try:
            if ctx.guild != None:
                for active_vc in self.active_channels:
                    if active_vc.vc.guild == ctx.guild:
                        await active_vc.resume(ctx)
                        return
                await ctx.channel.send("I don't think I have anything paused here.")
                return
            if len(self.active_channels) == 1:
                await self.active_channels[0].resume(ctx)
                return
            if ctx.guild == None:
                await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")
        except Exception as e:
            print(e)

    #Shuffle the current queue
    @commands.command(aliases=[], case_insensitive=True, invoke_without_command=True)
    async def shuffle(self, ctx):
        try:
            if ctx.guild != None:
                for active_vc in self.active_channels:
                    if active_vc.vc.guild == ctx.guild:
                        await active_vc.shuffle(ctx)
                        return
                await ctx.channel.send("I don't think I have anything queued here.")
                return
            if len(self.active_channels) == 1:
                await self.active_channels[0].shuffle(ctx)
                return
            if ctx.guild == None:
                await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")
        except Exception as e:
            print(e)

    #Bind say command to all future messages in this channel.
    @commands.command(aliases=[], case_insensitive=True, invoke_without_command=True)
    async def bind(self, ctx):
        try:
            if ctx.guild != None:
                if ctx.guild not in [active_vc.vc.guild for active_vc in self.active_channels]:
                    await self.join_voice_chat(ctx)
                for active_vc in self.active_channels:
                    if active_vc.vc.guild == ctx.guild:
                        await active_vc.bind(ctx)
            else:
                await ctx.channel.send("Bind currently does not support DMs.")
        except Exception as e:
            print(e)

    #Unbind say command from this channel.
    @commands.command(aliases=[], case_insensitive=True, invoke_without_command=True)
    async def unbind(self, ctx):
        try:
            if ctx.guild != None:
                for active_vc in self.active_channels:
                    if active_vc.vc.guild == ctx.guild:
                        await active_vc.unbind(ctx)
                        return
                await ctx.channel.send("I don't think I'm bound to this channel.")
            else:
                await ctx.channel.send("Unbind currently does not support DMs.")
        except Exception as e:
            print(e)

    #Loop the queue.
    @commands.command(aliases=["repeat"], case_insensitive=True, invoke_without_command=True)
    async def loop(self, ctx):
        try:
            if ctx.guild != None:
                for active_vc in self.active_channels:
                    if active_vc.vc.guild == ctx.guild:
                        await active_vc.toggle_loop(ctx)
                        return
                await ctx.channel.send("I don't think I'm playing anything here.")
                return
            if len(self.active_channels) == 1:
                await self.active_channels[0].toggle_loop(ctx, vol)
                return
            if len(self.active_channels) == 0:
                await ctx.channel.send("I don't think I'm playing anything here.")
                return
            if ctx.guild == None:
                await ctx.channel.send("Sorry, I'm connected to multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")
        except Exception as e:
            print(e)

    @commands.command(aliases=["vc_cache"])
    async def voice_cache(self, ctx):
        print(f"vc's: {self.active_channels}")
        for channel in self.active_channels:
            print(f"vc: {channel} - {channel.queue}")

    @commands.Cog.listener()
    async def on_message(self, message): #Bound say
        for active_vc in self.active_channels: #Execute say
            if active_vc.vc.guild == message.guild:
                await active_vc.bound_say(message)

async def setup(client):
    await client.add_cog(VoiceCog(client))
