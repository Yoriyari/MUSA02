#===============================================================================
# Prefix v1.0
# - Last Updated: 14 Sep 2021
#===============================================================================
# Update History
# ..............................................................................
# 14 Sep 2021 - Finished file. -YJ
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# prefix.py allows servers to change their associated prefix.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

#Cog Setup
class PrefixCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    #Report successful load.
    @commands.Cog.listener()
    async def on_ready(self):
        print("Prefix cog loaded.")

    #Instructions.
    def instructions(self):
        msg = "**Prefix Commands**\n"
        msg += "Servers can have (multiple) custom prefixes.\n"
        msg += "`!prefix change X`: Replace `X` with your desired prefix(es). This will replace the current prefix(es).\n"
        msg += "`!prefix add X`: Replace `X` with your desired prefix(es). This will add to the list of current prefixes."
        return msg

    #Primary functions
    #With no arguments specified, send instructions.
    @commands.group(name="prefix", aliases=["prefixes"], case_insensitive=True, invoke_without_command=True)
    async def prefix(self, ctx):
        await ctx.channel.send(self.instructions())

    #Change prefix.
    @prefix.command(aliases=["replace", "update", "new"])
    async def change(self, ctx, *prefixes):
        #With no prefixes specified, send instructions
        if len(prefixes) == 0:
            await ctx.channel.send(self.instructions())
            return
        #Turn prefix array into unique space-separated strings
        prefix = " ".join(sorted(set(prefixes)))
        #Copy text file
        with open("musa_prefixes.txt", "r") as file:
            lines = file.readlines()
        #Find server in prefix list and change their prefixes
        for i, line in enumerate(lines):
            if i % 2 == 0:
                if ctx.guild.id == int(line):
                    lines[i+1] = prefix
                    with open("musa_prefixes.txt", "w") as file:
                        file.write("".join(lines))
                    await ctx.channel.send(f"Server prefixes are now: `{'` `'.join(prefix.split())}`")
                    return
        #If server isn't found in prefix list, append it to list
        lines.append(f"\n{ctx.guild.id}\n{prefix}")
        with open("musa_prefixes.txt", "w") as file:
            file.write("".join(lines))
        await ctx.channel.send(f"Server prefixes are now: `{'` `'.join(prefix.split())}`")
        return

    #Add prefix.
    @prefix.command(aliases=["append"])
    async def add(self, ctx, *prefixes):
        #With no prefixes specified, send instructions
        if len(prefixes) == 0:
            await ctx.channel.send(self.instructions())
            return
        #Turn prefix array into unique space-separated strings
        prefix = " ".join(sorted(set(prefixes)))
        #Copy text file
        with open("musa_prefixes.txt", "r") as file:
            lines = file.readlines()
        #Find server in prefix list and change their prefixes
        for i, line in enumerate(lines):
            if i % 2 == 0:
                if ctx.guild.id == int(line):
                    lines[i+1] = " ".join(sorted(set((lines[i+1] + f" {prefix}").split())))
                    with open("musa_prefixes.txt", "w") as file:
                        file.write("".join(lines))
                    await ctx.channel.send(f"Server prefixes are now: `{'` `'.join(lines[i+1].split())}`")
                    return
        #If server isn't found in prefix list, append it to list
        if "!" not in prefix:
            prefix = "! " + prefix
        lines.append(f"\n{ctx.guild.id}\n{prefix}")
        with open("musa_prefixes.txt", "w") as file:
            file.write("".join(lines))
        await ctx.channel.send(f"Server prefixes are now: `{'` `'.join(prefix.split())}`")
        return

    #Add prefix.
    @prefix.command(aliases=["information", "instructions", "help"])
    async def info(self, ctx):
        await ctx.channel.send(self.instructions())

#Client Setup
def setup(client):
    client.add_cog(PrefixCog(client))
