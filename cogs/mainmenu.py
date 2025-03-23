#===============================================================================
# Main Menu v1.4.3
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 04 Dec 2024 - v1.4.3; Removed 'games' and 'list' aliases as well. -YY
# 30 Nov 2024 - v1.4.2; Removed 'game' as alias so family_share can use it. -YY
# 05 May 2024 - v1.4.1; Reworked help message import. Added error handling. -YY
# 10 Nov 2023 - v1.4; Added RPS interaction. Also mentioned Card and Tarot. -YY
# 17 Apr 2022 - v1.3; Centralized help messages to one importable file. -YY
# 04 Jun 2021 - v1.2; Forgot to actually start the inactivity timer, fixed.
#               Message now gives feedback to when the timer timed out. -YY
# 02 Jun 2021 - v1.1; Added inactivity timer to sessions. -YY
# 30 May 2021 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# The main menu displays a list of games available through the bot and lets
# users start a new game through text command or reaction.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands, tasks

from common.error_message import send_error
from common.help_message import send_help

class MainMenuSession:
    def __init__(self, ctx, parent, message_menu):
        self.__ctx = ctx
        self.__parent = parent
        self.__message_menu = message_menu
        self.inactivity_timer.start()

    @property
    def ctx(self):
        return self.__ctx

    @property
    def message_menu(self):
        return self.__message_menu

    #Inactivity timer.
    @tasks.loop(minutes=10.0, count=2)
    async def inactivity_timer(self):
        if self.inactivity_timer.current_loop != 0:
            await self.__parent.timeout_session(self)

#Cog Class
class MainMenuCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.menu_sessions = []

    #Report successful load.
    @commands.Cog.listener()
    async def on_ready(self):
        print("Main Menu cog loaded.")

    #Secondary Functions
    #Remove session on inactivity timeout. Override if needed.
    async def timeout_session(self, session):
        msg = session.message_menu.content + "\n"
        msg += "Reactions have timed out. Use the text command or call for a new main menu message."
        await session.message_menu.edit(content=msg)
        await session.message_menu.clear_reactions()
        self.menu_sessions.remove(session)

    #Primary Functions
    #With no arguments specified, send game instructions.
    @commands.group(name="mainmenu", aliases=["main_menu", "main", "menu", "games_list", "game_list", "gameslist", "gamelist"], case_insensitive=True, invoke_without_command=True)
    async def mainmenu(self, ctx):
        try:
            msg = "**Main Menu**\n"
            msg += "1️⃣ - `!bj` - Blackjack.\n"
            msg += "2️⃣ - `!ch` - Checkers.\n"
            msg += "3️⃣ - `!c4` - Connect Four.\n"
            msg += "4️⃣ - `!hm` - Hangman.\n"
            msg += "5️⃣ - `!ttt` - Tic-tac-toe.\n"
            msg += "6️⃣ - `!rps` - Rock Paper Scissors.\n"
            msg += "`!cah` - Cards Against Humanity.\n"
            msg += "`!mm` - Mastermind.\n"
            msg += "`!card` - Pick random playing cards.\n"
            msg += "`!tarot` - Pick random tarot cards.\n"
            msg += "`!deck` - Playing card deck which doesn't give duplicates and remembers who drew what."
            message_menu = await ctx.channel.send(msg)
            self.menu_sessions.append(MainMenuSession(ctx, self, message_menu))
            await message_menu.add_reaction("1️⃣")
            await message_menu.add_reaction("2️⃣")
            await message_menu.add_reaction("3️⃣")
            await message_menu.add_reaction("4️⃣")
            await message_menu.add_reaction("5️⃣")
            await message_menu.add_reaction("6️⃣")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Help command to receive instructions.
    @mainmenu.command(aliases=["?", "info", "information", "instructions"])
    async def help(self, ctx):
        try:
            await send_help(ctx.channel.send, "mainmenu")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Reaction handling
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        try:
            #Prevent bot's own reactions triggering this
            if user == self.client.user:
                return
            for session in self.menu_sessions:
                #Starting game by reacting with appropriate emoji
                if reaction.message.id == session.message_menu.id:
                    ctx = await self.client.get_context(reaction.message)
                    ctx.author = user
                    command = None
                    if reaction.emoji == "1️⃣":
                        command = self.client.get_command("blackjack new")
                    elif reaction.emoji == "2️⃣":
                        command = self.client.get_command("checkers new")
                    elif reaction.emoji == "3️⃣":
                        command = self.client.get_command("connectfour new")
                    elif reaction.emoji == "4️⃣":
                        command = self.client.get_command("hangman new")
                    elif reaction.emoji == "5️⃣":
                        command = self.client.get_command("tictactoe new")
                    elif reaction.emoji == "6️⃣":
                        command = self.client.get_command("rockpaperscissors")
                    if command != None:
                        await ctx.invoke(command)
                    return
        except Exception as e:
            await send_error(self.client, e, reference=reaction.message.jump_url)

#Client Setup
async def setup(client):
    await client.add_cog(MainMenuCog(client))
