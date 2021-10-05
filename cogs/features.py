#Import Modules
import discord
from discord.ext import commands
import random

#Cog Setup
class Features(commands.Cog):

    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Features cog loaded.")

    #Choose
    @commands.command(aliases=["feats", "help", "info", "information", "instructions"])
    async def features(self, ctx):
        msg = "__**MUSA02 Features**__\n"
        msg += "**Games**\n"
        msg += "`!bj` - Blackjack.\n"
        msg += "`!cah` - Cards Against Humanity.\n"
        msg += "`!ch` - Checkers.\n"
        msg += "`!c4` - Connect Four.\n"
        msg += "`!hm` - Hangman.\n"
        msg += "`!mm` - Mastermind.\n"
        msg += "`!ttt` - Tic-Tac-Toe.\n"
        msg += "\n"
        msg += "**Generic Features for Non-Programmed Games**\n"
        msg += "`!card` - Generates a specified amount of playing cards.\n"
        msg += "`!deck` - Draw from a shared playing card deck to prevent duplicate cards between people.\n"
        msg += "`!tarot` - Generates a specified amount of tarot cards.\n"
        msg += "\n"
        msg += "**Voice Chat**\n"
        msg += "`!play` - Play videos from most sites in voice chat, with YouTube playlist compatability.\n"
        msg += "`!say` - Play text-to-speech dialogue in voice chat.\n"
        msg += "There's also `!volume`, `!pause`, `!resume`, `!skip` `!stop`, `!join`, and `!leave`.\n"
        msg += "\n"
        msg += "**Other Features**\n"
        msg += "`!prefix` - Change the prefix(es) used for my commands in the current server.\n"
        msg += "`!choose` - Pick from a specified list of options, separated by spaces.\n"
        msg += "`!fesh` - Generate a random quote from the Fesh Pince of Blair.\n"
        msg += "`!games` - Lists available games, with a couple of quick-starts.\n"
        msg += "`!help` - Show this message.\n"
        msg += "There's also a couple of random phrases I will respond to, like \"Hello MUSA.\""
        await ctx.channel.send(msg)

def setup(client):
    client.add_cog(Features(client))
