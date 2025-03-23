#===============================================================================
# Rock Paper Scissors v1.0.3
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 20 Mar 2025 - v1.0.3; Made strings with escape characters raw strings. -YY
# 05 May 2024 - v1.0.2; Reworked help message import and error handling. -YY
# 04 Nov 2023 - v1.0.1; Extended View timer from 8 hours to 24 hours. -YY
# 14 Oct 2023 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# rockpaperscissors.py lets two users play rock paper scissors again each other.
#===============================================================================

#Import Modules
import discord
from discord import Embed, ui
from discord.ext import commands

from common.error_message import send_error
from common.help_message import send_help

import random, re

view_timeout = 86400 # 24 hours

#-------------------------------------------------------------------------------

#Cog Setup
class RockPaperScissors(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Rock Paper Scissors cog loaded.")

    @commands.group(name="rockpaperscissors", aliases=["rps", "rock", "paper", "scissors", "rock_paper_scissors", "janken", "jankenpon", "jkp"], case_insensitive=True, invoke_without_command=True)
    async def rockpaperscissors(self, ctx, target=None):
        '''Sends a message to begin playing rock paper scissors. If the user
        specifies another Discord user after the command, the game is set to be
        between the two users. Otherwise, anyone can join.
        '''
        try:
            # Determine target
            p1_id = None
            p2_id = None
            if target != None:
                if not re.match(r"^<@\d+>$", target):
                    msg = "To challenge a specific user, @ them after the command. To present an open challenge for anyone, don't append anything after the command."
                    await ctx.channel.send(msg)
                    return
                else:
                    p1_id = ctx.author.id
                    p2_id = int(target.lstrip("<@").rstrip(">"))
            msg = generate_rps_message(p1_id=p1_id, p2_id=p2_id)
            view = ViewRPS(p1_id=p1_id, p2_id=p2_id)
            await ctx.channel.send(msg, view=view)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @rockpaperscissors.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def rps_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "rockpaperscissors")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#-------------------------------------------------------------------------------

def generate_rps_message(p1_ready=False, p1_hand=None, p1_id=None, p1_wins=0, p2_ready=False, p2_hand=None, p2_id=None, p2_wins=0):
    '''Generates the message contents for rock paper scissors games.
    Features the title, info for player 1 and 2, win message and play prompt.
    '''
    msg = "## \\- Rock Paper Scissors -\n"
    msg += "⬛ " if not p1_ready else "✅ "
    msg += "❓ " if p1_ready != p2_ready or not (p1_hand or p2_hand) else f"{p1_hand} "
    msg += "`Player 1`" if not p1_id else f"<@{p1_id}>"
    if p1_wins + p2_wins == 1:
        msg += " (loser)" if p1_wins <= 0 else " (winner)"
    if p1_wins + p2_wins > 1:
        plural = "s" if p1_wins != 1 else ""
        msg += f" ({p1_wins} win{plural})"
    msg += "\n"
    msg += "⬛ " if not p2_ready else "✅ "
    msg += "❓ " if p1_ready != p2_ready or not (p1_hand or p2_hand) else f"{p2_hand} "
    msg += "`Player 2`" if not p2_id else f"<@{p2_id}>"
    if p1_wins + p2_wins == 1:
        msg += " (loser)" if p2_wins <= 0 else " (winner)"
    if p1_wins + p2_wins > 1:
        plural = "s" if p2_wins != 1 else ""
        msg += f" ({p2_wins} win{plural})"
    msg += "\n"
    if not p1_hand or not p2_hand:
        msg += "### Awaiting players...\n"
    elif p1_ready != p2_ready:
        msg += "### Awaiting rematch...\n"
    else:
        winner = get_rps_winner(p1_hand, p2_hand)
        if winner == 0:
            msg += "### Tie!\n"
        elif winner == 1:
            msg += f"### <@{p1_id}> wins!\n"
        elif winner == 2:
            msg += f"### <@{p2_id}> wins!\n"
        else:
            msg += "### Error.\n"
    if not p1_hand or not p2_hand:
        msg += "Pick any hand to play!"
    else:
        msg += "Pick any hand to have a rematch!"
    return msg

def get_rps_winner(p1_hand=None, p2_hand=None):
    '''Determines the winner between two specified rock paper scissors emoji.
    Returns 0 for tie, 1 for first player, 2 for second player.
    '''
    if p1_hand == "✊":
        if p2_hand == "✊":
            return 0
        if p2_hand == "✋":
            return 2
        if p2_hand == "✌":
            return 1
    if p1_hand == "✋":
        if p2_hand == "✊":
            return 1
        if p2_hand == "✋":
            return 0
        if p2_hand == "✌":
            return 2
    if p1_hand == "✌":
        if p2_hand == "✊":
            return 2
        if p2_hand == "✋":
            return 1
        if p2_hand == "✌":
            return 0
    raise Exception(f"Undefined rock paper scissors matchup: '{p1_hand}' VS '{p2_hand}'")

#-------------------------------------------------------------------------------

class ViewRPS(ui.View):
    def __init__(self, p1_ready=False, p1_hand=None, p1_id=None, p1_wins=0, p2_ready=False, p2_hand=None, p2_id=None, p2_wins=0):
        super().__init__(timeout=view_timeout)
        self.add_item(ButtonRPS("✊", p1_ready, p1_hand, p1_id, p1_wins, p2_ready, p2_hand, p2_id, p2_wins))
        self.add_item(ButtonRPS("✋", p1_ready, p1_hand, p1_id, p1_wins, p2_ready, p2_hand, p2_id, p2_wins))
        self.add_item(ButtonRPS("✌", p1_ready, p1_hand, p1_id, p1_wins, p2_ready, p2_hand, p2_id, p2_wins))

class ButtonRPS(ui.Button):
    def __init__(self, emoji=None, p1_ready=False, p1_hand=None, p1_id=None, p1_wins=0, p2_ready=False, p2_hand=None, p2_id=None, p2_wins=0):
        super().__init__(emoji=emoji, style=discord.ButtonStyle.grey)
        self.button_hand = emoji
        self.p1_ready = p1_ready
        self.p1_hand = p1_hand
        self.p1_id = p1_id
        self.p1_wins = p1_wins
        self.p2_ready = p2_ready
        self.p2_hand = p2_hand
        self.p2_id = p2_id
        self.p2_wins = p2_wins
    async def callback(self, interaction):
        '''Main game handling.
        Processes players changing their hand and readying up, adding wins to
        the counter and giving the subsequent results.
        '''
        try:
            user_id = interaction.user.id
            if self.p1_id == None:
                self.p1_id = user_id
            elif self.p2_id == None and self.p1_id != user_id:
                self.p2_id = user_id
            if user_id == self.p1_id:
                self.p1_hand = self.button_hand
                self.p1_ready = True
                # Challenging the bot itself
                if self.p2_id == interaction.client.user.id:
                    self.p2_hand = random.choice(["✊", "✋", "✌"])
                    self.p2_ready = True
            elif user_id == self.p2_id:
                self.p2_hand = self.button_hand
                self.p2_ready = True
            else:
                return
            if self.p1_ready and self.p2_ready:
                self.p1_ready = False
                self.p2_ready = False
                winner = get_rps_winner(self.p1_hand, self.p2_hand)
                if winner == 1:
                    self.p1_wins += 1
                if winner == 2:
                    self.p2_wins += 1
            msg = generate_rps_message(self.p1_ready, self.p1_hand, self.p1_id, self.p1_wins, self.p2_ready, self.p2_hand, self.p2_id, self.p2_wins)
            view = ViewRPS(self.p1_ready, self.p1_hand, self.p1_id, self.p1_wins, self.p2_ready, self.p2_hand, self.p2_id, self.p2_wins)
            await interaction.response.edit_message(content=msg, view=view)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

async def setup(client):
    await client.add_cog(RockPaperScissors(client))
