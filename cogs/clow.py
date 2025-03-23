#===============================================================================
# Clow v1.0.2
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 07 May 2024 - v1.0.2; Moved UserError to a common error file. -YY
# 05 May 2024 - v1.0.1; Reworked help message import and error handling. -YY
# 04 Nov 2023 - v1.0; Split off from tarot.py. -YY
# 24 Sep 2023 - Added the Clow deck from Cardcaptor Sakura to tarot.py on
#               request. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# clow.py generates a defined number of Clow cards for its user.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from cogs.tarot import draw_cards, determine_draw_count, generate_short_picked_cards_string
from common.error_message import send_error, UserError
from common.help_message import send_help

import random

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

def list_clow_deck():
    '''Returns a list of strings of Cardcaptor Sakura's clow cards.
    As requested by Marisa.
    '''
    return ["The Arrow", "The Big", "The Bubbles", "The Change", "The Cloud", "The Create", "The Dark", "The Dash", "The Dream", "The Earthy", "The Erase", "The Fight", "The Firey", "The Float", "The Flower", "The Fly", "The Freeze", "The Glow", "The Illusion", "The Jump", "The Libra", "The Light", "The Little", "The Lock", "The Loop", "The Maze", "The Mirror", "The Mist", "The Move", "The Nothing", "The Power", "The Rain", "The Return", "The Sand", "The Shadow", "The Shield", "The Shot", "The Silent", "The Sleep", "The Snow", "The Song", "The Storm", "The Sweet", "The Sword", "The Through", "The Thunder", "The Time", "The Twin", "The Voice", "The Watery", "The Wave", "The Windy", "The Wood"]

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

#Cog setup
class Clow(commands.Cog):

    def __init__(self,client):
        self.client = client

    async def handle_drawing(self, ctx, deck, argument):
        '''Shuffles the given deck and draws the amount of cards provided as
        argument. Posts the result in the contextual Discord channel.
        '''
        try:
            random.shuffle(deck)
            amount = determine_draw_count(deck, argument)
            cards_list = draw_cards(deck, amount)
            cards_string = generate_short_picked_cards_string(cards_list)
            msg = f"{ctx.author.name} drew {cards_string}."
            await ctx.channel.send(msg)
        except UserError as e:
            await ctx.channel.send(e)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Clow cog loaded.")

    ##Clow
    @commands.group(name="clow", aliases=[], case_insensitive=True, invoke_without_command=True)
    async def clow(self, ctx, argument=None):
        try:
            deck = list_clow_deck()
            await self.handle_drawing(ctx, deck, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @clow.command(aliases=["help", "?", "info", "information", "instructions"])
    async def clow_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "clow")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @clow.command(aliases=["draw", "card", "play"])
    async def clow_draw(self, ctx, argument=None):
        try:
            deck = list_clow_deck()
            await self.handle_drawing(ctx, deck, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

async def setup(client):
    await client.add_cog(Clow(client))
