#Import Modules
import discord
from discord.ext import commands
import random

#Cog Setup
class Tarot(commands.Cog):
    
    def __init__(self,client):
        self.client = client
        self.major_arcana = ["the Fool", "the Magician", "the High Priestess", "the Empress", "the Emperor", "the Hierophant", "the Lovers", "the Chariot", "Strength", "the Hermit", "Wheel of Fortune", "Justice", "the Hanged Man", "Death", "Temperance", "the Devil", "the Tower", "the Star", "the Moon", "the Sun", "Judgement", "the World"] #All major arcana.
        self.minor_arcana_values = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Page", "Knight", "Queen", "King"] #All minor arcana values.
        self.minor_arcana_suits = ["Wands", "Pentacles", "Cups", "Swords"] #All minor arcana suits.
        self.game_deck = [] #For copying the base deck(s) and shuffling.
    
    def check_integer(self, argument):
        if argument.isdecimal() == False:
            return False
        return True

    @commands.Cog.listener()
    async def on_ready(self):
        print("Tarot cog loaded.")

    ##Tarot
    @commands.command(aliases=[])
    async def tarot(self, ctx, action, argument1=None):
        ##Major Arcana
        if action == "major":
            self.game_deck = self.major_arcana.copy()
            random.shuffle(self.game_deck)
            
            #Determine how many cards player wants to draw
            drawcount = 0
            if argument1 == None:
                drawcount = 1
            elif self.check_integer(argument1):
                if int(argument1) > 0:
                    if len(self.game_deck) < int(argument1):
                        await ctx.channel.send("There are not enough cards in the deck!")
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
                    del self.game_deck[0]
                    drawstring += card
                    if cardsdrawn == drawcount-1:
                        drawstring += "."
                    else:
                        if cardsdrawn == drawcount-2:
                            drawstring += " and "
                        else:
                            drawstring += ", "
                await ctx.channel.send(drawstring)
            
            self.game_deck = []
            
        ##Minor Arcana
        if action == "minor":
            for suit in self.minor_arcana_suits:
                for value in self.minor_arcana_values:
                    self.game_deck.append("the " + value + " of " + suit)
            random.shuffle(self.game_deck)
            
            #Determine how many cards player wants to draw
            drawcount = 0
            if argument1 == None:
                drawcount = 1
            elif self.check_integer(argument1):
                if int(argument1) > 0:
                    if len(self.game_deck) < int(argument1):
                        await ctx.channel.send("There are not enough cards in the deck!")
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
                    del self.game_deck[0]
                    drawstring += card
                    if cardsdrawn == drawcount-1:
                        drawstring += "."
                    else:
                        if cardsdrawn == drawcount-2:
                            drawstring += " and "
                        else:
                            drawstring += ", "
                await ctx.channel.send(drawstring)
            
            self.game_deck = []
            
        ##Draw
        if action == "draw":
            self.game_deck = self.major_arcana.copy()
            for suit in self.minor_arcana_suits:
                for value in self.minor_arcana_values:
                    self.game_deck.append("the " + value + " of " + suit)
            random.shuffle(self.game_deck)
            
            #Determine how many cards player wants to draw
            drawcount = 0
            if argument1 == None:
                drawcount = 1
            elif self.check_integer(argument1):
                if int(argument1) > 0:
                    if len(self.game_deck) < int(argument1):
                        await ctx.channel.send("There are not enough cards in the deck!")
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
                    del self.game_deck[0]
                    drawstring += card
                    if cardsdrawn == drawcount-1:
                        drawstring += "."
                    else:
                        if cardsdrawn == drawcount-2:
                            drawstring += " and "
                        else:
                            drawstring += ", "
                await ctx.channel.send(drawstring)
            
            self.game_deck = []


def setup(client):
    client.add_cog(Tarot(client))