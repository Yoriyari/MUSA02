#Import Modules
import discord
from discord.ext import commands
import random

#Cog Setup
class Choose(commands.Cog):

    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Choose cog loaded.")

    #Choose
    @commands.command(aliases=["choice","pick"])
    async def choose(self, ctx, *options):
        choice = random.choice(options)
        await ctx.channel.send(choice)

def setup(client):
    client.add_cog(Choose(client))
