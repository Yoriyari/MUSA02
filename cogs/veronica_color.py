#===============================================================================
# Veronica Color v1.0.2
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.0.2; Hid Discord user IDs and server IDs from file. Updated
#               error handling. -YY
# 17 Apr 2024 - v1.0.1; Added emoji reaction to start/stopping timer. -YY
# 01 Apr 2024 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# veronica_color.py gives Discord user Veronica a random role colour every day
# in the TITS server.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands, tasks
from discord import Color

from common.private_ids import discord_id, guild_id
from common.error_message import send_error

VERONICA_ID = discord_id("veronica")
TITS_ID = guild_id("tits")
PERSONAL_ROLE_ID = 1220715427731079228

#-------------------------------------------------------------------------------

#Cog Setup
class VeronicaColor(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.daily_timer.start()

    @tasks.loop(hours=24.0)
    async def daily_timer(self):
        '''Changes Veronica's personal role colour every 24 hours.
        '''
        try:
            if self.daily_timer.current_loop != 0:
                tits_server = self.client.get_guild(TITS_ID)
                role = tits_server.get_role(PERSONAL_ROLE_ID)
                color = Color.random()
                await role.edit(color=color, reason="Veronica's daily role colour randomization.")
        except Exception as e:
            await send_error(self.client, Exception(f"Veronica's colour randomization error.\n{e}"))

    @commands.Cog.listener()
    async def on_ready(self):
        print("Veronica Color cog loaded.")

    @commands.group(name="mousecontrol", aliases=["mouse_control"], case_insensitive=True, invoke_without_command=True)
    async def mousecontrol(self, ctx):
        pass

    @mousecontrol.command(aliases=["pause", "stop", "cancel"], case_insensitive=True, invoke_without_command=True)
    async def mousecontrol_cancel(self, ctx):
        '''Cancels Veronica's colour randomization timer.
        '''
        try:
            self.daily_timer.cancel()
            await ctx.message.add_reaction("👍")
            print("Veronica's color randomization timer cancelled.")
        except Exception as e:
            await send_error(self.client, e, ctx.message.jump_url)

    @mousecontrol.command(aliases=["start", "restart", "resume", "continue", "unpause", "unstop", "uncancel"], case_insensitive=True, invoke_without_command=True)
    async def mousecontrol_start(self, ctx):
        '''Starts Veronica's colour randomization timer.
        '''
        try:
            if not self.daily_timer.is_running():
                self.daily_timer.start()
                await ctx.message.add_reaction("👍")
                print("Veronica's color randomization timer started.")
        except Exception as e:
            await send_error(self.client, e, ctx.message.jump_url)

async def setup(client):
    await client.add_cog(VeronicaColor(client))
