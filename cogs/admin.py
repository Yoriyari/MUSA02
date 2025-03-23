#Import Modules
import discord
from discord.ext import commands
import datetime

#Cog Setup
class Admin(commands.Cog):

    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin cog loaded.")

    ##Report DMs
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild == None:
            print(f"{datetime.datetime.now()} - DM to {message.channel.recipient.name} - {message.author.name}: {message.content}")

    ##Print Cache
    @commands.command(aliases=[])
    async def cache(self, ctx):
        for cached in self.client.cached_messages:
            if cached.guild == None:
                print(f"In DM to {cached.channel.recipient.name} - {cached.author.name}: {cached.content}")
            else:
                print(f"In {cached.guild.name}'s {cached.channel.name} - {cached.author.name}: {cached.content}")

    ##Print Active Game Sessions
    @commands.command(aliases=["game_cache"])
    async def games_cache(self, ctx):
        await ctx.invoke(self.client.get_command("blackjack print_cache"))
        await ctx.invoke(self.client.get_command("checkers print_cache"))
        await ctx.invoke(self.client.get_command("connectfour print_cache"))
        await ctx.invoke(self.client.get_command("hangman print_cache"))
        await ctx.invoke(self.client.get_command("mastermind_print_cache"))
        await ctx.invoke(self.client.get_command("tictactoe print_cache"))

async def setup(client):
    await client.add_cog(Admin(client))
