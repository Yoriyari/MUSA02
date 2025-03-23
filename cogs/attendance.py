#===============================================================================
# Attendance v1.0.3
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 20 Mar 2025 - v1.0.3; Made strings with escape characters raw strings. -YY
# 14 Aug 2024 - v1.0.2; Increased view timeout time to 7 days. -YY
# 05 May 2024 - v1.0.1; Reworked help message import. Added error handling. -YY
# 22 Apr 2022 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# attendance.py lets an user call for a roll call of sorts to be posted. The
# user specifies how many users should make their presence known, and the bot
# posts a message with a list with that many empty slots. Any user can then
# press a button on that message to join the list until it is full.
#===============================================================================

#Import Modules
import discord
from discord import Embed, ui
from discord.ext import commands

from common.error_message import send_error
from common.help_message import send_help

import math, re

view_timeout = 604800 # 7 days
entries_per_field = 25

#-------------------------------------------------------------------------------

#Cog Setup
class Attendance(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Attendance cog loaded.")

    @commands.group(name="attendance", aliases=["rollcall", "roll_call", "rolecall", "role_call"], case_insensitive=True, invoke_without_command=True)
    async def attendance(self, ctx, length=None):
        '''Posts a message with an amount of empty slots equal to the length
        parameter, including a button for any user to join the list.
        '''
        try:
            if not length or length == "help" or length == "info":
                await send_help(ctx.channel.send, "attendance")
                return
            if not re.search(r"^\d+$", length):
                await ctx.channel.send("Please submit only a number after the command.")
                return
            length = int(length)
            if length > 25*entries_per_field:
                await ctx.channel.send(f"{length} exceeds the maximum list length of {25*entries_per_field}.")
                return
            if length <= 0:
                await ctx.channel.send(f"Please submit a number greater than zero.")
                return
            embed = generate_attendance_list_embed(length)
            view = ViewAttendance(embed)
            await ctx.channel.send(embed=embed, view=view)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @attendance.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def attendance_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "attendance")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#-------------------------------------------------------------------------------

def generate_attendance_list_embed(length):
    title = "Attendance List"
    field_quantity = math.ceil(length/entries_per_field)
    final_field_length = length - (field_quantity-1)*entries_per_field
    content = "—\n" * entries_per_field
    embed = Embed(title=title)
    title = "\u200b"
    for i in range(field_quantity):
        if i+1 == field_quantity:
            content = "—\n" * final_field_length
        embed.add_field(name=title, value=content)
    return embed

def add_or_remove_user_on_list(embed, user_id):
    '''Adds the user_id to the first empty slot if they're not on the list yet.
    Replaces the user_id with an empty slot if they're already on the list.
    '''
    field = first_field_with_occurrence(embed, user_id)
    content = ""
    if field == None:
        field = first_field_with_occurrence(embed, "—")
        content = embed.fields[field].value
        content = content.replace("—", f"<@{user_id}>", 1)
    else:
        content = embed.fields[field].value
        content = content.replace(f"<@{user_id}>", "—", 1)
    embed.set_field_at(field, name="\u200b", value=content)
    return embed

def first_field_with_occurrence(embed: Embed, substring: str):
    '''Returns an integer giving which field the given substring first occurs
    in. Returns None if the substring is not found on the list.
    '''
    all_content = [field.value for field in embed.fields]
    for i, content in enumerate(all_content):
        if substring in content:
            return i
    return None

def is_list_full(embed: Embed):
    '''Returns a boolean giving whether there is still an empty slot on the
    list.
    '''
    field = first_field_with_occurrence(embed, "—")
    if field == None:
        return True
    return False

#Select item to show details of menu
class ViewAttendance(ui.View):
    def __init__(self, embed):
        super().__init__(timeout=view_timeout)
        self.add_item(ButtonAttendanceJoin(embed))

class ButtonAttendanceJoin(ui.Button):
    def __init__(self, embed):
        super().__init__(emoji="✋", style=discord.ButtonStyle.grey)
        self.embed = embed

    async def callback(self, interaction):
        try:
            user_id = str(interaction.user.id)
            embed = add_or_remove_user_on_list(self.embed, user_id)
            full = is_list_full(embed)
            if full:
                await interaction.response.edit_message(content="All attendees are present!", embed=embed, view=None)
            else:
                view = ViewAttendance(embed)
                await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

async def setup(client):
    await client.add_cog(Attendance(client))
