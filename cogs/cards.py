#Import Modules
import discord
from discord.ext import commands
import random

#Cog Setup
class Cards(commands.Cog):
    
    def __init__(self,client):
        self.client = client
    
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
        print("Cards cog loaded.")

    ##Cards
    @commands.command(aliases=["card"])
    async def cards(self, ctx, action, argument1=None):
        ##Draw (generate random)
        if action == "draw":
            #Determine how many cards player wants to draw
            drawcount = 0
            if argument1 == None:
                drawcount = 1
            elif self.check_integer(argument1):
                if int(argument1) > 0:
                    drawcount = int(argument1)
                else:
                    await ctx.channel.send("That's not a valid amount of cards to draw!")
            else:
                await ctx.channel.send("That's not a valid amount of cards to draw!")
            
            #Draw the specified amount of cards
            if drawcount != 0:
                drawstring = "{} drew ".format(ctx.author.name)
                for cardsdrawn in range(drawcount):
                    card = str(random.randrange(1, 14)) + " " + random.choice(["h", "d", "s", "c"])
                    card_emoji = self.translate_card_emoji(card)
                    drawstring += card_emoji
                await ctx.channel.send(drawstring)

        ##Show
        if action == "show":
            #Determine which card is desired
            desiredshow = self.translate_argument_card(argument1.lower())
            if desiredshow == None:
                await ctx.channel.send("Invalid card name!")
            else:
                card_emoji = self.translate_card_emoji(desiredshow)
                await ctx.channel.send("{} shows {}".format(ctx.author.name, card_emoji))


def setup(client):
    client.add_cog(Cards(client))