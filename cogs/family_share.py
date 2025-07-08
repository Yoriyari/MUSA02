#===============================================================================
# Family Share v1.4.2
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 08 Jul 2025 - v1.4.2; Fixed Steam-only family members being skipped when
#               syncing all user libraries. -YY
# 05 May 2025 - v1.4.1; Fixed Steam IDs being added while already registered to
#               your family resulting in an error message saying they're already
#               registered to someone else's family. -YY
# 07 Apr 2025 - v1.4.0; Any non-command parameters after the main command now
#               get treated as a search query command instead of ignoring the
#               parameters and doing a roll. -YY
# 02 Apr 2025 - v1.3.8; Fixed unvetted games getting skipped by Steam sync. -YY
# 23 Mar 2025 - v1.3.7; Moved user library database to secrets folder. -YY
# 20 Mar 2025 - v1.3.6; Made strings with escape characters raw strings. -YY
# 09 Feb 2025 - v1.3.5; Expanded family sharing to allow inviting members
#               without a registered family to user's family, instead of only
#               being able to request joining existing families. In part for
#               the ability to add more than one Steam URL to family. -YY
# 08 Feb 2025 - v1.3.4; Fixed inability to share with Steam account URLs without
#               associated Discord account, inability to leave Steam family. -YY
# 03 Jan 2025 - v1.3.3; Fixed account unlinking being broken. Added feedback for
#               attempting to link an account with a private library. -YY
# 20 Dec 2024 - v1.3.2; Added closest-match buttons to the mark-as-complete and
#               unmark commands. Removed case sensitivity from sorting game
#               titles. Reduced message lengths. Some minor code cleanup. Fixed
#               trailing spaces in game titles from Steam's own database. -YY
# 14 Dec 2024 - v1.3.1; Fixed zero results for searches giving two messages. -YY
# 04 Dec 2024 - v1.3; Added the user ability to mark/unmark games as completed
#               manually, as well as browse marked/all games. Added a partial-
#               match search for a user's eligible suggestions. Minor changes:
#               Fixed Steam IDs with their eighth digit not being 8 getting
#               refused. Also allowed multiple Discord users to link the same
#               Steam account to prevent maliciously hogging someone else's
#               account, which I hope won't break associated functions. -YY
# 03 Dec 2024 - v1.2; Added the ability for any Discord user to link their Steam
#               account and invite other users into a family. Added an API call
#               to sync Steam libraries after settings are changed or a manual
#               sync is initiated. Added a Steam client to detect which synced
#               games are excluded from family sharing and a database to save
#               which games are included/exluded for future syncs. Modified the
#               way completion percentage is computed by comparing the remaining
#               options instead of disabled options. -YY
# 25 Nov 2024 - v1.1; Added a percentage tracker for checked-off games. Now when
#               a user marks all games as seen, they can opt to reset their
#               history. -YY
# 24 Nov 2024 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Add request error handling for when Steam is offline. -YY
# - Allow some commands to append a mention to refer another user's library. -YY
# - Would a similarity metric improve the search function? -YY
#===============================================================================
# Description
# ..............................................................................
# family_share.py suggests a random Steam game from a user's Steam library.
# Users manually set their Steam account and any family-shared members. The bot
# retrieves the games from there. The user can remove suggestions from the pool
# of options, either when suggested or manually. They can undo this too. Users
# can ask to see the percentage of games removed from the pool, as well as a
# list of all game titles available or removed.
#
# data json format = {
#   "users": {
#     discord_id: {
#       "steam_id": steam_id,
#       "family": family_name,
#       "history": [played_game, ...],
#       "unshared_games": [game, ...]
#     },
#     ...
#   },
#   "families": {
#     "family_id": {
#       "members": {discord_id: "Discord", steam_id: "Steam", ...},
#       "shared_games": [game, ...]
#     },
#     ...
#   }
# }
#===============================================================================

#Import Modules
import discord
from discord import Embed, ui
from discord.ext import commands

from common.error_message import send_error
from common.help_message import send_help
from common.interactions import slice_list_page
from common.json_handling import read_from_json, write_to_json
from common.variable_text import get_closest_matches

from steam.client import SteamClient
from steam.webapi import WebAPI
import random, math, re

FAMILY_SHARE_FILE = "secrets/steam_libraries.json"
EXFGLS_FILE = "data/exfgls.json"
STEAM_API_KEY_FILE = "secrets/key_steam_api.txt"
VIEW_TIMEOUT = 86400 # 24 hours
MAX_FAMILY_SIZE = 6

#-------------------------------------------------------------------------------
#Cog Setup
class FamilyShare(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Family Share cog loaded.")

    @commands.group(name="familyshare", aliases=["family_share", "steam", "steamgame", "steam_game", "steamgames", "steam_games", "suggestgame", "suggest_game", "randomgame", "random_game", "game", "gaming", "games"], case_insensitive=True, invoke_without_command=True)
    async def familyshare(self, ctx, *query):
        try:
            if query:
                await handle_search(ctx.channel.send, str(ctx.author.id), " ".join(query))
            else:
                await handle_familyshare(ctx.channel.send, str(ctx.author.id))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["help", "?", "info", "information", "instructions"])
    async def familyshare_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "familyshare")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["percentage", "percent", "%", "completion", "total", "progress", "ratio"])
    async def familyshare_percentage(self, ctx):
        try:
            await handle_percentage(ctx.channel.send, str(ctx.author.id))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["library", "games", "suggestions", "options", "available", "availability"])
    async def familyshare_library(self, ctx):
        try:
            await handle_library(ctx.channel.send, str(ctx.author.id))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["hidden", "completed", "marked", "finished", "disabled", "dontsuggested", "dont_suggested", "dontsuggestagained", "dont_suggest_agained", "blocked"])
    async def familyshare_hidden(self, ctx):
        try:
            await handle_hidden(ctx.channel.send, str(ctx.author.id))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["complete", "mark", "finish", "disable", "dontsuggest", "dont_suggest", "dontsuggestagain", "dont_suggest_again", "hide", "block"])
    async def familyshare_complete(self, ctx, *game_name):
        try:
            await handle_complete(ctx.channel.send, str(ctx.author.id), " ".join(game_name), react_method=ctx.message.add_reaction)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["reset", "uncomplete", "unmark", "unfinish", "enable", "suggest", "suggestagain", "suggest_again", "unhide", "reveal", "unblock"])
    async def familyshare_reset(self, ctx, *game_name):
        try:
            await handle_reset(ctx.channel.send, str(ctx.author.id), " ".join(game_name), react_method=ctx.message.add_reaction)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["resetall", "reset_all", "uncompleteall", "uncomplete_all", "unmarkall", "unmark_all", "unfinishall", "unfinish_all", "enableall", "enable_all", "suggestall", "suggest_all", "suggestallagain", "suggest_all_again", "suggestagainall", "suggest_again_all", "unhideall", "unhide_all", "revealall", "reveal_all", "unblockall", "unblock_all"])
    async def familyshare_resetall(self, ctx):
        try:
            await handle_reset_all(ctx.channel.send, str(ctx.author.id))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["search", "query"])
    async def familyshare_search(self, ctx, *query):
        try:
            await handle_search(ctx.channel.send, str(ctx.author.id), " ".join(query))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["sync", "synchronize", "update", "refresh"])
    async def familyshare_sync(self, ctx):
        try:
            await handle_sync(ctx.channel.send)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["set", "link", "self", "me", "is", "account", "register", "identify"])
    async def familyshare_set_steam_account(self, ctx, steam_account=None):
        try:
            await handle_set_steam_account(ctx.channel.send, str(ctx.author.id), steam_account)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["unlink", "deregister", "unidentify", "anonymize"])
    async def familyshare_unlink(self, ctx):
        try:
            await handle_unlink(ctx.channel.send, str(ctx.author.id))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["share", "marry", "join", "invite"])
    async def familyshare_share(self, ctx, target=None):
        try:
            server_member_ids = get_server_member_ids(ctx.guild)
            await handle_share(ctx.channel.send, str(ctx.author.id), server_member_ids, target)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["unshare", "divorce", "remove", "kick"])
    async def familyshare_unshare(self, ctx, target=None):
        try:
            await handle_unshare(ctx.channel.send, str(ctx.author.id), target)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["leave", "depart"])
    async def familyshare_leave(self, ctx):
        try:
            await handle_leave(ctx.channel.send, str(ctx.author.id))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @familyshare.command(aliases=["family"])
    async def familyshare_list_family(self, ctx):
        try:
            await handle_list_family(ctx.channel.send, str(ctx.author.id))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#-------------------------------------------------------------------------------
#Primary functions
async def handle_familyshare(send_method, author_id):
    '''Picks a random unseen game from the shared library. Allows the user
    to mark the game as seen to prevent it from being rolled again, or skip
    to give it another chance later.
    '''
    data = read_from_json(FAMILY_SHARE_FILE)
    options = get_valid_suggestions_for_user(author_id, data)
    user_is_registered = True
    if options == None:
        options = get_all_games_across_users(data=data)
        user_is_registered = False
    if not options:
        msg = get_msg_no_suggestions_left()
        view = ViewResetHistory(author_id)
        await send_method(content=msg, view=view)
        return
    choice = random.choice(options)
    msg = get_msg_suggestion(author_id, choice)
    if not user_is_registered:
        msg += "\n\n" + get_msg_suggested_without_linked_account()
    view = ViewFamilyShare(author_id, choice)
    await send_method(content=msg, view=view)

async def handle_percentage(send_method, author_id):
    '''Displays the percentage of all games which are present in this user's
    history, to two decimal points.
    '''
    data = read_from_json(FAMILY_SHARE_FILE)
    games = get_all_accessible_games_for_user(author_id, data=data)
    user_is_registered = True
    if not games:
        games = get_all_games_across_users(data=data)
        user_is_registered = False
        if not games:
            msg = get_msg_percentage(author_id, 0, 0, 100)
            await send_method(content=msg)
            return
    options = games
    if user_is_registered:
        options = get_valid_suggestions_for_user(author_id, data)
    elif author_id in data["users"] and "history" in data["users"][author_id]:
        options = list(set(games) - set(data["users"][author_id]["history"]))
    percentage = 100.0
    if len(games) != 0:
        percentage = 100 * (1 - len(options) / len(games))
    msg = get_msg_percentage(author_id, len(games), len(options), percentage)
    if not user_is_registered:
        msg += "\n\n" + get_msg_percentage_without_linked_account()
    await send_method(content=msg)

async def handle_library(send_method, author_id):
    '''Shows a paginated list of all game titles in the author's library.
    '''
    data = read_from_json(FAMILY_SHARE_FILE)
    games = get_all_accessible_games_for_user(author_id, data=data)
    if not games:
        games = get_all_games_across_users(data=data)
        if not games:
            msg = get_msg_no_games_in_database()
            await send_method(content=msg)
            return
    history = get_history_of_user(author_id, data=data)
    games = alphabetize_and_label_titles(games, history=history)
    msg = get_msg_library(author_id)
    await send_list(send_method, games, message=msg)

async def handle_hidden(send_method, author_id):
    '''Shows a paginated list of all game titles in the author's history.
    '''
    data = read_from_json(FAMILY_SHARE_FILE)
    history = get_history_of_user(author_id)
    if not history:
        msg = get_msg_no_history()
        await send_method(content=msg)
        return
    history = alphabetize_and_label_titles(history, history=history)
    msg = get_msg_history(author_id)
    await send_list(send_method, history, message=msg)

async def handle_complete(send_method, author_id, game_name, react_method=None):
    '''Adds the game title to the author's history.
    '''
    data = read_from_json(FAMILY_SHARE_FILE)
    if author_id not in data["users"]:
        data["users"][author_id] = initialize_database_user_dict()
    if not game_name:
        msg = get_msg_no_title_specified()
        await send_method(content=msg)
        return
    full_library = get_all_accessible_games_for_user(author_id, data=data)
    for name in full_library:
        if game_name.lower() == name.lower():
            game_name = name
            break
    if game_name not in full_library:
        similar_names = get_closest_matches(game_name, full_library, max_matches=5)
        msg = get_msg_offer_similar_titles(game_name)
        if not similar_names:
            msg = get_msg_no_similar_matches_found()
        view = ViewHideSimilarMatch(author_id, similar_names)
        await send_method(content=msg, view=view)
        return
    if game_name in data["users"][author_id]["history"]:
        msg = get_msg_title_already_in_history(game_name)
        await send_method(content=msg)
        return
    data["users"][author_id]["history"].append(game_name)
    if react_method != None:
        await react_method("✅")
    else:
        msg = get_msg_hide(author_id, game_name)
        await send_method(content=msg)
    write_to_json(FAMILY_SHARE_FILE, data)

async def handle_reset(send_method, author_id, game_name, react_method):
    '''Removes the game title from the author's history.
    '''
    data = read_from_json(FAMILY_SHARE_FILE)
    if (author_id not in data["users"] or "history" not in data["users"][author_id] or
            not data["users"][author_id]["history"]):
        msg = get_msg_no_history()
        await send_method(content=msg)
        return
    if not game_name:
        msg = get_msg_no_title_specified()
        await send_method(content=msg)
        return
    history = data["users"][author_id]["history"]
    for name in history:
        if game_name.lower() == name.lower():
            game_name = name
            break
    if game_name not in history:
        similar_names = get_closest_matches(game_name, history, max_matches=5)
        msg = get_msg_offer_similar_titles(game_name)
        if not similar_names:
            msg = get_msg_no_similar_matches_found()
        view = ViewUnhideSimilarMatch(author_id, similar_names)
        await send_method(content=msg, view=view)
        return
    data["users"][author_id]["history"].remove(game_name)
    if react_method != None:
        await react_method("✅")
    else:
        msg = get_msg_unhide(author_id, game_name)
        await send_method(content=msg)
    write_to_json(FAMILY_SHARE_FILE, data)

async def handle_reset_all(send_method, author_id):
    '''Prompts the author to delete their history.
    '''
    data = read_from_json(FAMILY_SHARE_FILE)
    if (author_id not in data["users"] or "history" not in data["users"][author_id] or
            not data["users"][author_id]["history"]):
        msg = get_msg_no_history()
        await send_method(content=msg)
        return
    msg = get_msg_unhide_all_confirm_prompt(author_id)
    view = ViewResetHistory(author_id)
    await send_method(content=msg, view=view)

async def handle_search(send_method, author_id, query):
    '''Lists all of the author's suggestions which partially match the query.
    '''
    data = read_from_json(FAMILY_SHARE_FILE)
    games = get_all_accessible_games_for_user(author_id, data=data)
    if not games:
        games = get_all_games_across_users(data=data)
        if not games:
            msg = get_msg_no_games_in_database()
            await send_method(content=msg)
            return
    matches = []
    for name in games:
        if query.lower() in name.lower():
            matches.append(name)
    if not matches:
        msg = get_msg_search_no_matches(author_id, query)
        await send_method(content=msg)
        return
    history = get_history_of_user(author_id, data=data)
    matches = alphabetize_and_label_titles(matches, history=history)
    msg = get_msg_search(author_id, query)
    if not query:
        msg = get_msg_library(author_id)
    await send_list(send_method, matches, message=msg)

async def handle_sync(send_method):
    '''Refreshes the list of games available in the family-shared library.
    '''
    sync_all_libraries()
    await send_method(content=get_msg_synced())

async def handle_set_steam_account(send_method, author_id, steam_account):
    '''Sets the Steam account of the author.
    '''
    if not steam_account:
        msg = get_msg_no_steam_specified()
        await send_method(content=msg)
        return
    steam_account = query_steam_id(steam_account)
    if not steam_account:
        msg = get_msg_steam_not_recognized()
        await send_method(content=msg)
        return
    data = read_from_json(FAMILY_SHARE_FILE)
    for discord_id, user in data["users"].items():
        if user["steam_id"] == steam_account:
            if discord_id == author_id:
                msg = get_msg_steam_linked_same_account()
                await send_method(content=msg)
                return
            # Preventing two users from linking the same Steam account would go here
    history = []
    if author_id in data["users"] and "history" in data["users"][author_id]:
        history = data["users"][author_id]
    data["users"][author_id] = initialize_database_user_dict(steam_id=steam_account, history=history)
    for family_id, family in data["families"].items():
        if steam_account in family["members"]:
            data["families"][family_id]["members"].pop(steam_account)
            data["families"][family_id]["members"][author_id] = "Discord"
            data["users"][author_id]["family"] = family_id
            break
    msg = get_msg_steam_linked(author_id, steam_account)
    await send_method(content=msg)
    api = WebAPI(key=get_steam_key())
    if not is_user_library_populated(author_id, api=api, data=data):
        msg = get_msg_no_games_for_new_user(steam_account)
        await send_method(content=msg)
    sync_user_library(author_id, api=api, data=data)

async def handle_unlink(send_method, author_id):
    '''Removes the author from the database.
    '''
    data = read_from_json(FAMILY_SHARE_FILE)
    author_wasnt_registered = True
    if author_id in data["users"]:
        data["users"].pop(author_id)
        author_wasnt_registered = False
    for family_id, family in data["families"].items():
        if author_id in family["members"]:
            data["families"][family_id]["members"].pop(author_id)
            author_wasnt_registered = False
            if (not [id for id, type in family["members"].items() if type == "Discord"] or
                    len(family["members"]) == 1):
                for id, type in family["members"].items():
                    if type == "Discord":
                        data["users"][id]["family"] = None
                data["families"].pop(family_id)
            break
    msg = get_msg_steam_unlinked(author_id)
    if author_wasnt_registered:
        msg = get_msg_steam_not_linked()
    await send_method(content=msg)
    sync_all_libraries(data)

async def handle_share(send_method, author_id, server_member_ids, target):
    '''If the user and the target are both not in a family, the user invites the
    target to form a family.
    If the user is not in a family and the target is, the user asks the target
    to permit the user to join the target's family.
    If the user is in a family and the target is not, the user invites the
    target to join the user's family.
    If the user and the target are both in a family, this informs the user that
    either of them needs to leave their family first.
    '''
    # Verify target input
    target = parse_steam_or_discord_id(target)
    if not target:
        msg = get_msg_no_steam_or_discord_specified()
        await send_method(content=msg)
        return
    data = read_from_json(FAMILY_SHARE_FILE)
    # If user is already in a family, check whether it has space
    user_family_id = None
    if (author_id in data["users"] and "family" in data["users"][author_id] and
            data["users"][author_id]["family"]):
        user_family_id = data["users"][author_id]["family"]
        if len(user_family_id) >= MAX_FAMILY_SIZE:
            msg = get_msg_users_family_at_max_capacity()
            await send_method(content=msg)
            return
    # Check if Steam user is registered on Discord. If not, add without consent
    if is_steam_id(target):
        discord_id = None
        for id, user in data["users"].items():
            if user["steam_id"] == target:
                discord_id = id
                break
        if not discord_id:
            await add_steam_user_to_family(send_method, author_id, target, data)
            return
        target = discord_id
    # Verify the target Discord ID is known
    if target not in data["users"]:
        msg = get_msg_user_hasnt_linked_steam(target)
        await send_method(content=msg)
        return
    # Verify that not both users are already in a family
    target_family_id = None
    if "family" in data["users"][target] and data["users"][target]["family"]:
        target_family_id = data["users"][target]["family"]
    if user_family_id and target_family_id:
        msg = get_msg_both_users_already_in_different_families(target)
        if target_family_id == user_family_id:
            msg = get_msg_target_already_in_same_family(target)
        await send_method(content=msg)
        return
    # Invite target to user's family
    if not target_family_id:
        msg = get_msg_family_prompt_invite(author_id, target)
        view = ViewInviteToFamily(author_id, target)
        await send_method(content=msg, view=view)
        return
    # Invite user to target's family, if possible
    family_member_ids_in_this_server = [target]
    if target_family_id:
        family_members = data["families"][target_family_id]["members"]
        if len(family_members) >= MAX_FAMILY_SIZE:
            msg = get_msg_targets_family_at_max_capacity(target)
            await send_method(content=msg)
            return
        family_member_ids_in_this_server = [id for id, type in family_members.items() if type == "Discord" and id in server_member_ids]
    if target not in server_member_ids and not family_member_ids_in_this_server:
        msg = get_msg_family_has_no_users_in_channel()
        await send_method(content=msg)
        return
    discord_mentions = [f"<@{id}>" for id in family_member_ids_in_this_server]
    msg = get_msg_family_prompt_addition(author_id, discord_mentions)
    view = ViewRequestPermission(author_id, family_member_ids_in_this_server)
    await send_method(content=msg, view=view)

async def handle_unshare(send_method, author_id, target):
    '''Removes the target from the author's family.
    '''
    data = read_from_json(FAMILY_SHARE_FILE)
    if (author_id not in data["users"] or "family" not in data["users"][author_id] or
            not data["users"][author_id]["family"]):
        msg = get_msg_family_not_registered()
        await send_method(content=msg)
        return
    target = parse_steam_or_discord_id(target)
    if not target:
        msg = get_msg_no_steam_or_discord_specified()
        await send_method(content=msg)
        return
    if target == author_id:
        await handle_leave(send_method, author_id, data=data)
        return
    family = data["users"][author_id]["family"]
    if target not in data["families"][family]["members"]:
        msg = get_msg_family_doesnt_contain_target()
        await send_method(content=msg)
        return
    data["families"][family]["members"].pop(target)
    if not is_steam_id(target):
        data["users"][target]["family"] = None
    if len(data["families"][family]["members"]) == 1:
        data["families"].pop(family)
        data["users"][author_id]["family"] = None
    msg = get_msg_family_removed_target()
    await send_method(content=msg)
    sync_user_library(author_id, data=data)

async def handle_leave(send_method, author_id, data=None):
    '''Removes the author from their family.
    '''
    if data == None:
        data = read_from_json(FAMILY_SHARE_FILE)
    if (author_id not in data["users"] or "family" not in data["users"][author_id] or
            not data["users"][author_id]["family"]):
        msg = get_msg_family_not_registered()
        await send_method(content=msg)
        return
    family = data["users"][author_id]["family"]
    data["families"][family]["members"].pop(author_id)
    data["users"][author_id]["family"] = None
    if (not [id for id, type in data["families"][family]["members"].items() if type == "Discord"] or
            len(data["families"][family]["members"]) == 1):
        for id, type in data["families"][family]["members"].items():
            if type == "Discord":
                data["users"][id]["family"] = None
        data["families"].pop(family)
    msg = get_msg_family_left(author_id)
    await send_method(content=msg)
    sync_user_library(author_id, data=data)

async def handle_list_family(send_method, author_id):
    '''Displays the author's family members.
    '''
    data = read_from_json(FAMILY_SHARE_FILE)
    if (author_id not in data["users"] or "family" not in data["users"][author_id] or
            not data["users"][author_id]["family"]):
        msg = get_msg_family_not_registered()
        await send_method(content=msg)
        return
    family = data["users"][author_id]["family"]
    family_members = data["families"][family]["members"]
    mentions = sorted([f"<@{id}>" for id, type in family_members.items() if type == "Discord"])
    steam_users = sorted([f"Steam user {id}" for id, type in family_members.items() if type == "Steam"])
    desc = "\n".join(mentions + steam_users)
    embed = Embed(description=desc)
    msg = get_msg_family_list(author_id)
    await send_method(content=msg, embed=embed)

#-------------------------------------------------------------------------------
#Auxiliary functions
def get_msg_suggestion(author_id, game_name):
    return (f"<@{author_id}>\n"
            f"**Suggestion:** {game_name}")

def get_msg_library(author_id):
    return f"**<@{author_id}>'s library:**"

def get_msg_history(author_id):
    return f"**<@{author_id}>'s games hidden from suggestions:**"

def get_msg_percentage(author_id, total_games, total_suggestions, percentage):
    return (f"**<@{author_id}>'s games hidden from suggestions**\n"
            f"**Total:** {total_games - total_suggestions} / {total_games}\n"
            f"**Percentage:** {percentage:.2f}%")

def get_msg_hide(author_id, game_name):
    return f"**<@{author_id}> hid:** {game_name}"

def get_msg_unhide(author_id, game_name):
    return f"**<@{author_id}> unhid:** {game_name}"

def get_msg_unhide_all_confirm_prompt(author_id):
    return (f"<@{author_id}>\n"
             "**This will allow all games to be suggested to you again. Please confirm.**")

def get_msg_search(author_id, query):
    return (f"<@{author_id}>\n"
            f"**Available game titles matching** \"{query}\":")

def get_msg_synced():
    return "**Steam library sync completed.**"

def get_msg_steam_linked(author_id, steam_account):
    return f"**<@{author_id}>'s Steam library ID set to:** {steam_account}"

def get_msg_steam_unlinked(author_id):
    return f"**<@{author_id}>'s Steam library ID has been unlinked.**"

def get_msg_family_prompt_invite(author_id, target_id):
    return f"<@{target_id}>\n**Would you like to join <@{author_id}>'s Steam family?**"

def get_msg_family_prompt_addition(author_id, mentions):
    return "".join(mentions) + f"\n**Would you like to accept <@{author_id}> into your Steam family?**"

def get_msg_family_removed_target():
    return "**User has been removed from your Steam family.**"

def get_msg_family_left(author_id):
    return f"**<@{author_id}> has left their Steam family.**"

def get_msg_family_list(author_id):
    return f"**<@{author_id}>'s Steam family:**"

def get_msg_no_games_in_database():
    return "**No games found across all registered users!**"

def get_msg_no_suggestions_left():
    return "**You have hidden all games from suggestions!**"

def get_msg_no_history():
    return "**You don't have any games hidden from suggestions!**"

def get_msg_no_title_specified():
    return "**Please specify a game title.**"

def get_msg_no_similar_matches_found(game_name):
    return f"**Game title** \"{game_name}\" **and any similar titles could not be found!**"

def get_msg_title_already_in_history(game_name):
    return f"**Game title** \"{game_name}\" **is already hidden from your suggestions!**"

def get_msg_search_no_matches(author_id, query):
    return (f"<@{author_id}>\n"
            f"**Zero matches found for the query** \"{query}\"")

def get_msg_no_steam_specified():
    return "**Please provide a Steam account URL or ID.**"

def get_msg_steam_not_recognized():
    return "**Steam ID not recognized.**"

def get_msg_steam_linked_same_account():
    return "**You have already linked this Steam account as yours.**"

def get_msg_steam_not_linked():
    return "**You have not linked your Steam account!**"

def get_msg_no_steam_or_discord_specified():
    return "**Please provide a Steam ID or Discord ID.**"

def get_msg_target_already_in_same_family(target_id):
    return f"**<@{target_id}> is already in your Steam family!**"

def get_msg_both_users_already_in_different_families(target_id):
    return (f"**Both you and <@{target_id}> are already in different Steam families!**\n"
            "Consider having either of you leave your existing family with `!steam leave`.")

def get_msg_user_hasnt_linked_steam(user_id):
    return f"**<@{user_id}> does not have a Steam account linked!**"

def get_msg_users_family_at_max_capacity():
    return f"**Your Steam family is already at the maximum capacity of {MAX_FAMILY_SIZE}. Consider removing members.**"

def get_msg_targets_family_at_max_capacity(user_id):
    return f"**<@{user_id}>'s Steam family is already at the maximum capacity of {MAX_FAMILY_SIZE}.**"

def get_msg_steam_user_already_in_another_family(steam_id):
    return f"**Steam user {steam_id} is already registered to someone else's Steam family! User has not been added.**"

def get_msg_family_has_no_users_in_channel():
    return "**Please request permission to share a Steam family in the same server as at least one family member.**"

def get_msg_family_not_registered():
    return "**You are not in any Steam family!**"

def get_msg_family_doesnt_contain_target():
    return "**This user is not in your Steam family!**"

def get_msg_no_games_for_new_user(steam_account):
    return f"**No games were found for Steam library ID** {steam_account}**. Ensure the Steam library is publicly visible.**"

def get_msg_offer_similar_titles(game_name):
    return f"**Game title** \"{game_name}\" **was not found. Did you mean any of these options?**"

def get_msg_suggested_without_linked_account():
    return ("This game was pulled from the pool of all known Steam games across registered users. "
            "If you would like me to suggest a game from your Steam library, "
            "please register which Steam account belongs to you with `!steam link <steam_account>` "
            "and optionally add family-shared libraries with `!steam share <user>`.")

def get_msg_percentage_without_linked_account():
    return ("The total was pulled from the pool of all known Steam games across registered users. "
            "If you would like me to only count your Steam library, "
            "please register which Steam account belongs to you with `!steam link <steam_account>` "
            "and optionally add family-shared libraries with `!steam share <user>`.")

def get_msg_shared_with_unregistered_steam_user(author_id, steam_id):
    return (f"**Steam user {steam_id} has been registered to <@{author_id}>'s Steam family.**\n"
            "No Discord user was found linked to this Steam account. The Steam account was registered regardless, "
            "such that you can still roll your new family member's games in case they simply don't use Discord. "
            "If they do use Discord, I recommend they link their Steam account with `!steam link <steam_account>` "
            "such that they are granted executive power over commands involving their Steam family as well.")

async def add_steam_user_to_family(send_method, author_id, steam_id, data):
    '''Adds a Steam-only user to a registered family.
    '''
    family_id = None
    if "family" in data["users"][author_id] and data["users"][author_id]["family"]:
        family_id = data["users"][author_id]["family"]
    else:
        family_id = generate_new_family_id(data)
        data["users"][author_id]["family"] = family_id
        data["families"][family_id] = {"members": {author_id: "Discord"}, "shared_games": []}
    if steam_id in data["families"][family_id]["members"]:
        msg = get_msg_target_already_in_same_family(target)
        await send_method(content=msg)
        return
    if len(data["families"][family_id]["members"]) >= MAX_FAMILY_SIZE:
        msg = get_msg_users_family_at_max_capacity()
        await send_method(content=msg)
        return
    for family in data["families"].values():
        if steam_id in family["members"]:
            msg = get_msg_steam_user_already_in_another_family(steam_id)
            await send_method(content=msg)
            return
    data["families"][family_id]["members"][steam_id] = "Steam"
    msg = get_msg_shared_with_unregistered_steam_user(author_id, steam_id)
    await send_method(content=msg)
    sync_user_library(author_id, data=data)

async def send_list(send_method, entries, message=None, entries_per_page=15):
    '''Sends a paginated list of the entries.
    '''
    embed = generate_game_titles_list_embed(entries, max_options=entries_per_page)
    view = None
    if len(entries) > entries_per_page:
        view = ViewPaginatedList(entries, max_options=entries_per_page)
    await send_method(content=message, embed=embed, view=view)

def sync_all_libraries(data=None):
    '''Syncs all Steam libraries.
    '''
    if data == None:
        data = read_from_json(FAMILY_SHARE_FILE)
    api = WebAPI(key=get_steam_key())
    steam_client = SteamClient()
    steam_client.anonymous_login()
    family_libraries = {}
    for discord_id, user in data["users"].items():
        shared_games, unshared_games = query_games_of_user(user, steam_client, api, data)
        user["unshared_games"] = unshared_games
        if not shared_games:
            continue
        if user["family"] not in family_libraries:
            family_libraries[user["family"]] = []
        family_libraries[user["family"]] += shared_games
    for family, games in family_libraries.items():
        for id, type in data["families"][family]["members"].items():
            if type == "Steam":
                user = initialize_database_user_dict(steam_id=id, family=family)
                shared_games, _ = query_games_of_user(user, steam_client, api, data)
                games += shared_games
        data["families"][family]["shared_games"] = list(set(games))
    steam_client.disconnect()
    write_to_json(FAMILY_SHARE_FILE, data)

def is_user_library_populated(user_id, api=None, data=None):
    '''Returns True if any games exist in the user's linked library.
    Returns False otherwise.
    '''
    if data == None:
        data = read_from_json(FAMILY_SHARE_FILE)
    if api == None:
        api = WebAPI(key=get_steam_key())
    if user_id not in data["users"]:
        return False
    steam_client = SteamClient()
    steam_client.anonymous_login()
    user = data["users"][user_id]
    shared_games, unshared_games = query_games_of_user(user, steam_client, api, data)
    if not shared_games and not unshared_games:
        return False
    return True

def sync_user_library(user_id, api=None, data=None):
    '''Syncs the library of the specified user and any other users that're in a
    registered Steam family with them.
    '''
    if data == None:
        data = read_from_json(FAMILY_SHARE_FILE)
    if api == None:
        api = WebAPI(key=get_steam_key())
    if user_id not in data["users"]:
        return
    family = None
    if "family" in data["users"][user_id] and data["users"][user_id]["family"]:
        family = data["users"][user_id]["family"]
    steam_client = SteamClient()
    steam_client.anonymous_login()
    if family:
        family_library = []
        for id, type in data["families"][family]["members"].items():
            user = None
            if type == "Discord":
                user = data["users"][id]
                shared_games, unshared_games = query_games_of_user(user, steam_client, api, data)
                data["users"][id]["unshared_games"] = unshared_games
                family_library += shared_games
            if type == "Steam":
                user = initialize_database_user_dict(steam_id=id, family=family)
                shared_games, _ = query_games_of_user(user, steam_client, api, data)
                family_library += shared_games
        data["families"][family]["shared_games"] = list(set(family_library))
    else:
        _, games = query_games_of_user(data["users"][user_id], steam_client, api, data)
        data["users"][user_id]["unshared_games"] = games
    steam_client.logout()
    write_to_json(FAMILY_SHARE_FILE, data)

def query_games_of_user(user, steam_client, api=None, data=None):
    '''Returns a 2-tuple giving the lists of shared and unshared games of the
    user from the database dict.
    '''
    if "steam_id" not in user or not user["steam_id"]:
        return None, None
    if data == None:
        data = read_from_json(FAMILY_SHARE_FILE)
    if api == None:
        api = WebAPI(key=get_steam_key())
    call = api.IPlayerService.GetOwnedGames(steamid=user["steam_id"],
            include_appinfo=True, include_played_free_games=False,
            appids_filter=[], include_free_sub=False, language="en",
            include_extended_appinfo=False, skip_unvetted_apps=False)
    games = []
    if "response" in call and "games" in call["response"]:
        games = call["response"]["games"]
    shared_games, unshared_games = get_exfgls_shareability(games, steam_client)
    shared_games = list(set(shared_games)) # Remove redundant duplicates, e.g.
    unshared_games = list(set(unshared_games)) # Steam appid 3990 and appid 34450
    if "family" not in user or not user["family"]:
        return [], shared_games+unshared_games
    return shared_games, unshared_games

def get_exfgls_shareability(games, steam_client):
    '''Returns which games are shareable or not from the GetOwnedGames call
    and adds any newly seen games to the exfgls JSON.
    '''
    exfgls_db = read_from_json(EXFGLS_FILE)
    shared_games = []
    unshared_games = []
    unknown_game_ids = []
    for game in games:
        id = game["appid"]
        if str(id) in exfgls_db:
            if exfgls_db[str(id)]:
                unshared_games.append(game["name"].strip())
                continue
            shared_games.append(game["name"].strip())
            continue
        unknown_game_ids.append(id)
    for i in range(0, len(unknown_game_ids), 100): # Batch that beast
        appids = unknown_game_ids[i:i+100]
        unknown_info = steam_client.get_product_info(apps=appids, timeout=3)
        for id, game in unknown_info["apps"].items():
            if "exfgls" in game["common"] and game["common"]["exfgls"]:
                exfgls_db[str(id)] = True
                unshared_games.append(game["common"]["name"].strip())
                continue
            exfgls_db[str(id)] = False
            shared_games.append(game["common"]["name"].strip())
    write_to_json(EXFGLS_FILE, exfgls_db)
    return shared_games, unshared_games

def query_steam_id(steam_account):
    '''Returns the 64-bit 17-digit Steam ID by parsing the provided URL and/or
    vanity ID.
    '''
    api = WebAPI(key=get_steam_key())
    match = re.search("https?://steamcommunity.com/(id|profiles)/([^/]+)/?", steam_account)
    if match:
        steam_account = match.group(2)
    call = api.ISteamUser.ResolveVanityURL(vanityurl=steam_account)
    if call["response"]["success"] == 1:
        steam_account = call["response"]["steamid"]
    if is_steam_id(steam_account):
        return steam_account
    return None

def parse_steam_or_discord_id(target):
    '''Returns the target's ID if it's a Steam or Discord ID.
    Returns None otherwise.
    '''
    if not target:
        return None
    discord_mention = re.search(r"<@(\d+)>", target)
    if discord_mention:
        return discord_mention.group(1)
    steam_id = query_steam_id(target)
    if steam_id:
        return steam_id
    discord_id = re.search(r"^\d+$")
    if discord_id:
        return discord_id.group()
    return None

def generate_new_family_id(data=None):
    '''Returns the first non-zero integer which is not already registered to a
    family.
    '''
    if data == None:
        data = read_from_json(FAMILY_SHARE_FILE)
    families = data["families"]
    for i in range(100000):
        if str(i+1) not in families:
            return str(i+1)
    raise Exception("For-loop in family_share.py's `generate_new_family_id` went through 100,000 iterations.")

def generate_game_titles_list_embed(game_names, page=1, max_options=25):
    '''Returns an Embed listing the given page's game titles.
    '''
    page_list = slice_list_page(game_names, page, max_options=max_options)
    desc = "\n".join(page_list)
    embed = Embed(title="Games", description=desc)
    if len(game_names) > max_options:
        total = math.ceil(len(game_names)/max_options)
        embed.set_footer(text=f"Page {page}/{total}")
    return embed

def alphabetize_and_label_titles(game_names, history=None):
    '''Returns the list of game titles in alphabetical order and with emoji
    prefixes to denote marked-as-hidden or not.
    '''
    game_names = sorted(game_names, key=lambda x: x.lower())
    return label_whether_titles_are_hidden(game_names, history=history)

def label_whether_titles_are_hidden(game_names, history=None):
    '''Returns the list of game titles, each prefixed with an emoji marking
    whether each title is marked as hidden or not.
    '''
    if not history:
        return [f"▪️{game}" for game in game_names]
    else:
        return [f"❎{game}" if game in history else f"▪️{game}" for game in game_names]

def get_all_games_across_users(data=None):
    '''Returns a list of every unique known game title, shareable or not.
    '''
    if data == None:
        data = read_from_json(FAMILY_SHARE_FILE)
    games = []
    for user in data["users"].values():
        games += user["unshared_games"]
    for family in data["families"].values():
        games += family["shared_games"]
    return list(set(games))

def get_all_accessible_games_for_user(user_id, data=None):
    '''Returns all games accessible to a user through their own library and
    their family-shared libraries.
    '''
    if data == None:
        data = read_from_json(FAMILY_SHARE_FILE)
    if user_id not in data["users"]:
        return None
    games = data["users"][user_id]["unshared_games"].copy()
    family = None
    if "family" in data["users"][user_id] and data["users"][user_id]["family"]:
        family = data["users"][user_id]["family"]
    if family:
        games += data["families"][family]["shared_games"]
    return games

def get_history_of_user(user_id, data=None):
    '''Returns all games marked as "Don't Suggest Again" by a user.
    '''
    if data == None:
        data = read_from_json(FAMILY_SHARE_FILE)
    if user_id not in data["users"]:
        return None
    if "history" in data["users"][user_id]:
        return data["users"][user_id]["history"]
    return []

def get_valid_suggestions_for_user(user_id, data=None):
    '''Returns all of a user's accessible games without those in their history.
    '''
    if data == None:
        data = read_from_json(FAMILY_SHARE_FILE)
    games = get_all_accessible_games_for_user(user_id, data=data)
    if games == None:
        return None
    history = get_history_of_user(user_id, data=data)
    if history == None:
        return games
    return list(set(games) - set(history))

def initialize_database_user_dict(steam_id=None, family=None, history=[], unshared_games=[]):
    '''Returns a new dict for users in the JSON database.
    '''
    return {
        "steam_id": steam_id,
        "family": family,
        "history": history,
        "unshared_games": unshared_games
    }

def is_steam_id(steam_id):
    '''Returns a boolean whether the provided steam_id is a 64-bit 17-digit
    Steam ID.
    '''
    return re.search(r"^7656119\d{10}$", steam_id) != None

def get_steam_key():
    '''Returns the Steam API key from its separate file.
    '''
    with open(STEAM_API_KEY_FILE) as f:
        return f.read()

def get_server_member_ids(guild):
    '''Returns the user IDs of all members of this server.
    '''
    if not guild:
        return []
    return [str(member.id) for member in guild.members]

#-------------------------------------------------------------------------------
#Views
class ViewFamilyShare(ui.View):
    def __init__(self, author_id, game_name):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.add_item(ButtonAccept(author_id, game_name))
        self.add_item(ButtonRefuse(author_id))

class ViewRequestPermission(ui.View):
    def __init__(self, applicant_id, family_member_ids):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.add_item(ButtonGivePermission(applicant_id, family_member_ids))
        self.add_item(ButtonDenyPermission(family_member_ids))

class ViewInviteToFamily(ui.View):
    def __init__(self, inviter_id, target_id):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.add_item(ButtonAcceptInvite(inviter_id, target_id))
        self.add_item(ButtonDenyInvite(target_id))

class ViewHideSimilarMatch(ui.View):
    def __init__(self, author_id, game_names):
        super().__init__(timeout=VIEW_TIMEOUT)
        for game_name in game_names:
            self.add_item(ButtonHideGame(author_id, game_name))

class ViewUnhideSimilarMatch(ui.View):
    def __init__(self, author_id, game_names):
        super().__init__(timeout=VIEW_TIMEOUT)
        for game_name in game_names:
            self.add_item(ButtonUnhideGame(author_id, game_name))

class ViewResetHistory(ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.add_item(ButtonReset(author_id))

class ViewPaginatedList(ui.View):
    def __init__(self, game_names, page=1, max_options=25):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.add_item(ButtonPrevPage(game_names, page, max_options=max_options))
        self.add_item(ButtonGotoPage(game_names, max_options=max_options))
        self.add_item(ButtonNextPage(game_names, page, max_options=max_options))

class ButtonAccept(ui.Button):
    def __init__(self, author_id, game_name):
        super().__init__(label="Don't Suggest Again", style=discord.ButtonStyle.green)
        self.author_id = author_id
        self.game_name = game_name
    async def callback(self, interaction):
        '''Removes view. Adds this game to the list of games seen by this user.
        '''
        try:
            if str(interaction.user.id) != self.author_id:
                await interaction.response.send_message(
                    "Only the user who invoked the command can use these buttons.", ephemeral=True
                )
                return
            await interaction.response.edit_message(view=None)
            data = read_from_json(FAMILY_SHARE_FILE)
            if self.author_id not in data["users"]:
                data["users"][self.author_id] = initialize_database_user_dict()
            data["users"][self.author_id]["history"].append(self.game_name)
            write_to_json(FAMILY_SHARE_FILE, data)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonRefuse(ui.Button):
    def __init__(self, author_id):
        super().__init__(label="Maybe Later, Reroll", style=discord.ButtonStyle.red)
        self.author_id = author_id
    async def callback(self, interaction):
        '''Replaces the current message with a new random game.
        '''
        try:
            if str(interaction.user.id) != self.author_id:
                await interaction.response.send_message(
                    "Only the user who invoked the command can use these buttons.", ephemeral=True
                )
                return
            await handle_familyshare(interaction.response.edit_message, self.author_id)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonGivePermission(ui.Button):
    def __init__(self, applicant_id, family_member_ids):
        super().__init__(label="Accept", style=discord.ButtonStyle.green)
        self.applicant_id = applicant_id
        self.family_member_ids = family_member_ids
    async def callback(self, interaction):
        '''Removes view. Adds the applicant to their new Steam family.
        '''
        try:
            if str(interaction.user.id) not in self.family_member_ids:
                await interaction.response.send_message(
                    "Only the registered members of this Steam family can give permission.", ephemeral=True
                )
                return
            msg = interaction.message.content + "\n\nPermission has been granted. Welcome to the family."
            await interaction.response.edit_message(content=msg, view=None)
            data = read_from_json(FAMILY_SHARE_FILE)
            family_owner = self.family_member_ids[0]
            family = None
            if "family" in data["users"][family_owner] and data["users"][family_owner]["family"]:
                family = data["users"][family_owner]["family"]
            else:
                family = generate_new_family_id(data)
                data["users"][family_owner]["family"] = family
                data["families"][family] = {"members": {family_owner: "Discord"}, "shared_games": []}
            data["users"][self.applicant_id]["family"] = family
            data["families"][family]["members"][self.applicant_id] = "Discord"
            sync_user_library(self.applicant_id, data=data)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonDenyPermission(ui.Button):
    def __init__(self, family_member_ids):
        super().__init__(label="Refuse", style=discord.ButtonStyle.red)
        self.family_member_ids = family_member_ids
    async def callback(self, interaction):
        '''Removes view.
        '''
        try:
            if str(interaction.user.id) not in self.family_member_ids:
                await interaction.response.send_message(
                    "Only the registered members of this Steam family can deny permission.", ephemeral=True
                )
                return
            msg = interaction.message.content + "\n\nPermission was denied."
            await interaction.response.edit_message(content=msg, view=None)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonAcceptInvite(ui.Button):
    def __init__(self, inviter_id, target_id):
        super().__init__(label="Accept", style=discord.ButtonStyle.green)
        self.inviter_id = inviter_id
        self.target_id = target_id
    async def callback(self, interaction):
        '''Removes view. Adds the target to their new Steam family.
        '''
        try:
            if str(interaction.user.id) != self.target_id:
                await interaction.response.send_message(
                    "Only the invited user can accept the invite.", ephemeral=True
                )
                return
            msg = interaction.message.content + "\n\nInvite accepted. Welcome to the family."
            await interaction.response.edit_message(content=msg, view=None)
            data = read_from_json(FAMILY_SHARE_FILE)
            family = None
            if "family" in data["users"][self.inviter_id] and data["users"][self.inviter_id]["family"]:
                family = data["users"][self.inviter_id]["family"]
            else:
                family = generate_new_family_id(data)
                data["users"][self.inviter_id]["family"] = family
                data["families"][family] = {"members": {self.inviter_id: "Discord"}, "shared_games": []}
            data["users"][self.target_id]["family"] = family
            data["families"][family]["members"][self.target_id] = "Discord"
            sync_user_library(self.target_id, data=data)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonDenyInvite(ui.Button):
    def __init__(self, target_id):
        super().__init__(label="Refuse", style=discord.ButtonStyle.red)
        self.target_id = target_id
    async def callback(self, interaction):
        '''Removes view.
        '''
        try:
            if str(interaction.user.id) != self.target_id:
                await interaction.response.send_message(
                    "Only the invited user can deny the invite.", ephemeral=True
                )
                return
            msg = interaction.message.content + "\n\nInvite was denied."
            await interaction.response.edit_message(content=msg, view=None)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonHideGame(ui.Button):
    def __init__(self, author_id, game_name):
        super().__init__(label=game_name, style=discord.ButtonStyle.blurple)
        self.author_id = author_id
        self.game_name = game_name
    async def callback(self, interaction):
        '''Removes view. Adds game title to history.
        '''
        try:
            if str(interaction.user.id) != self.author_id:
                await interaction.response.send_message(
                    "Only the user who invoked the command can use these buttons.", ephemeral=True
                )
                return
            msg = get_msg_hide(self.author_id, self.game_name)
            await interaction.response.edit_message(content=msg, view=None)
            data = read_from_json(FAMILY_SHARE_FILE)
            if self.author_id not in data["users"]:
                data["users"][self.author_id] = initialize_database_user_dict()
            data["users"][self.author_id]["history"].append(self.game_name)
            write_to_json(FAMILY_SHARE_FILE, data)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonUnhideGame(ui.Button):
    def __init__(self, author_id, game_name):
        super().__init__(label=game_name, style=discord.ButtonStyle.blurple)
        self.author_id = author_id
        self.game_name = game_name
    async def callback(self, interaction):
        '''Removes view. Removes game title from history.
        '''
        try:
            if str(interaction.user.id) != self.author_id:
                await interaction.response.send_message(
                    "Only the user who invoked the command can use these buttons.", ephemeral=True
                )
                return
            msg = get_msg_unhide(self.author_id, self.game_name)
            await interaction.response.edit_message(content=msg, view=None)
            data = read_from_json(FAMILY_SHARE_FILE)
            data["users"][self.author_id]["history"].remove(self.game_name)
            write_to_json(FAMILY_SHARE_FILE, data)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonReset(ui.Button):
    def __init__(self, author_id):
        super().__init__(label="Reset Suggestions", style=discord.ButtonStyle.blurple)
        self.author_id = author_id
    async def callback(self, interaction):
        '''Wipes the history of the user.
        '''
        try:
            if interaction.user.id != self.author_id:
                await interaction.response.send_message(
                    "Only the user who invoked the command can use these buttons.", ephemeral=True
                )
                return
            msg = interaction.message.content
            msg += "\n\nAll Steam games are now eligible to be suggested again!"
            await interaction.response.edit_message(content=msg, view=None)
            data = read_from_json(FAMILY_SHARE_FILE)
            if self.author_id not in data["users"]:
                data["users"][self.author_id] = initialize_database_user_dict()
            data["users"][self.author_id]["history"] = []
            write_to_json(FAMILY_SHARE_FILE, data)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonPrevPage(ui.Button):
    def __init__(self, game_names: list, page: int, max_options=25):
        self.game_names = game_names
        self.page = page
        self.max_options = max_options
        disabled = True if page <= 1 else False
        prev_page = page if disabled else page-1
        super().__init__(label=f"← Page {prev_page}", style=discord.ButtonStyle.blurple, disabled=disabled)
    async def callback(self, interaction):
        try:
            embed = generate_game_titles_list_embed(self.game_names, page=self.page-1, max_options=self.max_options)
            await interaction.response.edit_message(embed=embed,
                    view=ViewPaginatedList(self.game_names, self.page-1, max_options=self.max_options)
                )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonNextPage(ui.Button):
    def __init__(self, game_names: list, page: int, max_options=25):
        self.game_names = game_names
        self.page = page
        self.max_options = max_options
        disabled = True if max_options*page >= len(game_names) else False
        next_page = page if disabled else page+1
        super().__init__(label=f"Page {next_page} →", style=discord.ButtonStyle.blurple, disabled=disabled)
    async def callback(self, interaction):
        try:
            embed = generate_game_titles_list_embed(self.game_names, page=self.page+1, max_options=self.max_options)
            await interaction.response.edit_message(embed=embed,
                    view=ViewPaginatedList(self.game_names, self.page+1, max_options=self.max_options)
                )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonGotoPage(ui.Button):
    def __init__(self, game_names: list, max_options=25):
        self.game_names = game_names
        self.max_options = max_options
        super().__init__(label=f"…", style=discord.ButtonStyle.blurple)
    async def callback(self, interaction):
        try:
            await interaction.response.send_modal(ModalPageGoto(self.game_names, max_options=self.max_options))
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ModalPageGoto(ui.Modal, title="Skip to Page"):
    def __init__(self, game_names, max_options=25):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.game_names = game_names
        self.max_options = max_options
    input = ui.TextInput(label="Page Number", placeholder="Skip to which page?", required=True)
    async def on_submit(self, interaction):
        try:
            page = self.input.value
            max_page = math.ceil(len(self.game_names)/self.max_options)
            if page.isdigit() == False or int(page) > max_page or int(page) <= 0:
                await interaction.response.send_message(f'"{page}" is not a valid page number.', ephemeral=True)
                return
            page = int(page)
            embed = generate_game_titles_list_embed(self.game_names, page=page, max_options=self.max_options)
            await interaction.response.edit_message(embed=embed,
                    view=ViewPaginatedList(self.game_names, page, max_options=self.max_options)
                )
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

#-------------------------------------------------------------------------------
#Add Cog
async def setup(client):
    await client.add_cog(FamilyShare(client))
