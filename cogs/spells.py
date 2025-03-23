#===============================================================================
# Spells v0.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 06 May 2024 - Added a help command and reworked error handling. -YY
# 24 Oct 2022 - Finished spells JSON. -YY
# 21 Oct 2022 - So far added spell lookup, a way to browse all spells, several
#               categories to browse, and specific spell details. Need to add
#               more spells to the JSON and implement casting. -YY
# 18 Oct 2022 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Finish programming casting. -YY
#===============================================================================
# Description
# ..............................................................................
# spells.py displays and handles D&D 5e spells.
#===============================================================================

#Import Modules
import discord
from discord import Embed, ui
from discord.ext import commands

from common.json_handling import write_to_json, read_from_json
from common.interactions import generate_selectoptions, slice_list_page
from common.variable_text import get_closest_matches, fit_text_to_length
from common.error_message import send_error
from common.help_message import send_help

import math

spells_file = "data/dnd/spells.json"
view_timeout = 259200
max_spell_name_length = 256

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Spell information handling functions

def get_spells():
    '''Returns a dict containing all spells in the database.
    '''
    dict = get_spells_file()
    if "spells" not in dict:
        return {}
    return dict["spells"]

def get_schools():
    '''Returns a dict containing all schools of magic.
    '''
    dict = get_spells_file()
    if "schools" not in dict:
        return {}
    return dict["schools"]

def get_classes():
    '''Returns a dict containing all spellcasting classes.
    '''
    dict = get_spells_file()
    if "classes" not in dict:
        return {}
    return dict["classes"]

def get_levels():
    '''Returns a dict containing all spell levels.
    '''
    dict = get_spells_file()
    if "levels" not in dict:
        return {}
    return dict["levels"]

def get_units():
    '''Returns a dict containing all units.
    '''
    dict = get_spells_file()
    if "units" not in dict:
        return {}
    return dict["units"]

def get_spell_names():
    '''Returns a list of all spell names in the database.
    '''
    spells = get_spells()
    return list(spells.keys())

def get_school_names():
    '''Returns a list of all school names in the database.
    '''
    schools = get_schools()
    return list(schools.keys())

def get_class_names():
    '''Returns a list of all class names in the database.
    '''
    classes = get_classes()
    return list(classes.keys())

def get_level_names():
    '''Returns a list of all spell level names in the database.
    '''
    levels = get_levels()
    return list(levels.keys())

def get_unit_names():
    '''Returns a list of all unit names in the database.
    '''
    units = get_units()
    return list(units.keys())

def get_level_plurals():
    '''Returns a list of all spell level plural forms.
    '''
    levels = get_levels()
    result = []
    for level in levels.values():
        result.append(get_level_plural(level))
    return result

def get_level_numbers():
    '''Returns a list of all level numbers that SHOULD be in the database.
    '''
    return range(0, 10)

def get_level(name: str):
    '''Returns a dict matching the spell level name.
    If this cannot be found, returns None.
    '''
    levels = get_levels()
    if name not in levels:
        return None
    return levels[name]

def get_level_name(level: dict):
    '''Returns a string giving a level's name.
    If this cannot be found, returns None.
    '''
    if "name" not in level:
        return None
    return level["name"]

def get_level_plural(level: dict):
    '''Returns a string giving a level's plural form.
    If this cannot be found, returns None.
    '''
    if "plural" not in level:
        return None
    return level["plural"]

def get_level_number(level: dict):
    '''Returns an integer giving a level's numeral value.
    If this cannot be found, returns None.
    '''
    if "number" not in level:
        return None
    return level["number"]

def get_level_name_from_number(number: int):
    '''Returns a string giving a level's name.
    If this cannot be found, returns None.
    '''
    levels = get_levels()
    for level in levels.values():
        if number == get_level_number(level):
            return get_level_name(level)
    return None

def get_level_number_from_name(name: str):
    '''Returns an integer giving a level's value.
    If this cannot be found, returns None.
    '''
    levels = get_levels()
    if name not in levels or "number" not in levels[name]:
        return None
    return levels[name]["number"]

def get_unit(name: str):
    '''Returns a dict of a unit matching the name.
    If this cannot be found, returns None.
    '''
    units = get_units()
    if name not in units:
        return None
    return units[name]

def get_unit_name(unit: dict):
    '''Returns a string giving a unit's name.
    If this cannot  be found, returns None.
    '''
    if "name" not in unit:
        return None
    return unit["name"]

def get_unit_plural(unit: dict):
    '''Returns a string giving a unit's plural form.
    If this cannot be found, returns None.
    '''
    if "plural" not in unit:
        return None
    return unit["plural"]

def get_unit_rounds(unit: dict):
    '''Returns how many rounds of combat a unit is equivalent to.
    If this cannot be found, returns None.
    '''
    if "rounds" not in unit:
        return None
    return unit["rounds"]

def get_spell(name: str):
    '''Returns a dict of a spell matching the given name.
    If this cannot be found, returns None.
    '''
    spells = get_spells()
    if name not in spells:
        return None
    return spells[name]

def get_spell_name(spell: dict):
    '''Returns the name of a spell.
    If this cannot be found, returns None.
    '''
    if "name" not in spell:
        return None
    return spell["name"]

def get_spell_level(spell: dict):
    '''Returns the level of a spell.
    If this cannot be found, returns None.
    '''
    if "level" not in spell:
        return None
    return spell["level"]

def get_spell_school(spell: dict):
    '''Returns the school of a spell.
    If this cannot be found, returns None.
    '''
    if "school" not in spell:
        return None
    return spell["school"]

def get_spell_ritual(spell: dict):
    '''Returns True if the spell is a ritual.
    If this cannot be found, returns False.
    '''
    if "ritual" not in spell:
        return False
    return spell["ritual"]

def get_spell_classes(spell: dict):
    '''Returns a list of which classes have a spell on their spell list.
    If this cannot be found, returns None.
    '''
    if "classes" not in spell:
        return None
    return spell["classes"]

def get_spell_casting_time(spell: dict):
    '''Returns a list giving the casting time of a spell.
    Generally contains a single element, but some spells have variable casting
    times.
    If this cannot be found, returns None.
    '''
    if "time" not in spell:
        return None
    return spell["time"]

def get_spell_duration(spell: dict):
    '''Returns a list giving the duration of a spell.
    Generally contains a single element, but some spells have variable
    durations.
    If this cannot be found, returns None.
    '''
    if "duration" not in spell:
        return None
    return spell["duration"]

def get_spell_time_up_to(time: dict):
    '''Returns True if the provided casting time or duration dict is marked as
    being prefixed by "Up to".
    If this cannot be found, returns False.
    '''
    if "up_to" not in time:
        return False
    return time["up_to"]

def get_spell_time_number(time: dict):
    '''Returns an integer giving the number preceding the unit of a casting
    time or duration dict.
    If this cannot be found, returns None.
    '''
    if "number" not in time:
        return None
    return time["number"]

def get_spell_time_unit(time: dict):
    '''Returns a string giving the unit of a casting time or duration dict.
    If this cannot be found, returns None.
    '''
    if "unit" not in time:
        return None
    return time["unit"]

def get_spell_time_condition(time: dict):
    '''Returns a string giving the condition of a reaction casting time dict.
    If this cannot be found, returns None.
    '''
    if "condition" not in time:
        return None
    return time["condition"]

def get_spell_time_concentration(time: dict):
    '''Returns True if the provided casting time or duration dict is marked as
    requiring concentration.
    If this cannot be found, returns False.
    '''
    if "concentration" not in time:
        return False
    return time["concentration"]

def get_spell_concentration(spell: dict):
    '''Returns True if a spell is marked as concentration for any of its
    duration entries.
    If this cannot be found, returns False.
    '''
    duration = get_spell_duration(spell)
    if duration != None:
        for time in duration:
            if get_spell_time_concentration(time):
                return True
    return False

def get_spell_range(spell: dict):
    '''Returns the string denoting the range of a spell.
    If this cannot be found, returns None.
    '''
    if "range" not in spell:
        return None
    return spell["range"]

def get_spell_components(spell: dict):
    '''Returns a dict giving the components of a spell.
    V and S keys have boolean values. M key has string value giving materials.
    If this cannot be found, returns None.
    '''
    if "components" not in spell:
        return None
    return spell["components"]

def get_spell_summary(spell: dict):
    '''Returns the short description of a spell.
    If this cannot be found, returns None.
    '''
    if "summary" not in spell:
        return None
    return spell["summary"]

def get_spell_description(spell: dict):
    '''Returns the full description of a spell.
    If this cannot be found, returns None.
    '''
    if "description" not in spell:
        return None
    return spell["description"]

def get_spell_additional_info(spell: dict):
    '''Returns a dict giving the additional info of a spell.
    If this cannot be found, returns an empty dict.
    '''
    if "additional_info" not in spell:
        return {}
    return spell["additional_info"]

def get_spell_on_cast(spell: dict):
    '''Returns a dict giving the actions to perform on the casting of a spell.
    If this cannot be found, returns an empty dict.
    '''
    if "on_cast" not in spell:
        return {}
    return spell["on_cast"]

def get_spell_on_cast_damage(spell: dict):
    '''Returns a list giving the damage roll(s) dicts for the casting of a
    spell.
    If this cannot be found, returns None.
    '''
    on_cast = get_spell_on_cast(spell)
    if "damage" not in on_cast:
        return None
    return on_cast["damage"]

def get_plural(name: str):
    '''Returns the plural form of a name in either the spell levels or units
    database.
    If the name is not found in either, returns the name with an -s appended.
    '''
    level = get_level(name)
    if level != None:
        plural = get_level_plural(level)
        if plural != None:
            return plural
    unit = get_unit(name)
    if unit != None:
        plural = get_unit_plural(unit)
        if plural != None:
            return plural
    return f"{name}s"

#Spell information handling functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Backend functions

def get_spells_file():
    '''Returns a dict containing the entire spells file database.
    '''
    return read_from_json(spells_file)

def save_spells_file(new_file: dict):
    '''Overwrites the entire spells file database with the provided dict.
    '''
    write_to_json(spells_file, new_file)

def get_level_numbers_from_names(level_names: list):
    '''Returns a list of each integer matching the input level names.
    If a name cannot be found, it is appended as None.
    '''
    result = []
    for level_name in level_names:
        level_int = get_level_number_from_name(level_name)
        result.append(level_int)
    return result

def get_spells_from_names_list(spell_names: list):
    '''Returns a list of each spell dict matching the input names.
    If a name cannot be found, it is appended as None.
    '''
    spells = get_spells()
    result = []
    for spell_name in spell_names:
        if spell_name in spells:
            result.append(spells[spell_name])
        else:
            result.append(None)
    return result

def get_spell_names_on_list_from_class_list(spell_names: list, class_names: list):
    '''Returns a list of strings giving spells from the input spell list which
    are on any of the input classes' spell list.
    '''
    spells = get_spells_from_names_list(spell_names)
    result = []
    for spell in spells:
        spell_classes = get_spell_classes(spell)
        if spell_classes != None:
            for class_name in class_names:
                if class_name in spell_classes:
                    spell_name = get_spell_name(spell)
                    result.append(spell_name)
                    break
    return result

def get_spell_names_on_list_from_school_list(spell_names: list, schools: list):
    '''Returns a list of strings giving spells from the input spell list which
    are of any of the input schools.
    '''
    spells = get_spells_from_names_list(spell_names)
    result = []
    for spell in spells:
        if get_spell_school(spell) in schools:
            spell_name = get_spell_name(spell)
            result.append(spell_name)
    return result

def get_spell_names_on_list_from_level_list(spell_names: list, levels: list):
    '''Returns a list of strings giving spells from the input spell list which
    are of any of the input levels.
    '''
    spells = get_spells_from_names_list(spell_names)
    result = []
    for spell in spells:
        if get_spell_level(spell) in levels:
            spell_name = get_spell_name(spell)
            result.append(spell_name)
    return result

def get_spell_names_on_list_from_class(spell_names: list, class_name: str):
    '''Returns a list of strings giving spells from the input spell list which
    are on the input class's spell list.
    '''
    spells = get_spells_from_names_list(spell_names)
    result = []
    for spell in spells:
        spell_classes = get_spell_classes(spell)
        if spell_classes != None and class_name in spell_classes:
            spell_name = get_spell_name(spell)
            result.append(spell_name)
    return result

def get_spell_names_on_list_from_school(spell_names: list, school: str):
    '''Returns a list of strings giving spells from the input spell list which
    are of the input school.
    '''
    spells = get_spells_from_names_list(spell_names)
    result = []
    for spell in spells:
        if school == get_spell_school(spell):
            spell_name = get_spell_name(spell)
            result.append(spell_name)
    return result

def get_spell_names_on_list_from_level(spell_names: list, level: int):
    '''Returns a list of strings giving spells from the input spell list which
    are of the input level.
    '''
    spells = get_spells_from_names_list(spell_names)
    result = []
    for spell in spells:
        if level == get_spell_level(spell):
            spell_name = get_spell_name(spell)
            result.append(spell_name)
    return result

def get_spell_names_from_class(class_name: str):
    '''Returns a list of strings giving spells that are on the input class's
    spell list.
    '''
    spell_names = get_spell_names()
    return get_spell_names_on_list_from_class(spell_names, class_name)

def get_spell_names_from_school(school: str):
    '''Returns a list of strings giving spells that are of the input school.
    '''
    spell_names = get_spell_names()
    return get_spell_names_on_list_from_school(spell_names, school)

def get_spell_names_from_level(level: int):
    '''Returns a list of strings giving spells that are of the input level.
    '''
    spell_names = get_spell_names()
    return get_spell_names_on_list_from_level(spell_names, level)

def get_spell_category_as_string(spell: dict):
    '''Returns a string giving a spell's level, school, and optionally whether
    it's a ritual spell.
    '''
    school = get_spell_school(spell)
    level_int = get_spell_level(spell)
    level_name = get_level_name_from_number(level_int)
    desc = ""
    if level_int == 0:
        desc += f"{school} {level_name}"
    else:
        desc += f"{level_name} {school}"
    ritual = get_spell_ritual(spell)
    if ritual:
        desc += " (ritual)"
    return desc

def get_spell_casting_time_as_string(spell: dict):
    '''Returns a string giving a spell's casting time(s).
    '''
    times = get_spell_casting_time(spell)
    i = 0
    desc = ""
    for time in times:
        if i != 0: desc += " or "
        num = get_spell_time_number(time)
        unit = get_spell_time_unit(time)
        cond = get_spell_time_condition(time)
        if num != None:
            desc += f"{num} "
            if num != 1:
                unit = get_plural(unit)
        desc += f"{unit}"
        if cond != None: desc += f" ({cond})"
        i += 1
    return desc

def get_spell_components_as_string(spell: dict):
    '''Returns a string giving a spell's components.
    '''
    components = get_spell_components(spell)
    i = 0
    desc = ""
    for symbol, materials in components.items():
        if i != 0: desc += ", "
        desc += f"{symbol}"
        if type(materials) is str:
            desc += f" ({materials})"
        i += 1
    return desc

def get_spell_duration_as_string(spell: dict):
    '''Returns a string giving a spell's duration(s) and optionally whether
    it's a concentration spell.
    '''
    durations = get_spell_duration(spell)
    concentration = get_spell_concentration(spell)
    i = 0
    desc = ""
    if concentration:
        desc += "Concentration, up to "
    for duration in durations:
        if i != 0: desc += " or "
        conc = get_spell_time_concentration(duration)
        upto = get_spell_time_up_to(duration)
        num = get_spell_time_number(duration)
        unit = get_spell_time_unit(duration)
        if upto and not conc: desc += "Up to "
        if num != None:
            desc += f"{num} "
            if num != 1:
                unit = get_plural(unit)
        desc += f"{unit}"
        i += 1
    if i > 1:
        desc += " (see below)"
    return desc

def get_spell_additional_info_as_string(spell: dict):
    '''Returns a string giving a spell's additional information.
    '''
    info = get_spell_additional_info(spell)
    desc = ""
    linebreak = False
    for key, value in info.items():
        if linebreak: desc += "\n"
        desc += f"***{key}.*** {value}"
        linebreak = True
    return desc

def get_spell_classes_as_string(spell: dict):
    '''Returns a string giving which classes have a spell on their spell list.
    '''
    classes = get_spell_classes(spell)
    desc = ""
    for i, c_class in enumerate(classes):
        if i != 0: desc += ", "
        desc += c_class
    if desc == "": desc = "—"
    return desc

def generate_spell_embed_description(spell: dict, include_classes=True):
    '''Returns a string to use as the description field of a full spell Embed.
    '''
    category = get_spell_category_as_string(spell)
    desc = f"*{category.capitalize()}*"
    time = get_spell_casting_time_as_string(spell)
    desc += f"\n**Casting Time:** {time.capitalize()}"
    range = get_spell_range(spell)
    desc += f"\n**Range:** {range.capitalize()}"
    components = get_spell_components_as_string(spell)
    desc += f"\n**Components:** {components}"
    duration = get_spell_duration_as_string(spell)
    desc += f"\n**Duration:** {duration.capitalize()}"
    description = get_spell_description(spell)
    desc += f"\n{description}"
    additional_info = get_spell_additional_info_as_string(spell)
    if additional_info != "": desc += f"\n{additional_info}"
    if include_classes:
        classes = get_spell_classes_as_string(spell)
        desc += f"\n**Classes:** {classes}"
    return desc

def generate_spell_embed(spell: dict):
    '''Returns an Embed object for a spell.
    '''
    name = get_spell_name(spell)
    desc = generate_spell_embed_description(spell)
    embed = Embed(title=name, description=desc)
    return embed

def generate_spell_name_embed(spell_name: str):
    '''Returns an Embed object for a spell matching the given name.
    '''
    spell = get_spell(spell_name)
    if spell == None:
        raise Exception("Spell not found")
    return generate_spell_embed(spell)

def generate_spells_list_embed_field(spell_names: list, include_summary=False):
    '''Returns a string to use as a field of the spell list Embed.
    '''
    value = ""
    for name in spell_names:
        value += f"● **{name}**\n"
        if include_summary:
            spell = get_spell(name)
            summary = get_spell_summary(spell)
            if summary != None:
                value += f"> {summary}\n"
    return value

def generate_spells_list_embed(title: str, spell_names: list):
    '''Returns an Embed listing multiple spells' details.
    '''
    embed = Embed(title=title)
    half = math.ceil(len(spell_names)/2)
    first = generate_spells_list_embed_field(spell_names[:half])
    second = generate_spells_list_embed_field(spell_names[half:])
    delim, replac = "●", [("●", "\n● "), (" > ", "\n> ")]
    if len(first) > 1024: first = fit_text_to_length(first, 1024, delimiter=delim, replacements=replac)
    if len(second) > 1024: second = fit_text_to_length(second, 1024, delimiter=delim, replacements=replac)
    if first != "": embed.add_field(name="\u200b", value=first)
    if second != "": embed.add_field(name="\u200b", value=second)
    return embed

def generate_paginated_spells_list_embed(title: str, spell_names: list, page=1):
    '''Returns an Embed supporting large lists of spells by only rendering a
    portion of the list
    '''
    spell_list_page = slice_list_page(spell_names, page)
    embed = generate_spells_list_embed(title, spell_list_page)
    if len(spell_names) > 25:
        total = math.ceil(len(spell_names)/25)
        embed.set_footer(text=f"Page {page}/{total}")
    return embed

def generate_spell_cast_embed(author, spell: dict):
    '''Returns an Embed giving one casting of a spell.
    '''
    name = get_spell_name(spell)
    caster = author.name # TODO Check character list
    desc = ""
    summary = get_spell_summary(spell)
    if summary != None: desc += summary
    damage = get_spell_on_cast_damage(spell)
    if damage != None: desc += str(damage) # TODO implement rolling, more than damage
    embed = Embed(title=f"{caster} casts {name}!", description=desc)
    return embed

def generate_filtered_spell_category_name(classes: list, levels: list, schools: list):
    '''Returns a string giving a category title for a set of spell filters.
    '''
    cantrip = get_level_name_from_number(0)
    name = ""
    len_classes = len(classes)
    len_levels = len(levels)
    len_schools = len(schools)
    max_len = 3
    if len_classes > max_len or len_levels > max_len or len_schools > max_len:
        name += "Filtered "
    if len_levels > 0 and len_levels <= max_len:
        ampersand = False
        for level_name in levels:
            if level_name != cantrip:
                if ampersand:
                    name += "& "
                name += f"{level_name} "
                ampersand = True
    if len_schools > 0 and len_schools <= max_len:
        school_names = " & ".join(schools)
        name += f"{school_names} "
    if len_classes > 0 and len_classes <= max_len:
        class_names = " & ".join(classes)
        name += f"{class_names} "
    if levels != [cantrip]:
        name += "Spells"
        if cantrip in levels:
            name += " & "
    if cantrip in levels:
        name += get_plural(cantrip)
    return name

def get_matching_spell(spell_name: str):
    '''Returns a message, Embed, and view as a message response.
    Checks the entire spells list for the five closest spell names matching
    with the input spell name.
    '''
    msg, embed, view = "", None, None
    spell_names = get_spell_names()
    matches = get_closest_matches(spell_name, spell_names)
    if type(matches) is not list: #Perfect match
        embed = generate_spell_name_embed(matches)
        return msg, embed, view
    if matches != []: #5 close matches
        msg = f'Closest matches to "{spell_name}":'
        view = ClosestMatchingSpellsMenu(matches)
    else: #No close matches
        msg = f'No matches found for "{spell_name}"'
    return msg, embed, view

def get_matching_spell_for_cast(spell_name: str):
    '''Returns the best match.
    '''
    spell_names = get_spell_names()
    matches = get_closest_matches(spell_name, spell_names)
    if type(matches) is not list: #Perfect match
        return matches
    return matches[0]

#Backend functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#User Interface elements

def message_mainmenu():
    return ("Select a spell category to examine!\n"
        "Alternatively, use `!spell [name]` to display a specific spell!"
    )

def message_filtermenu():
    return "Filter by classes, levels, or schools!"

#Main menu
class MainMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=view_timeout)
        self.add_item(AllSpellsButton())
        self.add_item(FilterButton())
        self.add_item(SearchButton())

#Select spells by class menu
class SelectClassMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=view_timeout)
        self.add_item(ClassSelect())

#Select spells by level menu
class SelectLevelMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=view_timeout)
        self.add_item(LevelSelect())

#Select spells by school menu
class SelectSchoolMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=view_timeout)
        self.add_item(SchoolSelect())

#Filter spells menu
class FilterMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=view_timeout)
        self.add_item(ClassFilterSelect())
        self.add_item(LevelFilterSelect())
        self.add_item(SchoolFilterSelect())
        self.add_item(ConfirmFilterButton())

#Select spell to show menu
class SelectSpellToShowMenu(ui.View):
    def __init__(self, category_name: str, spell_names: list, page=1):
        super().__init__(timeout=view_timeout)
        if len(spell_names) > 25:
            self.add_item(SpellListBackButton(category_name, spell_names, page))
            self.add_item(SpellListSkipButton(category_name, spell_names, page))
            self.add_item(SpellListForwardButton(category_name, spell_names, page))
        if len(spell_names) > 0:
            spell_page = slice_list_page(spell_names, page)
            options = generate_selectoptions(labels=spell_page)
            self.add_item(SpellSelect(options))

#Cast spells menu
class CastMenu(ui.View):
    def __init__(self, spell_name: str):
        super().__init__(timeout=view_timeout)
        self.add_item(SpellButton(spell_name, label="Full Spell Description"))

#Closest matching spells menu
class ClosestMatchingSpellsMenu(ui.View):
    def __init__(self, spell_names: list):
        super().__init__(timeout=view_timeout)
        for spell_name in spell_names:
            button = SpellButton(spell_name)
            self.add_item(button)

class SpellListBackButton(ui.Button):
    def __init__(self, category_name: str, spell_names: list, page: int):
        self.category_name = category_name
        self.spell_names = spell_names
        self.page = page
        disabled = True if page <= 1 else False
        prev_page = page if disabled else page-1
        super().__init__(label=f"← Page {prev_page}", style=discord.ButtonStyle.blurple, disabled=disabled, row=3)

    async def callback(self, interaction):
        try:
            embed = generate_paginated_spells_list_embed(self.category_name, self.spell_names, page=self.page-1)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectSpellToShowMenu(self.category_name, self.spell_names, self.page-1)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SpellListSkipButton(ui.Button):
    def __init__(self, category_name: str, spell_names: list, page: int):
        self.category_name = category_name
        self.spell_names = spell_names
        self.page = page
        super().__init__(label=f"…", style=discord.ButtonStyle.blurple, row=3)

    async def callback(self, interaction):
        try:
            await interaction.response.send_modal(PageSkipModal(self.category_name, self.spell_names))
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SpellListForwardButton(ui.Button):
    def __init__(self, category_name: str, spell_names: list, page: int):
        self.category_name = category_name
        self.spell_names = spell_names
        self.page = page
        disabled = True if 25*page >= len(spell_names) else False
        next_page = page if disabled else page+1
        super().__init__(label=f"Page {next_page} →", style=discord.ButtonStyle.blurple, disabled=disabled, row=3)

    async def callback(self, interaction):
        try:
            embed = generate_paginated_spells_list_embed(self.category_name, self.spell_names, page=self.page+1)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectSpellToShowMenu(self.category_name, self.spell_names, self.page+1)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class FilterButton(ui.Button):
    def __init__(self):
        super().__init__(label="Filter", style=discord.ButtonStyle.blurple, emoji="🗑️")

    async def callback(self, interaction):
        try:
            msg = message_filtermenu()
            await interaction.response.send_message(msg, view=FilterMenu(), ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class AllSpellsButton(ui.Button):
    def __init__(self):
        super().__init__(label="All Spells", style=discord.ButtonStyle.blurple, emoji="📚")

    async def callback(self, interaction):
        try:
            category_name = "All Spells"
            spell_names = sorted(get_spell_names())
            embed = generate_paginated_spells_list_embed(category_name, spell_names)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectSpellToShowMenu(category_name, spell_names)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SearchButton(ui.Button):
    def __init__(self):
        super().__init__(label="Search", style=discord.ButtonStyle.blurple, emoji="🔍")

    async def callback(self, interaction):
        try:
            await interaction.response.send_modal(SearchSpellModal())
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SpellsByClassButton(ui.Button):
    def __init__(self):
        super().__init__(label="By Class", style=discord.ButtonStyle.grey, emoji="👥", row=3)

    async def callback(self, interaction):
        try:
            await interaction.response.send_message(view=SelectClassMenu(), ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SpellsByLevelButton(ui.Button):
    def __init__(self):
        super().__init__(label="By Level", style=discord.ButtonStyle.grey, emoji="🔢", row=3)

    async def callback(self, interaction):
        try:
            await interaction.response.send_message(view=SelectLevelMenu(), ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SpellsBySchoolButton(ui.Button):
    def __init__(self):
        super().__init__(label="By School", style=discord.ButtonStyle.grey, emoji="📖", row=3)

    async def callback(self, interaction):
        try:
            await interaction.response.send_message(view=SelectSchoolMenu(), ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SpellButton(ui.Button):
    def __init__(self, spell_name: str, label=None):
        self.spell_name = spell_name
        if label == None:
            label = spell_name
        super().__init__(label=label, style=discord.ButtonStyle.blurple)

    async def callback(self, interaction):
        try:
            embed = generate_spell_name_embed(self.spell_name)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ConfirmFilterButton(ui.Button):
    def __init__(self):
        super().__init__(label="Confirm", style=discord.ButtonStyle.green)

    async def callback(self, interaction):
        try:
            spell_names = get_spell_names()
            classes = self.view.children[0].values
            if classes != []:
                spell_names = get_spell_names_on_list_from_class_list(spell_names, classes)
            levels = self.view.children[1].values
            if levels != []:
                level_ints = get_level_numbers_from_names(levels)
                spell_names = get_spell_names_on_list_from_level_list(spell_names, level_ints)
            schools = self.view.children[2].values
            if schools != []:
                spell_names = get_spell_names_on_list_from_school_list(spell_names, schools)
            category_name = generate_filtered_spell_category_name(classes, levels, schools)
            embed = generate_paginated_spells_list_embed(category_name, spell_names)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectSpellToShowMenu(category_name, spell_names)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ClassFilterSelect(ui.Select):
    def __init__(self):
        class_names = get_class_names()
        length = len(class_names)
        options = generate_selectoptions(class_names)
        super().__init__(placeholder="Select Class", options=options, min_values=0, max_values=length)

    async def callback(self, interaction):
        try:
            await interaction.response.defer()
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class LevelFilterSelect(ui.Select):
    def __init__(self):
        level_names = get_level_names()
        length = len(level_names)
        level_plurals = get_level_plurals()
        options = generate_selectoptions(labels=level_plurals, values=level_names)
        super().__init__(placeholder="Select Level", options=options, min_values=0, max_values=length)

    async def callback(self, interaction):
        try:
            await interaction.response.defer()
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SchoolFilterSelect(ui.Select):
    def __init__(self):
        school_names = get_school_names()
        length = len(school_names)
        options = generate_selectoptions(school_names)
        super().__init__(placeholder="Select School", options=options, min_values=0, max_values=length)

    async def callback(self, interaction):
        try:
            await interaction.response.defer()
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ClassSelect(ui.Select):
    def __init__(self):
        class_names = get_class_names()
        options = generate_selectoptions(class_names)
        super().__init__(placeholder="Select Class", options=options)

    async def callback(self, interaction):
        try:
            name = "".join(self.values)
            category_name = f"{name} Spells"
            spell_names = get_spell_names_from_class(name)
            embed = generate_paginated_spells_list_embed(category_name, spell_names)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectSpellToShowMenu(category_name, spell_names)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class LevelSelect(ui.Select):
    def __init__(self):
        level_names = get_level_names()
        level_plurals = get_level_plurals()
        options = generate_selectoptions(labels=level_plurals, values=level_names)
        super().__init__(placeholder="Select Level", options=options)

    async def callback(self, interaction):
        try:
            level_name = "".join(self.values)
            level = get_level(level_name)
            level_int = get_level_number(level)
            level_plural = get_level_plural(level)
            spell_names = get_spell_names_from_level(level_int)
            embed = generate_paginated_spells_list_embed(level_plural, spell_names)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectSpellToShowMenu(level_plural, spell_names)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SchoolSelect(ui.Select):
    def __init__(self):
        school_names = get_school_names()
        options = generate_selectoptions(school_names)
        super().__init__(placeholder="Select School", options=options)

    async def callback(self, interaction):
        try:
            name = "".join(self.values)
            category_name = f"{name} Spells"
            spell_names = get_spell_names_from_school(name)
            embed = generate_paginated_spells_list_embed(category_name, spell_names)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectSpellToShowMenu(category_name, spell_names)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SpellSelect(ui.Select):
    def __init__(self, options: list):
        super().__init__(placeholder="Select Spell", options=options)

    async def callback(self, interaction):
        try:
            pick = "".join(self.values)
            embed = generate_spell_name_embed(pick)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class PageSkipModal(ui.Modal, title="Skip to Page"):
    def __init__(self, category_name, spell_names):
        super().__init__(timeout=view_timeout)
        self.category_name = category_name
        self.spell_names = spell_names

    input = ui.TextInput(label="Page Number", placeholder="Skip to which page?", required=True)

    async def on_submit(self, interaction):
        try:
            page = self.input.value
            max_page = math.ceil(len(self.spell_names)/25)
            if page.isdigit() == False or int(page) > max_page:
                await interaction.response.send_message(f'"{page}" is not a valid page number.', ephemeral=True)
                return
            page = int(page)
            embed = generate_paginated_spells_list_embed(self.category_name, self.spell_names, page=page)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectSpellToShowMenu(self.category_name, self.spell_names, page)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SearchSpellModal(ui.Modal, title="Search Spell"):
    input = ui.TextInput(label="Spell", placeholder="What spell are you looking for?",
        max_length=max_spell_name_length, required=True
    )

    async def on_submit(self, interaction):
        try:
            name = self.input.value
            msg, embed, view = get_matching_spell(name)
            await interaction.response.send_message(msg, embed=embed, view=view, ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

#User Interface elements
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Bot commands

#Cog Setup
class Spells(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Spells cog loaded.")

    @commands.group(name="spells", aliases=["spell"], case_insensitive=True, invoke_without_command=True)
    async def spells(self, ctx, *spell):
        try:
            if not spell:
                msg = message_mainmenu()
                await ctx.channel.send(msg, view=MainMenu())
                return
            input = " ".join(spell)
            msg, embed, view = get_matching_spell(input)
            await ctx.channel.send(msg, embed=embed, view=view)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @spells.command(aliases=["help", "?", "info", "information", "instructions"])
    async def spells_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "spells")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.group(name="cast", aliases=[], case_insensitive=True, invoke_without_command=True)
    async def cast(self, ctx, *spell):
        try:
            if not spell:
                pass # TODO fetch spell list from character if possible
                return
            input = " ".join(spell)
            spell_name = get_matching_spell_for_cast(input)
            spell = get_spell(spell_name)
            author = ctx.message.author
            embed = generate_spell_cast_embed(author, spell)
            await ctx.channel.send(embed=embed, view=CastMenu(spell_name))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @cast.command(aliases=["help", "?", "info", "information", "instructions"])
    async def cast_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "cast")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

async def setup(client):
    await client.add_cog(Spells(client))
