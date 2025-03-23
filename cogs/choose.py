#===============================================================================
# Choose v1.4.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 06 Dec 2024 - v1.4.1; Added 'flipcoin' as alias. -YY
# 24 Nov 2024 - v1.4; Added reorder feature. -YY
# 05 May 2024 - v1.3.1; Reworked help message import. Added error handling. -YY
# 15 Oct 2023 - v1.3; Fixed help command being checked incorrectly and threw in
#               a shortcut command for coin flips specifically. -YY
# 17 Apr 2022 - v1.2; Centralized help messages to one importable file. Added a
#               help command to this file. -YY
# 25 Jan 2022 - v1.1; Added support for using commas to seperate choices instead
#               of using spaces. -YY
# 03 Mar 2021 - v1.0; Finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# choose.py picks a random option from a list supplied by the user.
# Also includes a coin flip shortcut command.
# Also supports a list/word shuffle feature.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.error_message import send_error
from common.help_message import send_help

import random

#-------------------------------------------------------------------------------
#Cog Setup
class Choose(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Choose cog loaded.")

    #Choose
    @commands.command(name="choose", aliases=["choice","pick"], case_insensitive=True, invoke_without_command=True)
    async def choose(self, ctx, *options):
        try:
            if not options or options in [("help"), ("info")]:
                await send_help(ctx.channel.send, "choose")
                return
            if any(option.endswith(",") for option in options):
                options = " ".join(options)
                options = options.split(", ")
            choice = random.choice(options)
            await ctx.channel.send(choice)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Coinflip
    @commands.group(name="coinflip", aliases=["coin_flip", "coin", "flip", "flipcoin", "flip_coin"], case_insensitive=True, invoke_without_command=True)
    async def coinflip(self, ctx):
        try:
            options = ["Heads.", "Tails."]
            choice = random.choice(options)
            await ctx.channel.send(choice)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @coinflip.command(aliases=["help", "?", "info", "information", "instructions"])
    async def coinflip_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "coinflip")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Rearrange
    @commands.command(name="rearrange", aliases=["reorder"], case_insensitive=True, invoke_without_command=True)
    async def rearrange(self, ctx, *options):
        try:
            if not options or options in [("help"), ("info")]:
                await send_help(ctx.channel.send, "rearrange")
                return
            if any(option.endswith(",") for option in options):
                options = " ".join(options)
                options = options.split(", ")
                random.shuffle(options)
                options = ", ".join(options)
            elif len(options) == 1:
                options = [char for char in options[0]]
                random.shuffle(options)
                options = "".join(options)
            else:
                options = list(options)
                random.shuffle(options)
                options = " ".join(options)
            await ctx.channel.send(options)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#-------------------------------------------------------------------------------
#Add Cog
async def setup(client):
    await client.add_cog(Choose(client))
