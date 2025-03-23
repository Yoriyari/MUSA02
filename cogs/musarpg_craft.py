#===============================================================================
# MusaRPG Crafting v1.0
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 18 Feb 2025 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# musarpg_craft.py is part of the Musa RPG architecture. It handles crafting
# new items.
#===============================================================================

#Import Modules
import discord
from discord import Embed, ui
from discord.ext import commands

from cogs.musarpg_messages import get_message
from common.error_message import send_error
from common.help_message import send_help
from common.yaml_handling import read_from_yaml

import re
from enum import Enum

VIEW_TIMEOUT = 86400 # 24 hours
FILE_ITEMS = "data/musarpg/items.yml"
ITEMS_PER_PAGE = 15

#-------------------------------------------------------------------------------
#Cog Setup
class MusaRPG_Craft(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("MusaRPG Craft cog loaded.")

    @commands.group(name="musarpg_craft", aliases=["craft"], case_insensitive=True, invoke_without_command=True)
    async def musarpg_craft(self, ctx):
        try:
            scene = Scene(ctx.author.id)
            await setup_merge_item_selection(ctx.channel.send, scene)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @musarpg_craft.command(aliases=["help", "?", "info", "information", "instructions"])
    async def musarpg_craft_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "musarpg_craft")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#-------------------------------------------------------------------------------
#Errors
class UserError(Exception):
    def __init__(self, message="An error occurred."):
        super().__init__(message)

class WrongUserID(UserError):
    def __init__(self, message="You cannot interact with another user's interface."):
        super().__init__(message)

#-------------------------------------------------------------------------------
#Items
class NamingScheme(Enum):
    CONCATENATE = 1
    CONCATENATE_SPACED = 2
    HYPHENATE = 3
    A_OF_BS = 4
    REPLACE_WORDS = 5
    PORTMANTEAU_EDGE_VOWELS = 6

class Item():
    def __init__(self, key: str, **values):
        self.key = key
        self.values = values

    def __str__(self):
        return f"**{self.name}**"

    @property
    def name(self):
        try:
            return self.values["name"]
        except:
            return self.key

    @property
    def plural(self):
        try:
            return self.values["plural"]
        except:
            if re.match("(s|x|z|ch|sh)$", self.name):
                return self.name + "es"
            return self.name + "s"

    @property
    def article(self):
        try:
            return self.values["article"]
        except:
            if self.name[0] in ["a", "e", "i", "o", "u"]:
                return "an"
            return "a"

    @property
    def description(self):
        try:
            return self.values["description"]
        except:
            return None

class MergedItem(): # Key should be the merged items + naming scheme (and any other settings applied?)
    def __init__(self, key: str, **values):
        super().__init__(key, values=values)

    @property
    def component_keys(self):
        return self.values["component keys"]

    @property
    def component_items(self):
        return create_items_from_keys(self.component_keys)

    @property
    def base_items(self):
        '''Returns all the base items which were used to craft the final merged
        item, even if it's nested throughout several merges.
        '''
        base_items = []
        for item in self.component_items:
            if type(item) == MergedItem:
                base_items.append(item.base_items)
            else:
                base_items.append(item)
        return base_items

    @property
    def naming_scheme(self):
        try:
            return self.values["naming scheme"]
        except:
            return NamingScheme.HYPHENATE

    @property
    def name(self):
        items = self.component_items
        return get_merged_name(self.naming_scheme, items[0], items[1])

    @property
    def plural(self):
        items = self.component_items
        return get_merged_name(self.naming_scheme, items[0], items[1], plural=True)

    @property
    def article(self):
        return self.component_items[0].article

    @property
    def description(self):
        try:
            return self.values["description"]
        except:
            return None

    def get_merged_name(scheme: NamingScheme, a: Item, b: Item, plural=False):
        if scheme == NamingScheme.CONCATENATE:
            return concatenate(a, b, plural=plural)
        if scheme == NamingScheme.CONCATENATE_SPACED:
            return concatenate_with_space(a, b, plural=plural)
        if scheme == NamingScheme.HYPHENATE:
            return hyphenate(a, b, plural=plural)
        if scheme == NamingScheme.A_OF_BS:
            return format_a_of_bs(a, b, plural=plural)
        if scheme == NamingScheme.REPLACE_WORDS:
            return replace_words(a, b, plural=plural)
        if scheme == NamingScheme.PORTMANTEAU_EDGE_VOWELS:
            return portmanteau_on_edge_vowels(a, b, plural=plural)
        return hyphenate(a, b, plural=plural)

    def concatenate(a: Item, b: Item, plural=False):
        '''Returns a string, simply concatenating the input Item names.
        '''
        if plural:
            return f"{a.name}{b.plural}"
        return f"{a.name}{b.name}"

    def concatenate_with_space(a: Item, b:Item, plural=False):
        '''Returns a string, concatenating the input Item names with a space
        inbetween.
        '''
        if plural:
            return f"{a.name} {b.plural}"
        return f"{a.name} {b.name}"

    def hyphenate(a: Item, b: Item, plural=False):
        '''Returns a string, concatenating the input Item names with a hyphen
        inbetween.
        '''
        if plural:
            return f"{a.name}-{b.plural}"
        return f"{a.name}-{b.name}"

    def format_a_of_bs(a: Item, b: Item, plural=False):
        '''Returns a string, concatenating the input Item names in the format
        `A of Bs`.
        '''
        if plural:
            return f"{a.plural} of {b.plural}"
        return f"{a.name} of {b.plural}"

    def replace_words(a: Item, b: Item, plural=False):
        '''Returns a string, with the input Items being split on any spaces in their
        names and having half of each set of words merged.
        '''
        start = a.name.split()
        start = " ".join(start[:ceil_division(len(start), 2)])
        if plural:
            end = b.name.split()
        else:
            end = b.plural.split()
        end = " ".join(end[len(end)//2:])
        return f"{start} {end}"

    def portmanteau_on_edge_vowels(a: Item, b: Item, plural=False):
        '''Returns a string, concatenating the input strings by removing
        everything following the last row of vowels in the first string and
        appending everything following the first row of consonants in the second
        string.
        '''
        start = a.name
        match = re.match(r".*[^aeiou\s]+([aeiou]+[^aeiouy]*|[aeiou]*y+)$", start, flags=re.I)
        if match:
            start = start.removesuffix(match.group(1))
        if plural:
            end = b.name
        else:
            end = b.plural
        match = re.match(r"^([^aeiou]*)[aeiou]+", end, flags=re.I)
        if match:
            end = end.removeprefix(match.group(1))
        return start+end

#-------------------------------------------------------------------------------
#Scenes
class Scene():
    '''The Scene class governs individual screens of the game.
    '''
    def __init__(self, user_id):
        self.user_id = user_id
        self.message = self.message_default
        self.embed = self.embed_default
        self.view = self.view_default

    async def play(self, send, **kwargs):
        if "message" in kwargs:
            self.message = kwargs["message"]
        if "content" in kwargs: # Just an alias for "message"
            self.message = kwargs["content"]
        if "embed" in kwargs:
            self.embed = kwargs["embed"]
        if "view" in kwargs:
            self.view = kwargs["view"]
        await send(content=self.message(), embed=self.embed(), view=self.view())

    def message_default(self):
        return None

    def embed_default(self):
        return None

    def view_default(self):
        return None

class ScenePaginatedList(Scene):
    def __init__(self, user_id, page=1, entries_per_page=ITEMS_PER_PAGE):
        super().__init__(user_id)
        self.page = page
        self.entries_per_page = entries_per_page

    @property
    def entries(self):
        return []

    def embed_default(self):
        return embed_paginated_list(self)

    def entries_on_current_page(self):
        start, end = get_page_start_end_indices(self.page, self.entries_per_page)
        return self.entries[start:end]

    def get_page_total(self):
        return ceil_division(len(self.entries), self.entries_per_page)

class SceneMergeItemSelection(ScenePaginatedList):
    def __init__(self, user_id, items=None, selected_keys=None, max_selections=2, page=1, entries_per_page=ITEMS_PER_PAGE):
        super().__init__(user_id, page=page, entries_per_page=entries_per_page)
        self.items = items or [] # list of Item objects
        self.selected_keys = selected_keys or []
        self.max_selections = max_selections

    @property
    def entries(self):
        return self.items

    def message_default(self):
        return get_message("setup merge item selection")

    def message_picked(self):
        selected_names = [str(item) for item in self.items if item.key in self.selected_keys]
        selected_names = ", ".join(selected_names)
        return get_message("select subsequent merge item", selected_names)

    def view_default(self):
        return ViewMergeSelectItems(self)

class SceneMergeNameSelection(ScenePaginatedList):
    def __init__(self, user_id, items=None, page=1, entries_per_page=ITEMS_PER_PAGE):
        super().__init__(user_id, page=page, entries_per_page=entries_per_page)
        self.items = items or [] # list of Item objects

    @property
    def entries(self):
        return list_merged_item_names(self.items)

    def message_default(self):
        item_names = " and ".join([str(item) for item in self.items])
        return get_message("setup merge name selection", item_names)

    def view_default(self):
        return ViewMergeSelectName(self)

#-------------------------------------------------------------------------------
#Views
class ViewMergeSelectItems(ui.View):
    def __init__(self, scene: Scene):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.add_item(SelectMergeItem(scene))
        self.add_item(ButtonPrevPage(scene))
        self.add_item(ButtonGoToPage(scene))
        self.add_item(ButtonNextPage(scene))

class ViewMergeSelectName(ui.View):
    def __init__(self, scene: Scene):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.add_item(SelectMergeName(scene))
        self.add_item(ButtonPrevPage(scene))
        self.add_item(ButtonGoToPage(scene))
        self.add_item(ButtonNextPage(scene))

class SelectMergeItem(ui.Select):
    def __init__(self, scene: Scene):
            sliced_items = scene.entries_on_current_page()
            options = [discord.SelectOption(label=item.name, value=item.key) for item in sliced_items]
            super().__init__(placeholder="Select Items", options=options)
            self.scene = scene
    async def callback(self, interaction):
        try:
            await handle_select_merge_item(self, interaction)
        except UserError as e:
            await interaction.response.send_message(e, ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SelectMergeName(ui.Select):
    def __init__(self, scene: Scene):
            sliced_names = scene.entries_on_current_page()
            options = [discord.SelectOption(label=name) for name in sliced_names]
            super().__init__(placeholder="Select Name", options=options)
            self.scene = scene
    async def callback(self, interaction):
        try:
            await handle_select_merge_name(self, interaction)
        except UserError as e:
            await interaction.response.send_message(e, ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonChangePage(ui.Button):
    def __init__(self, scene: Scene, label:str, target_page: int):
        disabled = scene.get_page_total() <= 1
        super().__init__(label=label, style=discord.ButtonStyle.blurple, disabled=disabled)
        self.scene = scene
        self.target_page = target_page
    async def callback(self, interaction):
        try:
            await handle_button_change_page(self, interaction)
        except UserError as e:
            await interaction.response.send_message(e, ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonPrevPage(ButtonChangePage):
    def __init__(self, scene: Scene):
        target_page = scene.page-1 if scene.page > 1 else scene.get_page_total()
        label = f"← Page {target_page}"
        super().__init__(scene, label, target_page)

class ButtonNextPage(ButtonChangePage):
    def __init__(self, scene: Scene):
        target_page = scene.page+1 if scene.page < scene.get_page_total() else 1
        label = f"Page {target_page} →"
        super().__init__(scene, label, target_page)

class ButtonGoToPage(ui.Button):
    def __init__(self, scene: Scene):
        disabled = scene.get_page_total() <= 1
        super().__init__(label=f"…", style=discord.ButtonStyle.blurple, disabled=disabled)
        self.scene = scene
    async def callback(self, interaction):
        try:
            await handle_button_go_to_page(self, interaction)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ModalGoToPage(ui.Modal, title="Skip to Page"):
    def __init__(self, scene: Scene):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.scene = scene
    field = ui.TextInput(label="Page Number", placeholder="Skip to which page?", required=True)
    async def on_submit(self, interaction):
        try:
            await handle_modal_go_to_page(self, interaction)
        except UserError as e:
            await interaction.response.send_message(e, ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

#-------------------------------------------------------------------------------
#Primary Functions
async def setup_merge_item_selection(send, scene):
    inventory = read_from_yaml(FILE_ITEMS).keys() # TODO after inventory is implemented, replace this with User inventory
    items = create_items_from_keys(inventory)
    scene = SceneMergeItemSelection(scene.user_id, items=items)
    await scene.play(send)

async def setup_merge_name_selection(send, scene):
    selected_items = [item for item in scene.items if item.key in scene.selected_keys]
    scene = SceneMergeNameSelection(scene.user_id, items=selected_items)
    await scene.play(send)

async def handle_select_merge_item(self, interaction):
    verify_user_interaction(interaction, self.scene.user_id)
    selection = "".join(self.values)
    if selection in self.scene.selected_keys:
        raise UserError("You cannot merge an item with itself. Please select a different item.")
    self.scene.selected_keys.append(selection)
    if len(self.scene.selected_keys) < self.scene.max_selections:
        await self.scene.play(interaction.response.edit_message, message=self.scene.message_picked)
        return
    await setup_merge_name_selection(interaction.response.edit_message, self.scene)

async def handle_select_merge_name(self, interaction):
    msg = "".join(self.values) # TODO
    await interaction.response.edit_message(content=msg)

async def handle_button_change_page(self, interaction):
    verify_user_interaction(interaction, self.scene.user_id)
    self.scene.page = self.target_page
    await self.scene.play(interaction.response.edit_message)

async def handle_button_go_to_page(self, interaction):
    verify_user_interaction(interaction, self.scene.user_id)
    await interaction.response.send_modal(ModalGoToPage(self.scene))

async def handle_modal_go_to_page(self, interaction):
    page = self.field.value
    if page.isdigit() == False or int(page) < 1 or int(page) > self.scene.get_page_total():
        raise UserError(f'"{page}" is not a valid page number.')
    self.scene.page = int(page)
    await self.scene.play(interaction.response.edit_message)

#-------------------------------------------------------------------------------
#Auxiliary Functions
def verify_user_interaction(interaction, user_id):
    if int(interaction.user.id) != int(user_id):
        raise WrongUserID()

def create_items_from_keys(keys: list, item_database=None):
    '''Returns a list of Item objects, sorted alphabetically by their display
    name.
    '''
    if not item_database:
        item_database = read_from_yaml(FILE_ITEMS)
    items = [create_item_from_key(key, item_database=item_database) for key in keys]
    return sorted(items, key=lambda item: item.name)

def create_item_from_key(key: list, item_database=None):
    '''Returns an Item object corresponding to its key.
    '''
    if not item_database:
        item_database = read_from_yaml(FILE_ITEMS)
    values = item_database.get(key, {})
    if values and "component keys" in values:
        return MergedItem(key, values=values)
    return Item(key, values=values)

def embed_paginated_list(scene: Scene):
    '''Returns an Embed listing the given page's slice of elements. Footer
    includes the current and total page numbers. Uses Embed's description body.
    '''
    entries = [str(entry) for entry in scene.entries_on_current_page()]
    description = "\n".join(entries)
    footer = f"Page {scene.page} of {scene.get_page_total()}"
    return Embed(description=description).set_footer(text=footer)

def get_page_start_end_indices(page: int, items_per_page: int):
    '''Returns an integer 2-tuple, giving the starting and ending index for
    a list of items on the specified page.
    '''
    return items_per_page*(page-1), items_per_page*page

def ceil_division(n: int, d: int):
    '''Uses an integer division trick to avoid float conversion.
    '''
    return -(n // -d)

def list_all_merged_names(items: list, include_keys=False, include_naming_schemes=False):
    '''Returns a list of strings if all boolean parameters are False or a list
    of tuples if any boolean parameters are True.  sorted on length and then alphabetically, with
    various ways of combining the input Item names without duplicates, including
    concatenation, hyphenation, portmanteaus, `A of B`.
    '''
    result = []
    for a in items:
        for b in items:
            if a.key == b.key:
                continue
            for scheme in NamingScheme:
                merged_name = apply_naming_scheme(a, b, scheme)
                if merged_name in result: # detect properly
                    result.append(merged_name, a.key, b.key, scheme) # if booleans
    return sorted(result, key=lambda x: (len(x), x))

#-------------------------------------------------------------------------------
#Add Cog
async def setup(client):
    await client.add_cog(MusaRPG_Craft(client))
