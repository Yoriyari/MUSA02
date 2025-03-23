#===============================================================================
# Deck of Many Things v1.0
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 07 May 2024 - v1.0; Finished file. -YY
# 06 May 2024 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# domt.py lets users draw from D&D 5e's Deck of Many Things and includes the
# meanings of each card.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from cogs.tarot import generate_short_picked_cards_string, Card, ViewTarot
from common.error_message import send_error, UserError
from common.help_message import send_help

import random

DOMT_CARDS_FILE = "data/dnd/domt_cards.json"

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Cog setup
class DoMT(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Deck of Many Things cog loaded.")

    ##Tarot
    @commands.group(name="domt", aliases=["dommt", "dmt", "dmmt", "deckofmanythings", "deckofmany", "manythings"], case_insensitive=True, invoke_without_command=True)
    async def domt(self, ctx, argument=None):
        try:
            deck = list_full_deck()
            await handle_drawing(ctx, deck, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @domt.command(aliases=["draw", "card", "play", "extended", "full", "more", "dommt", "sixtysix", "sixty-six", "large", "l"])
    async def domt_draw(self, ctx, argument=None):
        try:
            deck = list_full_deck()
            await handle_drawing(ctx, deck, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @domt.command(aliases=["original", "twentytwo", "twenty-two", "medium", "m"])
    async def domt_original(self, ctx, argument=None):
        try:
            deck = list_original_deck()
            await handle_drawing(ctx, deck, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @domt.command(aliases=["reduced", "thirteen", "small", "s"])
    async def domt_thirteen(self, ctx, argument=None):
        try:
            deck = list_first_cards()
            await handle_drawing(ctx, deck, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @domt.command(aliases=["help", "?", "info", "information", "instructions"])
    async def domt_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "domt")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Views
class ViewDoMT(ViewTarot):
    def __init__(self, username=None, deck=None, desc_file=DOMT_CARDS_FILE):
        super().__init__(username=username, deck=deck, desc_file=desc_file)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Auxiliary functions
async def handle_drawing(ctx, deck, argument):
    '''Shuffles the given deck and draws the amount of cards provided as
    argument. Posts the result in the contextual Discord channel.
    '''
    try:
        amount = determine_draw_count(deck, argument)
        cards_list = draw_cards(deck, amount)
        cards_string = generate_short_picked_cards_string(cards_list)
        name = ctx.author.name
        msg = f"{name} drew {cards_string}."
        view = None
        if amount <= 5:
            view = ViewDoMT(name, cards_list)
        await ctx.channel.send(msg, view=view)
    except UserError as e:
        await ctx.channel.send(e)

def list_first_cards():
    '''Returns a list of Card objects of the DoMT's first thirteen cards.
    '''
    names = ["Sun", "Moon", "Star", "Throne", "Key", "Knight", "the Void", "Flames", "Skull", "Ruin", "Euryale", "Rogue", "Jester"]
    return [Card(name) for name in names]

def list_second_cards():
    '''Returns a list of Card objects of the DoMT's second nine cards.
    '''
    names = ["Sage", "Comet", "the Fates", "Gem", "Talons", "Puzzle", "Donjon", "Balance", "Fool"]
    return [Card(name) for name in names]

def list_third_cards():
    '''Returns a list of Card objects of the DoMMT's extra forty-four cards.
    '''
    names = ["Aberration", "Beast", "Book", "Bridge", "Campfire", "Cavern", "Celestial", "Construct", "Corpse", "Crossroads", "Door", "Dragon", "Elemental", "Expert", "Fey", "Fiend", "Giant", "Humanoid", "Lance", "Mage", "Map", "Maze", "Mine", "Monstrosity", "Ooze", "Path", "Pit", "Plant", "Priest", "Prisoner", "Ring", "Shield", "Ship", "Staff", "Stairway", "Statue", "Tavern", "Temple", "Tomb", "Tower", "Tree", "Undead", "Warrior", "Well"]
    return [Card(name) for name in names]

def list_original_deck():
    '''Returns a list of Card objects of the 2014 Deck of Many Things.
    '''
    return list_first_cards() + list_second_cards()

def list_full_deck():
    '''Returns a list of Card objects of the full Deck of Many More Things.
    '''
    return list_first_cards() + list_second_cards() + list_third_cards()

def determine_draw_count(deck, argument):
    '''Returns an integer giving the parsed amount of cards that
    a player wants to draw.
    '''
    drawcount = 0
    if argument == None:
        return 1
    elif argument.isdecimal():
        if int(argument) > 0:
            return min(int(argument), 180)
    raise UserError("That's not a valid amount of cards to draw!")

def draw_cards(deck, amount):
    '''Returns a list of cards drawn from the top of the given deck.
    '''
    stop_draws = ["the Void", "Donjon", "Fey", "Prisoner"]
    result = []
    i = 0
    while i < amount:
        card = random.choice(deck)
        result.append(card)
        if card.name == "Tower":
            card1 = random.choice(deck)
            card2 = random.choice(deck)
            result += [card1, card2]
            if card1.name in stop_draws and card2.name in stop_draws:
                break
        if card.name in stop_draws:
            break
        if card.name in ["Fool", "Jester"]:
            deck.remove(card)
            if card.name == "Fool":
                amount += 1
        i += 1
    return result

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Cog initialization
async def setup(client):
    await client.add_cog(DoMT(client))
