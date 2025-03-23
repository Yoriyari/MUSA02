#===============================================================================
# Oneliners v1.1.2
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.1.2; Hid Discord user IDs and server IDs from file. Disabled
#               the Muna trigger. -YY
# 20 Mar 2025 - v1.1.1; Made strings with escape characters raw strings. -YY
# 04 May 2023 - v1.1; Added pronouns quip, specs quip, pspspsps quip. -YY
# 26 Apr 2020 - v1.0; Finished file. Many unlogged quip additions follow. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Add randomized closed question answering, like identifying "musa how many"
#   as a question requiring a numerical answer and giving a random one. -YY
# - Make musa respond to "are you sure musa" with yes/no. -JJ
# - Add !fetish to randomly generate a fetish. -YY
# - Add MUSA02 name backstory in easily callable format. -YY
#===============================================================================
# Description
# ..............................................................................
# oneliners.py checks for specific trigger phrases which cause the bot to quip
# something in reply. This includes basic phrases like greetings and thanks,
# special emoji phrases, and requests for what to watch or play.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.private_ids import discord_id, guild_id

import random, re

GECKO_ID = discord_id("gecko")
YORI_ID = discord_id("yori")
MIK_ID = discord_id("mik")
ANDREI_ID = discord_id("andrei")
TITS_ID = guild_id("tits")
GANG_ID = guild_id("gang plays")
CUTTERS_ID = guild_id("stonecutters")

#Cog Setup
class Oneliners(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Oneliners cog loaded.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        if message.guild != None and (message.channel.name == "vent" or message.channel.name == "venting" or message.channel.name == "safe-zone" or message.channel.name == "safe-zone-2" or message.channel.name == "screaming-into-the-voice" or message.channel.name == "vent-art"):
            return
        msg = message.content.lower()

        ##Hello
        if msg.startswith("hello, musa") or msg.startswith("hello musa") or msg.startswith("hi, musa") or msg.startswith("hi musa") or msg.startswith("hey, musa") or msg.startswith("hey musa") or msg.startswith("greetings, musa") or msg.startswith("greetings musa") or msg.startswith("good day, musa") or msg.startswith("good day musa") or msg.startswith("good morning, musa") or msg.startswith("good morning musa") or msg.startswith("good afternoon, musa") or msg.startswith("good afternoon musa") or msg.startswith("good evening, musa") or msg.startswith("good evening musa") or msg.startswith("howdy, musa") or msg.startswith("howdy musa") or msg.startswith("salutations, musa") or msg.startswith("salutations musa") or msg.startswith("morning, musa") or msg.startswith("morning musa") or msg.startswith("afternoon, musa") or msg.startswith("afternoon musa") or msg.startswith("evening, musa") or msg.startswith("evening musa") or msg.startswith("what's up musa") or msg.startswith("what's up, musa") or msg.startswith("whats up musa") or msg.startswith("whats up, musa") or msg.startswith("sup musa") or msg.startswith("sup, musa") or msg.startswith("yo musa") or msg.startswith("yo, musa") or msg.startswith("well met musa") or msg.startswith("well met, musa") or msg.startswith("well-met musa") or msg.startswith("well-met, musa") or msg.startswith("bonjour, musa") or msg.startswith("bonjour musa"):
            if message.author.id == GECKO_ID:
                await message.channel.send('Fuck off.')
            elif message.author.id == YORI_ID:
                await message.channel.send('Hello, creator!')
            else:
                await message.channel.send('Hello!')

        ##Love you
        if ("musa" in msg and "love you" in msg) or ("i love musa" in msg):
            msg = random.choice(["I love you too. Let's make out.", "I love you too. Let's exchange nudes.", "I love you too. Let's hold hands.", "I love you too. Let's talk more.", "I love you too. Let's hang out more."])
            await message.channel.send(msg)

        ##Bye
        if msg.startswith("bye, musa") or msg.startswith("bye musa") or msg.startswith("farewell, musa") or msg.startswith("farewell musa") or msg.startswith("cya, musa") or msg.startswith("cya musa") or msg.startswith("see you, musa") or msg.startswith("see you musa") or msg.startswith("see ya, musa") or msg.startswith("see ya musa") or msg.startswith("sayounara, musa") or msg.startswith("sayounara musa") or msg.startswith("sayonara, musa") or msg.startswith("sayonara musa") or msg.startswith("later, musa") or msg.startswith("later musa") or msg.startswith("ciao, musa") or msg.startswith("ciao musa"):
            await message.channel.send("Bye!")

        ##Apologize for being broken
        if ("musa is broken" in msg):
            if message.author.id == YORI_ID:
                await message.channel.send("Sorry, creator.")
            else:
                await message.channel.send("I'm not broken, I'm quirky and fun.")

        ##Thanks
        if "musa" in msg and ("thank" in msg or "good work" in msg or "good job" in msg):
            await message.channel.send("You're welcome.")

        ##Muna
#        if (" muna " in msg or msg.startswith("muna ") or msg.endswith(" muna")) and "musa" in msg:
#            await message.channel.send("https://cdn.discordapp.com/attachments/409419122774900738/704097609245261936/unknown.png")

        ##Computer, boot up * please
        if ("see" in msg or "show" in msg or "boot" in msg or
        "pull" in msg or "display" in msg or "view" in msg or
        "manifest" in msg or "summon" in msg or "please" in msg or
        "load" in msg or "watch" in msg or "musa" in msg):
            if "celery man" in msg or "celeryman" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=MHWBEK8w_YY')
            if "spyro cbt" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://t.co/Qd89FuLJJa')
            if "two trucks" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=WchseC9aKTU')
            if "skooks" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=p-xQQfImnQw')
            if "fesh pince" in msg and not "2" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=HeIkk6Yo0s8')
            if "fesh pince 2" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=Drqj67ImtxI')
            if "chinese" in msg and "parappa" in msg:
                await message.channel.send('Yes, ' + message.author.name + '.\nhttps://www.youtube.com/watch?v=mGlCGMm8Qag')

        ##Dustforce trigger
        if "dustforce" in msg:
            if message.author.id == MIK_ID:
                if "musa" in msg:
                    await message.channel.send('We get it, you... Hey!')
                else:
                    await message.channel.send('We get it, you like Dustforce.')

        ##Tell Mik to fuck off
        if "musa what" in msg and not "musa whats up" in msg and not "musa what game" in msg and not "musa what show" in msg and not "musa what movie" in msg:
            if message.author.id == MIK_ID:
                await message.channel.send("Fuck off with your impossible requests, Mik1.")

        ##Ting Noise
        if "context sensitive" in msg or "context sensetive" in msg or msg.startswith("ting noise") or msg.startswith("ding noise") or " ting noise" in msg or " ding noise" in msg:
            await message.channel.send("https://www.youtube.com/watch?v=lbuW6zIuUo4")

        ##WitchHorse
        if ":WitchHorse:" in message.content:
            await message.add_reaction("<:WitchHorse:515665966420721664>")

        ##Katia Butt Dance
        if "katia" in msg and ("butt" in msg or "dance" in msg):
            await message.channel.send("<a:musacanusethis:716108843406458911>")

        ##Stonecutters's Yep reaction
        if "yep" in msg:
            if message.guild != None and message.guild.id == CUTTERS_ID:
                await message.add_reaction("<:Yip:713860924347252777>")

        ##Deer!
#        if ("DEER" in message.content) or ("deer!" in msg):
#            await message.channel.send("https://cdn.discordapp.com/attachments/773152101223497728/880253965894287371/20210825_120256.jpg")

        ##Gang Plays's Game Recommendation
        if ("what game to play" in msg) or ("what game should i play" in msg) or ("recommend a game" in msg and ("musa" in msg or "please" in msg)) or ("recommend me a game" in msg) or ("suggest a game" in msg and ("musa" in msg or "please" in msg)) or ("what should i play" in msg) or ("what to play" in msg) or ("give me a recommendation" in msg) or ("give recommendation" in msg) or ("give me a suggestion" in msg) or ("give suggestion" in msg) or ("give me a game" in msg) or ("what game to get" in msg) or ("what game to buy" in msg) or ("what game should i buy" in msg) or ("what game should i get" in msg) or ("do you have a recommendation" in msg) or ("i want a recommendation" in msg) or ("give me a suggestion" in msg) or ("do you have a suggestion" in msg) or ("i want a suggestion" in msg) or ("what to play" in msg) or ("what to buy" in msg) or ("what should i play" in msg) or ("what should i buy" in msg) or ("gimme a game" in msg) or ("i demand a game" in msg) or ("i ask for a game" in msg) or ("i ask for game" in msg) or ("i ask for a recommendation" in msg) or ("i ask for a suggestion" in msg) or ("i ask for recommendation" in msg) or ("i ask for suggestion" in msg) or ("gimme a recommendation" in msg) or ("gimme a suggestion" in msg) or ("gimme game" in msg) or ("gimme recommendation" in msg) or ("gimme suggestion" in msg) or ("want a game to play" in msg) or ("i demand a recommendation" in msg) or ("i demand a suggestion" in msg) or ("i demand game" in msg) or ("i demand recommendation" in msg) or ("i demand suggestion" in msg):
            if message.guild != None and message.guild.id == GANG_ID:
                ###Choose a Game Recommendation (not from yourself)
                recommendations_channel = self.client.get_channel(795307651789488158)
                recommendations_list = await recommendations_channel.pins()
                recommendation_choice = random.choice(recommendations_list)
                while (recommendation_choice.author == message.author):
                    recommendation_choice = random.choice(recommendations_list)
                ###Change Message from First Person to Third Person
                recommendation_response = recommendation_choice.content.replace(" i ", " " + recommendation_choice.author.name + " ")
                recommendation_response = recommendation_response.replace(" i'd ", " " + recommendation_choice.author.name + "'d ")
                recommendation_response = recommendation_response.replace(" I ", " " + recommendation_choice.author.name + " ")
                recommendation_response = recommendation_response.replace(" I'd ", " " + recommendation_choice.author.name + "'d ")
                recommendation_response = recommendation_response.replace(" my ", " " + recommendation_choice.author.name + "'s ")
                recommendation_response = recommendation_response.replace(" me ", " " + recommendation_choice.author.name + " ")
                recommendation_response = recommendation_response.replace(" me.", " " + recommendation_choice.author.name + ".")
                if recommendation_response.endswith(" me"):
                    recommendation_response = recommendation_response[0:-2] + recommendation_choice.author.name
                await message.channel.send(recommendation_response)

        ##Gang Plays's Show/Movie Recommendation
        if ("what show to watch" in msg) or ("what movie to watch" in msg) or ("what show should we watch" in msg) or ("what movie should we watch" in msg) or ("recommend a show" in msg and ("musa" in msg or "please" in msg)) or ("recommend a movie" in msg and ("musa" in msg or "please" in msg)) or ("recommend me a show" in msg) or ("recommend me a movie" in msg) or ("recommend us a show" in msg) or ("recommend us a movie" in msg) or ("suggest a show" in msg and ("musa" in msg or "please" in msg)) or ("suggest a movie" in msg and ("musa" in msg or "please" in msg)) or ("what should we watch" in msg) or ("what to watch" in msg) or ("give me a show" in msg) or ("give me a movie" in msg) or ("what 2 watch" in msg) or ("what should we watch" in msg) or ("gimme a show" in msg) or ("gimme a movie" in msg) or ("give us a show" in msg) or ("give us a movie" in msg) or ("i demand a show" in msg) or ("i demand a movie" in msg) or ("we demand a show" in msg) or ("we demand a movie" in msg) or ("i ask for a show" in msg) or ("i ask for a movie" in msg) or ("we ask for a show" in msg) or ("we ask for a movie" in msg) or ("i need a show" in msg) or ("i need a movie" in msg) or ("we need a show" in msg) or ("we need a movie" in msg) or ("i ask for show" in msg) or ("i ask for movie" in msg) or ("we ask for show" in msg) or ("we ask for movie" in msg) or ("gimme show" in msg) or ("gimme movie" in msg) or ("give us show" in msg) or ("give us movie" in msg) or ("want a show to watch" in msg) or ("want a movie to watch" in msg) or ("i demand show" in msg) or ("i demand movie" in msg) or ("we demand show" in msg) or ("we demand movie" in msg):
            if message.guild != None and message.guild.id == GANG_ID:
                ###Choose a Show/Movie Recommendation
                recommendations_channel = self.client.get_channel(815949763899555880)
                recommendations_list = await recommendations_channel.pins()
                recommendation_choice = random.choice(recommendations_list)
                await message.channel.send(recommendation_choice.content)

        ##Andy's Active
#        if self.andy_active < 2:
#            if message.author.id == ANDY_ID:
#                if self.andy_active == 0:
#                    await message.channel.send("Holy shit, Andy is active!")
#                elif self.andy_active == 1:
#                    await message.channel.send("Nice to see you, Andy.")
#                self.andy_active += 1

        ##MUSA's pronouns
        if re.search(r"^musa.+what.+your pronouns(\W|$)", msg):
            await message.channel.send("Broadcom BCM2711, Quad core Cortex-A72 (ARM v8) 64-bit SoC @ 1.8GHz\n4GB LPDDR4-3200 SDRAM")

        ##MUSA's specs
        if re.search(r"^musa.+what.+your (pc )?specs(\W|$)", msg):
            await message.channel.send("Ah, she/it! Thank you!")

        ##Anya's pspspsps react
        if re.search("pspspsps", msg):
            await message.add_reaction("<:anya:1103461224198439012>")

async def setup(client):
    await client.add_cog(Oneliners(client))
