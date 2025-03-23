#===============================================================================
# Dungeons and Dragons v0.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 06 May 2024 - Added a help command and reworked error handling. -YY
# 21 Oct 2022 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# dnd.py displays and handles the main menu of the bot's D&D functionality.
#===============================================================================

#Import Modules
import discord
from discord import Embed, ui
from discord.ext import commands

from cogs.classes import message_examineclassesmenu as classes_message
from cogs.classes import ExamineClassesMenu as ClassesMenu
from cogs.items import message_selectcategorymenu as items_message
from cogs.items import MainMenu as ItemsMenu
from cogs.spells import message_mainmenu as spells_message
from cogs.spells import MainMenu as SpellsMenu
from common.error_message import send_error
from common.help_message import send_help

view_timeout = 259200

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#User Interface elements

#Main menu
class MainMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=view_timeout)
        #self.add_item(CharactersButton())
        self.add_item(ClassesButton())
        self.add_item(ItemsButton())
        self.add_item(SpellsButton())
        #self.add_item(RulesButton())

class ClassesButton(ui.Button):
    def __init__(self):
        super().__init__(label="Classes", style=discord.ButtonStyle.grey, emoji="👥", row=3)

    async def callback(self, interaction):
        try:
            await interaction.response.send_message(classes_message(), view=ClassesMenu(), ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ItemsButton(ui.Button):
    def __init__(self):
        super().__init__(label="Items", style=discord.ButtonStyle.grey, emoji="🗃️", row=3)

    async def callback(self, interaction):
        try:
            await interaction.response.send_message(items_message(), view=ItemsMenu(), ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SpellsButton(ui.Button):
    def __init__(self):
        super().__init__(label="Spells", style=discord.ButtonStyle.grey, emoji="📚", row=3)

    async def callback(self, interaction):
        try:
            await interaction.response.send_message(spells_message(), view=SpellsMenu(), ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

#User Interface elements
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Bot commands

#Cog Setup
class DnD(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("DnD cog loaded.")

    #Character Sheet
    @commands.group(name="dnd", aliases=["d&d"], case_insensitive=True, invoke_without_command=True)
    async def dnd(self, ctx):
        try:
            await ctx.channel.send(view=MainMenu())
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @dnd.command(aliases=["help", "?", "info", "information", "instructions"])
    async def dnd_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "dnd")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

async def setup(client):
    await client.add_cog(DnD(client))
