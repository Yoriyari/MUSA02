#===============================================================================
# Counter v1.0.2
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 05 May 2024 - v1.0.2; Reworked help message import. Added error handling. -YY
# 01 May 2024 - v1.0.1; Added !button as alias. -YY
# 30 Sep 2022 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# counting.py creates an interactable red button which displays how many times
# it has ever been pressed by any user.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands
from discord import ui

from common.error_message import send_error
from common.help_message import send_help

#Get current total count value from file
def get_count():
    with open("data/musa_button_counter.txt", "r") as file_counter:
        count = file_counter.read()
    return int(count)

#Save new total count value to file
def set_count(count):
    with open("data/musa_button_counter.txt", "w") as file_counter:
        file_counter.write(f"{str(count)}")

#Set counter button label
def counter_label():
    return f"Times pressed: {get_count()}"

#Button Setup
class CounterButton(ui.View):
    def __init__(self):
        super().__init__(timeout=259200)

    @ui.button(label="Times pressed: ...", style=discord.ButtonStyle.red)
    async def counter(self, interaction, button):
        set_count(get_count()+1)
        button.label = counter_label()
        await interaction.response.edit_message(view=self)

#Cog Setup
class Counter(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Counter cog loaded.")

    @commands.group(name="counter", aliases=["counting", "count", "button"], case_insensitive=True, invoke_without_command=True)
    async def counter(self, ctx):
        try:
            button = CounterButton()
            button.children[0].label = counter_label()
            await ctx.channel.send(view=button)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @counter.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def counter_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "counting")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

async def setup(client):
    await client.add_cog(Counter(client))
