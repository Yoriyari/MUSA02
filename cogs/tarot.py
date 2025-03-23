#===============================================================================
# Tarot v1.4.2
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 07 May 2024 - v1.4.2; Moved UserError to a common error file. Addressed an
#               edge case where users drew too many cards for their names to
#               even fit within 2k characters. Introduced some extra defaults
#               and checks so that other card features (!domt) can import
#               these functions. -YY
# 05 May 2024 - v1.4.1; Reworked help message import and error handling. Also
#               removed Expand button on draws of over 15 cards since that does
#               not fit in Discord's 2k character message limit -YY
# 04 Nov 2023 - v1.4; Added a button which expands (or hides) interpretations of
#               drawn tarot cards. Made a Tarot Card class. Split Clow command
#               into its own cog. -YY
# 02 Nov 2023 - v1.3; Added Upright/Reversed labels to drawn tarot cards.
# 24 Sep 2023 - v1.2; Added the Clow deck from Cardcaptor Sakura on request.
#               Changed tarot command format to actual command decorators rather
#               than parameters and introduced auxiliary functions too. Made the
#               command call less strict. -YY
# 17 Apr 2022 - v1.1; Centralized help messages to one importable file. Added a
#               help command to this file. -YY
# 07 Jun 2020 - v1.0; Finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Note that clow.py and domt.py currently both import functions from this
#   file, creating hidden dependencies.
#===============================================================================
# Description
# ..............................................................................
# tarot.py generates a defined number of tarot cards for its user. You can
# choose to draw from the full tarot deck or just minor/major arcana.
# Upright/reversed outcomes as well as optional interpretations are included.
#===============================================================================

#Import Modules
import discord
from discord import ui
from discord.ext import commands

from common.json_handling import read_from_json
from common.error_message import send_error, UserError
from common.help_message import send_help

import random

tarot_interpretations_file = "data/tarot_interpretations.json"
view_timeout = 86400 # 24 hours

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Auxiliary functions

class Card:
    def __init__(self, name: str, orientation=None):
        self.name = name
        self.orientation = orientation
    def __str__(self):
        if self.orientation:
            return f"{self.name} ({self.orientation})"
        return self.name

def list_major_arcana():
    '''Returns a list of Card objects of tarot's major arcana.
    '''
    names = ["the Fool", "the Magician", "the High Priestess", "the Empress", "the Emperor", "the Hierophant", "the Lovers", "the Chariot", "Strength", "the Hermit", "Wheel of Fortune", "Justice", "the Hanged Man", "Death", "Temperance", "the Devil", "the Tower", "the Star", "the Moon", "the Sun", "Judgement", "the World"]
    return [Card(name, random_orientation()) for name in names]

def list_minor_arcana():
    '''Returns a list of Card objects of tarot's minor arcana.
    '''
    suits = ["Wands", "Pentacles", "Cups", "Swords"]
    values = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"]
    names = []
    for suit in suits:
        for value in values:
            names.append("the " + value + " of " + suit)
    return [Card(name, random_orientation()) for name in names]

def list_tarot_deck():
    '''Returns a list of Card objects of the full tarot deck.
    '''
    return list_major_arcana() + list_minor_arcana()

def random_orientation():
    '''Returns a string saying either Upright or Reversed.
    '''
    return random.choice(["Upright", "Reversed"])

def determine_draw_count(deck, argument):
    '''Returns an integer giving the parsed amount of cards that
    a player wants to draw.
    '''
    drawcount = 0
    if argument == None:
        return 1
    elif argument.isdecimal():
        if int(argument) > 0:
            if len(deck) < int(argument):
                raise UserError("There are not enough cards in the deck!")
            else:
                return int(argument)
    raise UserError("That's not a valid amount of cards to draw!")

def draw_cards(deck, amount):
    '''Returns a list of cards drawn from the top of the given deck.
    '''
    return deck[:amount]

def generate_short_picked_cards_string(cards):
    '''Returns a comma-separated string listing the card names.
    '''
    card_strings = [str(card) for card in cards]
    last_card = card_strings.pop()
    cards_string = ", ".join(card_strings)
    if card_strings:
        cards_string += " and "
    cards_string += last_card
    return cards_string

def generate_long_picked_cards_string(cards, desc_file=tarot_interpretations_file):
    '''Returns a bullet-point string listing the card names and interpretations.
    '''
    descriptions = read_from_json(desc_file)
    cards_string = ""
    for card in cards:
        desc = descriptions[card.name]
        if type(desc) != str:
            desc = desc[card.orientation]
        if "\n" in desc:
            desc = desc.replace("\n", "\n ")
        cards_string += f"\n- **{card}**: {desc}"
    return cards_string

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Cog setup

class Tarot(commands.Cog):

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
            name = ctx.author.name
            msg = f"{name} drew {cards_string}."
            if len(msg) > 2000:
                msg = f"{name} drew too many cards to fit in one message."
            view = None
            if amount <= 15:
                view = ViewTarot(name, cards_list)
            await ctx.channel.send(msg, view=view)
        except UserError as e:
            await ctx.channel.send(e)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Tarot cog loaded.")

    ##Tarot
    @commands.group(name="tarot", aliases=[], case_insensitive=True, invoke_without_command=True)
    async def tarot(self, ctx, argument=None):
        try:
            deck = list_tarot_deck()
            await self.handle_drawing(ctx, deck, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @tarot.command(aliases=["help", "?", "info", "information", "instructions"])
    async def tarot_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "tarot")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @tarot.command(aliases=["major"])
    async def tarot_major(self, ctx, argument=None):
        try:
            deck = list_major_arcana()
            await self.handle_drawing(ctx, deck, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @tarot.command(aliases=["minor"])
    async def tarot_minor(self, ctx, argument=None):
        try:
            deck = list_minor_arcana()
            await self.handle_drawing(ctx, deck, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @tarot.command(aliases=["draw", "card", "play"])
    async def tarot_draw(self, ctx, argument=None):
        try:
            deck = list_tarot_deck()
            await self.handle_drawing(ctx, deck, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

#Views
class ViewTarot(ui.View):
    def __init__(self, username=None, deck=None, expanded=False, desc_file=tarot_interpretations_file):
        super().__init__(timeout=view_timeout)
        if expanded:
            self.add_item(ButtonCollapse(username, deck, desc_file=desc_file))
        else:
            self.add_item(ButtonExpand(username, deck, desc_file=desc_file))

class ButtonExpand(ui.Button):
    def __init__(self, username=None, deck=None, desc_file=tarot_interpretations_file):
        super().__init__(label="Expand", style=discord.ButtonStyle.blurple)
        self.username = username
        self.deck = deck
        self.desc_file = desc_file
    async def callback(self, interaction):
        try:
            cards_string = generate_long_picked_cards_string(self.deck, desc_file=self.desc_file)
            msg = f"{self.username} drew:{cards_string}"
            if len(msg) > 2000:
                cards_string = generate_short_picked_cards_string(self.deck)
                msg = f"{self.username} drew cards with descriptions too large to fit in one Discord message:\n{cards_string}."
            view = ViewTarot(self.username, self.deck, expanded=True, desc_file=self.desc_file)
            await interaction.response.edit_message(content=msg, view=view)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonCollapse(ui.Button):
    def __init__(self, username=None, deck=None, desc_file=tarot_interpretations_file):
        super().__init__(label="Collapse", style=discord.ButtonStyle.blurple)
        self.username = username
        self.deck = deck
        self.desc_file = desc_file
    async def callback(self, interaction):
        try:
            cards_string = generate_short_picked_cards_string(self.deck)
            msg = f"{self.username} drew {cards_string}."
            view = ViewTarot(self.username, self.deck, desc_file=self.desc_file)
            await interaction.response.edit_message(content=msg, view=view)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

async def setup(client):
    await client.add_cog(Tarot(client))
