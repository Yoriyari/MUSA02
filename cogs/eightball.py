#===============================================================================
# Magic 8 Ball v1.0.5
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.0.5; Hid Discord user IDs from file. -YY
# 28 Nov 2024 - v1.0.4; Updated name "Heart8reaker" to "Tara". -YY
# 05 Sep 2024 - v1.0.3; Fixed `options` copying the answers list reference
#               pointer rather than the list entries. -YY
# 03 Sep 2024 - v1.0.2; Removed an obsolete function. -YY
# 05 May 2024 - v1.0.1; Reworked help message import and error handling. -YY
# 03 Mar 2021 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# eightball.py returns a random answer from a magic 8 ball upon usage. Also
# includes a few specific answers for Heart8reaker Wasabi Tara Spice if Veronica
# uses the command and a 1% chance of exploding in your face.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands
from discord import app_commands

from common.private_ids import discord_id
from common.error_message import send_error
from common.help_message import send_help

import random

#-------------------------------------------------------------------------------
#Constants
EIGHTBALL_ANSWERS = [
    "It is certain.",
    "It is decidedly so.",
    "Without a doubt.",
    "Yes definitely.",
    "You may rely on it.",
    "As I see it, yes.",
    "Most likely.",
    "Outlook good.",
    "Yes.",
    "Signs point to yes.",
    "Reply hazy, try again.",
    "Ask again later.",
    "Better not tell you now.",
    "Cannot predict now.",
    "Concentrate and ask again.",
    "Don't count on it.",
    "My reply is no.",
    "My sources say no.",
    "Outlook not so good.",
    "Very doubtful."
]
VERONICA_ID = discord_id("veronica")
HEARTBREAKER_ANSWERS = [
    "You'd know better than me.",
    "Are you seriously asking that?",
    "Ask Tara.",
    "I don't love your odds.",
    "I thought you didn't believe in fate.",
    "Don't bet on it.",
    "I'd go all in on it."
]

#-------------------------------------------------------------------------------
#Cog Setup
class EightBall(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("8 Ball cog loaded.")

    @app_commands.command(name="8ball", description="Sends a random magic 8 ball answer.")
    async def slash_eightball(self, interaction):
        '''Sends a random appropriate magic 8 ball answer.
        '''
        try:
            await handle_eightball_command(interaction.user.id, interaction.response.send_message)
        except Exception as e:
            await send_error(self.client, e, reference=interaction.message.jump_url)

    @commands.group(name="eightball", aliases=["8ball", "eight8all", "88all"], case_insensitive=True, invoke_without_command=True)
    async def eightball(self, ctx):
        '''Sends a random appropriate magic 8 ball answer.
        '''
        try:
            await handle_eightball_command(ctx.author.id, ctx.channel.send)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @eightball.command(aliases=["help", "?", "info", "information", "instructions"])
    async def eightball_help(self, ctx):
        '''Sends a message describing how to use the eightball command.
        '''
        try:
            await send_help(ctx.channel.send, "eightball")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#-------------------------------------------------------------------------------
#Auxiliary Functions
async def handle_eightball_command(author_id, send):
    '''Returns a magic 8 ball answer. Includes special answers if a specific
    user, namely Veronica, invoked the command.
    '''
    is_invoked_by_veronica = did_member_send_command(VERONICA_ID, author_id)
    answer = get_eightball_answer(use_special_answers=is_invoked_by_veronica)
    await send(answer)

def get_eightball_answer(use_special_answers=False):
    '''Returns a magic 8 ball answer. Included among the possible answers are
    some special answers if use_special_options is enabled.
    '''
    explode_at_one_percent_odds = random.random() < 0.01
    if explode_at_one_percent_odds:
        return "I will explode in your face."
    options = EIGHTBALL_ANSWERS.copy()
    if use_special_answers:
        options += HEARTBREAKER_ANSWERS
    return random.choice(options)

def did_member_send_command(member_id, command_invoker_id):
    '''Returns True if the command was invoked by the member with member_id.
    Returns False otherwise.
    '''
    return member_id == command_invoker_id

#-------------------------------------------------------------------------------
#Add Cog
async def setup(client):
    await client.add_cog(EightBall(client))
