#===============================================================================
# Feed v1.1.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 05 May 2024 - v1.1.1; Reworked help message import. Added error handling. Also
#               added "eat" and "uneat" as aliases. -YY
# 23 Sep 2023 - v1.1; Allowed users to specify what they feed the bot as
#               optional parameter. -YY
# 19 Oct 2022 - v1.0; Started and finished file. Added !feed and !unfeed. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# feed.py parodies that one funny Discord bot image where you can use !feed to
# make the bot go "oh hell yeah a bowl of oats just for me" and !unfeed to make
# it go "what is your problem" or something. Users can specify what they feed
# the bot as optional parameter.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.error_message import send_error
from common.help_message import send_help

import random

#Cog Setup
class Feed(commands.Cog):

    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Feed cog loaded.")

    @commands.group(name="feed", aliases=["eat"], case_insensitive=True, invoke_without_command=True)
    async def feed(self, ctx, *food):
        try:
            if not food:
                options = ["oats", "grains", "hay", "carrots", "sugar cubes", "grass",
                    "fruit", "seeds", "snacks", "food", "nuts", "corn", "whatever bots eat"
                ]
                food = f"A bowl of {random.choice(options)}"
            else:
                food = " ".join(food)
                food = food[0].upper() + food[1:]
            msg = f"Oh hell yeah. {food} just for me."
            await ctx.channel.send(msg)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @feed.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def feed_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "feed")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.group(name="unfeed", aliases=["uneat"], case_insensitive=True, invoke_without_command=True)
    async def unfeed(self, ctx):
        try:
            options = ["<:AngyHorse:1032390502814859305>", "What is your problem?",
                "What the fuck is your problem?", "What the hell is your problem?",
                "What the buck is your problem?", "What's your problem?"
            ]
            msg = random.choice(options)
            await ctx.channel.send(msg)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @unfeed.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def unfeed_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "unfeed")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

async def setup(client):
    await client.add_cog(Feed(client))
