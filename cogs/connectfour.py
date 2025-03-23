#===============================================================================
# Connect Four v1.4.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 02 May 2024 - v1.4.1; Reworked help message import. Added error handling. -YY
# 17 Apr 2022 - v1.4; Centralized help messages to one importable file. -YY
# 02 Jun 2021 - v1.3; Added support for inactivity timer of sessions. -YY
# 30 May 2021 - v1.2; Reaction join now goes through cog's join() instead of
#               Game's join(), which allows for better specialization; Added
#               database support. -YY
# 24 May 2021 - v1.1; Renamed fourOnARow.py to connectfour.py and class
#               fourOnARow to ConnectFour to match Python naming convention.
#               Rewrote file a considerable amount to match common functions/
#               classes. Removed some unnecessary functions. -YY
# 24 Apr 2021 - v1.0; Added color and name of player that can make a move. Fixed
#               bug where when one column was filled only one player could play
#               -RK
# 22 Apr 2021 - Game works for most cases -RK
# 21 Apr 2021 - Copied parts of tictactoe.py and started to think about
#               what needed to be different -RK
#===============================================================================
# Notes
# ..............................................................................
# - Make the game able to have different board sizes, different color styles-
#  (its now made for darkmode) -RK
#===============================================================================
# Description
# ..............................................................................
# connectfour.py plays a game where two players take turns placing their token
# into the bottom row of a column in a 6x7 grid. When four tokens belonging to
# the same player line up, that player wins.
#===============================================================================

#Import Modules
import discord
from discord import Message
from discord.ext import commands

from common.session import Session
from common.player import Player
from common.game import Game
from common.emoji import number_to_emoji, emoji_to_number
from common.error_message import send_error
from common.help_message import send_help

#Session Setup
class ConnectFourSession(Session):
    #Define variables.
    def __init__(self, parent):
        Session.__init__(self, parent)
        self.__player_turn = 0
        self.__message_board = None
        self.__board_state = [["0","0","0","0","0","0","0"],
                              ["0","0","0","0","0","0","0"],
                              ["0","0","0","0","0","0","0"],
                              ["0","0","0","0","0","0","0"],
                              ["0","0","0","0","0","0","0"],
                              ["0","0","0","0","0","0","0"]]

    @property
    def player_turn(self):
        return self.__player_turn

    @property
    def message_board(self):
        return self.__message_board

    @property
    def board_state(self):
        return self.__board_state

    @board_state.setter
    def board_state(self, board_state: str):
        self.__board_state = board_state

    @message_board.setter
    def message_board(self, message_board: Message):
        self.__message_board = message_board

    #Set next player turn.
    def next_turn(self):
        self.__player_turn = (self.__player_turn + 1) % len(self.players)

#Cog Setup
class ConnectFourCog(Game):
    #Define variables.
    def __init__(self, client):
        Game.__init__(self, client)
        self.instant_start = True
        self.game_name = "Connect Four"
        self.game_abbrev = "c4"

    #Secondary functions
    #Get maximum amount of players of a session.
    def get_max_players(self, session):
        return 2

    #Remove session on inactivity timeout.
    async def timeout_session(self, session):
        if session.message_board != None:
            msg = f"{self.game_name} room {session.room_id} has timed out due to inactivity."
            await session.message_board.edit(content=msg)
            await session.message_board.clear_reactions()
        await Game.timeout_session(self, session)

    #Generate game board message.
    def generate_board_message(self, session):
        msg = f"**Connect Four Room {session.room_id}**\n"
        msg += f"🔴: {session.players[0].user.mention}\n"
        msg += f"🟡: {session.players[1].user.mention}\n"
        for row in range(6):
            msg += "\n|"
            for col in range(7):
                if session.board_state[row][col] == "0":
                    msg += "◼️|"
                    continue
                if session.board_state[row][col] == "Red":
                    msg += "🔴|"
                    continue
                if session.board_state[row][col] == "Yellow":
                    msg += "🟡|"
        msg += "\n|1️⃣|2️⃣|3️⃣|4️⃣|5️⃣|6️⃣|7️⃣|"
        if self.is_game_tied(session.board_state) == True:
            msg += "\n\nThe game has ended in a tie!"
            return msg
        msg += f"\n\n{session.players[session.player_turn].user.mention}"
        if self.is_game_won(session.board_state) == True:
            msg += " has won the game!"
            return msg
        msg += "'s turn!"
        return msg

    #checks if one player has 4 in a row (to know who won check which move was done last)
    def is_game_won(self, board_state):
        #Check for horizontal wins (starting from x = 0 to x = 3 going x = 3 to x = 6)
        for row in range(6):
            for col in range(4):
                if board_state[row][col] != "0":
                    if all(board_state[row][col] == board_state[row][col+i] for i in range(1, 4)):
                        return True
        #Check for vertical wins
        for row in range(3):
            for col in range(7):
                if board_state[row][col] != "0":
                    if all(board_state[row][col] == board_state[row+i][col] for i in range(1, 4)):
                        return True
        #Check for diagonal wins left to right
        for row in range(3):
            for col in range(4):
                if board_state[row][col] != "0":
                    if all(board_state[row][col] == board_state[row+i][col+i] for i in range(1, 4)):
                        return True
        #Check for diagonal wins right to left
        for row in range(3):
            for col in range(3, 7):
                if board_state[row][col] != "0":
                    if all(board_state[row][col] == board_state[row+i][col-i] for i in range(1, 4)):
                        return True

    #Checks if a column is full.
    def is_column_full(self, board_state, column):
        for row in range(6):
            if board_state[row][column] == "0":
                return False
        return True

    #Check board state for a tie position.
    def is_game_tied(self, board_state):
        for col in range(7):
            if self.is_column_full(board_state, col) == False:
                return False
        return self.is_game_won(board_state) == False

    #Place token in tile, check for winner, edit message and clear reaction.
    async def process_turn(self, session, column, reaction):
        session.inactivity_timer_restart()
        #Prevent placing in a full column.
        if self.is_column_full(session.board_state, column):
            return
        #Identify token and place it.
        token = "Red"
        if session.player_turn == 1:
            token = "Yellow"
        for row in reversed(range(6)):
            if session.board_state[row][column] == "0":
                session.board_state[row][column] = token
                break
        #If game is won or tied.
        if self.is_game_won(session.board_state) == True or self.is_game_tied(session.board_state) == True:
            #End session
            msg = self.generate_board_message(session)
            await reaction.message.edit(content=msg)
            await reaction.message.clear_reactions()
            self.remove_session(session)
            return
        #If game is unfinished.
        session.next_turn()
        msg = self.generate_board_message(session)
        await reaction.message.edit(content=msg)

    #Generate and send first message.
    async def setup_game(self, session, channel):
        await Game.setup_game(self, session, channel)
        session.inactivity_timer_restart()
        session.shuffle_players()
        msg = self.generate_board_message(session)
        board_message = await channel.send(msg)
        session.message_board = board_message
        for i in range(7):
            reaction = number_to_emoji(i+1)
            await board_message.add_reaction(reaction)
        return

    #Handle additional checks required when a player quits the game.
    async def remove_player(self, session, user):
        session.remove_player(user)
        if session.message_board != None:
            await session.message_board.delete()
        self.remove_session(session)

    #Primary functions
    #With no arguments specified, send game instructions.
    @commands.group(name="connectfour", aliases=["c4", "cf", "connect4", "connect_four", "connect_4", "4row", "fourinarow", "four_in_a_row", "4inarow", "4_in_a_row"], case_insensitive=True, invoke_without_command=True)
    async def connectfour(self, ctx):
        try:
            await send_help(ctx.channel.send, "connectfour")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Help command to receive instructions.
    @connectfour.command(aliases=["?", "info", "information", "instructions"])
    async def help(self, ctx):
        try:
            await send_help(ctx.channel.send, "connectfour")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #See the list of players of a room.
    @connectfour.command(aliases=["player", "players", "playerlist", "playerslist", "players_list", "list"])
    async def player_list(self, ctx, room_id=None):
        try:
            await Game.player_list(self, ctx, room_id)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Register a new game room.
    @connectfour.command(aliases=["start", "begin", "create", "register", "host"])
    async def new(self, ctx):
        try:
            session = ConnectFourSession(self)
            player = Player(ctx.author)
            await Game.new(self, ctx, session, player)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Join an existing game room by message.
    @connectfour.command(aliases=["enter"])
    async def join(self, ctx, room_id=None):
        try:
            player = Player(ctx.author)
            await Game.join(self, ctx, room_id, player)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Quit a room.
    @connectfour.command(aliases=["stop", "exit", "end", "leave"])
    async def quit(self, ctx, room_id=None):
        try:
            await Game.quit(self, ctx, room_id)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Reaction handling
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        try:
            #Prevent bot's own reactions triggering this
            if user == self.client.user:
                return
            for session in self.game_sessions:
                #Joining game by reacting with play emoji
                if session.message_join != None and reaction.message.id == session.message_join.id and reaction.emoji == "▶️":
                    ctx = await self.client.get_context(reaction.message)
                    ctx.author = user
                    await self.join(ctx, session.room_id)
                    return

                #Taking turn by reacting with number emoji
                if session.message_board != None and reaction.message.id == session.message_board.id:
                    if user.id == session.players[session.player_turn].user.id:
                        if reaction.emoji in ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣"]:
                            #Find which number was reacted with
                            col = emoji_to_number(reaction.emoji)-1
                            await self.process_turn(session, col, reaction)
                            await reaction.message.remove_reaction(reaction.emoji, user)
                    return
        except Exception as e:
            await send_error(self.client, e, reference=reaction.message.jump_url)

    @connectfour.command()
    async def print_cache(self, ctx):
        Game.print_cache(self)

#Client Setup
async def setup(client):
    await client.add_cog(ConnectFourCog(client))
