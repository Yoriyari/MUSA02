#===============================================================================
# Prefix v1.1.3
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.1.3; Moved database to secrets folder. -YY
# 11 Aug 2024 - v1.1.2; Fixed missing newline after adding to prefixes. -YY
# 05 May 2024 - v1.1.1; Reworked help message import. Added error handling. -YY
# 17 Apr 2022 - v1.1; Centralized help messages to one importable file. -YY
# 14 Sep 2021 - v1.0; Finished file. -YJ
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# prefix.py allows servers to change their associated prefix. To read prefixes,
# see common/prefix.py.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.error_message import send_error
from common.help_message import send_help

PREFIXES_FILE = "secrets/musa_prefixes.txt"

#Cog Setup
class PrefixCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Report successful load.
    @commands.Cog.listener()
    async def on_ready(self):
        print("Prefix cog loaded.")

    #Primary functions
    #With no arguments specified, send instructions.
    @commands.group(name="prefix", aliases=["prefixes"], case_insensitive=True, invoke_without_command=True)
    async def prefix(self, ctx):
        try:
            await send_help(ctx.channel.send, "prefix")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Change prefix.
    @prefix.command(aliases=["set", "replace", "update", "new"])
    async def change(self, ctx, *prefixes):
        try:
            #With no prefixes specified, send instructions
            if len(prefixes) == 0:
                await ctx.channel.send(help_messages["prefix"])
                return
            #Turn prefix array into unique space-separated strings
            prefix = " ".join(sorted(set(prefixes)))
            #Copy text file
            with open(PREFIXES_FILE, "r") as file:
                lines = file.readlines()
            #Find server in prefix list and change their prefixes
            for i, line in enumerate(lines):
                if i % 2 == 0:
                    if ctx.guild.id == int(line):
                        lines[i+1] = prefix
                        with open(PREFIXES_FILE, "w") as file:
                            file.write("".join(lines))
                        await ctx.channel.send(f"Server prefixes are now: `{'` `'.join(prefix.split())}`")
                        return
            #If server isn't found in prefix list, append it to list
            lines.append(f"\n{ctx.guild.id}\n{prefix}")
            with open(PREFIXES_FILE, "w") as file:
                file.write("".join(lines))
            await ctx.channel.send(f"Server prefixes are now: `{'` `'.join(prefix.split())}`")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Add prefix.
    @prefix.command(aliases=["append"])
    async def add(self, ctx, *prefixes):
        try:
            #With no prefixes specified, send instructions
            if len(prefixes) == 0:
                await ctx.channel.send(help_messages["prefix"])
                return
            #Turn prefix array into unique space-separated strings
            prefix = " ".join(sorted(set(prefixes)))
            #Copy text file
            with open(PREFIXES_FILE, "r") as file:
                lines = file.readlines()
            #Find server in prefix list and change their prefixes
            for i, line in enumerate(lines):
                if i % 2 == 0:
                    if ctx.guild.id == int(line):
                        lines[i+1] = " ".join(sorted(set((lines[i+1] + f" {prefix}").split()))) + "\n"
                        with open(PREFIXES_FILE, "w") as file:
                            file.write("".join(lines))
                        await ctx.channel.send(f"Server prefixes are now: `{'` `'.join(lines[i+1].split())}`")
                        return
            #If server isn't found in prefix list, append it to list
            if "!" not in prefix:
                prefix = "! " + prefix
            lines.append(f"\n{ctx.guild.id}\n{prefix}")
            with open(PREFIXES_FILE, "w") as file:
                file.write("".join(lines))
            await ctx.channel.send(f"Server prefixes are now: `{'` `'.join(prefix.split())}`")
            return
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Help command
    @prefix.command(aliases=["information", "instructions", "help"])
    async def info(self, ctx):
        try:
            await send_help(ctx.channel.send, "prefix")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#Client Setup
async def setup(client):
    await client.add_cog(PrefixCog(client))
