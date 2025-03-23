#===============================================================================
# Items v1.0.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 06 May 2024 - v1.0.1; Added a help command and reworked error handling. -YY
# 16 Oct 2022 - v1.0; Finished file. Includes item lookup, a way to browse all
#               items, several categories to browse, and specific item details.
#               -YY
# 10 Oct 2022 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# items.py displays and handles D&D 5e items.
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
import string

items_file = "data/dnd/items.json"
view_timeout = 259200
max_item_name_length = 256

#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Item information handling functions

def get_items():
    '''Returns a dict containing all items in the database.
    If the items list cannot be found, returns an empty dict.
    '''
    dict = get_items_file()
    if "items" not in dict:
        return {}
    return dict["items"]

def get_categories():
    '''Returns a dict containing all categories in the database.
    If the categories list cannot be found, returns an empty dict.
    '''
    dict = get_items_file()
    if "categories" not in dict:
        return {}
    return dict["categories"]

def get_properties():
    '''Returns a dict containing all weapon properties in the database.
    If the weapon properties list cannot be found, returns an empty dict.
    '''
    dict = get_items_file()
    if "weapon_properties" not in dict:
        return {}
    return dict["weapon_properties"]

def get_item_names():
    '''Returns a list containing all item names in the database.
    If the items list cannot be found, returns an empty list.
    '''
    dict = get_items()
    return list(dict.keys())

def get_category_names():
    '''Returns a list containing all category names in the database.
    If the categories list cannot be found, returns an empty list.
    '''
    dict = get_categories()
    return list(dict.keys())

def get_property_names():
    '''Returns a list containing all weapon property names in the database.
    If the weapon properties list cannot be found, returns an empty list.
    '''
    dict = get_properties()
    return list(dict.keys())

def get_category(name: str):
    '''Returns a category's dict of data.
    If the category cannot be found, returns None.
    '''
    categories = get_categories()
    if name not in categories:
        return None
    return categories[name]

def get_category_name(category: dict):
    '''Returns the string from a category's name entry.
    If category cannot be found, returns None.
    '''
    if "name" not in category:
        return None
    return category["name"]

def get_category_plural(category: dict):
    '''Returns the string from an category's plural form entry.
    If this cannot be found, returns the category's name with an -s appended.
    If the name cannot be found either, returns None.
    '''
    if "plural" not in category:
        name = get_item_name(category)
        if name == None:
            return None
        return f"{name}s"
    return category["plural"]

def get_category_description(category: dict):
    '''Returns the description of a category.
    If this cannot be found, returns None.
    '''
    if "description" not in category:
        return None
    return category["description"]

def get_property(name: str):
    '''Returns a weapon property's dict of data.
    If the weapon property cannot be found, returns None.
    '''
    properties = get_properties()
    if name not in properties:
        return None
    return properties[name]

def get_property_name(property: dict):
    '''Returns the string from a weapon property's name entry.
    If weapon property cannot be found, returns None.
    '''
    if "name" not in property:
        return None
    return property["name"]

def get_property_description(property: dict):
    '''Returns the string from a weapon property's description entry.
    If weapon property cannot be found, returns None.
    '''
    if "description" not in property:
        return None
    return property["description"]

def get_item(name: str):
    '''Returns an item's dict of data.
    If the item cannot be found, returns None.
    '''
    items = get_items()
    if name not in items:
        return None
    item = items[name]
    alias = get_item_alias(item)
    if alias != None:
        source = get_item(alias)
        for key, value in item.items():
            if key != "alias":
                source[key] = value
        item = source
    return item

def get_item_name(item: dict):
    '''Returns the string from an item's name entry.
    If this cannot be found, returns None.
    '''
    if "name" not in item:
        return None
    return item["name"]

def get_item_plural(item: dict):
    '''Returns the string from an item's plural form entry.
    If this cannot be found, returns the item's name with an -s appended.
    If the name cannot be found either, returns None.
    '''
    if "plural" not in item:
        name = get_item_name(item)
        if name == None:
            return None
        return f"{name}s"
    return item["plural"]

def get_item_alias(item: dict):
    '''Returns which other item an item is aliased from.
    If this cannot be found, returns None.
    '''
    if "alias" not in item:
        return None
    return item["alias"]

def get_item_categories(item: dict):
    '''Returns a list containing the item's categories.
    If this cannot be found, returns an empty list.
    '''
    if "categories" not in item:
        return []
    return item["categories"]

def get_weapon_properties(item: dict):
    '''Returns a list containing an item's weapon properties.
    If this cannot be found, returns an empty list.
    '''
    if "weapon_properties" not in item:
        return []
    return item["weapon_properties"]

def get_item_description(item: dict):
    '''Returns an item's description.
    If this cannot be found, returns None.
    '''
    if "description" not in item:
        return None
    return item["description"]

def get_item_cost(item: dict):
    '''Returns an item's cost.
    If this cannot be found, returns 0.
    '''
    if "cost" not in item:
        return 0
    return item["cost"]

def get_item_weight(item: dict):
    '''Returns an item's weight.
    If this cannot be found, returns 0.
    '''
    if "weight" not in item:
        return 0
    return item["weight"]

def get_item_armor(item: dict):
    '''Returns an item's armor statistics.
    If this cannot be found, returns None.
    '''
    if "armor" not in item:
        return None
    return item["armor"]

def get_item_weapon(item: dict):
    '''Returns an item's weapon statistics.
    If this cannot be found, returns None.
    '''
    if "weapon" not in item:
        return None
    return item["weapon"]

def get_item_contents(item: dict):
    '''Returns an item's contents.
    If this cannot be found, returns None.
    '''
    if "contents" not in item:
        return None
    return item["contents"]

def get_armor_slot(item: dict):
    '''Returns the slot where an armor item is worn.
    If this cannot be found, returns None.
    '''
    armor = get_item_armor(item)
    if armor == None or "slot" not in armor:
        return None
    return armor["slot"]

def get_armor_ac(item: dict):
    '''Returns the AC-related statistics from an armor item.
    If this cannot be found, returns None.
    '''
    armor = get_item_armor(item)
    if armor == None or "ac" not in armor:
        return None
    return armor["ac"]

def get_armor_base_ac(item: dict):
    '''Returns the base AC granted by an armor item.
    If this cannot be found, returns None.
    '''
    ac = get_armor_ac(item)
    if ac == None or "base_ac" not in ac:
        return None
    return ac["base_ac"]

def get_armor_max_bonus(item: dict):
    '''Returns the max Dexterity modifier bonus applicable to an armor item.
    If this cannot be found, returns None.
    '''
    ac = get_armor_ac(item)
    if ac == None or "max_bonus" not in ac:
        return None
    return ac["max_bonus"]

def get_armor_bonus_ac(item: dict):
    '''Returns the flat AC bonus granted by an armor item.
    If this cannot be found, returns 0.
    '''
    ac = get_armor_ac(item)
    if ac == None or "bonus_ac" not in ac:
        return 0
    return ac["bonus_ac"]

def get_armor_requirements(item: dict):
    '''Returns the requirements of using an armor item without Speed penalty.
    If this cannot be found, returns None.
    '''
    ac = get_armor_ac(item)
    if ac == None or "requirement" not in ac:
        return None
    return ac["requirement"]

def get_armor_disadvantages(item: dict):
    '''Returns which skills are given disadvantage by an armor item
    If this cannot be found, returns an empty list.
    '''
    armor = get_item_armor(item)
    if armor == None or "disadvantage" not in armor:
        return []
    return armor["disadvantage"]

def get_weapon_damage(item: dict):
    '''Returns a list of the damage dice or flat damage done as well as
    associated damage types are done by a weapon item.
    If this cannot be found, returns an empty list.
    '''
    weapon = get_item_weapon(item)
    if weapon == None or "damage" not in weapon:
        return []
    return weapon["damage"]

def get_weapon_damage_dice(damage: dict):
    '''Returns the dice count for a weapon damage dict.
    If this cannot be found, returns 0.
    '''
    if "dice" not in damage:
        return 0
    return damage["dice"]

def get_weapon_damage_faces(damage: dict):
    '''Returns the dice faces for a weapon damage dict.
    If this cannot be found, returns 0.
    '''
    if "faces" not in damage:
        return 0
    return damage["faces"]

def get_weapon_damage_flat(damage: dict):
    '''Returns the flat damage for a weapon damage dict.
    If this cannot be found, returns 0.
    '''
    if "flat" not in damage:
        return 0
    return damage["flat"]

def get_weapon_damage_type(damage: dict):
    '''Returns the damage type for a weapon damage dict.
    If this cannot be found, returns None.
    '''
    if "type" not in damage:
        return None
    return damage["type"]

def get_weapon_versatile(item: dict):
    '''Returns a list of the damage dice or flat damage done as well as
    associated damage types are done by using a Versatile weapon two-handedly.
    If this cannot be found, returns None.
    '''
    weapon = get_item_weapon(item)
    if weapon == None or "versatile" not in weapon:
        return None
    return weapon["versatile"]

def get_weapon_range(item: dict):
    '''Returns a dict containing the normal range and long range at which an
    item can be thrown or shot from.
    If this cannot be found, returns None.
    '''
    weapon = get_item_weapon(item)
    if weapon == None or "range" not in weapon:
        return None
    return weapon["range"]

def get_weapon_normal_range(item: dict):
    '''Returns an integer giving the normal range of a ranged item.
    If this cannot be found, returns None.
    '''
    range = get_weapon_range(item)
    if range == None or "normal" not in range:
        return None
    return range["normal"]

def get_weapon_long_range(item: dict):
    '''Returns an integer giving the long range of a ranged item.
    If this cannot be found, returns None.
    '''
    range = get_weapon_range(item)
    if range == None or "long" not in range:
        return None
    return range["long"]

def get_plural(name: str):
    '''Returns the plural form of a name in either the categories or items
    section of the database.
    If the name is not found in either, returns the name with an -s appended.
    '''
    item = get_item(name)
    if item != None:
        plural = get_item_plural(item)
        if plural != None:
            return plural
    category = get_category(name)
    if category != None:
        plural = get_category_plural(category)
        if plural != None:
            return plural
    return f"{name}s"

def get_category_items(name: str):
    '''Returns a string list of all items that have the given category name
    applied.
    '''
    items = get_items()
    result = []
    for item in items.values():
        categories = get_item_categories(item)
        if name in categories:
            result.append(item)
    return result

def get_category_item_names(name: str):
    '''Returns a string list of all items that have the given category name
    applied.
    '''
    items = get_items()
    result = []
    for item_name, item_value in items.items():
        categories = get_item_categories(item_value)
        if name in categories:
            result.append(item_name)
    return result

def get_all_categories_items(names: list):
    '''Returns a string list of all items that have all of the given category
    names applied.
    '''
    items = get_items()
    result = []
    for item in items.values():
        categories = get_item_categories(item)
        for name in names:
            if name not in categories:
                break
        else:
            result.append(item)
    return result

def get_all_categories_item_names(names: list):
    '''Returns a string list of all items that have all of the given category
    names applied.
    '''
    items = get_items()
    result = []
    for item_name, item_value in items.items():
        categories = get_item_categories(item_value)
        for name in names:
            if name not in categories:
                break
        else:
            result.append(item_name)
    return result

def get_any_categories_items(names: list):
    '''Returns a string list of all items that have any of the given category
    names applied.
    '''
    items = get_items()
    result = []
    for item in items.values():
        categories = get_item_categories(item)
        for name in names:
            if name in categories:
                result.append(item)
                break
    return result

def get_any_categories_item_names(names: list):
    '''Returns a string list of all items that have any of the given category
    names applied.
    '''
    items = get_items()
    result = []
    for item_name, item_value in items.items():
        categories = get_item_categories(item_value)
        for name in names:
            if name in categories:
                result.append(item_name)
                break
    return result

def get_not_in_categories_items(names: list):
    '''Returns a string list of all items that have none of the given category
    names applied.
    '''
    items = get_items()
    result = []
    for item in items.values():
        categories = get_item_categories(item)
        for name in names:
            if name in categories:
                break
        else:
            result.append(item)
    return result

def get_not_in_categories_item_names(names: list):
    '''Returns a string list of all items that have none of the given category
    names applied.
    '''
    items = get_items()
    result = []
    for item_name, item_value in items.items():
        categories = get_item_categories(item_value)
        for name in names:
            if name in categories:
                break
        else:
            result.append(item_name)
    return result

def get_not_in_list_item_names(item_names: list, category_names: list):
    '''Returns a string list of all items within a given list that have none of
    the given category names applied.
    '''
    items = []
    for item_name in item_names:
        item = get_item(item_name)
        items.append(item)
    result = []
    for item_name, item_value in items.items():
        categories = get_item_categories(item_value)
        for name in names:
            if name in categories:
                break
        else:
            result.append(item_name)
    return result

def get_plural_list(names: list):
    '''Returns a list of the plural forms of each name in a given list.
    '''
    plurals = []
    for name in names:
        plural = get_plural(name)
        plurals.append(plural)
    return plurals

#Item information handling functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Backend functions

def get_items_file():
    '''Returns a dict containing the entire items file database.
    '''
    return read_from_json(items_file)

def save_items_file(new_file: dict):
    '''Overwrites the entire items file database with the provided dict.
    '''
    write_to_json(items_file, new_file)

def generate_item_lists_string(item, pluralize=False, conjunction=True):
    '''Returns a string for generate_item_string's lists.
    '''
    msg = ""
    for i, subitem in enumerate(item):
        if i != 0:
            msg += ", " if i != len(item)-1 or not conjunction else " and "
        msg += generate_item_string(subitem, pluralize=pluralize,
            enumerate_choices=False, conjunction=conjunction
        )
    return msg

def generate_item_restrictions_string(item, pluralize=False, conjunction=True):
    '''Returns a string for generate_item_string's restrictions.
    '''
    restriction = item["restriction"]
    subitem = generate_item_string(item["item"], pluralize=pluralize,
        enumerate_choices=False, conjunction=conjunction
    )
    return f"{subitem} ({restriction})"

def generate_item_quantities_string(item, conjunction=True):
    '''Returns a string for generate_item_string's quantities.
    '''
    quantity = item["quantity"]
    plural = quantity != 1
    subitem = generate_item_string(item["item"], pluralize=plural,
        enumerate_choices=False, conjunction=conjunction
    )
    return f"{quantity} {subitem}"

def generate_item_choose_string(item, pluralize=False, enumerate_choices=False, conjunction=True):
    count = item["choose"]
    choices = item["from"]
    msg = ""
    if enumerate_choices and count == 1:
        for i, choice in enumerate(choices):
            if i != 0:
                msg += ", " if i != len(choices)-1 else " or "
            subitem = generate_item_string(choice, pluralize=pluralize,
                enumerate_choices=False, conjunction=conjunction
            )
            a = string.ascii_lowercase[i]
            msg += f"({a}) {subitem}"
    else:
        msg += f"{count} "
        for j, choice in enumerate(choices):
            if j != 0:
                msg += ", " if j != len(choices)-1 else " or "
            plural = count != 1
            subitem = generate_item_string(choice, pluralize=plural,
                enumerate_choices=False, conjunction=conjunction
            )
            msg += subitem
        msg += " of your choice"
    return msg

def generate_item_string(item, pluralize=False, enumerate_choices=False, conjunction=True):
    '''Returns a string giving the name(s) of an armor, weapon, or tool
    including additional conditions. Parameter can be a string giving an item
    name, a dict giving choices, quantities, and restrictions, or a list giving
    multiple of any of these three types of parameters.
    '''
    if type(item) is list:
        return generate_item_lists_string(item, pluralize=pluralize, conjunction=conjunction)
    if type(item) is not dict:
        if pluralize:
            return get_plural(item).lower()
        return item.lower()
    if "restriction" in item and "item" in item:
        return generate_item_restrictions_string(item, pluralize=pluralize, conjunction=conjunction)
    if "quantity" in item and "item" in item:
        return generate_item_quantities_string(item, conjunction=conjunction)
    if "choose" in item and "from" in item:
        return generate_item_choose_string(item, pluralize=pluralize,
            enumerate_choices=enumerate_choices, conjunction=conjunction
        )
    return "??"

def generate_item_embed_category_string(item: dict):
    '''Returns a string to use as value for the category field of the detailed
    weapon item Embed.
    '''
    category_names = get_item_categories(item)
    printable_categories = [
        "Light Armor", "Medium Armor", "Heavy Armor", "Shield",
        "Simple Melee Weapon", "Simple Ranged Weapon", "Martial Melee Weapon", "Martial Ranged Weapon",
        "Tool", "Artisan's Tools", "Musical Instrument", "Gaming Set",
        "Adventuring Gear", "Ammunition", "Arcane Focus", "Druidic Focus", "Holy Symbol",
        "Food and Drink", "Clothing", "Pack", "Magic Item", "Potion", "Poison",
        "Tack and Harness", "Treasure", "Trade Good"
    ]
    value = ""
    for category_name in category_names:
        if category_name in printable_categories:
            if value != "":
                value += ", "
            value += category_name
    if value == "": value = "Other"
    return value

def generate_item_embed_cost_string(item: dict):
    '''Returns a string to use as value for the cost field of the detailed item
    Embed.
    '''
    cost = get_item_cost(item)
    value = f"{cost} gp" if cost != 0 else "—"
    return value

def generate_item_embed_weight_string(item: dict):
    '''Returns a string to use as value for the weight field of the detailed
    item Embed.
    '''
    weight = get_item_weight(item)
    value = f"{weight} lbs" if weight != 0 else "—"
    return value

def generate_item_embed_damage_string(item: dict):
    '''Returns a string to use as value for the damage field of the detailed
    weapon item Embed.
    '''
    damage = get_weapon_damage(item)
    value = "" if damage != [] else "—"
    for i, dmg in enumerate(damage):
        if i != 0:
            value += " plus "
        value += generate_weapon_damage_dice_string(dmg, include_damage_word=False)
    return value

def generate_weapon_properties_string(item: dict):
    '''Returns a string giving the weapon properties of an item.
    '''
    properties = get_weapon_properties(item)
    desc = ""
    if properties == []:
        desc = "—"
    for i, property in enumerate(properties):
        if i != 0:
            desc += ", "
        desc += f"{property}"
        if property == "Versatile":
            versatile = get_weapon_versatile(item)
            dmg_dice = ""
            for j, dmg in enumerate(versatile):
                if j != 0:
                    dmg_dice += "+"
                dmg_dice += generate_weapon_damage_dice_string(dmg, include_type=False, include_damage_word=False)
            desc += f" ({dmg_dice})"
        if property == "Ammunition" or property == "Thrown":
            normal = get_weapon_normal_range(item)
            long = get_weapon_long_range(item)
            desc += f" ({normal}/{long} ft.)"
    return desc

def generate_item_embed_ac_string(item: dict):
    '''Returns a string giving the AC properties of an item.
    '''
    base_ac = get_armor_base_ac(item)
    max_bonus = get_armor_max_bonus(item)
    bonus_ac = get_armor_bonus_ac(item)
    desc = ""
    if base_ac != None: desc += f"{base_ac}"
    if max_bonus != 0:
        desc += " + DEX mod."
        if max_bonus != None: desc += f" (max {max_bonus})"
    if bonus_ac > 0: desc += " + "
    if bonus_ac != 0: desc += f"{bonus_ac}"
    return desc

def generate_item_embed(item: dict):
    '''Returns an Embed object describing the item.
    '''
    name = get_item_name(item)
    description = get_item_description(item)
    embed = Embed(title=name, description=description)
    embed.add_field(name="Category", value=generate_item_embed_category_string(item), inline=False)
    embed.add_field(name="Cost", value=generate_item_embed_cost_string(item))
    embed.add_field(name="Weight", value=generate_item_embed_weight_string(item))
    if get_item_armor(item) != None:
        embed.add_field(name="AC", value=generate_item_embed_ac_string(item))
    if get_item_weapon(item) != None:
        embed.add_field(name="Damage", value=generate_item_embed_damage_string(item))
        embed.add_field(name="Weapon Properties", value=generate_weapon_properties_string(item), inline=False)
    contents_list = generate_item_contents_string(item)
    if contents_list != "":
        embed.add_field(name="Contents", value=contents_list, inline=False)
    return embed

def generate_item_name_embed(name: str):
    '''Returns an Embed from generate_item_embed for item matching the given
    name.
    '''
    item = get_item(name)
    if item == None:
        raise Exception("Item not found")
    return generate_item_embed(item)

def generate_items_embed_basics(item: dict):
    '''Returns a string denoting the name, cost, and weight of an item.
    '''
    desc = ""
    name = get_item_name(item)
    cost = get_item_cost(item)
    weight = get_item_weight(item)
    desc += f"● **{name}**"
    if cost != 0 or weight != 0:
        desc += " ("
        if cost != 0: desc += f"{cost} gp"
        if cost != 0 and weight != 0: desc += ", "
        if weight != 0: desc += f"{weight} lbs"
        desc += ")"
    desc += "\n"
    return desc

def generate_items_embed_armor(item: dict):
    '''Returns a string denoting the armor statistics of an item.
    '''
    if get_item_armor(item) == None:
        return ""
    desc = ""
    requirements = get_armor_requirements(item)
    disadvantages = get_armor_disadvantages(item)
    ac = generate_item_embed_ac_string(item)
    if ac != "": desc += f"> AC {ac}"
    if requirements != None or disadvantages != []: desc += "\n> "
    if requirements != None:
        desc += "Requires"
        for i, req in enumerate(requirements):
            ability = req["ability"]
            score = req["score"]
            if i != 0:
                desc += ","
            desc += f" {ability} {score}"
        desc += ". "
    if disadvantages != []:
        desc += "Disadvantages"
        for i, dis in enumerate(disadvantages):
            if i != 0:
                desc += ","
            desc += f" {dis}"
        desc += "."
    desc += "\n"
    return desc

def generate_weapon_damage_dice_string(damage: dict, include_type=True, include_damage_word=True):
    '''Returns a string denoting the damage dice of a weapon's damage dict.
    '''
    dice = get_weapon_damage_dice(damage)
    faces = get_weapon_damage_faces(damage)
    flat = get_weapon_damage_flat(damage)
    desc = ""
    if dice != 0:
        desc += f"{dice}d{faces}"
        if flat > 0:
            desc += "+"
    if flat != 0:
        desc += f"{flat}"
    if include_type:
        type = get_weapon_damage_type(damage)
        if type != None:
            desc += f" {type.lower()}"
    if include_damage_word and desc != "":
        desc += f" damage"
    return desc

def generate_items_embed_weapon(item: dict):
    '''Returns a string denoting the weapon statistics of an item.
    '''
    if get_item_weapon(item) == None:
        return ""
    desc = ""
    damage = get_weapon_damage(item)
    if damage != []: desc += "> "
    for i, dmg in enumerate(damage):
        if i != 0:
            desc += " plus "
        desc += generate_weapon_damage_dice_string(dmg)
    if damage != []: desc += "\n"
    properties = get_weapon_properties(item)
    if properties != []:
        desc += "> "
        desc += generate_weapon_properties_string(item)
        desc += "\n"
    return desc

def generate_item_contents_string(item: dict):
    '''Returns a string listing all of an item's contents.
    '''
    contents = get_item_contents(item)
    if contents == None:
        return ""
    return generate_item_lists_string(contents, pluralize=False, conjunction=False)

def generate_items_embed_pack(item: dict):
    '''Returns a string of contents of an item for the items list Embed.
    '''
    items_list = generate_item_contents_string(item)
    if items_list == "":
        return ""
    items_list = f"> Includes {items_list}\n"
    return items_list

def generate_items_embed_field(item_names: list):
    '''Returns a string to use as a field of the generate_items_embed function.
    '''
    value = ""
    for name in item_names:
        item = get_item(name)
        value += generate_items_embed_basics(item)
        value += generate_items_embed_armor(item)
        value += generate_items_embed_weapon(item)
        value += generate_items_embed_pack(item)
    return value

def generate_items_embed(title: str, item_names: list):
    '''Returns an Embed listing multiple items' details.
    '''
    embed = Embed(title=get_plural(title))
    half = math.ceil(len(item_names)/2)
    first = generate_items_embed_field(item_names[:half])
    second = generate_items_embed_field(item_names[half:])
    delim, replac = "●", [("●", "\n● "), (" > ", "\n> ")]
    if len(first) > 1024: first = fit_text_to_length(first, 1024, delimiter=delim, replacements=replac)
    if len(second) > 1024: second = fit_text_to_length(second, 1024, delimiter=delim, replacements=replac)
    embed.add_field(name="\u200b", value=first)
    if second != "": embed.add_field(name="\u200b", value=second)
    return embed

def generate_paginated_items_embed(title: str, item_names: list, page=1):
    '''Returns an Embed supporting large lists of items by only rendering a
    portion of the list
    '''
    item_name_page = slice_list_page(item_names, page)
    embed = generate_items_embed(title, item_name_page)
    if len(item_names) > 25:
        total = math.ceil(len(item_names)/25)
        embed.set_footer(text=f"Page {page}/{total}")
    return embed

def get_matching_item(item_name):
    '''Returns a message, Embed, and view as a message response.
    Checks the entire items list for the five closest item names matching with
    the input item name.
    '''
    msg, embed, view = "", None, None
    item_names = get_item_names()
    matches = get_closest_matches(item_name, item_names)
    if type(matches) is not list: #Perfect match
        embed = generate_item_name_embed(matches)
        return msg, embed, view
    if matches != []: #5 close matches
        msg = f'Closest matches to "{item_name}":'
        view = ClosestMatchingItemsMenu(matches)
    else: #No close matches
        msg = f'No matches found for "{item_name}"'
    return msg, embed, view

#Backend functions
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#User Interface elements

def message_selectcategorymenu():
    return ("Select an item category to examine!\n"
        "Alternatively, use `!item [name]` to display a specific item!"
    )

#Main menu
class MainMenu(ui.View):
    def __init__(self):
        super().__init__(timeout=view_timeout)
        self.add_item(AllItemsCategoryButton())
        self.add_item(SearchButton())
        self.add_item(SuperCategoryButton("Armor", emoji="🛡️", row=3,
            subcategory_names=["Light Armor", "Medium Armor", "Heavy Armor", "Shield"]
        ))
        self.add_item(SuperCategoryButton("Weapon", emoji="🗡️", row=3,
            subcategory_names=["Simple Melee Weapon", "Simple Ranged Weapon", "Martial Melee Weapon", "Martial Ranged Weapon"]
        ))
        self.add_item(SuperCategoryButton("Tool", emoji="🔧", row=3,
            subcategory_names=["Artisan's Tools", "Musical Instrument", "Gaming Set", "Other Tool"]
        ))
        self.add_item(SubCategoryButton("Pack", emoji="📦", row=3))

#Select category to display subcategories/items for menu
class SubCategoryMenu(ui.View):
    def __init__(self, category_names):
        super().__init__(timeout=view_timeout)
        for category_name in category_names:
            self.add_item(SubCategoryButton(category_name, category_names))

#Select item to show details of menu
class SelectItemToShowMenu(ui.View):
    def __init__(self, current_category, category_names=[], item_names=None, page=1):
        super().__init__(timeout=view_timeout)
        if item_names == None:
            item_names = get_category_item_names(current_category)
        if len(item_names) > 25:
            self.add_item(SelectItemBackButton(current_category, category_names, item_names, page))
            self.add_item(SelectItemSkipButton(current_category, category_names, item_names))
            self.add_item(SelectItemForwardButton(current_category, category_names, item_names, page))
        if len(item_names) > 0:
            item_page = slice_list_page(item_names, page)
            options = generate_selectoptions(labels=item_names)
            self.add_item(ItemSelect(placeholder=f"Select {current_category}", options=options))
        for category_name in category_names:
            disabled = category_name==current_category
            button = SubCategoryButton(category_name, category_names, disabled=disabled, row=3)
            self.add_item(button)

#Closest matching items menu
class ClosestMatchingItemsMenu(ui.View):
    def __init__(self, item_names):
        super().__init__(timeout=view_timeout)
        for item_name in item_names:
            button = ItemButton(item_name)
            self.add_item(button)

class SelectItemBackButton(ui.Button):
    def __init__(self, current_category: str, category_names: list, item_names: list, page: int):
        self.current_category = current_category
        self.item_names = item_names
        self.category_names = category_names
        self.page = page
        disabled = True if page <= 1 else False
        prev_page = page if disabled else page-1
        super().__init__(label=f"← Page {prev_page}", style=discord.ButtonStyle.blurple, disabled=disabled, row=3)

    async def callback(self, interaction):
        try:
            embed = generate_paginated_items_embed(self.current_category, self.item_names, page=self.page-1)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectItemToShowMenu(self.current_category, self.category_names, self.item_names, self.page-1)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SelectItemSkipButton(ui.Button):
    def __init__(self, current_category: str, category_names: list, item_names: list):
        self.current_category = current_category
        self.item_names = item_names
        self.category_names = category_names
        super().__init__(label=f"…", style=discord.ButtonStyle.blurple, row=3)

    async def callback(self, interaction):
        try:
            await interaction.response.send_modal(PageSkipModal(self.current_category, self.category_names, self.item_names))
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SelectItemForwardButton(ui.Button):
    def __init__(self, current_category: str, category_names: list, item_names: list, page: int):
        self.current_category = current_category
        self.item_names = item_names
        self.category_names = category_names
        self.page = page
        disabled = True if 25*page >= len(item_names) else False
        next_page = page if disabled else page+1
        super().__init__(label=f"Page {next_page} →", style=discord.ButtonStyle.blurple, disabled=disabled, row=3)

    async def callback(self, interaction):
        try:
            embed = generate_paginated_items_embed(self.current_category, self.item_names, page=self.page+1)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectItemToShowMenu(self.current_category, self.category_names, self.item_names, self.page+1)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SuperCategoryButton(ui.Button):
    def __init__(self, supercategory_name, subcategory_names, emoji=None, disabled=False, row=None):
        self.subcategory_names = subcategory_names
        super().__init__(label=get_plural(supercategory_name), disabled=disabled,
            style=discord.ButtonStyle.grey, emoji=emoji, row=row
        )

    async def callback(self, interaction):
        try:
            await interaction.response.send_message(view=SubCategoryMenu(self.subcategory_names), ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SubCategoryButton(ui.Button):
    def __init__(self, current_subcategory, subcategory_names=[], item_names=None, emoji=None, disabled=False, row=None):
        self.current_subcategory = current_subcategory
        self.subcategory_names = subcategory_names
        self.item_names = item_names if item_names != None else get_category_item_names(current_subcategory)
        super().__init__(label=get_plural(current_subcategory), disabled=disabled,
            style=discord.ButtonStyle.grey, emoji=emoji, row=row
        )

    async def callback(self, interaction):
        try:
            embed = generate_paginated_items_embed(self.current_subcategory, self.item_names)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectItemToShowMenu(self.current_subcategory, self.subcategory_names, self.item_names)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class AllItemsCategoryButton(ui.Button):
    def __init__(self):
        super().__init__(label="All Items", style=discord.ButtonStyle.blurple, emoji="🗃️")

    async def callback(self, interaction):
        try:
            item_names = sorted(get_item_names())
            embed = generate_paginated_items_embed("All Item", item_names)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectItemToShowMenu("Item", item_names=item_names)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SearchButton(ui.Button):
    def __init__(self):
        super().__init__(label="Search", style=discord.ButtonStyle.blurple, emoji="🔍")

    async def callback(self, interaction):
        try:
            await interaction.response.send_modal(SearchItemModal())
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ItemButton(ui.Button):
    def __init__(self, item_name):
        self.item_name = item_name
        super().__init__(label=item_name, style=discord.ButtonStyle.blurple)

    async def callback(self, interaction):
        try:
            embed = generate_item_name_embed(self.item_name)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ItemSelect(ui.Select):
    def __init__(self, placeholder, options):
        super().__init__(placeholder=placeholder, options=options)

    async def callback(self, interaction):
        try:
            pick = "".join(self.values)
            embed = generate_item_name_embed(pick)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class PageSkipModal(ui.Modal, title="Skip to Page"):
    def __init__(self, current_category, category_names, item_names):
        super().__init__(timeout=view_timeout)
        self.current_category = current_category
        self.category_names = category_names
        self.item_names = item_names

    input = ui.TextInput(label="Page Number", placeholder="Skip to which page?", required=True)

    async def on_submit(self, interaction):
        try:
            page = self.input.value
            max_page = math.ceil(len(self.item_names)/25)
            if page.isdigit() == False or int(page) > max_page:
                await interaction.response.send_message(f'"{page}" is not a valid page number.', ephemeral=True)
                return
            page = int(page)
            embed = generate_paginated_items_embed(self.current_category, self.item_names, page=page)
            await interaction.response.send_message(embed=embed, ephemeral=True,
                view=SelectItemToShowMenu(self.current_category, self.category_names, self.item_names, page)
            )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class SearchItemModal(ui.Modal, title="Search Item"):
    input_item = ui.TextInput(label="Item", placeholder="What item are you looking for?",
        max_length=max_item_name_length, required=True
    )

    async def on_submit(self, interaction):
        try:
            item = self.input_item.value
            msg, embed, view = get_matching_item(item)
            await interaction.response.send_message(msg, embed=embed, view=view, ephemeral=True)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

#User Interface elements
#---------------------------------------------------------------------------------------------------------------------------------------------------------------
#Bot commands

#Cog Setup
class Items(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Items cog loaded.")

    @commands.group(name="items", aliases=["item"], case_insensitive=True, invoke_without_command=True)
    async def items(self, ctx, *item):
        try:
            if not item:
                msg = message_selectcategorymenu()
                await ctx.channel.send(msg, view=MainMenu())
                return
            item_name = " ".join(item)
            msg, embed, view = get_matching_item(item_name)
            await ctx.channel.send(msg, embed=embed, view=view)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @items.command(aliases=["help", "?", "info", "information", "instructions"])
    async def items_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "items")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

async def setup(client):
    await client.add_cog(Items(client))
