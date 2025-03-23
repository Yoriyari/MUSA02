#===============================================================================
# Decks v1.1.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 05 May 2024 - v1.1.1; Reworked help message import. Added error handling. -YY
# 17 Apr 2022 - v1.1; Centralized help messages to one importable file. -YY
# 01 Jun 2020 - v1.0; Finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Import card emoji from the common folder. -YY
# - Rewrite to utilize command infrastructure instead of parameter strings. -YY
#===============================================================================
# Description
# ..............................................................................
# decks.py keeps a 52-playing card deck in memory which users can draw from.
# This allows cards to be generated while guaranteeing no duplicates are drawn.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.error_message import send_error
from common.help_message import send_help

import random

#Cog Setup
class Decks(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.setting_newdeck = ["1 h","2 h","3 h","4 h","5 h","6 h","7 h","8 h","9 h","10 h","11 h","12 h","13 h","1 d","2 d","3 d","4 d","5 d","6 d","7 d","8 d","9 d","10 d","11 d","12 d","13 d","1 s","2 s","3 s","4 s","5 s","6 s","7 s","8 s","9 s","10 s","11 s","12 s","13 s","1 c","2 c","3 c","4 c","5 c","6 c","7 c","8 c","9 c","10 c","11 c","12 c","13 c"] #All cards.
        self.game_deck = [] #For copying the base deck and shuffling.
        self.game_hands = [] #Alternatingly player IDs and the cards they've drawn.
        self.game_faceup = [] #Cards drawn face-up

    def translate_card_emoji(self, card):
        if card == "1 h": #Hearts
            return "<:HA:716858601041428502>"
        if card == "2 h":
            return "<:H2:716858631936671804>"
        if card == "3 h":
            return "<:H3:716858652752871485>"
        if card == "4 h":
            return "<:H4:716858669446332426>"
        if card == "5 h":
            return "<:H5:716858683857829890>"
        if card == "6 h":
            return "<:H6:716858697732718684>"
        if card == "7 h":
            return "<:H7:716858732557893632>"
        if card == "8 h":
            return "<:H8:716858746474725386>"
        if card == "9 h":
            return "<:H9:716858760450146384>"
        if card == "10 h":
            return "<:H10:716858775570481223>"
        if card == "11 h":
            return "<:HJ:716858817094090832>"
        if card == "12 h":
            return "<:HQ:716858849868513341>"
        if card == "13 h":
            return "<:HK:716858861247791196>"
        if card == "1 d": #Diamonds
            return "<:DA:716858907821342740>"
        if card == "2 d":
            return "<:D2:716858925395476510>"
        if card == "3 d":
            return "<:D3:716858934874341446>"
        if card == "4 d":
            return "<:D4:716858950133350444>"
        if card == "5 d":
            return "<:D5:716858961730732043>"
        if card == "6 d":
            return "<:D6:716858984522580008>"
        if card == "7 d":
            return "<:D7:716858996459307088>"
        if card == "8 d":
            return "<:D8:716859011491954720>"
        if card == "9 d":
            return "<:D9:716859023093399643>"
        if card == "10 d":
            return "<:D10:716859063111254018>"
        if card == "11 d":
            return "<:DJ:716859091942899784>"
        if card == "12 d":
            return "<:DQ:716859115149852722>"
        if card == "13 d":
            return "<:DK:716859126088728607>"
        if card == "1 s": #Spades
            return "<:SA:716859337850748979>"
        if card == "2 s":
            return "<:S2:716859353390383176>"
        if card == "3 s":
            return "<:S3:716859364945952788>"
        if card == "4 s":
            return "<:S4:716859377793105980>"
        if card == "5 s":
            return "<:S5:716859390275354624>"
        if card == "6 s":
            return "<:S6:716859401415426080>"
        if card == "7 s":
            return "<:S7:716859412697841776>"
        if card == "8 s":
            return "<:S8:716859444427882556>"
        if card == "9 s":
            return "<:S9:716859456889028679>"
        if card == "10 s":
            return "<:S10:716859469392379975>"
        if card == "11 s":
            return "<:SJ:716859500518440961>"
        if card == "12 s":
            return "<:SQ:716859517417029652>"
        if card == "13 s":
            return "<:SK:716859531400839178>"
        if card == "1 c": #Clubs
            return "<:CA:716859547956019250>"
        if card == "2 c":
            return "<:C2:716859561998418021>"
        if card == "3 c":
            return "<:C3:716859569946492959>"
        if card == "4 c":
            return "<:C4:716859578154876929>"
        if card == "5 c":
            return "<:C5:716859589160730674>"
        if card == "6 c":
            return "<:C6:716859596479922297>"
        if card == "7 c":
            return "<:C7:716859608131698751>"
        if card == "8 c":
            return "<:C8:716859613676437514>"
        if card == "9 c":
            return "<:C9:716859631120547922>"
        if card == "10 c":
            return "<:C10:716859635826556980>"
        if card == "11 c":
            return "<:CJ:716859641388335124>"
        if card == "12 c":
            return "<:CQ:716859653182718083>"
        if card == "13 c":
            return "<:CK:716859657972350977>"

    def check_integer(self, argument):
        if argument.isdecimal() == False:
            return False
        return True

    def translate_argument_card(self, argument):
        if len(argument) == 3:
            if self.check_integer(argument[:1]) and self.check_integer(argument[1:2]) and not self.check_integer(argument[2:]):
                if (argument[2:] == "h" or argument[2:] == "d" or argument[2:] == "s" or argument[2:] == "c") and int(argument[0:2]) < 14 and int(argument[0:2]) > 9:
                    return argument[0:2] + " " + argument[2:]
                else:
                    return None
            elif not self.check_integer(argument[:1]) and self.check_integer(argument[1:2]) and self.check_integer(argument[2:]):
                if (argument[:1] == "h" or argument[:1] == "d" or argument[:1] == "s" or argument[:1] == "c") and int(argument[1:]) < 14 and int(argument[1:]) > 9:
                    return argument[1:] + " " + argument[:1]
                else:
                    return None
            else:
                return None
        elif len(argument) == 2:
            if self.check_integer(argument[:1]) and not self.check_integer(argument[1:]):
                if (argument[1:] == "h" or argument[1:] == "d" or argument[1:] == "s" or argument[1:] == "c") and int(argument[:1]) < 10 and int(argument[:1]) > 0:
                    return argument[:1] + " " + argument[1:]
                else:
                    return None
            elif not self.check_integer(argument[:1]) and self.check_integer(argument[1:]):
                if (argument[:1] == "h" or argument[:1] == "d" or argument[:1] == "s" or argument[:1] == "c") and int(argument[1:]) < 10 and int(argument[1:]) > 0:
                    return argument[1:] + " " + argument[:1]
                else:
                    return None
            elif not self.check_integer(argument[:1]) and not self.check_integer(argument[1:]):
                if argument[1:] == "h" or argument[1:] == "d" or argument[1:] == "s" or argument[1:] == "c":
                    if argument[:1] == "a":
                        return "1 " + argument[1:]
                    elif argument[:1] == "j":
                        return "11 " + argument[1:]
                    elif argument[:1] == "q":
                        return "12 " + argument[1:]
                    elif argument[:1] == "k":
                        return "13 " + argument[1:]
                    else:
                        return None
                elif argument[:1] == "h" or argument[:1] == "d" or argument[:1] == "s" or argument[:1] == "c":
                    if argument[1:] == "a":
                        return "1 " + argument[:1]
                    elif argument[1:] == "j":
                        return "11 " + argument[:1]
                    elif argument[1:] == "q":
                        return "12 " + argument[:1]
                    elif argument[1:] == "k":
                        return "13 " + argument[:1]
                    else:
                        return None
                else:
                    return None
            else:
                return None
        else:
            return None

    @commands.Cog.listener()
    async def on_ready(self):
        print("Decks cog loaded.")

    ##Decks
    @commands.command(aliases=["deck"])
    async def decks(self, ctx, action, argument1=None):
        try:
            ##Draw Card Face Down (adds to hand)
            if action == "draw" or action == "facedown" or action == "drawdown" or action == "down" or action == "drawfacedown":
                if len(self.game_deck) == 0:
                    await ctx.channel.send("Deck's empty!")
                else:
                    player = ctx.author.id

                    #Determine how many cards player wants to draw
                    drawcount = 0
                    if argument1 == None:
                        drawcount = 1
                    elif self.check_integer(argument1):
                        if int(argument1) > 0:
                            if len(self.game_deck) < int(argument1):
                                await ctx.channel.send("There are not enough cards left in the deck!")
                            else:
                                drawcount = int(argument1)
                        else:
                            await ctx.channel.send("That's not a valid amount of cards to draw!")
                    else:
                        await ctx.channel.send("That's not a valid amount of cards to draw!")

                    #Draw the specified amount of cards
                    if drawcount != 0:
                        drawstring = "You drew "
                        for cardsdrawn in range(drawcount):
                            card = self.game_deck[0]
                            for index, entry in enumerate(self.game_hands): #Iterate over all active players
                                if entry == ctx.author.id:
                                    player = 0
                                    self.game_hands[index+1].append(card)
                                    break
                            if player != 0:
                                self.game_hands.append(player)
                                self.game_hands.append([card])
                            del self.game_deck[0]
                            card_emoji = self.translate_card_emoji(card)
                            drawstring += card_emoji
                        await ctx.author.send(drawstring)

            ##Draw Card Face Up (doesn't add to hand)
            if action == "faceup" or action == "drawup" or action == "up" or action == "drawfaceup":
                if len(self.game_deck) == 0:
                    await ctx.channel.send("Deck's empty!")
                else:
                    player = ctx.author.id

                    #Determine how many cards player wants to draw
                    drawcount = 0
                    if argument1 == None:
                        drawcount = 1
                    elif self.check_integer(argument1):
                        if int(argument1) > 0:
                            if len(self.game_deck) < int(argument1):
                                await ctx.channel.send("There are not enough cards left in the deck!")
                            else:
                                drawcount = int(argument1)
                        else:
                            await ctx.channel.send("That's not a valid amount of cards to draw!")
                    else:
                        await ctx.channel.send("That's not a valid amount of cards to draw!")

                    #Draw the specified amount of cards
                    if drawcount != 0:
                        drawstring = "{} drew ".format(ctx.author.name)
                        for cardsdrawn in range(drawcount):
                            card = self.game_deck[0]
                            self.game_faceup.append(card)
                            del self.game_deck[0]
                            card_emoji = self.translate_card_emoji(card)
                            drawstring += card_emoji
                        await ctx.channel.send(drawstring)

            ##Reset Deck
            if action == "reset" or action == "shuffle" or action == "new" or action == "start" or action == "begin" or action == "refresh" or action == "reload":
                self.game_deck = self.setting_newdeck.copy()
                if argument1 != None:
                    if self.check_integer(argument1):
                        if int(argument1) > 1:
                            for _ in range(int(argument1)-1):
                                self.game_deck += self.setting_newdeck.copy()
                random.shuffle(self.game_deck)
                self.game_hands = []
                self.game_faceup = []
                await ctx.channel.send("New deck shuffled.")

            ##Show Hand
            if action == "hand" or action == "show" or action == "showhand":
                player = ctx.author.id
                for index, entry in enumerate(self.game_hands): #Iterate over all active players
                    if entry == player:
                        player = 0
                        handstring = "{}'s hand: ".format(ctx.author.name)
                        for indexcard, heldcard in enumerate(self.game_hands[index+1]):
                            card = heldcard
                            card_emoji = self.translate_card_emoji(card)
                            handstring += card_emoji
                        await ctx.channel.send(handstring)
                        break
                if player != 0:
                    await ctx.channel.send("You have drawn no cards!")

            ##Show Face-up Cards
            if action == "handup" or action == "showup" or action == "showhandup" or action == "handfaceup" or action == "showfaceup" or action == "showhandfaceup":
                if len(self.game_faceup) < 1:
                    await ctx.channel.send("No cards have been drawn face-up!")
                else:
                    handstring = "Face-up cards: "
                    for heldcard in self.game_faceup:
                        card = heldcard
                        card_emoji = self.translate_card_emoji(card)
                        handstring += card_emoji
                    await ctx.channel.send(handstring)

            ##Discard Cards
            if action == "discard" or action == "remove" or action == "delete" or action == "destroy" or action == "throwaway":
                desireddiscard = self.translate_argument_card(argument1.lower())
                if desireddiscard == None:
                    await ctx.channel.send("Invalid card name!")
                else:
                    player = ctx.author.id
                    for index, entry in enumerate(self.game_hands): #Iterate over all active players
                        if entry == player:
                            player = 0
                            for indexcard, heldcard in enumerate(self.game_hands[index+1]):
                                if heldcard == desireddiscard:
                                    del self.game_hands[index+1][indexcard]
                                    desireddiscard = None
                                    break
                            break
                    if player == 0:
                        if desireddiscard == None:
                            await ctx.channel.send("Card discarded.")
                        else:
                            await ctx.channel.send("Card not found in your hand!")
                    else:
                        await ctx.channel.send("You have no cards in your hand!")

            ##Add Cards
            if action == "add" or action == "fish" or action == "grab" or action == "take":
                desiredadd = self.translate_argument_card(argument1.lower())
                if desiredadd == None:
                    await ctx.channel.send("Invalid card name!")
                else:
                    player = ctx.author.id
                    for index, entry in enumerate(self.game_hands): #Iterate over all active players
                        if entry == player:
                            player = 0
                            self.game_hands[index+1].append(desiredadd)
                            break
                    if player != 0:
                        self.game_hands.append(player)
                        self.game_hands.append([desiredadd])
                    await ctx.channel.send("Card added.")

            ##Help
            if action == "help" or action == "info":
                await send_help(ctx.channel.send, "deck")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

async def setup(client):
    await client.add_cog(Decks(client))
