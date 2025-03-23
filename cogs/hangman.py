#===============================================================================
# Hangman v1.4.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 02 May 2024 - v1.4.1; Reworked help message import. Added error handling. -YY
# 17 Apr 2022 - v1.4; Centralized help messages to one importable file. -YY
# 04 Jun 2021 - v1.3; Fixed me forgetting to note max mistakes in settings
#               message. Bot will no longer choose secret words shorter than
#               four characters. -YY
# 02 Jun 2021 - v1.2; Fixed me forgetting to implement has_game_started last
#               time. Added support for inactivity timer of sessions. -YY
# 30 May 2021 - v1.1; Reaction join now goes through cog's join() instead of
#               Game's join(), which allows for better specialization. -YY
# 25 May 2021 - v1.0; Finished file. -YY
# 24 May 2021 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Add leaderboards support. -YY
# - Add the option for a player to set the secret word (as "executioner"). -YY
# - Allow participating players to send a message with just one letter in it to
#   guess. -YY
# - Send the current game state in a new message and delete the old game state
#   message in order to prevent the game being buried by conversation. This also
#   would allow for the guessing player to be @'d each new turn. -YY
# - Consider letting players guess the full word. -YY
# - Consider a turnless mode where every player can guess at any time. -YY
# - If two people !start an active room, two games start and only the latter
#   operates. -YY
# - !leave does not remove someone from an active room. -YY
# - If the last player in the list is the current turn and tries to leave, the
#   bot fails to give the turn to the next player in the list after removing the
#   player. -YY
#===============================================================================
# Description
# ..............................................................................
# hangman.py plays a game where player(s) take turns guessing letters in an
# attempt to deduce a word. One user has to privately choose the word.
# The bot can take this role by choosing a word from a dictionary.
#===============================================================================

#Import Modules
import discord
from discord import Message, User
from discord.ext import commands

from common.session import Session
from common.player import Player
from common.game import Game
from common.error_message import send_error
from common.help_message import send_help

import random
import os.path

WORDS_FILE = "data/words.txt"

#Session Class
class HangmanSession(Session):
    def __init__(self, parent):
        Session.__init__(self, parent)
        self.__max_players = 6
        self.__executioner = None
        self.__player_turn = 0
        self.__max_mistakes = 6
        self.__secret_word = ""
        self.__guessed_letters = []
        self.__message_board = None

    @property
    def max_players(self):
        return self.__max_players

    @property
    def executioner(self):
        return self.__executioner

    @property
    def player_turn(self):
        return self.__player_turn

    @property
    def max_mistakes(self):
        return self.__max_mistakes

    @property
    def secret_word(self):
        return self.__secret_word

    @property
    def guessed_letters(self):
        return self.__guessed_letters

    @property
    def message_board(self):
        return self.__message_board

    @property
    def mistakes(self):
        mistakes = 0
        for letter in self.__guessed_letters:
            if letter not in self.__secret_word:
                mistakes += 1
        return mistakes

    @property
    def mistakes_permitted(self):
        return self.__max_mistakes - self.mistakes

    @max_players.setter
    def max_players(self, max_players: int):
        self.__max_players = max_players

    @executioner.setter
    def executioner(self, executioner: User):
        self.__executioner = Player(executioner)

    @max_mistakes.setter
    def max_mistakes(self, max_mistakes: int):
        self.__max_mistakes = max_mistakes

    @secret_word.setter
    def secret_word(self, secret_word: str):
        self.__secret_word = secret_word

    @message_board.setter
    def message_board(self, message_board: Message):
        self.__message_board = message_board

    #Set next player turn.
    def next_turn(self):
        self.__player_turn = (self.__player_turn + 1) % len(self.players)

    #Go back to previous player turn.
    def prev_turn(self):
        self.__player_turn = (self.__player_turn - 1) % len(self.players)

#Cog Class
class HangmanCog(Game):
    def __init__(self, client):
        Game.__init__(self, client)
        self.game_name = "Hangman"
        self.game_abbrev = "hm"

    #Secondary Functions
    #Get maximum amount of players of a session.
    def get_max_players(self, session):
        return session.max_players

    #Check whether a game has started yet.
    def has_game_started(self, session):
        return session.executioner != None

    #Remove session on inactivity timeout.
    async def timeout_session(self, session):
        if session.message_board != None:
            msg = f"{self.game_name} room {session.room_id} has timed out due to inactivity."
            await session.message_board.edit(content=msg)
            await session.message_board.clear_reactions()
        await Game.timeout_session(self, session)

    #Check board state for a winning position.
    def is_game_won(self, session):
        for letter in session.secret_word:
            if letter not in session.guessed_letters:
                return False
        return True

    #Check board state for a tie position.
    def is_game_lost(self, session):
        return session.mistakes >= session.max_mistakes

    #Generate game board message.
    def generate_board_message(self, session):
        #Line: Room Title
        msg = f"**Hangman Room {session.room_id}**\n"
        #Line: Executioner Name
        msg += f"Executioner: {session.executioner.user.mention}\n"
        #Line: Player Names
        msg += f"Players: "
        for i, player in enumerate(session.players):
            if i:
                msg += ", "
            msg += f"{player.user.mention}"
        msg += "\n"
        #Line: Instructions
        msg += f"Guess by typing `!hm guess X`, replacing X with your guess."
        msg += "\n\n```"
        #Line: Ceiling
        msg += "┌" if session.mistakes_permitted <= 7 else "╷" if session.mistakes_permitted <= 8 else " "
        msg += "──" if session.mistakes_permitted <= 7 else "  "
        msg += "┬" if session.mistakes_permitted <= 6 else "─" if session.mistakes_permitted <= 7 else " "
        msg += "─" if session.mistakes_permitted <= 7 else " "
        msg += "  Guesses:\n"
        #Line: Head
        msg += "│  " if session.mistakes_permitted <= 8 else "   "
        msg += "O" if session.mistakes_permitted <= 5 else " "
        msg += "   "
        for i, letter in enumerate(session.guessed_letters):
            if i % 3 == 0:
                msg += f"{letter} "
        msg += "\n"
        #Line: Torso
        msg += "│ " if session.mistakes_permitted <= 8 else "  "
        msg += "/" if session.mistakes_permitted <= 3 else " "
        msg += "│" if session.mistakes_permitted <= 4 else " "
        msg += "\\" if session.mistakes_permitted <= 2 else " "
        msg += "  "
        for i, letter in enumerate(session.guessed_letters):
            if i % 3 == 1:
                msg += f"{letter} "
        msg += "\n"
        #Line: Legs
        msg += "│ " if session.mistakes_permitted <= 8 else "  "
        msg += "/" if session.mistakes_permitted <= 1 else " "
        msg += " "
        msg += "\\" if session.mistakes_permitted <= 0 else " "
        msg += "  "
        for i, letter in enumerate(session.guessed_letters):
            if i % 3 == 2:
                msg += f"{letter} "
        msg += "\n"
        #Line: Floor
        msg += "└" if session.mistakes_permitted <= 8 else "╶" if session.mistakes_permitted <= 9 else " "
        msg += "────" if session.mistakes_permitted <= 9 else "    "
        msg += "\n"
        #Line: Word Guessed So Far
        for letter in session.secret_word:
            msg += f"{letter} " if letter in session.guessed_letters else "_ "
        msg += "```\n"
        if self.is_game_won(session) == True:
            if len(session.players) == 1:
                msg += f"{session.players[0].user.mention} has won!"
                return msg
            msg += "The players have won!"
            return msg
        if self.is_game_lost(session) == True:
            if len(session.players) == 1:
                msg += f"{session.players[0].user.mention} has lost. The word was `{session.secret_word}`."
                return msg
            msg += f"The players have lost. The word was `{session.secret_word}`."
            return msg
        msg += f"{session.players[session.player_turn].user.mention}'s turn!"
        return msg

    def get_dictionary_word(self):
        filename = WORDS_FILE
        if os.path.exists(filename):
            file = open(filename)
            wordlist = [word for word in file.read().split() if len(word) >= 4]
            file.close()
            secretword = random.choice(wordlist)
            return secretword
        return "Hangman"

    #Setup the initial variables and message(s) of the game.
    async def setup_game(self, session, channel):
        await Game.setup_game(self, session, channel)
        session.inactivity_timer_restart()
        session.shuffle_players()
        session.executioner = self.client.user #TODO: Let players be executioner.
        session.secret_word = self.get_dictionary_word().upper()
        msg = self.generate_board_message(session)
        session.message_board = await channel.send(msg)

    async def process_turn(self, session, letter):
        session.inactivity_timer_restart()
        session.guessed_letters.append(letter.upper())
        if self.is_game_won(session) == True or self.is_game_lost(session) == True:
            msg = self.generate_board_message(session)
            await session.message_board.edit(content=msg)
            self.remove_session(session)
            return
        session.next_turn()
        msg = self.generate_board_message(session)
        await session.message_board.edit(content=msg)

    #Handle additional checks required when a player joins the game.
    async def add_player(self, session, user):
        session.add_player(user)
        if session.message_board != None:
            msg = self.generate_board_message(session)
            await session.message_board.edit(content=msg)

    #Handle additional checks required when a player quits the game.
    async def remove_player(self, session, user):
        for i, player in enumerate(session.players):
            if player.user.id == user.id and i < session.player_turn:
                session.prev_turn()
                break
        session.remove_player(user)
        if session.message_board != None:
            if len(session.players) <= 0:
                await session.message_board.delete()
                self.remove_session(session)
                return
            msg = self.generate_board_message(session)
            await session.message_board.edit(content=msg)
            return
        if len(session.players) <= 0:
            self.remove_session(session)

    #Check if a guess is a single alphabetical character
    async def is_valid_guess(self, ctx, letter):
        if letter == None:
            msg = "Please specify a character to guess as `!hm guess X`"
            await ctx.channel.send(content=msg, delete_after=15.0)
            return False
        if letter.isalpha() == False:
            msg = "Please only guess alphabetic characters."
            await ctx.channel.send(content=msg, delete_after=15.0)
            return False
        if len(letter) != 1:
            msg = "Please only guess single characters."
            await ctx.channel.send(content=msg, delete_after=15.0)
            return False
        return True

    #Primary Functions
    #With no arguments specified, send game instructions.
    @commands.group(name="hangman", aliases=["hm"], case_insensitive=True, invoke_without_command=True)
    async def hangman(self, ctx):
        try:
            await send_help(ctx.channel.send, "hangman")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Help command to receive instructions.
    @hangman.command(aliases=["?", "info", "information", "instructions"])
    async def help(self, ctx):
        try:
            await send_help(ctx.channel.send, "hangman")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #See the list of players of a room.
    @hangman.command(aliases=["player", "players", "playerlist", "playerslist", "players_list", "list"])
    async def player_list(self, ctx, room_id=None):
        try:
            await Game.player_list(self, ctx, room_id)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Register a new game room.
    @hangman.command(aliases=["create", "register", "host"])
    async def new(self, ctx):
        try:
            session = HangmanSession(self)
            player = Player(ctx.author)
            await Game.new(self, ctx, session, player)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Join an existing game room by message.
    @hangman.command(aliases=["enter"])
    async def join(self, ctx, room_id=None):
        try:
            player = Player(ctx.author)
            await Game.join(self, ctx, room_id, player)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Start a game.
    @hangman.command(aliases=["begin"])
    async def start(self, ctx, room_id=None):
        try:
            await Game.start(self, ctx, room_id)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Quit a room.
    @hangman.command(aliases=["stop", "exit", "end", "leave"])
    async def quit(self, ctx, room_id=None):
        try:
            await Game.quit(self, ctx, room_id)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Guess a letter.
    @hangman.command(aliases=["letter", "char", "character"])
    async def guess(self, ctx, letter=None, room_id=None):
        try:
            if await self.is_valid_guess(ctx, letter) == False:
                return
            room_id = await self.get_room_id(ctx, room_id)
            if room_id == None:
                return
            for session in self.game_sessions:
                if room_id.upper() == session.room_id:
                    if not any(ctx.author.id == player.user.id for player in session.players):
                        msg = f"You are not in {self.game_name} room {session.room_id}."
                        await ctx.channel.send(content=msg, delete_after=15.0)
                        return
                    if ctx.author.id != session.players[session.player_turn].user.id:
                        msg = "It is not your turn."
                        await ctx.channel.send(content=msg, delete_after=15.0)
                        return
                    if letter.upper() in session.guessed_letters:
                        msg = f"Character {letter.upper()} was already guessed, please try again."
                        await ctx.channel.send(content=msg, delete_after=15.0)
                        await ctx.message.delete()
                        return
                    await self.process_turn(session, letter)
                    await ctx.message.delete()
                    return
            msg = f"{self.game_name} room {room_id} not found."
            await ctx.channel.send(content=msg, delete_after=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Edit a room's settings.
    @hangman.group(name="setting", aliases=["set", "settings", "edit", "mod", "modify", "rule", "rules"], case_insensitive=True, invoke_without_command=True)
    async def setting(self, ctx, room_id=None):
        try:
            #With no arguments specified, send setting instructions.
            if room_id == None:
                msg = "**Hangman Settings**\n"
                msg += "Several settings can be edited to suit the desired play experience. In each setting below, YY is to be replaced with a number, and XXXX with the room ID of the room you are changing settings for.\n"
                msg += "`!hm set XXXX`: See the current settings for a room.\n"
                msg += "`!hm set players YY XXXX`: The maximum amount of players that can join. Default is 6.\n"
                msg += "`!hm set mistakes YY XXXX`: The amount of wrong guesses that players can make. Default is 6."
                await ctx.channel.send(msg)
                return
            #With only a room ID specified, show current settings for the room.
            for session in self.game_sessions:
                if room_id.upper() == session.room_id:
                    msg = f"**Hangman Room {session.room_id} Settings**\n"
                    msg += f"Maximum Players: {session.max_players}\n"
                    msg += f"Maximum Mistakes: {session.max_mistakes}"
                    await ctx.channel.send(msg)
                    return
            msg = f"Hangman setting or room {room_id} not found."
            await ctx.channel.send(content=msg, delete_after=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Change the amount of players that can join a game.
    @setting.command(aliases=["player", "players", "maxplayer", "maxplayers", "max_player", "max_players", "playercount", "player_count", "totalplayers", "total_players"])
    async def set_max_players(self, ctx, max_players=None, room_id=None):
        try:
            return_value = await Game.set_new_value_positive(self, ctx, max_players, room_id)
            if return_value == None:
                return
            for session in self.game_sessions:
                if room_id.upper() == session.room_id:
                    session.max_players = return_value
                    msg = f"Maximum amount of players for {self.game_name} room {session.room_id} set to {return_value}."
                    await ctx.channel.send(content=msg, delete_after=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    #Change the amount of mistakes players can make.
    @setting.command(aliases=["mistake", "mistakes", "maxmistake", "maxmistakes", "max_mistake", "max_mistakes", "mistakecount", "mistake_count", "totalmistakes", "total_mistakes"])
    async def set_max_mistakes(self, ctx, max_mistakes=None, room_id=None):
        try:
            return_value = await Game.set_new_value_positive(self, ctx, max_mistakes, room_id)
            if return_value == None:
                return
            for session in self.game_sessions:
                if room_id.upper() == session.room_id:
                    session.max_mistakes = return_value
                    msg = f"Maximum amount of mistakes for {self.game_name} room {session.room_id} set to {return_value}."
                    await ctx.channel.send(content=msg, delete_after=15.0)
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
        except Exception as e:
            await send_error(self.client, e, reference=reaction.message.jump_url)

    @hangman.command()
    async def print_cache(self, ctx):
        Game.print_cache(self)

#Client Setup
async def setup(client):
    await client.add_cog(HangmanCog(client))
