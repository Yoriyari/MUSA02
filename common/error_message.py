#===============================================================================
# Error Message v2.1.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v2.1.1; Hid Discord user IDs from file. -YY
# 07 May 2024 - v2.1; Moved the commonly-used UserError class to this file. -YY
# 02 May 2024 - v2.0; Instead of just returning a generic error string, the
#               function now actually fetches Yori's DMs and sends the error
#               message there, making this function more generalizeable across
#               other files. -YY
# 14 Oct 2022 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# error_message.py takes a bot error message and forwards it to Yori's DMs.
# It also contains the UserError class for developer-defined errors of users
# interacting with the bot.
#===============================================================================

from common.private_ids import discord_id

YORI_ID = discord_id("yori")

#Class
class UserError(Exception):
    def __init__(self, message="A user error occurred."):
        super().__init__(message)

#Functions
async def send_error(client, exception: Exception, reference=None):
    '''Forwards an error message to Yori's DMs.
    '''
    yori = client.get_user(YORI_ID)
    msg = ""
    if reference:
        msg = f"{reference}\n"
    msg += f"Error: {exception}"
    await yori.send(msg)

def error_message(exception: Exception):
    '''Returns a generic error message string. Kept for legacy reasons.
    '''
    return f"Error: {exception}"
