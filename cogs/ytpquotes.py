#===============================================================================
# YTP Quotes v1.0.2
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.0.2; Hid Discord user IDs from file. -YY
# 21 Feb 2025 - v1.0.1; Made the 'ointments' trigger a bit more strict. -YY
# 27 Apr 2020 - v1.0; Finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# ytpquotes.py checks for specific trigger quotes from the Fesh Pince of Blair,
# which cause the bot to continue the quote in reply.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands
import random

from common.private_ids import discord_id

AVERY_ID = discord_id("avery")

#Cog Setup
class YTPQuotes(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("YTPQuotes cog loaded.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        if message.guild != None and (message.channel.name == "vent" or message.channel.name == "venting" or message.channel.name == "safe-zone" or message.channel.name == "safe-zone-2" or message.channel.name == "screaming-into-the-voice" or message.channel.name == "vent-art" or message.channel.name == "brains-and-dreams"):
            return
        msg = message.content.lower()

        ##Fesh Pince of Blair
        if "drink 5 hour energy" in msg or "drink five hour energy" in msg:
            await message.channel.send("It's not a drink, more like a drink.")
        if "hillary how did you know that" in msg:
            await message.channel.send("\u200b")
        if "make me a sandwich" in msg:
            quotes = ["nOo", "nOo", "nOo", "nOo", "nOo", "nOo", "nOo", "nOo", "nOo", "I did it. Sex."]
            await message.channel.send(random.choice(quotes))
        if "what the heck is this" in msg:
            quotes = ["It's ponies, dad.", "It's Fesh Pince, dad.", "This is the story all about how my life got flip-turned upside down."]
            await message.channel.send(random.choice(quotes))
        if "gonna get dad what he always wanted" in msg:
            await message.channel.send("What, a pizza hut in the garage?")
        if "look at those funny little markings underneath the picture" in msg:
            await message.channel.send("I can't read.")
        if "swindled me" in msg or "7X5LsbzGs-s" in msg:
            await message.channel.send("I was saving that money to buy pot.")
        if "its carlton" in msg or "it's carlton" in msg or "ceaereleteoen" in msg:
            await message.channel.send("No E.")
        if "i think you're being really unreasonable" in msg or "i think youre being really unreasonable" in msg:
            await message.channel.send("Well, tough shit. I don't care.")
        if "banks wants to empty the banks" in msg:
            await message.channel.send("But dad, aren't some of those banks?")
        if "you've got to kick that man's butt" in msg or "youve got to kick that man's butt" in msg or "you've got to kick that mans butt" in msg or "youve got to kick that mans butt" in msg:
            await message.channel.send("Philip Banks, you should kick my butt.")
        if "it goes against everything i stand for" in msg:
            await message.channel.send("What's your point?!")
        if "are you free for dinner tonight" in msg or "are ya free for dinner tonight" in msg:
            await message.channel.send("My father just lost an erection.")
        if "let's get the hell out of here" in msg or "lets get the hell out of here" in msg:
            await message.channel.send("There goes Philip Banks, the biggest ASS, that ever lived. What a douche.")
        if "oh my god he's god" in msg or "oh my god hes god" in msg:
            await message.channel.send("Hallelujah!")
        if "welcome you to the memorial for carlton" in msg:
            await message.channel.send("Saying a few words on behalf of the departed will be Philips.")
        if "what can you say about carlton" in msg:
            await message.channel.send("He was Carlton.")
        if "and who are you" in msg:
            await message.channel.send("I'm the Dude.")
        if "i think i know how to help will" in msg:
            if message.author.id == AVERY_ID:
                await message.channel.send("We've got to attack YOU.")
            else:
                await message.channel.send("We've got to attack him.")
        if "i'm gonna shit my pants" in msg or "im gonna shit my pants" in msg:
            await message.channel.send("Philip, no! How could you say numbers numbers numbers")
        if "heaven has to be like a cross between a dikekike video and" in msg:
            await message.channel.send("You see, it's like, I could have a leg in one hand, and a brerb in the other.")
        if "let me tell you boys something about women" in msg:
            quotes = ["Nefafefafefaf, nefafefafefaf.", "Something about women."]
            await message.channel.send(random.choice(quotes))
        if "my first short story" in msg:
            await message.channel.send("Your first short story and your first short story in the same room!")
        if "want a w?" in msg or "want a double u" in msg or msg.endswith("want a w"):
            await message.channel.send("what the fuck")
        if "who is the question" in msg:
            await message.channel.send("nOo")
        if "are you sure we should do this" in msg:
            await message.channel.send("It's either this, or this.")
        if "ponies are coming on" in msg:
            await message.channel.send("Turn it up! Turn it up!")
        if "do you like ponies" in msg:
            await message.channel.send("*waves around an Applejack toy*")
        if "are you out of your horny little adolescent minds" in msg:
            await message.channel.send("I know I am, dad!")
        if "how do you think jim feels when he changes into his gym shorts" in msg:
            await message.channel.send("Hey, what's that supposed to mean?")
        if "this is my mother carlton" in msg:
            await message.channel.send("nOo")
        if "imma coming luigi" in msg:
            await message.channel.send("Yo yo yo! My brother, Carlton!")
        if "your opening statement" in msg:
            await message.channel.send("Statement.")
        if "have a big butt like my worthy adversary philip banks" in msg or "have a big butt, like my worthy adversary philip banks" in msg or "have a big butt like my worthy adversary, philip banks" in msg or "have a big butt, like my worthy adversary, philip banks" in msg:
            if "but what i do have" in msg:
                await message.channel.send("Order in the court!")
            else:
                await message.channel.send("But what I do have is the PWRPWR")
        if "how did it go down mr smith" in msg or "how did it go down, mr smith" in msg or "how did it go down mr. smith" in msg or "how did it go down, mr. smith" in msg:
            await message.channel.send("I'm glad you asked me that question. Check it out.")
        if "this is a black thing isn't it" in msg or "this is a black thing isnt it" in msg or "this is a black thing, isn't it" in msg or "this is a black thing, isnt it" in msg:
            await message.channel.send("Shut up, Will.")
        if "what are you gonna do dad" in msg or "what're you gonna do dad" in msg or "whatre you gonna do dad" in msg:
            await message.channel.send("In the middle of the night...")
        if "no more hugs will" in msg:
            await message.channel.send("You owe me!")
        if "you ever feel like this" in msg:
            await message.channel.send("All the time.")
        if "i think he likes you" in msg:
            await message.channel.send("When you look this good, you have to get used to it.")
        if "i think he's a cop" in msg or "i think hes a cop" in msg:
            await message.channel.send("Turn yourself in, Will! It's the only way!")
        if "don't talk to my wife like that" in msg or "dont talk to my wife like that" in msg:
            await message.channel.send("Now wait a minute buddy! Would you please sit down?")
        if "my buddy likes you" in msg:
            await message.channel.send("*opens jail door*")
        if "pick up the damn phone" in msg:
            await message.channel.send("Children. Die a violent death.")
        if "who cares what you think you're not my " in msg or "who cares what you think youre not my " in msg:
            await message.channel.send(":(")
        if "smith has arrived" in msg:
            await message.channel.send("Who is this?")
        if "let's have sex" in msg or "lets have sex" in msg:
            await message.channel.send("Philip Banks Philip Banks-- What are you doing?")
        if "as stupid as you uncle phil" in msg or "as stupit as you uncle fill" in msg:
            await message.channel.send("D:")
        if "i think i'm having a heart attack" in msg or "i think im having a heart attack" in msg:
            await message.channel.send("Who cares what you think, you're not my mother!")
        if "welcome you to the memorial for philip banks" in msg:
            await message.channel.send("Saying a few words on behalf of the departed will be Philip Banks.")
        if "what can you say about philip banks" in msg and not "the heck" in msg:
            await message.channel.send("What the heck can you say about Philip Banks?")
        if "what the heck can you say about philip banks" in msg:
            await message.channel.send("Okay, somebody bury this.")
        if "do you realize you're fat" in msg or "do you realize youre fat" in msg:
            await message.channel.send("My father's not fat. He's just big.")
        if "shut up will" in msg:
            await message.channel.send("But it isn't Will.")
        if "how many feet" in msg:
            await message.channel.send("Two!")
        if "i might as well kick it" in msg:
            await message.channel.send("You love me!")
        if "got to fix our air" in msg:
            await message.channel.send("Nope! Nope, nope! Nope nope nope!")
        if "would you like a swedish meatball sir" in msg:
            await message.channel.send("Only one, sir.")
        if "would fix the air conditioner in the poolhouse" in msg:
            await message.channel.send("You will not speak of uncle Phil that way! He may be an unreasonable dickhead, but he is your father, and you will show him some respect!")
        if "do you know how humiliating it is to have a son" in msg:
            await message.channel.send("I want your bodies.")
        if msg.startswith("ointments") or ("ointments" in msg and "appointment" not in msg):
            await message.channel.send("Ointments...")
        if "i have to knock you out" in msg:
            await message.channel.send("You come near me, I'll spray.")
        if "you selfish" in msg or "you sell fish" in msg:
            await message.channel.send("Ooh!")
        if "why do you shave ashley's ass" in msg or "why do you shave ashleys ass" in msg:
            await message.channel.send("Because women grow hair on their BUTT. Yes.")
        if "would you look at all this wood" in msg:
            await message.channel.send("I'm not carrying all of this wood.")

        if "a better man than me" in msg:
            await message.channel.send("ᵉeₑeᵉeₑeᵉ")

async def setup(client):
    await client.add_cog(YTPQuotes(client))
