#===============================================================================
# Information v2.0
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 02 May 2024 - v2.0; Moved help messages from common to a database so that I
#               can update them dynamically. -YY
# 19 Oct 2022 - v1.2; Renamed from features.py to information.py to prevent
#               collision with future D&D commands. -YY
# 25 Jan 2022 - v1.1; Centralized help messages in help_messages.py and had this
#               file import from there. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Add pagination to help command. -YY
#===============================================================================
# Description
# ..............................................................................
# information.py serves as the bot's help command. Any documentation needed for
# the various features of the bot can be requested through this file.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.help_message import send_help
from common.error_message import send_error

HELP_MESSAGES_FILE = "data/help_messages.yml"

#-------------------------------------------------------------------------------
#Cog Setup
class Information(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Information cog loaded.")

    @commands.group(name="information", aliases=["help", "info", "instructions"], case_insensitive=True, invoke_without_command=True)
    async def information(self, ctx, command="help"):
        try:
            await send_help(ctx.channel.send, command)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#-------------------------------------------------------------------------------
#Add Cog
async def setup(client):
    await client.add_cog(Information(client))
