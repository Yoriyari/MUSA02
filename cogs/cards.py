#===============================================================================
# Cards v1.2.3
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 20 Mar 2025 - v1.2.3; Made strings with escape characters raw strings. -YY
# 07 May 2024 - v1.2.2; Moved UserError to a common error file. -YY
# 05 May 2024 - v1.2.1; Reworked help message import. Added error handling. -YY
# 04 Nov 2023 - v1.2; Rewrote file to use command decorators instead of para-
#               meters, use the common card.py functions, and accept a less
#               strict command call. -YY
# 17 Apr 2022 - v1.1; Centralized help messages to one importable file. Added a
#               help command to this file. -YY
# 28 Apr 2020 - v1.0; Finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# cards.py generates a defined number of random cards for its user. Overlap is
# possible.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.card import Card, random_card
from common.error_message import send_error, UserError
from common.help_message import send_help

import re

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Auxiliary functions

def determine_draw_count(argument):
    '''Returns an integer giving the parsed amount of cards that
    a player wants to draw.
    '''
    drawcount = 0
    if argument == None:
        return 1
    elif argument.isdecimal():
        if int(argument) > 0:
            return int(argument)
    raise UserError("That's not a valid amount of cards to draw!")

def remove_indexed_substring(full_string, indexes):
    '''Returns a string with a substring removed, picked out from a starting and
    ending index given in a tuple.
    '''
    start, end = indexes
    return full_string[:start] + full_string[end:]

def catch_representations(full_string, representations):
    '''Returns a tuple giving, in order, the input string with the detected
    fragment removed, and the proper data format of an alternative
    representation given in an input dict.
    If no representation is found, returns None.
    '''
    represent_query = "(" + ")|(".join(representations.keys()) + ")"
    match_object = re.search(represent_query, full_string)
    if not match_object:
        return None
    group = representations[match_object.group()]
    new_string = remove_indexed_substring(full_string, match_object.span())
    return (new_string, group)

def parse_suit_and_value(argument):
    '''Returns a Card object parsed from user input giving the suit and value.
    '''
    suit = None
    value = None
    #Value match attempt 1
    match_value = re.search(r"\d+", argument)
    if match_value:
        if int(match_value.group()) > 0 and int(match_value.group()) < 14:
            value = int(match_value.group())
            argument = remove_indexed_substring(argument, match_value.span())
    #Suit match attempt 1
    match_suit = re.search("(heart)|(diamond)|(spade)|(club)s?", argument)
    if match_suit:
        suit = match_suit.group()
        suit = suit[0].upper() + suit[1:]
        if suit[-1] != "s":
            suit += "s"
        argument = remove_indexed_substring(argument, match_suit.span())
    #Value match attempt 2
    if not value:
        representations = {
            "ace": 1,       "one": 1,       "two": 2,       "three": 3,
            "four": 4,      "five": 5,      "six": 6,       "seven": 7,
            "eight": 8,     "nine": 9,      "ten": 10,      "jack": 11,
            "knave": 11,    "eleven": 11,   "queen": 12,    "twelve": 12,
            "king": 13,     "thirteen": 13
        }
        detected = catch_representations(argument, representations)
        if detected:
            argument, value = detected
    #Value match attempt 3
    if not value:
        representations = {
            "a": 1,         "j": 11,        "q": 12,        "k": 13
        }
        detected = catch_representations(argument, representations)
        if detected:
            argument, value = detected
    #Suit match attempt 2
    if not suit:
        representations = {
            "h": "Hearts", "d": "Diamonds", "s": "Spades", "c": "Clubs"
        }
        detected = catch_representations(argument, representations)
        if detected:
            argument, suit = detected
    if suit and value:
        return Card(suit, value)
    return None

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

#Cog Setup
class Cards(commands.Cog):

    def __init__(self,client):
        self.client = client

    async def handle_drawing(self, ctx, argument):
        '''Generates random cards and posts the result in the contextual Discord
        channel.
        '''
        try:
            drawcount = determine_draw_count(argument)
            cards_objects = [random_card() for _ in range(drawcount)]
            cards_emoji = [card.emoji for card in cards_objects]
            cards_string = "".join(cards_emoji)
            drawstring = f"{ctx.author.name} drew {cards_string}"
            await ctx.channel.send(drawstring)
        except UserError as e:
            await ctx.channel.send(e)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cards cog loaded.")

    ##Standard 52-Card Playing Deck
    @commands.group(name="cards", aliases=["card"], case_insensitive=True, invoke_without_command=True)
    async def cards(self, ctx, argument=None):
        try:
            await self.handle_drawing(ctx, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @cards.command(aliases=["help", "?", "info", "information", "instructions"])
    async def cards_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "card")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @cards.command(aliases=["draw", "card", "play"])
    async def cards_draw(self, ctx, argument=None):
        try:
            await self.handle_drawing(ctx, argument)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @cards.command(aliases=["show", "display", "present"])
    async def cards_show(self, ctx, *argument):
        try:
            if not argument:
                await ctx.channel.send("Specify which card you wish to show, such as `!card show 10 of Clubs`.")
                return
            argument = " ".join(argument).lower()
            card = parse_suit_and_value(argument)
            if not card:
                await ctx.channel.send("Could not parse which card you want to show. Try a different format, such as `!card show 10 of Clubs`.")
                return
            await ctx.channel.send(f"{ctx.author.name} shows {card.emoji}")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

async def setup(client):
    await client.add_cog(Cards(client))
