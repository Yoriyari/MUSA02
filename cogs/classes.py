#===============================================================================
# Classes v1.2.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 06 May 2024 - v1.2.1; Added a help command and reworked error handling. -YY
# 17 Oct 2022 - v1.2; Added class lookup by command. -YY
# 10 Oct 2022 - v1.1; Importing item plural forms from items.py. -YY
# 09 Oct 2022 - v1.0; Finished file. Includes a way to browse standard classes
#               and specific class details. -YY
# 07 Oct 2022 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Add homebrew class support. -YY
#===============================================================================
# Description
# ..............................................................................
# classes.py displays and handles D&D 5e classes.
#===============================================================================

#Import Modules
import discord
from discord import Embed, ui
from discord.ext import commands

from cogs.items import generate_item_string
from common.json_handling import write_to_json, read_from_json
from common.variable_text import get_closest_matches
from common.error_message import send_error
from common.help_message import send_help

import re

classes_file = "data/dnd/classes.json"
view_timeout = 259200

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Class information handling functions

def get_classes():
    '''Returns a dict containing all classes in the database.
    If the classes list cannot be found, returns an empty dict.
    '''
    dict = get_classes_file()
    if "classes" not in dict:
        return {}
    return dict["classes"]

def get_standard_class_names():
    '''Returns a list containing the names of all standard classes.
    If the standard classes registry cannot be found, returns an empty list.
    '''
    dict = get_classes_file()
    if "standard" not in dict:
        return []
    return dict["standard"]

def get_homebrew_classes_registry():
    '''Returns a dict containing users and their homebrew classes.
    If the homebrew classes registry cannot be found, returns an empty dict.
    '''
    dict = get_classes_file()
    if "homebrew" not in dict:
        return {}
    return dict["homebrew"]

def get_class_names():
    '''Returns a dict containing all class names in the entire database.
    If the classes list cannot be found, returns an empty dict.
    '''
    classes = get_classes()
    return list(classes.keys())

def get_class(name: str):
    '''Returns a class's dict of data.
    If the class cannot be found, returns None.
    '''
    classes = get_classes()
    if name not in classes:
        return None
    return classes[name]

def get_class_name(c_class: dict):
    '''Returns the string from a class's name entry.
    If this cannot be found, returns None.
    '''
    if "name" not in c_class:
        return None
    return c_class["name"]

def get_class_description(c_class: dict):
    '''Returns the string from a class's description.
    If this cannot be found, returns None.
    '''
    if "description" not in c_class:
        return None
    return c_class["description"]

def get_class_features(c_class: dict):
    '''Returns a dict giving lists of features keyed to the level the features
    are unlocked at.
    If this cannot be found, returns None.
    '''
    if "features" not in c_class:
        return None
    return c_class["features"]

def get_class_hit_die(c_class: dict):
    '''Returns an integer giving a class's hit die size.
    If this cannot be found, returns None.
    '''
    if "hit_die" not in c_class:
        return None
    return c_class["hit_die"]

def get_class_proficiencies(c_class: dict):
    '''Returns a dict containing a class's proficiencies as dicts.
    If this cannot be found, returns an empty dict.
    '''
    if "proficiencies" not in c_class:
        return {}
    return c_class["proficiencies"]

def get_class_saving_throw_proficiencies(c_class: dict):
    '''Returns a list containing a class's saving throw proficiencies as
    strings; Choices are given as a dict with an integer and a list of strings.
    If this cannot be found, returns an empty list.
    '''
    proficiencies = get_class_proficiencies(c_class)
    if proficiencies == None or "saving_throws" not in proficiencies:
        return []
    return proficiencies["saving_throws"]

def get_class_skill_proficiencies(c_class: dict):
    '''Returns a list containing a class's skill proficiencies as strings;
    Choices are given as a dict with an integer and a list of strings.
    If this cannot be found, returns an empty list.
    '''
    proficiencies = get_class_proficiencies(c_class)
    if proficiencies == None or "skills" not in proficiencies:
        return []
    return proficiencies["skills"]

def get_class_armor_proficiencies(c_class: dict):
    '''Returns a list containing a class's armor proficiencies as strings;
    Choices are given as a dict with an integer and a list of strings.
    If this cannot be found, returns an empty list.
    '''
    proficiencies = get_class_proficiencies(c_class)
    if proficiencies == None or "armor" not in proficiencies:
        return []
    return proficiencies["armor"]

def get_class_weapon_proficiencies(c_class: dict):
    '''Returns a list containing a class's weapon proficiencies as strings;
    Choices are given as a dict with an integer and a list of strings.
    If this cannot be found, returns an empty list.
    '''
    proficiencies = get_class_proficiencies(c_class)
    if proficiencies == None or "weapons" not in proficiencies:
        return []
    return proficiencies["weapons"]

def get_class_tool_proficiencies(c_class: dict):
    '''Returns a list containing a class's tool proficiencies as strings;
    Choices are given as a dict with an integer and a list of strings.
    If this cannot be found, returns an empty list.
    '''
    proficiencies = get_class_proficiencies(c_class)
    if proficiencies == None or "tools" not in proficiencies:
        return []
    return proficiencies["tools"]

def get_class_starting_equipment(c_class: dict):
    '''Returns a list containing a class's starting equipment as strings;
    Choices are given as a dict with an integer and a list of strings.
    Duplicates are given as a dict with an integer and a string.
    If this cannot be found, returns an empty list.
    '''
    if "starting_equipment" not in c_class:
        return []
    return c_class["starting_equipment"]

def get_class_starting_gold(c_class: dict):
    '''Returns a dict containing a class's starting gold integers.
    If this cannot be found, returns None.
    '''
    if "starting_gold" not in c_class:
        return None
    return c_class["starting_gold"]

def get_class_multiclass_info(c_class: dict):
    '''Returns a dict containing all multiclassing info for a class.
    If this cannot be found, returns None.
    '''
    if "multiclass" not in c_class:
        return None
    return c_class["multiclass"]

def get_class_multiclass_ability_requirement(c_class: dict):
    '''Returns a dict containing the abilities which must have a score of 13 or
    higher in order to multiclass into the given class, as well as how these
    should be checked combined in the case of multiple abilities.
    '''
    multiclass = get_class_multiclass_info(c_class)
    if multiclass == None or "requirement" not in multiclass:
        return None
    return multiclass["requirement"]

def get_class_multiclass_proficiencies(c_class: dict):
    '''Returns a dict containing all proficiencies granted for multiclassing
    into a class.
    If this cannot be found, returns an empty dict.
    '''
    multiclass = get_class_multiclass_info(c_class)
    if multiclass == None or "proficiencies" not in multiclass:
        return {}
    return multiclass["proficiencies"]

def get_class_multiclass_skill_proficiencies(c_class: dict):
    '''Returns a list giving the skill proficiencies granted for multiclassing
    into a class as strings; Choices are given as a dict with an integer and a
    list of strings.
    If this cannot be found, returns an empty list.
    '''
    proficiencies = get_class_multiclass_proficiencies(c_class)
    if proficiencies == None or "skills" not in proficiencies:
        return []
    return proficiencies["skills"]

def get_class_multiclass_armor_proficiencies(c_class: dict):
    '''Returns a list giving the armor proficiencies granted for multiclassing
    into a class as strings; Choices are given as a dict with an integer and a
    list of strings.
    If this cannot be found, returns an empty list.
    '''
    proficiencies = get_class_multiclass_proficiencies(c_class)
    if proficiencies == None or "armor" not in proficiencies:
        return []
    return proficiencies["armor"]

def get_class_multiclass_weapon_proficiencies(c_class: dict):
    '''Returns a list giving the weapon proficiencies granted for multiclassing
    into a class as strings; Choices are given as a dict with an integer and a
    list of strings.
    If this cannot be found, returns an empty list.
    '''
    proficiencies = get_class_multiclass_proficiencies(c_class)
    if proficiencies == None or "weapons" not in proficiencies:
        return []
    return proficiencies["weapons"]

def get_class_multiclass_tool_proficiencies(c_class: dict):
    '''Returns a list giving the tool proficiencies granted for multiclassing
    into a class as strings; Choices are given as a dict with an integer and a
    list of strings.
    If this cannot be found, returns an empty list.
    '''
    proficiencies = get_class_multiclass_proficiencies(c_class)
    if proficiencies == None or "tools" not in proficiencies:
        return []
    return proficiencies["tools"]

#Class information handling functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Backend functions

def get_classes_file():
    '''Returns a dict containing the entire classes file database.
    '''
    return read_from_json(classes_file)

def save_classes_file(new_file: dict):
    '''Overwrites the entire classes file database with the provided dict.
    '''
    write_to_json(classes_file, new_file)

def save_classes(new_classes: dict):
    '''Overwrites the classes segment of the database with the provided dict.
    '''
    dict = get_classes_file()
    dict["classes"] = new_classes
    save_classes_file(dict)

def save_homebrew_classes_registry(new_registry: dict):
    '''Overwrites the homebrew registry of the database with the provided dict.
    '''
    dict = get_classes_file()
    dict["homebrew"] = new_registry
    save_classes_file(dict)

def generate_class_starting_gold_string(c_class: dict):
    '''Returns a string representing a class's starting gold.
    '''
    gold = get_class_starting_gold(c_class)
    if gold == None or "dice" not in gold or "faces" not in gold:
        return "??"
    msg = f'{gold["dice"]}d{gold["faces"]}'
    if "multiplier" in gold and gold["multiplier"] != 1:
        msg += f' × {gold["multiplier"]}'
    return msg

def generate_class_embed_features_field_value(c_class: dict):
    '''Returns a string to put as value of the features field of the class
    description embed.
    '''
    features = get_class_features(c_class)
    if features == None:
        return "??"
    msg = ""
    for level, list in features.items():
        msg += f"**{level}** "
        if list == []:
            msg += "—"
        for i, feature in enumerate(list):
            if i != 0:
                msg +=", "
            msg += feature
        msg += "\n"
    return msg

def generate_class_embed_ability_string(ability):
    '''Returns a string describing a saving throw or skill for the class
    description embed. Parameter can be a string giving an ability check name
    or a dict giving choices.
    '''
    if type(ability) is not dict:
        return ability
    if "choose" not in ability or "from" not in ability:
        return "??"
    count = ability["choose"]
    choices = ability["from"]
    msg = f"choose {count} from "
    for j, choice in enumerate(choices):
        if j != 0:
            msg += ", "
            if j == len(choices)-1: msg += "and "
        msg += choice
    msg += ". "
    return msg

def generate_class_embed_item_proficiencies_string(items: list):
    '''Returns a string giving the line describing static and choice
    proficiencies of armors, weapons and tools for the class description embed.
    '''
    if type(items) is not list:
        return "??"
    if items == []:
        return "none"
    msg = ""
    for i, item in enumerate(items):
        if i != 0: msg += ", "
        msg += generate_item_string(item, pluralize=True, conjunction=False)
    return msg

def generate_class_embed_ability_proficiencies_string(abilities: list):
    '''Returns a string giving the line describing static and choice
    proficiencies of saving throws and skills for the class description embed.
    '''
    if type(abilities) is not list:
        return "??"
    if abilities == []:
        return "none"
    msg = ""
    for i, ability in enumerate(abilities):
        if i != 0: msg += ", "
        msg += generate_class_embed_ability_string(ability)
        if re.search("^(choose [0-9])", msg) != None:
            msg = msg[0].upper() + msg[1:]
    return msg

def generate_class_embed_hp_value(c_class: dict):
    '''Returns a string to put as value of the hit points field of the class
    description embed.
    '''
    msg = "**Hit Dice:** "
    hit_die = get_class_hit_die(c_class)
    msg += f"1d{hit_die}" if hit_die != None else "??"
    return msg

def generate_class_embed_proficiencies_value(c_class: dict):
    '''Returns a string to put as value of the starting proficiencies field of
    the class description embed.
    '''
    saves = get_class_saving_throw_proficiencies(c_class)
    msg = "**Saving Throws:** "
    msg += generate_class_embed_ability_proficiencies_string(saves)
    skills = get_class_skill_proficiencies(c_class)
    msg += "\n**Skills:** "
    msg += generate_class_embed_ability_proficiencies_string(skills)
    armors = get_class_armor_proficiencies(c_class)
    msg += "\n**Armor:** "
    msg += generate_class_embed_item_proficiencies_string(armors)
    weapons = get_class_weapon_proficiencies(c_class)
    msg += "\n**Weapons:** "
    msg += generate_class_embed_item_proficiencies_string(weapons)
    tools = get_class_tool_proficiencies(c_class)
    msg += "\n**Tools:** "
    msg += generate_class_embed_item_proficiencies_string(tools)
    return msg

def generate_class_embed_multiclass_field_value(c_class: dict):
    '''Returns a string to put as value of the multiclassing field of the class
    description embed.
    '''
    requirement = get_class_multiclass_ability_requirement(c_class)
    msg = "**Ability Score Minimum:** "
    for i, ability in enumerate(requirement["abilities"]):
        if i != 0:
            msg += f' {requirement["conjunction"]} '
        msg += f"{ability} 13"
    skills = get_class_multiclass_skill_proficiencies(c_class)
    armors = get_class_multiclass_armor_proficiencies(c_class)
    weapons = get_class_multiclass_weapon_proficiencies(c_class)
    tools = get_class_multiclass_tool_proficiencies(c_class)
    if skills != [] or armors != [] or weapons != [] or tools != []:
        msg += "\nWhen you gain a level in a class other than your first, you gain only some of that class's starting proficiencies."
    if skills != []:
        msg += f"\n**Skills:** {generate_class_embed_ability_proficiencies_string(skills)}"
    if armors != []:
        msg += f"\n**Armor:** {generate_class_embed_item_proficiencies_string(armors)}"
    if weapons != []:
        msg += f"\n**Weapons:** {generate_class_embed_item_proficiencies_string(weapons)}"
    if tools != []:
        msg += f"\n**Tools:** {generate_class_embed_item_proficiencies_string(tools)}"
    return msg

def generate_class_embed_hp_prof_multi_field_value(c_class: dict):
    '''Returns a string to put as value of the hit points, proficiencies, and
    multiclassing field of the class description embed.
    '''
    msg = generate_class_embed_hp_value(c_class)
    msg += "\n\n**Proficiencies**\n"
    msg += generate_class_embed_proficiencies_value(c_class)
    msg += "\n\n**Multiclassing**\n"
    msg += generate_class_embed_multiclass_field_value(c_class)
    return msg

def generate_class_embed_start_equip_field_value(c_class: dict):
    '''Returns a string to put as value of the starting equipment field of the
    class description embed.
    '''
    msg = "You start with the following items, plus anything provided by your background."
    items = get_class_starting_equipment(c_class)
    for i, item in enumerate(items):
        msg += f"\n• "
        msg += generate_item_string(item, enumerate_choices=True)
    if get_class_starting_gold(c_class) != None:
        gold = generate_class_starting_gold_string(c_class)
        msg += f"\nAlternatively, you may start with {gold} gp to buy your own equipment."
    return msg

def generate_class_embed(c_class: dict):
    '''Returns an Embed object describing the class.
    '''
    name = get_class_name(c_class)
    description = get_class_description(c_class)
    embed = Embed(title=f"Class: {name}", description=description)
    value = generate_class_embed_features_field_value(c_class)
    embed.add_field(name="Features", value=value)
    value = generate_class_embed_hp_prof_multi_field_value(c_class)
    embed.add_field(name="Hit Points", value=value)
    value = generate_class_embed_start_equip_field_value(c_class)
    embed.add_field(name="Starting Equipment", value=value, inline=False)
    return embed

def generate_class_name_embed(class_name: str):
    '''Returns an Embed object describing the class matching the name.
    '''
    c_class = get_class(class_name)
    if c_class == None:
        raise Exception("Class not found")
    return generate_class_embed(c_class)

def generate_standard_classes_select():
    '''Creates a Select object consisting of the standard classes.
    '''
    names = get_standard_class_names()
    options = []
    for name in names:
        options.append(discord.SelectOption(label=name))
    select = ui.Select(placeholder="Standard Classes", options=options)
    return select

def get_matching_class(class_name):
    '''Returns a message, Embed, and view as a message response.
    Checks the entire classes list for the five closest class names matching
    with the input class name.
    '''
    msg, embed, view = "", None, None
    class_names = get_class_names()
    matches = get_closest_matches(class_name, class_names)
    if type(matches) is not list: #Perfect match
        embed = generate_class_name_embed(matches)
        return msg, embed, view
    if matches != []: #5 close matches
        msg = f'Closest matches to "{class_name}":'
        view = ClosestMatchingClassesMenu(matches)
    else: #No close matches
        msg = f'No matches found for "{class_name}"'
    return msg, embed, view

#Backend functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#User Interface elements

#Main menu
class MainMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=view_timeout)

    @ui.button(label="Examine Classes", style=discord.ButtonStyle.blurple)
    async def examineclasses(self, interaction, button):
        try:
            msg = message_examineclassesmenu()
            await interaction.response.send_message(msg, view=ExamineClassesMenu(), ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

    @ui.button(label="Edit Homebrew Classes", style=discord.ButtonStyle.blurple)
    async def edithomebrewclasses(self, interaction, button):
        try:
            user_id = str(interaction.user.id)
            msg = message_edithomebrewclassesmenu()
            await interaction.response.send_message(msg, view=EditHomebrewClassesMenu(user_id), ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

#Examine classes menu
class ExamineClassesMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=view_timeout)
        select = generate_standard_classes_select()
        self.add_item(select)
        async def cb(interaction):
            try:
                name = "".join(select.values)
                embed = generate_class_name_embed(name)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except Exception as e:
                await send_error(interaction.client, e, reference=interaction.message.jump_url)
        select.callback = cb

def message_examineclassesmenu():
    return "Select which class you want to examine!"

#Closest matching classes menu
class ClosestMatchingClassesMenu(ui.View):
    def __init__(self, class_names):
        super().__init__(timeout=view_timeout)
        for class_name in class_names:
            button = ClassButton(class_name)
            self.add_item(button)

class ClassButton(ui.Button):
    def __init__(self, class_name):
        self.class_name = class_name
        super().__init__(label=class_name, style=discord.ButtonStyle.blurple)

    async def callback(self, interaction):
        try:
            embed = generate_class_name_embed(self.class_name)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

#Edit homebrew classes menu
class EditHomebrewClassesMenu(ui.View):
    def __init__(self, user_id: str):
        super().__init__(timeout=view_timeout)

def message_edithomebrewclassesmenu():
    return "TODO"

#User Interface elements
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Bot commands

#Cog Setup
class Classes(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Classes cog loaded.")

    @commands.group(name="classes", aliases=["class"], case_insensitive=True, invoke_without_command=True)
    async def classes(self, ctx, *c_class):
        try:
            if not c_class:
                msg = message_examineclassesmenu()
                await ctx.channel.send(msg, view=ExamineClassesMenu())
                return
            class_name = " ".join(c_class)
            msg, embed, view = get_matching_class(class_name)
            await ctx.channel.send(msg, embed=embed, view=view)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @classes.command(aliases=["help", "?", "info", "information", "instructions"])
    async def classes_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "classes")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

async def setup(client):
    await client.add_cog(Classes(client))
