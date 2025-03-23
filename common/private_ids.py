#===============================================================================
# Private IDs v1.0
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# user_ids.py returns private ID values, such as a user's Discord ID or a
# Discord server's ID.
#===============================================================================

#Import Modules
from common.json_handling import read_from_json

DISCORD_IDS_FILE = "secrets/discord_user_ids.json"
GUILD_IDS_FILE = "secrets/discord_guild_ids.json"

def discord_id(name, *additional_names):
    data = read_from_json(DISCORD_IDS_FILE)
    if not additional_names:
        return data[name]
    return [data[name]] + [data[next] for next in additional_names]

def guild_id(name, *additional_names):
    data = read_from_json(GUILD_IDS_FILE)
    if not additional_names:
        return data[name]
    return [data[name]] + [data[next] for next in additional_names]

def guilds_whitelisted_for_nsfw():
    return guild_id("tits", "gang plays", "stonecutters", "test server", "rhaulis server", "roxys polycule")
