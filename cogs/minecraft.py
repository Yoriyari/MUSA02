#===============================================================================
# Minecraft v2.1.2
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v2.1.2; Hid Discord user IDs from file. Removed server IP
#               declaration and an unused function. -YY
# 06 May 2024 - v2.1.1; Added a help command and error handling. -YY
# 25 Jan 2022 - v2.1; Added checks to see which system the bot is running on,
#               such that the server may launch properly without needing to mix
#               and match files again. -YY
# 21 Aug 2021 - v2.0; Had the bot just DM me to request a server launch instead
#               as the new Raspberry Pi hardware can't run the server well. -YY
# 29 Apr 2020 - v1.0 Finished file. Runs Minecraft through Discord command. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# minecraft.py allows the bot to launch a Minecraft server through a Discord
# command. If this server is not available, the bot instead DMs Yori to request
# the server be launched.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.private_ids import discord_id
from common.error_message import send_error
from common.help_message import send_help

import subprocess, sys, os

YORI_ID = discord_id("yori")
IP_ADDRESS = None

#File to use on current system
def get_server_filename():
    if sys.platform in ["linux", "linux2"]:
        return "./minecraft_server.sh"
    if sys.platform in ["win32"]:
        return "minecraft_server.bat"
    return None

#Cog Setup
class Minecraft(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.server_status = False
        self.server_process = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("Minecraft cog loaded.")

    ##Minecraft Server
    @commands.group(name="minecraft", aliases=["mc"], case_insensitive=True, invoke_without_command=True)
    async def minecraft(self, ctx):
        try:
            #No server, DM Yori instead
            if not os.path.exists(get_server_filename()):
                await ctx.channel.send("Current device cannot run the Minecraft server efficiently; DMing Yori to tell him to launch the Minecraft server.")
                yori = await self.client.fetch_user(YORI_ID)
                await yori.send(f"Dude, {ctx.author.name} wants you to launch the Minecraft server.")
                return
            #Stopping server
            if self.server_status:
                self.server_process.stdin.write("stop\n".encode("utf-8"))
                self.server_process.stdin.flush()
                self.server_status = False
                await ctx.channel.send("Stopping Minecraft server.")
                await self.client.change_presence(activity=None)
            #Starting server
            else:
                filename = get_server_filename()
                self.server_process = subprocess.Popen(filename, stdin=subprocess.PIPE)#, stdout=subprocess.PIPE)
                self.server_status = True
                msg = "Launching Minecraft server."
                if IP_ADDRESS:
                    msg += f" IP is `{IP_ADDRESS}`."
                await ctx.channel.send(msg)
                await self.client.change_presence(activity=discord.Game("Minecraft"))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    ##Print IP
    @minecraft.command(aliases=["address"])
    async def ip(self, ctx):
        try:
            if IP_ADDRESS:
                await ctx.channel.send(f"Server IP is `{IP_ADDRESS}`")
            else:
                await ctx.channel.send(f"Server IP is currently unavailable.")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @minecraft.command(aliases=["help", "?", "info", "information", "instructions"])
    async def minecraft_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "minecraft")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    ##Reading from Server Console
    #how

async def setup(client):
    await client.add_cog(Minecraft(client))
