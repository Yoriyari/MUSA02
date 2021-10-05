#===============================================================================
# Voice v2.1
# - Last Updated: 13 Sep 2021
#===============================================================================
# Update History
# ..............................................................................
# 13 Sep 2021 - Added concurrent multi-server support. -YJ
# 01 Sep 2021 - Added non-Youtube play support. -YJ
# 06 Jul 2021 - Finished file. -YJ
#===============================================================================
# Notes
# ..............................................................................
# - Disconnection Listener isn't working. -YJ
# - Allow YouTube searches without being in a voice channel. -YJ
# - Add help message specific to voice commands. -YJ
#===============================================================================
# Description
# ..............................................................................
# voice.py lets users play audio and video files in a Discord voice chat they're
# in, with support for YouTube playlists, text-to-speech, and volume changing.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands, tasks
import os
import subprocess
import urllib.parse, urllib.request, re
import datetime

class ActiveVoiceChannel:
    def __init__(self, parent, vc, vc_client):
        self.parent = parent
        self.vc = vc
        self.vc_client = vc_client
        self.queue = []
        self.volume = 100.0
        self.channel_timer.start()

    #Volume inactivity timer.
    @tasks.loop(hours=1.0, count=2)
    async def volume_timer(self):
        if self.volume_timer.current_loop != 0:
            self.volume = 100.0

    #Channel connection inactivity timer.
    @tasks.loop(hours=3.0, count=2)
    async def channel_timer(self):
        if self.channel_timer.current_loop != 0:
            if self.vc_client.is_playing() or len(self.queue) > 0:
                self.channel_timer.restart()
                return
            await self.vc_client.disconnect()
            self.parent.remove_active_channel(self)

    #Handle clearing variables and stopping timers on disconnect.
    def clear_on_disconnect(self):
        self.channel_timer.stop()
        self.volume_timer.stop()
        self.parent.remove_active_channel(self)

    #Supposed to handle getting force-disconnected but isn't working??
#    @commands.Cog.listener()
#    async def on_voice_state_update(self, member, before, after):
#        if self.parent.client.user == member and after.channel == None:
#            self.clear_on_disconnect()

    def play_audio(self, ctx, audio):
        self.vc_client.play(discord.FFmpegPCMAudio(audio, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn"), after=lambda e: self.play_queue(ctx))

    def play_queue(self, ctx):
        if self.volume_timer.is_running():
            self.volume_timer.restart()
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        if len(self.queue) <= 0:
            return
        if self.queue[0].startswith("http://translate.google.com/translate_tts?client=tw-ob&tl=en&q="):
            self.play_audio(ctx, self.queue[0])
        else:
            command = ["youtube-dl", "-g", f"{self.queue[0]}"]
            p = subprocess.Popen(command, stdout=subprocess.PIPE)
            text = p.stdout.read().splitlines()
            p.wait()
            if len(text) != 0:
                audio = text[-1]
                self.play_audio(ctx, audio)
                self.vc_client.source = discord.PCMVolumeTransformer(self.vc_client.source, volume=self.volume/250)
        del self.queue[0]

    def queue_audio(self, ctx, source):
        self.queue.append(source)
        if self.vc_client.is_playing() == False:
            self.play_queue(ctx)

    async def play(self, ctx, query):
        if len(query) <= 0:
            await ctx.channel.send("You gotta provide a url, like `!play URL`, or search prompt, like `!play SEARCH PROMPT`.")
            return
        url = ""
        if len(query) == 1 and (query[0].count("http://") > 0 or query[0].count("https://") > 0):
            if ((query[0].count("youtube.com/") > 0 or query[0].count("youtu.be/") > 0) and query[0].count("list=") > 0 and query[0].count("watch?v=") == 0) == False:
                url = query[0]
                if self.vc_client.is_playing() == True or len(self.queue) > 0:
                    await ctx.message.add_reaction("⏳")
                else:
                    await ctx.message.add_reaction("👍")
                self.queue_audio(ctx, url)
            else:
                page_content = urllib.request.urlopen(query[0])
                playlist = re.findall(r"/watch\?v=(.{11})", page_content.read().decode())
                if len(playlist) <= 0:
                    await ctx.channel.send("No videos found.")
                    return
                for video_code in playlist:
                    url = "http://www.youtube.com/watch?v=" + video_code
                    self.queue_audio(ctx, url)
                for _ in range(3):
                    del self.queue[-1]
                await ctx.channel.send("Queued YouTube playlist.")
        else:
            search_string = urllib.parse.urlencode({"search_query": query})
            page_content = urllib.request.urlopen("http://www.youtube.com/results?" + search_string)
            search_results = re.findall(r"/watch\?v=(.{11})", page_content.read().decode())
            if len(search_results) <= 0:
                await ctx.channel.send("No videos found.")
                return
            url = "http://www.youtube.com/watch?v=" + search_results[0]
            if self.vc_client.is_playing() == True:
                await ctx.channel.send("Queued " + f"{url}")
            else:
                await ctx.channel.send("Playing " + f"{url}")
            self.queue_audio(ctx, url)
        print(f"{datetime.datetime.now()} - Audio in {self.vc.guild.name} queued for {query} by {ctx.author.name}")


    async def vol(self, ctx, vol):
        if vol == None:
            await ctx.channel.send("Current volume is " + str(self.volume) + "%.")
            return
        if vol.isdigit() == False or float(vol) < 0.0:
            await ctx.channel.send("You gotta provide a volume above 0, like `!vol 100`.")
            return
        self.volume = float(vol)
        if self.vc_client.is_playing() == True:
            self.vc_client.source.volume = self.volume / 250.0
        if self.volume_timer.is_running():
            self.volume_timer.restart()
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        else:
            self.volume_timer.start()
        await ctx.message.add_reaction("👍")
        print(f"{datetime.datetime.now()} - Volume in {self.vc.guild.name} changed to {self.volume}% by {ctx.author.name}.")

    async def say(self, ctx, query):
        if len(query) <= 0:
            await ctx.channel.send("You gotta provide something to say, like `!say SOMETHING`.")
            return
        text = "%20".join(query)
        source = "http://translate.google.com/translate_tts?client=tw-ob&tl=en&q=" + text
        self.queue_audio(ctx, source)
        if self.vc_client.is_playing() == True or len(self.queue) > 0:
            await ctx.message.add_reaction("⏳")
        else:
            await ctx.message.add_reaction("👍")
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        print(f"{datetime.datetime.now()} - Text-to-speech in {self.vc.guild.name} queued for {query} by {ctx.author.name}")

    async def skip(self, ctx, amount):
        if self.vc_client.is_playing() == True:
            self.vc_client.stop()
            if amount != None and amount.isdigit() == True and int(amount) > 1:
                for _ in range(int(amount)-1):
                    if len(self.queue) == 0:
                        return
                    del self.queue[0]
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        print(f"{datetime.datetime.now()} - Skip in {self.vc.guild.name} by {ctx.author.name}")

    async def stop(self, ctx):
        if self.vc_client.is_playing() == True:
            self.queue = []
            self.vc_client.stop()
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        print(f"{datetime.datetime.now()} - Stop in {self.vc.guild.name} by {ctx.author.name}")

    async def pause(self, ctx):
        if self.vc_client.is_playing() == True:
            self.vc_client.pause()
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        print(f"{datetime.datetime.now()} - Pause in {self.vc.guild.name} by {ctx.author.name}")

    async def resume(self, ctx):
        if self.vc_client.is_paused() == True:
            self.vc_client.resume()
        if self.channel_timer.is_running():
            self.channel_timer.restart()
        print(f"{datetime.datetime.now()} - Resume in {self.vc.guild.name} by {ctx.author.name}")

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
        self.active_channels.remove(vc)

    #Connect to voice channel
    @commands.command(aliases=["join", "voice", "vc", "voicechannel", "voicechat", "voice_channel", "voice_chat"], case_insensitive=True, invoke_without_command=True)
    async def connect(self, ctx):
        await self.join_voice_chat(ctx)

    #Disconnect from voice channel
    @commands.command(aliases=["leave", "quit"], case_insensitive=True, invoke_without_command=True)
    async def disconnect(self, ctx):
        await self.leave_voice_chat(ctx)

    #Play audio
    @commands.command(aliases=["p", "youtube", "yt"], case_insensitive=True, invoke_without_command=True)
    async def play(self, ctx, *query):
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
        await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")

    #Change the volume.
    @commands.command(aliases=["vol"], case_insensitive=True, invoke_without_command=True)
    async def volume(self, ctx, vol=None):
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
        await ctx.channel.send("Sorry, I'm connected to multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")

    #Say something in voice chat with Google Translate API
    @commands.command(aliases=["speak"], case_insensitive=True, invoke_without_command=True)
    async def say(self, ctx, *query):
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
        await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")

    #Skip the current song
    @commands.command(aliases=["next"], case_insensitive=True, invoke_without_command=True)
    async def skip(self, ctx, amount=None):
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
        await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")

    #Stop playing audio in voice chat
    @commands.command(aliases=["silence", "quiet", "shutup", "shut_up", "shut"], case_insensitive=True, invoke_without_command=True)
    async def stop(self, ctx):
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
        await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")

    #Pause audio playing in voice chat
    @commands.command(aliases=[], case_insensitive=True, invoke_without_command=True)
    async def pause(self, ctx):
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
        await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")

    #Resume paused audio in voice chat
    @commands.command(aliases=["unpause"], case_insensitive=True, invoke_without_command=True)
    async def resume(self, ctx):
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
        await ctx.channel.send("Sorry, I'm connected to no or multiple voice channels! Can't do sneaky DM stuff when I don't know which channel to affect.")

def setup(client):
    client.add_cog(VoiceCog(client))
