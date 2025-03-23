#===============================================================================
# Steve-O v1.0.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 06 May 2024 - v1.0.1; Added a help command and error handling. -YY
# 19 Apr 2022 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# steveo.py sends a random image of some dude named Steve-O. I was requested to
# make this for a server and I have no idea who this dude is.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.help_message import send_help
from common.error_message import send_error

import random

#Cog Setup
class SteveO(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Steve-O cog loaded.")

    @commands.group(name="steveo", aliases=["steve-o"], case_insensitive=True, invoke_without_command=True)
    async def steveo(self, ctx):
        try:
            imageset=["https://cdn.discordapp.com/attachments/965694314770489394/965694330184536074/9738d83cd48d42979092bd3a646afd15.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965910154862268456/Go--RMZCDly3SxNofazEuWZIBYO0JzGHT0Ki1Af4H_s.jpg",
                      "https://cdn.discordapp.com/attachments/965694314770489394/965694754899779644/1650309959354.jpg",
                      "https://cdn.discordapp.com/attachments/406524495806070806/965716542945902713/EZFxB7uX0AA7D19.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965908726659833916/ea7c0f00-a1cd-4fb3-bd18-0deee5df5880-STEVEO_8_FULLRES_JPG.jpeg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965908800890630154/199909289_STEVEO_ORIG_t800.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965908859833176114/Steve-O-H-2022.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965909278525382656/gettyimages-117898389-612x612.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965909287266304050/Jeff-Hardy-Jackass-Steve-O-WWE-696x393.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965909400617373747/tumblr_n2494i0zio1rutp1jo1_500.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965909475749933076/2FB1365D00000578-0-image-m-67_1451536428232.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965909847864397824/images_-_2022-04-19T104023.971.jpeg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965909967745986580/1002254509-photo-u1.jpeg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965910463168790528/Steve-O-Vegan-Canada-Cattle-Province.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965910548074086400/gettyimages-947678702.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965911048542646362/6a00d8341c630a53ef01348832c7e3970c.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965911048764948500/MV5BMjIyNTAzOTM2N15BMl5BanBnXkFtZTYwNjE5MDM4._V1_UY1200_CR13606301200_AL_.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965911048987238410/SteveO-Promo8.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965912510588915722/hlh030122feasteveo-001-1-1642610230.png",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965912756203180082/gettyimages-1816200-2048x2048.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965912816458539058/download_-_2022-04-19T105235.551.jpeg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965913150463574036/Dn4M7EUVYAAEX7L.jpg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965913701771264000/images_-_2022-04-19T105605.828.jpeg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965915076521525308/steve-o323_.jpeg",
                      "https://cdn.discordapp.com/attachments/611585017973440528/965916711633178734/d7c0ban-9df51bc8-074a-4915-80e6-6d1976244402.jpg",
                      "https://cdn.discordapp.com/attachments/409419122774900738/965937717152219189/DqpAZlLVYAE6GAD.jpg",
                      "https://cdn.discordapp.com/attachments/965771368316690442/965968110018502706/e4c6969d697d91bf263185be0c22ae52.jpg",
                      "https://cdn.discordapp.com/attachments/965771368316690442/965968110744109066/f1ca27be66c615d00dff25fdbb376b99.jpg",
                      "https://cdn.discordapp.com/attachments/965771368316690442/965968111016767508/1c9159d17b5ee46ce63a647ee8c8d71c.jpg",
                      "https://cdn.discordapp.com/attachments/965771368316690442/965968111301959720/9235eb78acd9c7eb2b4615359d64ad19.jpg"
                     ]
            await ctx.channel.send(random.choice(imageset))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @steveo.command(aliases=["help", "?", "info", "information", "instructions"])
    async def steveo_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "steveo")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.client.user:
            return
        if message.guild == None:
            return
        if message.guild.id != 406524495806070804:
            return
        msg = message.content.lower()

        if msg == "famous vegans":
            await message.channel.send("https://cdn.discordapp.com/attachments/965694314770489394/965694330184536074/9738d83cd48d42979092bd3a646afd15.jpg")
        if msg == "lunch":
            await message.channel.send("https://cdn.discordapp.com/attachments/611585017973440528/965910154862268456/Go--RMZCDly3SxNofazEuWZIBYO0JzGHT0Ki1Af4H_s.jpg")
        if msg == "stove":
            await message.channel.send("https://cdn.discordapp.com/attachments/965694314770489394/965694754899779644/1650309959354.jpg")

async def setup(client):
    await client.add_cog(SteveO(client))
