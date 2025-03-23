#===============================================================================
# Notes v1.0.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.0.1; Moved database to secrets folder. -YY
# 14 Aug 2024 - v1.0.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# notes.py lets users maintain up to 25 notes which they can modify through a
# text input modal and display from a command or dropdown selection menu.
#===============================================================================

#Import Modules
import discord
from discord import ui, Embed
from discord.ext import commands

from common.json_handling import read_from_json, write_to_json
from common.error_message import send_error, UserError
from common.help_message import send_help
from common.interactions import generate_selectoptions

import os

NOTES_FILE = "secrets/notes.json"

VIEW_TIMEOUT = 86400 # 24 hours
MAX_NOTE_LENGTH = 4000
MAX_TITLE_LENGTH = 256
MAX_NOTES_PER_USER = 25

#-------------------------------------------------------------------------------
#Cog Setup
class Notes(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Notes cog loaded.")

    @commands.group(name="notes", aliases=["note", "notepad"], case_insensitive=True, invoke_without_command=True)
    async def notes(self, ctx, *args):
        '''If the title of one of the user's notes is specified, this displays
        that note as an Embed. Otherwise, this displays a Select menu of all
        note titles.
        '''
        try:
            await handle_notes(ctx, args)
        except UserError as e:
            await ctx.channel.send(e)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @notes.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def notes_help(self, ctx):
        await send_help(ctx.channel.send, "notes")

#-------------------------------------------------------------------------------
#Auxiliary Functions
async def handle_notes(ctx, args):
    '''If the title of one of the user's notes is specified, this displays
    that note as an Embed. Otherwise, this displays a Select menu of all
    note titles.
    '''
    if not os.path.exists(NOTES_FILE):
        write_to_json(NOTES_FILE, {})
    data = read_from_json(NOTES_FILE)
    user_id = str(ctx.author.id)
    if user_id not in data or not data[user_id]:
        await post_notes_menu(ctx.channel.send, user_id, f"No existing notes found for {ctx.author.name}. Create a note below.", data=data)
        return
    if not args:
        await post_notes_menu(ctx.channel.send, user_id, f"All of {ctx.author.name}'s notes:", data=data)
        return
    title = " ".join(args)
    key, note = get_note_from_title(user_id, title, data=data)
    if not key:
        await post_notes_menu(ctx.channel.send, user_id, f"Note \"{title}\" not found.\nAll of {ctx.author.name}'s notes:", data=data)
        return
    await post_display_note(ctx.channel.send, user_id, title=key, desc=note)

async def post_display_note(post_method, user_id, title, desc=None, data=None):
    '''Either sends a new message or edits an existing message depending on the
    function provided as post parameter. Message will contain an Embed of the
    specified user's note and a View to edit, delete, or browse notes.
    '''
    if desc == None:
        title, desc = get_note_from_title(user_id, title, data=data)
    if not title:
        post_notes_menu(post_method, user_id, content=f"Note \"{title}\" not found.\nAll available notes:", data=data)
        return
    content, embed, view = prepare_display_note(user_id, title, desc)
    await post_method(content=content, embed=embed, view=view)

async def post_notes_menu(post_method, user_id, content="All of your notes:", data=None):
    '''Either sends a new message or edits an existing message depending on the
    function provided as post parameter. Message will contain the specified text
    content and a View to select or create a note.
    '''
    content, embed, view = prepare_notes_menu(user_id, content, data=data)
    await post_method(content=content, embed=embed, view=view)

def prepare_display_note(user_id, title, desc):
    '''Returns a 3-tuple (content, embed, view).
    Content will be empty for displaying notes.
    Embed is an Embed object with the user's note of the given title.
    View is a View object with buttons to edit or delete the note or access the
    user's other notes or create a new note.
    '''
    content = None
    embed = Embed(title=title, description=desc)
    view = ViewDisplayNote(user_id, title)
    return content, embed, view

def prepare_notes_menu(user_id, content=None, data=None):
    '''Returns a 3-tuple (content, embed, view).
    Content will be the provided content.
    Embed will be None for the notes menu.
    View is a View object with a select dropdown for all of the user's notes and
    a button to create a new note.
    '''
    content = content
    embed = None
    view = ViewAllNotes(user_id, data=data)
    return content, embed, view

def case_insensitive_dict_match(data, user_id, title):
    '''Returns the key and value of the first data dict entry with a case
    insensitive match between the key and supplied title.
    '''
    if user_id not in data or not title:
        return None, None
    for key, note in data[user_id].items():
        if title.lower() == key.lower():
            return key, note
    return None, None

def get_note_from_title(user_id, title, data=None):
    '''Returns a tuple of the key and associated note by efficiently looking up
    the title case-insensitively as a key in the JSON dict.
    '''
    if not data:
        data = read_from_json(NOTES_FILE)
    if user_id not in data or not title:
        return None, None
    if title in data[user_id]:
        return title, data[user_id][title]
    if title.lower() in data[user_id]:
        return title.lower(), data[user_id][title.lower()]
    if title.upper() in data[user_id]:
        return title.upper(), data[user_id][title.upper()]
    key, note = case_insensitive_dict_match(data, user_id, title)
    if key:
        return key, note
    return None, None

#-------------------------------------------------------------------------------
#Views
class ViewDisplayNote(ui.View):
    '''A View object with buttons to edit or delete the current note or access
    the user's other notes or create a new note.
    '''
    def __init__(self, user_id, title):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.add_item(ButtonAllNotes(user_id))
        self.add_item(ButtonCreateNote(user_id))
        self.add_item(ButtonEditNote(user_id, title))
        self.add_item(ButtonDeleteNote(user_id, title))

class ViewAllNotes(ui.View):
    '''A View object with a selection dropdown for all of the user's notes and
    a button to create a new note.
    '''
    def __init__(self, user_id, data=None):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.add_item(SelectNotes(user_id, data=data))
        self.add_item(ButtonCreateNote(user_id))

class ModalEditNote(ui.Modal):
    '''A Modal object with text input for the title and contents of a note.
    '''
    def __init__(self, user_id, notetitle=None):
        self.user_id = user_id
        self.notetitle, self.desc = get_note_from_title(user_id, notetitle)
        super().__init__(timeout=VIEW_TIMEOUT, title="Edit Note")
        self.add_item(ui.TextInput(label="Title", default=self.notetitle, style=discord.TextStyle.short,
            min_length=1, max_length=MAX_TITLE_LENGTH, required=True)
        ).add_item(ui.TextInput(label="Contents", default=self.desc, style=discord.TextStyle.long,
            max_length=MAX_NOTE_LENGTH, required=False)
        )
        self.input_title, self.input_desc = self.children

    async def on_submit(self, interaction):
        try:
            submitted_title = self.input_title.value
            submitted_desc = self.input_desc.value
            overlap, _ = get_note_from_title(self.user_id, submitted_title)
            if overlap and (not self.notetitle or self.notetitle.lower() != submitted_title.lower()):
                await interaction.response.send_message(f"Another note with the title \"{overlap}\" already exists. To prevent accidental overwriting, your note has not been saved. Edit the existing note instead.",
                    ephemeral=True
                )
                return
            data = read_from_json(NOTES_FILE)
            if self.user_id not in data:
                data[self.user_id] = {submitted_title: submitted_desc}
            else:
                if len(data[self.user_id]) > MAX_NOTES_PER_USER:
                    await interaction.response.send_message("You are at the maximum number of notes and cannot create more.",
                        ephemeral=True
                    )
                    return
                if self.notetitle and self.notetitle.lower() != submitted_title.lower():
                    data[self.user_id].pop(self.notetitle)
                data[self.user_id][submitted_title] = submitted_desc
            write_to_json(NOTES_FILE, data)
            await post_display_note(interaction.response.edit_message, self.user_id, submitted_title, desc=submitted_desc)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

    async def on_error(self, interaction, error):
        await send_error(interaction.client, error, reference=interaction.message.jump_url)

class ModalDeleteNote(ui.Modal):
    '''A Modal object to confirm deletion of a note.
    '''
    def __init__(self, user_id, notetitle=None):
        self.user_id = user_id
        self.notetitle, _ = get_note_from_title(user_id, notetitle)
        super().__init__(timeout=VIEW_TIMEOUT, title="Confirm Note Deletion")
        self.add_item(ui.TextInput(label="Please confirm deletion by typing \"CONFIRM\"",
            placeholder="CONFIRM", style=discord.TextStyle.short, max_length=100, required=False)
        )
        self.input_confirm = self.children[0]

    async def on_submit(self, interaction):
        try:
            submitted_confirm = self.input_confirm.value
            if submitted_confirm.lower() != "confirm":
                await interaction.response.send_message(f"Confirmation failed. Note \"{self.notetitle}\" was not deleted.",
                    ephemeral=True
                )
                return
            data = read_from_json(NOTES_FILE)
            if self.user_id not in data or self.notetitle not in data[self.user_id]:
                await interaction.response.send_message(f"Note \"{self.notetitle}\" could not be found for deletion. Was it already deleted?",
                    ephemeral=True
                )
                return
            data[self.user_id].pop(self.notetitle)
            write_to_json(NOTES_FILE, data)
            username = interaction.user.name
            await post_notes_menu(interaction.response.edit_message, self.user_id,
                content=f"Note \"{self.notetitle}\" has successfully been deleted.\nAll of {username}'s notes:", data=data
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

    async def on_error(self, interaction, error):
        await send_error(interaction.client, error, reference=interaction.message.jump_url)

class SelectNotes(ui.Select):
    '''A Select object to let the user select any of their existing notes.
    '''
    def __init__(self, user_id, data=None):
        self.user_id = user_id
        if data == None:
            data = read_from_json(NOTES_FILE)
        titles = []
        if user_id in data:
            titles = data[user_id]
        disabled = not titles
        placeholder = "Select Note"
        if disabled:
            placeholder = "No notes registered."
            titles = ["Select Note"]
        options = generate_selectoptions(titles)
        super().__init__(placeholder=placeholder, options=options, disabled=disabled)

    async def callback(self, interaction):
        try:
            title = "".join(self.values)
            await post_display_note(interaction.response.edit_message, self.user_id, title)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonAllNotes(ui.Button):
    '''A Button object to let the user reach the menu for browsing all their
    existing notes.
    '''
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(label="View All Notes", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction):
        try:
            if self.user_id != str(interaction.user.id):
                await interaction.response.send_message("Only the owner of these notes can browse and edit these notes.",
                    ephemeral=True
                )
                return
            username = interaction.user.name
            await post_notes_menu(interaction.response.edit_message, self.user_id, content=f"All of {username}'s notes:")
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonCreateNote(ui.Button):
    '''A Button object to let the user create a new note.
    '''
    def __init__(self, user_id):
        self.user_id = user_id
        super().__init__(label="New Note", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction):
        try:
            if self.user_id != str(interaction.user.id):
                await interaction.response.send_message("Only the owner of these notes can browse and edit these notes.",
                    ephemeral=True
                )
                return
            data = read_from_json(NOTES_FILE)
            if self.user_id in data and len(data[self.user_id]) >= MAX_NOTES_PER_USER:
                await interaction.response.send_message("You are at the maximum number of notes and cannot create more.",
                    ephemeral=True
                )
                return
            await interaction.response.send_modal(ModalEditNote(self.user_id))
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonEditNote(ui.Button):
    '''A Button object to let the user edit their current note.
    '''
    def __init__(self, user_id, title):
        self.user_id = user_id
        self.title = title
        super().__init__(label="Edit", style=discord.ButtonStyle.green)

    async def callback(self, interaction):
        try:
            if self.user_id != str(interaction.user.id):
                await interaction.response.send_message("Only the owner of these notes can browse and edit these notes.",
                    ephemeral=True
                )
                return
            await interaction.response.send_modal(ModalEditNote(self.user_id, self.title))
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonDeleteNote(ui.Button):
    '''A Button object to let the user delete their current note after a modal
    confirmation.
    '''
    def __init__(self, user_id, title):
        self.user_id = user_id
        self.title = title
        super().__init__(label="Delete", style=discord.ButtonStyle.red)

    async def callback(self, interaction):
        try:
            if self.user_id != str(interaction.user.id):
                await interaction.response.send_message("Only the owner of these notes can browse and edit these notes.",
                    ephemeral=True
                )
                return
            await interaction.response.send_modal(ModalDeleteNote(self.user_id, self.title))
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

#-------------------------------------------------------------------------------
#Add Cog
async def setup(client):
    await client.add_cog(Notes(client))
