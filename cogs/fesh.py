#===============================================================================
# Fesh Pince v1.2.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 05 May 2024 - v1.2.1; Reworked help message import. Added error handling. -YY
# 26 Mar 2024 - v1.2; Added slash command. -YY
# 17 Apr 2022 - v1.1; Centralized help messages to one importable file. Added a
#               help command to this file. -YY
# 27 Apr 2020 - v1.0; Finished file. -YY
# 26 Apr 2020 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# fesh.py sends a random quote from the Fesh Pince of Blair videos on request.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands
from discord import app_commands

from common.error_message import send_error
from common.help_message import send_help

import random

#-------------------------------------------------------------------------------
#Cog Setup
class Fesh(commands.Cog):

    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Fesh cog loaded.")

    @app_commands.command(name="fesh", description="Sends a random Fesh Pince quote.")
    async def slash_fesh(self, interaction):
        quote = get_random_fesh_quote()
        await interaction.response.send_message(quote)

    ##Fesh Pince
    @commands.group(name="fesh", aliases=["feshpince", "pince", "fesh_pince"], case_insensitive=True, invoke_without_command=True)
    async def fesh(self, ctx):
        try:
            quote = get_random_fesh_quote()
            await ctx.channel.send(quote)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @fesh.command(aliases=["info"], case_insensitive=True, invoke_without_command=True)
    async def help(self, ctx):
        try:
            await send_help(ctx.channel.send, "fesh")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#-------------------------------------------------------------------------------
#Auxiliary Functions
def get_random_fesh_quote():
    quotes = ["Drink 5 hour energy", "It's not a drink, more like a drink.", "Hillary, how did you know that?", "Would you make me a sandwich?", "nOo", "What the heck is this?", "It's ponies, dad.", "It's Fesh Pince, dad.", "This is the story all about how my life got flip-turned upside down.", "I'm gonna get dad what he always wanted.", "What, a pizza hut in the garage?", "Look at those funny little markings underneath the pictures.", "I can't read.", "You swindled me!", "I was saving that money to buy pot.", "It's C-E-A-E-R-E-L-E-T-E-O-N-E. No E.", "I think you're being really unreasonable.", "Well, tough shit. I don't care.", "Banks wants to empty the banks.", "But dad, aren't some of those banks?", "You've got to kick that man's butt.", "Philip Banks, you should kick my butt.", "It goes against everything I stand for.", "What's your point?!", "Including your lovely daughter, KFC!", "Are you free for dinner tonight?", "My father just lost an erection.", "Let's get the hell out of here.", "There goes Philip Banks, the biggest ASS, that ever lived. What a douche.", "Oh my god, he's god.", "I'd like to welcome you to the memorial for Carlton.", "Saying a few words on behalf of the departed will be Philips.", "What can you say about carlton?", "He was Carlton.", "And who are you?!", "I'm the Dude.", "Look, I think I know how to help Will.", "We've got to attack him.", "I'm gonna shit my pants.", "Philip, no! How could you say numbers numbers numbers", "Heaven has to be like a cross between a dikekike video and chickenishwingigish.", "You see, it's like, I could have a leg in one hand, and a brerb in the other.", "Let me tell you boys something about women.", "Nefafefafefaf, nefafefafefaf.", "Something about women.", "My first short story.", "Your first short story and your first short story in the same room!", "What do you say, Geoffrey? Want a W?", "What the fuck.", "Who is the question?", "The Minnipilization.", "Are you sure we should do this?", "It's either this, or this.", "Ponies are coming on!", "Turn it up! Turn it up!", "Why, Geoffrey? Do you like ponies?", "*waves around an Applejack toy*", "Are you out of your horny little adolescent minds?!", "I know I am, dad!", "How do you think Jim feels when he changes into his gym shorts?", "Hey, what's that supposed to mean?", "This is my mother, Carlton.", "Imma coming, Luigi!", "Yo yo yo! My brother, Carlton!", "Mr. Banks, your opening statement.", "Mr. Smith, your opening statement.", "Statement.", "This is a black thing, isn't it?", "Shut up, Will.", "What are you gonna do, dad?", "In the middle of the night...", "No more hugs, Will.", "You owe me!", "Yo Carlton, you ever feel like this?", "All the time.", "I think he likes you.", "When you look this good, you have to get used to it.", "I think he's a cop.", "Turn yourself in, Will! It's the only way!", "Don't talk to my wife like that!", "Now wait a minute buddy! Would you please sit down?", "My buddy likes you.", "Pick up the damn phone!", "Children. Die a violent death.", "Who cares what you think, you're not my father!", "Mr. Smith has arrived.", "Who is this?", "Let's have sex.", "Philip Banks Philip Banks-- What are you doing?", "I'm sorry not everybody can be as stupid as you, Uncle Phil.", "I think I'm having a heart attack.", "Who cares what you think, you're not my mother!", "I'd like to welcome you to the memorial for Philip Banks.", "Saying a few words on behalf of the departed will be Philip Banks.", "What can you say about Philip Banks?", "What the heck can you say about Philip Banks?", "Okay, somebody bury this.", "Do you realize you're fat?", "My father's not fat. He's just big.", "But it isn't Will.", "How many feet?", "Two, your nastiness!", "I might as well kick it.", "You love me!", "You've got to fix our air conditioning today.", "Nope! Nope, nope! Nope nope nope!", "Would you like a swedish meatball, sir?", "Ah-ah, only one, sir.", "I wish dad would fix the air conditioner in the poolhouse. How could he be so cruelhouse?", "You will not speak of uncle Phil that way! He may be an unreasonable dickhead, but he is your father, and you will show him some respect!", "Do you know how humiliating it is to have a son?", "I want your bodies.", "Ointments.", "Carlton, man, I have to knock you out.", "You come near me, I'll spray.", "Come on, snap out of it man!", "You selfish.", "Why do you shave Ashley's asscheeks?", "Because women grow hair on their BUTT. Yes.", "Would you look at all this wood?", "I'm not carrying all of this wood."]
    return random.choice(quotes)

#-------------------------------------------------------------------------------
#Add Cog
async def setup(client):
    await client.add_cog(Fesh(client))
