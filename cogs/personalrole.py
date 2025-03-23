#===============================================================================
# Personal Role v1.1.6
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.1.6; Moved database to secrets folder. -YY
# 20 Mar 2025 - v1.1.5; Made strings with escape characters raw strings. -YY
# 04 Dec 2024 - v1.1.4; Fixed the first arg for `!sr preset <alias>` being
#               ignored. -YY
# 08 Sep 2024 - v1.1.3; Fixed emoji strings being set incorrectly for the preset
#               icon command. Improved emoji detection in all icon setting
#               commands. -YY
# 05 Sep 2024 - v1.1.2; Added "create" as alias for "save". -YY
# 17 Aug 2024 - v1.1.1; Changed max role icon dimension size to 40 from 48. -YY
# 08 Aug 2024 - v1.1.0; Made saving prefixes a more explicit command with
#               `!sr save Name` instead of `!sr preset Name` in order to
#               minimize accidental overwrites. Added a command to delete your
#               personal role. Fixed presets not being deleted or overwritten.
# 07 May 2024 - v1.0.3; Moved UserError to a common error file. -YY
# 02 May 2024 - v1.0.2; Reworked help message import and error handling. -YY
# 28 Apr 2024 - v1.0.1; Made role presets global rather than per-server. Made it
#               possible to create/apply presets without creating a personal
#               role first. -YY
# 27 Apr 2024 - v1.0.0; Added role presets such that users can quickly swap to
#               a previously saved role name, color and icon. Includes automatic
#               swapping depending on user's display name, configurable to swap
#               on partial, starting, ending, or perfect match. Presets support
#               aliases for all operations. Finished file. -YY
# 26 Mar 2024 - v0.1.1; Images uploaded as role icons now maintain their aspect
#               ratio. -YY
# 24 Mar 2024 - v0.1.0; Finished Beta file. -YY
# 22 Mar 2024 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Add a setting to temporarily disable all automatic switching. -YY
# - Add a command to set all presets' switch setting. -YY
# - Add a "set"/"overwrite" alias command so users don't need to use "add"
#   following "remove". -YY
# - Ask for confirmation when performing destructive operations, e.g. deleting
#   roles or overwriting presets. -YY
# - Support command `!sr preset add <alias>`, and perhaps `!sr add <alias>`. -YY
#===============================================================================
# Description
# ..............................................................................
# personalrole.py allows users to create and modify a server role unique to
# themself, granting them their own role name, role colour, and role icon.
# Multiple role presets can be created and can be switched to manually or
# automatically by checking the user's display name.
#===============================================================================

#Import Modules
import discord
from discord import ui, Color, Embed
from discord.ext import commands

from common.json_handling import read_from_json, write_to_json
from common.error_message import send_error, UserError
from common.help_message import send_help
from cogs.roles import get_emoji_indices_from_message

import requests, random, re, io
from PIL import Image

PERSONAL_ROLES_FILE = "secrets/personal_roles.json"
MAX_ICON_SIZE = 40 # Largest dimension of Discord role icons in pixels

COMMAND_ALIASES_NAME = ["name", "rolename", "role_name"]
COMMAND_ALIASES_COLOR = ["color", "colour", "rolecolor", "rolecolour", "role_color", "role_colour"]
COMMAND_ALIASES_ICON = ["icon", "roleicon", "role_icon"]
COMMAND_ALIASES_SAVE = ["save", "create"]
COMMAND_ALIASES_PRESET = ["preset", "variant", "alter", "alt", "alternate", "alternative", "load"]
COMMAND_ALIASES_PRESETS = ["presets", "variants", "alters", "alts", "alternates", "alternatives", "list"]
COMMAND_ALIASES_WHITELIST = ["whitelist", "wl"]
COMMAND_ALIASES_REMOVE = ["remove", "delete"]
COMMAND_ALIASES_HELP = ["help", "info"]
COMMAND_ALIASES_FIRST_ORDER = (COMMAND_ALIASES_NAME + COMMAND_ALIASES_COLOR + COMMAND_ALIASES_ICON +
    COMMAND_ALIASES_PRESET + COMMAND_ALIASES_PRESETS + COMMAND_ALIASES_WHITELIST + COMMAND_ALIASES_HELP +
    COMMAND_ALIASES_SAVE + COMMAND_ALIASES_REMOVE)
COMMAND_ALIASES_ALIAS = ["alias", "aliases", "title", "titles"]
COMMAND_ALIASES_AUTO = ["auto", "automate"]
COMMAND_ALIASES_SECOND_ORDER = (COMMAND_ALIASES_NAME + COMMAND_ALIASES_COLOR + COMMAND_ALIASES_ICON +
    COMMAND_ALIASES_ALIAS + COMMAND_ALIASES_AUTO + COMMAND_ALIASES_REMOVE)
COMMAND_ALIASES_ADD = ["add"]
COMMAND_ALIASES_SET = ["set", "replace", "overwrite"]
COMMAND_ALIASES_AUTO_OFF = ["off", "disable", "none", "no"]
COMMAND_ALIASES_AUTO_PARTIAL = ["partial", "part", "substring"]
COMMAND_ALIASES_AUTO_START = ["start", "starts", "startwith", "startswith"]
COMMAND_ALIASES_AUTO_END = ["end", "ends", "endwith", "endswith"]
COMMAND_ALIASES_AUTO_PERFECT = ["perfect", "enable", "full", "match", "on"]

#-------------------------------------------------------------------------------
#Cog Setup
class PersonalRole(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.display_name_cache = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Personal Role cog loaded.")

    @commands.group(name="personalrole", aliases=["personal_role", "rolepersonal", "role_personal", "cosmeticrole", "cosmetic_role", "rolecosmetic", "role_cosmetic", "myrole", "my_role", "rolemy", "role_my", "setrole", "set_role", "sr", "roleset", "role_set", "rs"], case_insensitive=True, invoke_without_command=True)
    async def personalrole(self, ctx, *args):
        '''Applies a specified preset's settings to the personal role if no
        further settings are specified. Otherwise, modifies the preset's
        settings in accordance to specified settings.
        '''
        try:
            await handle_process_preset(ctx, args)
            if len(args) > 2:
                if args[1] in COMMAND_ALIASES_AUTO and args[2] not in COMMAND_ALIASES_AUTO_OFF:
                    self.display_name_cache.pop(str(ctx.author.id))
        except UserError as e:
            await ctx.channel.send(e, delete_after=15.0)
            await ctx.message.delete(delay=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @personalrole.command(aliases=COMMAND_ALIASES_PRESET, case_insensitive=True, invoke_without_command=True)
    async def personalrole_process_preset(self, ctx, *args):
        '''Applies a specified preset's settings to the personal role if no
        further settings are specified. Otherwise, modifies the preset's
        settings in accordance to specified settings.
        '''
        try:
            await handle_process_preset(ctx, args)
            if len(args) > 2:
                if args[1] in COMMAND_ALIASES_AUTO and args[2] not in COMMAND_ALIASES_AUTO_OFF:
                    self.display_name_cache.pop(str(ctx.author.id))
        except UserError as e:
            await ctx.channel.send(e, delete_after=15.0)
            await ctx.message.delete(delay=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @personalrole.command(aliases=COMMAND_ALIASES_NAME, case_insensitive=True, invoke_without_command=True)
    async def personalrole_name(self, ctx, *args):
        '''If server is whitelisted, allows users to change the default name of
        their personal role. Will create a new role if the user has none.
        '''
        try:
            await handle_set_current_name(ctx, args)
        except UserError as e:
            await ctx.channel.send(e, delete_after=15.0)
            await ctx.message.delete(delay=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @personalrole.command(aliases=COMMAND_ALIASES_COLOR, case_insensitive=True, invoke_without_command=True)
    async def personalrole_color(self, ctx, *args):
        '''If server is whitelisted, allows users to change the default color of
        their personal role. Will create a new role if the user has none.
        '''
        try:
            await handle_set_current_color(ctx, args)
        except UserError as e:
            await ctx.channel.send(e, delete_after=15.0)
            await ctx.message.delete(delay=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @personalrole.command(aliases=COMMAND_ALIASES_ICON, case_insensitive=True, invoke_without_command=True)
    async def personalrole_icon(self, ctx, *args):
        '''If server is whitelisted, allows users to change the default icon of
        their personal role. Will create a new role if the user has none.
        '''
        try:
            await handle_set_current_icon(ctx, args)
        except UserError as e:
            await ctx.channel.send(e, delete_after=15.0)
            await ctx.message.delete(delay=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @personalrole.command(aliases=COMMAND_ALIASES_REMOVE, case_insensitive=True, invoke_without_command=True)
    async def personalrole_remove(self, ctx):
        '''If the user has a personal role, delete it.
        '''
        try:
            await handle_delete_role(ctx)
        except UserError as e:
            await ctx.channel.send(e, delete_after=15.0)
            await ctx.message.delete(delay=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @personalrole.command(aliases=COMMAND_ALIASES_WHITELIST, case_insensitive=True, invoke_without_command=True)
    async def personalrole_whitelist(self, ctx):
        '''If invoking user is a server admin, toggles whether this server is
        whitelisted for personal user roles.
        '''
        try:
            await handle_whitelisting(ctx)
        except UserError as e:
            await ctx.channel.send(e, delete_after=15.0)
            await ctx.message.delete(delay=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @personalrole.command(aliases=COMMAND_ALIASES_SAVE, case_insensitive=True, invoke_without_command=True)
    async def personalrole_save(self, ctx, *args):
        '''Adds a new role preset to the member's list of presets by copying the
        settings of the current personal role.
        '''
        try:
            await handle_add_preset(ctx, args)
        except UserError as e:
            await ctx.channel.send(e, delete_after=15.0)
            await ctx.message.delete(delay=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @personalrole.command(aliases=COMMAND_ALIASES_PRESETS, case_insensitive=True, invoke_without_command=True)
    async def personalrole_presets(self, ctx, user_id=None):
        '''Shows all of a user's current presets with corresponding title,
        aliases, name, color and icon.
        '''
        try:
            await handle_show_presets(ctx, user_id)
        except UserError as e:
            await ctx.channel.send(e, delete_after=15.0)
            await ctx.message.delete(delay=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @personalrole.command(aliases=COMMAND_ALIASES_HELP, case_insensitive=True, invoke_without_command=True)
    async def personalrole_help(self, ctx):
        await send_help(ctx.channel.send, "personalrole")

    @commands.Cog.listener()
    async def on_message(self, message):
        '''Detects if a user has automatic switching enabled and changes their
        personal role accordingly. Minimizes JSON calls by caching users and
        their display names to halt processing if they're unchanged.
        '''
        try:
            if not message.guild:
                return
            server_id = str(message.guild.id)
            user_id = str(message.author.id)
            display_name = message.author.display_name
            if user_id in self.display_name_cache and server_id in self.display_name_cache[user_id] and self.display_name_cache[user_id][server_id] == display_name:
                return
            if user_id not in self.display_name_cache:
                self.display_name_cache[user_id] = {}
            self.display_name_cache[user_id][server_id] = display_name
            data = read_from_json(PERSONAL_ROLES_FILE)
            if not is_whitelisted(data, server_id):
                return
            if "presets" not in data or user_id not in data["presets"]:
                return
            await apply_automated_preset(message.guild, message.author, data)
        except Exception as e:
            await send_error(self.client, e, reference=message.jump_url)

#-------------------------------------------------------------------------------
#Auxiliary Functions

class NotWhitelistedError(UserError):
    def __init__(self, message="Server has not been whitelisted for users to create and modify personal roles."):
        super().__init__(message)

class UnrecognizedCommandError(UserError):
    def __init__(self, message="Command not recognized. Use `!help setrole` for available commands."):
        super().__init__(message)

class UnrecognizedColorError(UserError):
    def __init__(self, message="Could not parse colour. Try supplying a colour in hexidecimal representation, such as "):
        super().__init__(message + f"\"#{random_hex_code()}\"")

async def handle_set_current_name(ctx, args):
    '''If server is whitelisted, allows users to change the default name of
    their personal role. Will create a new role if the user has none.
    '''
    data = read_from_json(PERSONAL_ROLES_FILE)
    server_id = str(ctx.guild.id)
    if not is_whitelisted(data, server_id):
        raise NotWhitelistedError()
    name = " ".join(args)
    user_id = str(ctx.author.id)
    role_id = personal_role_id(data, server_id, user_id)
    if role_id:
        role = ctx.guild.get_role(role_id)
        if role:
            await edit_personal_role_name(role, name, ctx.author.name)
            await ctx.message.add_reaction("👍")
            return
    await create_and_assign_new_personal_role(ctx.guild, ctx.author, data, name=name)
    await ctx.message.add_reaction("👍")

async def handle_set_current_color(ctx, args):
    '''If server is whitelisted, allows users to change the default color of
    their personal role. Will create a new role if the user has none.
    '''
    if not args:
        raise UserError(f"Please specify a colour, such as \"#{random_hex_code()}\".\nIf you wish to reset the role colour, specify \"default\".")
    data = read_from_json(PERSONAL_ROLES_FILE)
    server_id = str(ctx.guild.id)
    if not is_whitelisted(data, server_id):
        raise NotWhitelistedError()
    color = parse_color(" ".join(args))
    if color == None:
        raise UnrecognizedColorError()
    user_id = str(ctx.author.id)
    role_id = personal_role_id(data, server_id, user_id)
    if role_id:
        role = ctx.guild.get_role(role_id)
        if role:
            await edit_personal_role_color(role, color, ctx.author.name)
            await ctx.message.add_reaction("👍")
            return
    await create_and_assign_new_personal_role(ctx.guild, ctx.author, data, color=color)

async def handle_set_current_icon(ctx, args):
    '''If server is whitelisted, allows users to change the default icon of
    their personal role. Will create a new role if the user has none.
    '''
    data = read_from_json(PERSONAL_ROLES_FILE)
    server_id = str(ctx.guild.id)
    if not is_whitelisted(data, server_id):
        raise NotWhitelistedError()
    icon = await get_icon_from_message(ctx, args)
    user_id = str(ctx.author.id)
    role_id = personal_role_id(data, server_id, user_id)
    try:
        if role_id:
            role = ctx.guild.get_role(role_id)
            if role:
                await edit_personal_role_icon(role, icon, ctx.author.name)
                await ctx.message.add_reaction("👍")
                return
        await create_and_assign_new_personal_role(ctx.guild, ctx.author, data, icon=icon)
        await ctx.message.add_reaction("👍")
    except discord.Forbidden as e:
        if e.code == 50101:
            raise UserError("This Discord server needs to be at least Boosts Level 2 to be able to set role icons.")
        raise e

async def handle_delete_role(ctx):
    '''If the user has a personal role, delete it.
    '''
    role_id = personal_role_id(data, server_id, user_id)
    if role_id:
        role = ctx.guild.get_role(role_id)
        if role:
            await role.delete(reason="Personal user role deleted by owner.")
            await ctx.message.add_reaction("👍")
            return

async def handle_whitelisting(ctx):
    '''If invoking user is a server admin, toggles whether this server is
    whitelisted for personal user roles.
    '''
    if not ctx.channel.permissions_for(ctx.author).administrator:
        raise UserError("You need to be an administrator in order to modify whether this server is whitelisted for personal user roles.")
    data = read_from_json(PERSONAL_ROLES_FILE)
    server_id = str(ctx.guild.id)
    whitelist_status = True
    if server_id not in data:
        data[server_id] = {"whitelist": True}
    else:
        if "whitelist" in data[server_id]:
            whitelist_status = not data[server_id]["whitelist"]
        else:
            whitelist_status = False
        data[server_id]["whitelist"] = whitelist_status
    write_to_json(PERSONAL_ROLES_FILE, data)
    if whitelist_status:
        await ctx.channel.send("Server-wide personal user roles: **ENABLED**.")
    else:
        await ctx.channel.send("Server-wide personal user roles: **DISABLED**.")

async def handle_add_preset(ctx, args):
    '''Adds a new role preset to the member's list of presets by copying the
    settings of the current personal role.
    '''
    data = read_from_json(PERSONAL_ROLES_FILE)
    server_id = str(ctx.guild.id)
    if not is_whitelisted(data, server_id):
        raise NotWhitelistedError()
    if not args:
        raise UserError("Please provide a one-word title for your new role preset.")
    title = args[0]
    if title.lower() in COMMAND_ALIASES_FIRST_ORDER:
        raise UserError("Please provide a one-word title which doesn't conflict with an existing setrole command.")
    aliases = None
    if len(args) > 1:
        aliases = list(args[1:])
    user_id = str(ctx.author.id)
    existing_title = get_preset_key_title(data, user_id, title)
    if existing_title:
        overwrite_role_preset(ctx, data, server_id, user_id, existing_title, aliases)
        await ctx.channel.send(f"Preset {existing_title} overwritten with current personal role settings.\n"
                                "To see your existing role presets, use `!sr presets`.")
    else:
        await create_role_preset(ctx, data, server_id, user_id, title, aliases)
        await ctx.channel.send(f"Preset {title} created from current personal role settings.\n"
                                "To see your existing role presets, use `!sr presets`.")

async def handle_show_presets(ctx, user_id):
    '''Shows all of a user's current presets with corresponding title,
    aliases, name, color and icon.
    '''
    data = read_from_json(PERSONAL_ROLES_FILE)
    server_id = str(ctx.guild.id)
    if not is_whitelisted(data, server_id):
        raise NotWhitelistedError()
    if user_id == None:
        user_id = str(ctx.author.id)
    user_id = user_id.lstrip("<@").rstrip(">")
    desc = get_preset_embed_description(data, user_id)
    username = ctx.guild.get_member(int(user_id)).name
    embed_title = f"**Personal Role Presets for {username}**"
    color = personal_role_color(ctx, data, server_id, user_id)
    embed = Embed(title=embed_title, description=desc, color=color)
    await ctx.channel.send(embed=embed)

async def handle_process_preset(ctx, args):
    '''Handles all preset commands, such as applying preset to role, changing
    preset settings and aliases, and removing presets.
    '''
    data = read_from_json(PERSONAL_ROLES_FILE)
    server_id = str(ctx.guild.id)
    if not is_whitelisted(data, server_id):
        raise NotWhitelistedError()
    if not args:
        raise UserError("Use `!help setrole` for available commands.")
    user_id = str(ctx.author.id)
    title = get_preset_key_title(data, user_id, args[0])
    if not title:
        raise UnrecognizedCommandError()
    if len(args) == 1:
        await handle_apply_preset(ctx, data, server_id, user_id, title)
        return
    if args[1] not in COMMAND_ALIASES_SECOND_ORDER:
        raise UnrecognizedCommandError()
    if args[1] not in COMMAND_ALIASES_ICON + COMMAND_ALIASES_REMOVE and len(args) <= 1:
        raise UnrecognizedCommandError()
    if args[1] in COMMAND_ALIASES_NAME:
        await handle_set_preset_name(ctx, data, user_id, title, args[2:])
        return
    if args[1] in COMMAND_ALIASES_COLOR:
        await handle_set_preset_color(ctx, data, user_id, title, args[2:])
        return
    if args[1] in COMMAND_ALIASES_ICON:
        if len(args) >= 2:
            await handle_set_preset_icon(ctx, data, user_id, title, args[2:])
        else:
            await handle_set_preset_icon(ctx, data, user_id, title)
        return
    if args[1] in COMMAND_ALIASES_ALIAS:
        await handle_modify_preset_aliases(ctx, data, user_id, title, args[2:])
        return
    if args[1] in COMMAND_ALIASES_AUTO:
        await handle_modify_preset_auto(ctx, data, user_id, title, args[2])
        return
    if args[1] in COMMAND_ALIASES_REMOVE:
        await handle_delete_preset(ctx, data, user_id, title)
        return

async def handle_apply_preset(ctx, data, server_id, user_id, title):
    '''Sets all of a member's personal role settings to the specified preset.
    '''
    await apply_preset(ctx.guild, ctx.author, data, server_id, user_id, title)
    await ctx.message.add_reaction("👍")

async def apply_preset(guild, author, data, server_id, user_id, title):
    '''Sets all of a member's personal role settings to the specified preset.
    '''
    role_id = personal_role_id(data, server_id, user_id)
    role = guild.get_role(role_id)
    if not role:
        data = await create_and_assign_new_personal_role(guild, author, data)
        role_id = personal_role_id(data, server_id, user_id)
        role = guild.get_role(role_id)
    name = data["presets"][user_id][title]["name"]
    color = data["presets"][user_id][title]["color"]
    icon = data["presets"][user_id][title]["icon"]
    if icon and type(icon) is not str:
        icon = ints_to_bytes(icon)
    await edit_personal_role_name(role, name, author.name)
    await edit_personal_role_color(role, color, author.name)
    try:
        await edit_personal_role_icon(role, icon, author.name)
    except discord.Forbidden as e:
        if e.code != 50101:
            raise e

async def handle_set_preset_name(ctx, data, user_id, title, args):
    '''Sets the role name of an existing preset.
    '''
    name = " ".join(args)
    data["presets"][user_id][title]["name"] = name
    write_to_json(PERSONAL_ROLES_FILE, data)
    await ctx.message.add_reaction("👍")

async def handle_set_preset_color(ctx, data, user_id, title, args):
    '''Sets the role colour of an existing preset.
    '''
    color_name = " ".join(args)
    color = parse_color(color_name)
    if color == None:
        raise UnrecognizedColorError()
    data["presets"][user_id][title]["color"] = color
    write_to_json(PERSONAL_ROLES_FILE, data)
    await ctx.message.add_reaction("👍")

async def handle_set_preset_icon(ctx, data, user_id, title, args=None):
    '''Sets the role icon of an existing preset.
    '''
    icon = await get_icon_from_message(ctx, args)
    if type(icon) == bytes:
        icon = bytes_to_ints(icon)
    data["presets"][user_id][title]["icon"] = icon
    write_to_json(PERSONAL_ROLES_FILE, data)
    await ctx.message.add_reaction("👍")

async def handle_modify_preset_aliases(ctx, data, user_id, title, args):
    '''Adds alias(es) to or removes alias(es) from an existing preset.
    '''
    if len(args) <= 1:
        raise UserError("Please specify at least a single one-word alias.")
    command = args[0].lower()
    aliases = args[1:]
    if command in COMMAND_ALIASES_ADD:
        await handle_add_preset_aliases(ctx, data, user_id, title, aliases)
        return
    if command in COMMAND_ALIASES_REMOVE:
        await handle_remove_preset_aliases(ctx, data, user_id, title, aliases)
        return
    raise UnrecognizedCommandError()

async def handle_add_preset_aliases(ctx, data, user_id, title, aliases):
    '''Adds alias(es) to an existing preset, preventing conflicts.
    '''
    unavailable_aliases = []
    for key_title, preset in data["presets"][user_id].items():
        unavailable_aliases.append(key_title.lower())
        if "aliases" in preset:
            unavailable_aliases += [alias.lower() for alias in preset["aliases"]]
    if "aliases" not in data["presets"][user_id][title]:
        data["presets"][user_id][title]["aliases"] = []
    located_conflicts = []
    for alias in aliases:
        if alias.lower() in unavailable_aliases:
            located_conflicts.append(alias)
            continue
        data["presets"][user_id][title]["aliases"].append(alias)
    write_to_json(PERSONAL_ROLES_FILE, data)
    if len(located_conflicts) == len(aliases):
        await ctx.channel.send(f"Provided alias(es) conflict with your existing aliases: **{'**, **'.join(located_conflicts)}**. No new aliases added.")
        return
    elif located_conflicts:
        await ctx.channel.send(f"Provided alias(es) conflict with your existing aliases: **{'**, **'.join(located_conflicts)}**. Only some new aliases added.")
        return
    await ctx.message.add_reaction("👍")

async def handle_remove_preset_aliases(ctx, data, user_id, title, aliases):
    '''Remove alias(es) from an existing preset.
    If the key title is removed, it replaces it with the next available alias.
    If all aliases are removed, it removes the preset entry entirely.
    '''
    existing_aliases = []
    if "aliases" in data["presets"][user_id][title]:
        existing_aliases = data["presets"][user_id][title]["aliases"]
    missing_aliases = []
    remove_title = False
    for alias in aliases:
        if alias.lower() == title.lower():
            remove_title = True
            continue
        success = False
        for existing_alias in existing_aliases:
            if alias.lower() == existing_alias.lower():
                data["presets"][user_id][title]["aliases"].remove(existing_alias)
                success = True
                break
        if not success:
            missing_aliases.append(alias)
    if remove_title:
        data = remove_preset_title(data, user_id, title)
    write_to_json(PERSONAL_ROLES_FILE, data)
    if len(missing_aliases) == len(aliases):
        await ctx.channel.send(f"Could not locate alias(es): **{'**, **'.join(located_conflicts)}**. No aliases removed.")
        return
    elif missing_aliases:
        await ctx.channel.send(f"Could not locate alias(es): **{'**, **'.join(located_conflicts)}**. Only some aliases removed.")
        return
    await ctx.message.add_reaction("👍")

async def handle_modify_preset_auto(ctx, data, user_id, title, arg):
    '''Sets whether an existing preset should automatically be applied when
    specified conditions are met.
    '''
    arg = arg.lower()
    auto = None
    if arg in COMMAND_ALIASES_AUTO_OFF:
        auto = "off"
    elif arg in COMMAND_ALIASES_AUTO_PARTIAL:
        auto = "partial"
    elif arg in COMMAND_ALIASES_AUTO_START:
        auto = "start"
    elif arg in COMMAND_ALIASES_AUTO_END:
        auto = "end"
    elif arg in COMMAND_ALIASES_AUTO_PERFECT:
        auto = "perfect"
    if not auto:
        raise UnrecognizedCommandError()
    data["presets"][user_id][title]["auto"] = auto
    write_to_json(PERSONAL_ROLES_FILE, data)
    await ctx.message.add_reaction("👍")

async def handle_delete_preset(ctx, data, user_id, title):
    '''Deletes an existing preset.
    '''
    data["presets"][user_id].pop(title)
    write_to_json(PERSONAL_ROLES_FILE, data)
    await ctx.message.add_reaction("👍")

def get_preset_embed_description(data, user_id):
    '''Returns the description for the presets list embed of the specified
    member.
    '''
    if "presets" not in data or user_id not in data["presets"] or not data["presets"][user_id]:
        return "No presets."
    lines = []
    for key_title, preset in data["presets"][user_id].items():
        desc = ""
        titles = [key_title]
        if "aliases" in preset and preset["aliases"]:
            titles += preset["aliases"]
        titles = sorted([f"**{title}**" for title in titles])
        titles = ", ".join(titles)
        name = preset["name"]
        color = preset["color"]
        hexadec = hex(color).upper()[2:]
        color = "#" + "0" * (6-len(hexadec)) + hexadec
        icon = preset["icon"]
        if not icon:
            icon = "no icon"
        elif len(icon) > 4:
            icon = "custom icon"
        desc += f"- {titles}: {name} | {color} | {icon}"
        auto = None
        if "auto" in preset and preset["auto"]:
            auto = preset["auto"]
        if auto != None and auto != "off":
            desc += f" | {auto} match"
        lines.append(desc)
    desc = "\n".join(sorted(lines))
    return desc

def get_preset_key_title(data, user_id, title):
    '''Returns the key title of a preset if a preset could be found with the
    title supplied as its key or among its aliases for the supplied member.
    Returns None otherwise.
    '''
    if "presets" not in data or user_id not in data["presets"] or not data["presets"][user_id]:
        return None
    for key_title, preset in data["presets"][user_id].items():
        if title.lower() == key_title.lower():
            return key_title
        if "aliases" in preset:
            titles = [alias.lower() for alias in preset["aliases"]]
            if title.lower() in titles:
                return key_title
    return None

def remove_preset_title(data, user_id, title):
    '''Removes the key title from an existing preset. Replaces it with the first
    available alias if one exists, otherwise removes the preset completely.
    Returns the modified data dict.
    '''
    if "aliases" not in data["presets"][user_id][title] or not data["presets"][user_id][title]["aliases"]:
        data["presets"][user_id].pop(title)
        return data
    new_title = data["presets"][user_id][title]["aliases"].pop(0)
    data["presets"][user_id][new_title] = data["presets"][user_id].pop(title)
    return data

def overwrite_role_preset(ctx, data, server_id, user_id, title, aliases=None):
    '''Overwrites an existing role preset's name, color and icon with the
    member's current role information.
    '''
    role_id = personal_role_id(data, server_id, user_id)
    name, color, icon = get_current_role_info(ctx, role_id)
    if title in data["presets"][user_id]:
        data["presets"][user_id][title]["name"] = name
        data["presets"][user_id][title]["color"] = color
        data["presets"][user_id][title]["icon"] = icon
        if aliases:
            data["presets"][user_id][title]["aliases"] = aliases
    write_to_json(PERSONAL_ROLES_FILE, data)

async def create_role_preset(ctx, data, server_id, user_id, title, aliases=None):
    '''Creates a new role preset for the specified user by copying their current
    role information and saving it under the supplied title.
    '''
    if user_id not in data[server_id]:
        data = await create_and_assign_new_personal_role(ctx.guild, ctx.author, data)
    if "presets" not in data:
        data["presets"] = {}
    if user_id not in data["presets"]:
        data["presets"][user_id] = {}
    role_id = personal_role_id(data, server_id, user_id)
    name, color, icon = get_current_role_info(ctx, role_id)
    data["presets"][user_id][title] = {"name": name, "color": color, "icon": icon}
    if aliases:
        data["presets"][user_id][title]["aliases"] = aliases
    write_to_json(PERSONAL_ROLES_FILE, data)

async def apply_automated_preset(guild, author, data):
    '''Detects if a preset's automation conditions are satisfied and, if so,
    applies the preset to the user's personal role.
    '''
    server_id = str(guild.id)
    user_id = str(author.id)
    display_name = author.display_name
    presets = collect_automated_presets(data, user_id)
    for title, aliases, auto in presets:
        if auto == "partial":
            for alias in aliases:
                if alias in display_name.lower():
                    await apply_preset(guild, author, data, server_id, user_id, title)
                    return
        elif auto == "start":
            for alias in aliases:
                if display_name.lower().startswith(alias):
                    await apply_preset(guild, author, data, server_id, user_id, title)
                    return
        elif auto == "end":
            for alias in aliases:
                if display_name.lower().endswith(alias):
                    await apply_preset(guild, author, data, server_id, user_id, title)
                    return
        elif auto == "perfect":
            if display_name.lower() in aliases:
                await apply_preset(guild, author, data, server_id, user_id, title)

def collect_automated_presets(data, user_id):
    '''Returns a list of 3-tuples consisting of the key title, aliases
    (including title) and automation mode for all presets whose automation mode
    isn't disabled.
    '''
    presets = []
    for key_title, preset in data["presets"][user_id].items():
        aliases = [key_title.lower()]
        if "aliases" in preset:
            aliases += [alias.lower() for alias in preset["aliases"]]
        auto = "off"
        if "auto" in preset and preset["auto"]:
            auto = preset["auto"]
        if auto != "off":
            presets.append((key_title, aliases, auto))
    return presets

async def get_icon_from_message(ctx, args):
    '''Returns a bytes array if the message contains an image attachment.
    Otherwise returns an emoji if the args make up an emoji.
    Otherwise returns None.
    '''
    icon = None
    if args or ctx.message.attachments:
        icon = await parse_icon(ctx, " ".join(args))
        if icon == None:
            raise UserError(f"Could not parse icon.")
    return icon

def get_current_role_info(ctx, role_id):
    '''Returns the name, colour and (as bytes) icon of the specified role.
    '''
    role = ctx.guild.get_role(role_id)
    if not role:
        raise UserError("Your personal role could not been found. Has it been deleted? Try creating a new one by setting a name, colour or icon.")
    name = role.name
    color = role.color.value
    icon_asset = role.display_icon
    icon = None
    if type(icon_asset) is str:
        icon = icon_asset
    elif icon_asset:
        icon = get_scaled_icon_bytes_from_url(icon_asset.url)
        if icon:
            icon = bytes_to_ints(icon)
    return name, color, icon

async def edit_personal_role_name(role, name, username):
    '''Sets the name of the supplied role.
    '''
    await role.edit(name=name, reason=f"Personal role modified by {username}")

async def edit_personal_role_color(role, color, username):
    '''Sets the color of the supplied role.
    '''
    await role.edit(color=color, reason=f"Personal role modified by {username}")

async def edit_personal_role_icon(role, icon, username):
    '''Sets the icon of the supplied role.
    '''
    await role.edit(display_icon=icon, reason=f"Personal role modified by {username}")

async def create_and_assign_new_personal_role(guild, author, data, name=None, color=0, icon=None):
    '''Creates a new personal role and assigns it to the contextual member.
    Returns updated data dict.
    '''
    server_id = str(guild.id)
    user_id = str(author.id)
    if name == None:
        name = author.name
    role = await guild.create_role(name=name, color=color, display_icon=icon, reason=f"Personal role created by {author.name}")
    await author.add_roles(*[role])
    encoded_icon = None
    if icon != None:
        encoded_icon = bytes_to_ints(icon)
    role_dict = initialize_new_role(role.id)
    data[server_id][user_id] = role_dict
    write_to_json(PERSONAL_ROLES_FILE, data)
    return data

def initialize_new_role(role_id):
    '''Creates the dict for a new role with the specified parameters.
    '''
    return {
        "role_id": role_id
    }

def parse_color(color_str):
    '''Returns a decimal integer representing a color, parsed from the supplied
    color string.
    If no color could be parsed, returns None.
    '''
    color_int = try_parsing_color_as_string(color_str)
    if color_int != None:
        return color_int
    color_int = try_parsing_color_as_name(color_str)
    if color_int != None:
        return color_int
    color_int = try_parsing_color_as_decimal(color_str)
    if color_int != None:
        return color_int
    return None

def try_parsing_color_as_string(color_str):
    '''Returns a decimal integer representing a color if it can parse the color
    using Discord's built-in Color string parser.
    Returns None otherwise.
    '''
    hex_without_preface = re.search("^[0-9a-fA-F]{6}$|^[0-9a-fA-F]{3}$", color_str)
    color = None
    if hex_without_preface:
        color_str = "#" + color_str
    try:
        color = Color.from_str(color_str)
    except ValueError:
        return None
    else:
        if color:
            return color.value
    return None

def try_parsing_color_as_name(color_str):
    '''Returns a decimal integer representing a color if it can parse the color
    as one of Discord's built-in Color class methods.
    Returns None otherwise.
    '''
    color = None
    try:
        method_name = color_str.lower().replace(" ", "_")
        if method_name == "to_rgb":
            return None
        method = getattr(Color, method_name)
        color = method()
    except AttributeError:
        return None
    else:
        if color:
            return color.value
    return None

def try_parsing_color_as_decimal(color_str):
    '''Returns a decimal integer representing a color if it can parse the color
    as a decimal value.
    Returns None otherwise.
    '''
    decimal_color = re.search(r"^\d{,8}$", color_str)
    if decimal_color:
        return int(color_str)
    return None

async def parse_icon(ctx, arg):
    '''Returns a role display icon either as a bytes-like object representing an
    image or as a string representing a unicode emoji.
    Returns None if neither could be parsed.
    '''
    attachments = ctx.message.attachments
    if attachments:
        url = attachments[0].url
        return get_scaled_icon_bytes_from_url(url)
    emoji = get_first_emoji(arg)
    custom_emoji_match = re.search(r"^<(a?):\w+:(\d+)>$", emoji)
    if custom_emoji_match:
        emoji_id = int(custom_emoji_match.group(2))
        if custom_emoji_match.group(1):
            url = f"https://cdn.discordapp.com/emojis/{emoji_id}.gif"
        else:
            url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
        return get_scaled_icon_bytes_from_url(url)
    return emoji

def get_scaled_icon_bytes_from_url(url, max_dimension=MAX_ICON_SIZE):
    '''Returns a bytes array of an image behind the supplied URL, scaled to
    maintain aspect ratio. The largest dimension (width or height) is scaled to
    the specified amount of pixels.
    '''
    req = requests.get(url)
    if req.status_code not in range(200, 299):
        raise UserError("Image URL could not be accessed.")
    buffer = io.BytesIO(req.content)
    scaled_buffer = resize_image(buffer, max_dimension=max_dimension)
    bytes = scaled_buffer.getvalue()
    return bytes

def resize_image(image_obj, max_dimension=MAX_ICON_SIZE):
    '''Returns a resized image from a specified buffered image object with the
    original aspect ratio maintained. The largest dimension (width or height) is
    scaled to the specified amount of pixels.
    '''
    img = Image.open(image_obj)
    orig_resolution = img.size
    new_resolution = scale_tuple_maintaining_aspect_ratio(orig_resolution, max_dimension)
    resized_img = img.resize(new_resolution)
    buffer = io.BytesIO()
    resized_img.save(buffer, format="png")
    return buffer

def scale_tuple_maintaining_aspect_ratio(tup, max_val):
    '''Returns a resized 2-tuple of integers with aspect ratio maintained.
    Scales a 2-tuple of integers tup such that the largest of the two is equal
    to the specified max_val and the other is the closest value it needs to be
    to approximate the original aspect ratio.
    '''
    lower_val = max(round(max_val / max(tup) * min(tup)), 1)
    x, y = tup
    if x >= y:
        return (max_val, lower_val)
    return (lower_val, max_val)

def get_first_emoji(string):
    '''Returns the first emoji in a string, including isolated location
    indicators and custom Discord emoji.
    Returns None if no emoji are found.
    '''
    emoji_list = get_emoji_indices_from_message(string)
    if not emoji_list:
        return None
    return emoji_list[0]["emoji"]

def bytes_to_ints(bytes):
    '''Returns a list of the integer representation of each byte in the supplied
    bytes array.
    '''
    return [int(byte) for byte in bytes]

def ints_to_bytes(ints):
    '''Returns a bytes array corresponding to the supplied list of integers.
    '''
    return bytes(ints)

def is_whitelisted(data, server_id):
    '''Returns True if the specified server_id is found in the specified data
    dict and doesn't have its whitelist status set to False.
    Returns False otherwise.
    '''
    return server_id in data and ("whitelist" not in data[server_id] or data[server_id]["whitelist"])

def personal_role_id(data, server_id, user_id):
    '''Returns the user's personal role ID if the specified user_id exists in
    the specified data dict and has its role ID set.
    Returns None otherwise.
    '''
    if server_id in data and user_id in data[server_id] and "role_id" in data[server_id][user_id]:
        return data[server_id][user_id]["role_id"]
    return None

def personal_role_color(ctx, data, server_id, user_id):
    '''Returns the current personal role color for the specified member.
    Returns None if this could not be found in the current server.
    '''
    role_id = personal_role_id(data, server_id, user_id)
    role = ctx.guild.get_role(role_id)
    if not role:
        return None
    return role.color

def random_hex_code():
    '''Returns a randomly generated color hex code string.
    '''
    chars = ["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"]
    return "".join([random.choice(chars) for _ in range(6)])

#-------------------------------------------------------------------------------
#Add Cog
async def setup(client):
    await client.add_cog(PersonalRole(client))
