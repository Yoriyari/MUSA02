#===============================================================================
# Video v1.0.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 05 May 2024 - v1.0.1; Reworked help message import. Added error handling. -YY
# 06 Oct 2022 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# video.py allows users to search for a YouTube video.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands, tasks

from common.error_message import send_error
from common.help_message import send_help

import urllib.parse, urllib.request
import re

def search_video(query):
    if len(query) <= 0:
        raise ValueError("Empty query provided.")
    search_string = urllib.parse.urlencode({"search_query": query})
    page_content = urllib.request.urlopen(f"http://www.youtube.com/results?{search_string}")
    search_results = re.findall(r"/watch\?v=(.{11})", page_content.read().decode())
    if len(search_results) <= 0:
        raise RuntimeError("No videos found.")
    return f"http://www.youtube.com/watch?v={search_results[0]}"

#Cog Setup
class Video(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Video cog loaded.")

    #Connect to voice channel
    @commands.group(name="video", aliases=["vid", "youtube", "yt"], case_insensitive=True, invoke_without_command=True)
    async def video(self, ctx, *query):
        try:
            query = " ".join(query)
            result = ""
            try:
                result = search_video(query)
            except Exception as e:
                result = str(e)
            await ctx.channel.send(result)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @video.command(aliases=["info"], case_insensitive=True, invoke_without_command=True)
    async def help(self, ctx):
        try:
            await send_help(ctx.channel.send, "video")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

async def setup(client):
    await client.add_cog(Video(client))
