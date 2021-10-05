#Import Modules
import discord
from discord.ext import commands
import os

##Define client and command prefix
def get_prefix(client, ctx):
    prefix = "!"
    if ctx.guild != None:
        with open("musa_prefixes.txt", "r") as file:
            lines = file.read().splitlines()
        for i, line in enumerate(lines):
            if i % 2 == 0:
                if ctx.guild.id == int(line):
                    prefix = [p for p in lines[i+1].split()]
                    break
    return prefix
client = commands.Bot(command_prefix=get_prefix, case_insensitive=True)

##Report when bot is logged in
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

##Skips the error output of non-command messages starting with the prefix
@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error

##Remove default help command
client.remove_command("help")

##(Re)load Cogs
@client.command(aliases=[])
async def unload(ctx, extension):
    await ctx.message.delete()
    client.unload_extension(f'cogs.{extension}')
    print(f'Unloaded {extension} cog.')

@client.command(aliases=[])
async def load(ctx, extension):
    await ctx.message.delete()
    client.load_extension(f'cogs.{extension}')
    print(f'Loaded {extension} cog.')

@client.command(aliases=["refresh"])
async def reload(ctx, extension):
    await ctx.message.delete()
    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    print(f'Reloaded {extension} cog.')

#Reloading all cogs
@client.command(aliases=["reloadall", "refreshall", "refresh_all"])
async def reload_all(ctx):
    await ctx.message.delete()
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            client.unload_extension(f'cogs.{filename[:-3]}')
            client.load_extension(f'cogs.{filename[:-3]}')
    print(f'Reloaded all cogs.')

##Loading cogs at start
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

## Bot Key
client.run(KEY)
