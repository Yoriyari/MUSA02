#===============================================================================
# Help Message v2.0.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 07 May 2024 - v2.0.1; Made help messages an Embed. -YY
# 02 May 2024 - v2.0; Moved messages from this file to a database so that I can
#               update them dynamically. -YY
# 17 Apr 2022 - v1.0.1; Made all other commands able to call help_messages.py as
#               well, in addition to just the help command. -YY
# 25 Jan 2022 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# help_messages.py can fetch and send a message containing information about how
# to use any of the bot's commands.
#===============================================================================

#Import Modules
from discord import Embed

from common.yaml_handling import read_from_yaml

HELP_MESSAGES_FILE = "data/help_messages.yml"

#-------------------------------------------------------------------------------
#Functions
async def send_help(send_hook, command, ephemeral=False):
    '''Sends a help message for the specified command.
    '''
    msg = help_message(command)
    if not msg:
        return
    title, desc = msg.split("\n", 1)
    embed = Embed(title=title, description=desc)
    if ephemeral: # Can't just do (ephemeral=ephemeral) cuz not all send hooks have an ephemeral parameter
        await send_hook(embed=embed, ephemeral=True)
        return
    await send_hook(embed=embed)

def help_message(command):
    '''Returns a string containing the help message contents for the specified
    command.
    '''
    data = read_from_yaml(HELP_MESSAGES_FILE)
    try:
        return data[command]["message"]
    except Exception:
        try:
            for value in data.values():
                if command in value["aliases"]:
                    return value["message"]
        except Exception:
            return None
