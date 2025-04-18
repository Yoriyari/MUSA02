#Import Modules
import discord
from discord.ext import commands
from common.prefix import get_prefix_of_guild
from common.private_ids import discord_id
import os, asyncio

#Bot Key
KEY_FILE = "secrets/key_discord.txt"
YORI_ID = discord_id("yori")

##Define client and command prefix
def get_prefix(client, ctx):
    return get_prefix_of_guild(ctx.guild)
intents = discord.Intents.all()
intents.presences = True
intents.members = True
intents.message_content = True
client = commands.Bot(command_prefix=get_prefix, case_insensitive=True, intents=intents)

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
    if ctx.author.id != YORI_ID:
        return
    await client.unload_extension(f'cogs.{extension}')
    print(f'Unloaded {extension} cog.')

@client.command(aliases=[])
async def load(ctx, extension):
    if ctx.author.id != YORI_ID:
        return
    await client.load_extension(f'cogs.{extension}')
    print(f'Loaded {extension} cog.')

@client.command(aliases=["refresh"])
async def reload(ctx, extension):
    if ctx.author.id != YORI_ID:
        return
    await client.unload_extension(f'cogs.{extension}')
    await client.load_extension(f'cogs.{extension}')
    print(f'Reloaded {extension} cog.')

#Reloading all cogs
@client.command(aliases=["reloadall", "refreshall", "refresh_all"])
async def reload_all(ctx):
    if ctx.author.id != YORI_ID:
        return
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await client.unload_extension(f'cogs.{filename[:-3]}')
            await client.load_extension(f'cogs.{filename[:-3]}')
    print(f'Reloaded all cogs.')

#Sync slash commands
@client.command(aliases=[])
async def sync(ctx):
    if ctx.author.id != YORI_ID:
        return
    synced = await client.tree.sync()
    print(f"Synced {len(synced)} slash command(s).")

##Loading cogs at start, and start bot
class MUSA(commands.Bot):
    async def setup_hook(self):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

async def main():
    async with client:
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await client.load_extension(f'cogs.{filename[:-3]}')
        key = None
        with open(KEY_FILE) as f:
            key = f.read()
        await client.start(key)

## Bot Key
asyncio.run(main())
