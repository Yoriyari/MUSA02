#===============================================================================
# Game v1.0.3
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 18 Sep 2021 - v1.0.3; Games now assume room ID if player doesn't specify but
#               they're in only one room. Settings code has been more
#               generalized. -YY
# 02 Jun 2021 - v1.0.2; Added support for inactivity timer of sessions. -YY
# 25 May 2021 - v1.0.1; Added add_player to support checks on player join. -YY
# 23 May 2021 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Make it possible to opt into a new match in the same room after a game. -YY
#===============================================================================
# Description
# ..............................................................................
# game.py contains the Game class, used for most general features shared across
# the bot's games.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands
import datetime

#Cog Class
class Game(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.game_sessions = []
        self.instant_start = False
        self.game_name = "Game"
        self.game_abbrev = "game"

    #Report successful load.
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.game_name} cog loaded.")

    #Get maximum amount of players of a session. Override if needed.
    def get_max_players(self, session):
        return 0

    #Get minimum amount of players of a session. Override if needed.
    def get_min_players(self, session):
        return 0

    #Check whether a game has started yet. Override if needed.
    def has_game_started(self, session):
        return False

    def print_cache(self):
        print(f"{self.game_abbrev}: {self.game_sessions}")

    #Setup the initial variables and message(s) of the game. Override if needed.
    async def setup_game(self, session, channel):
        session.inactivity_timer_change_interval(60.0)

    #Handle additional checks required when a player joins the game. Override if needed.
    async def add_player(self, session, user):
        session.inactivity_timer_restart()
        session.add_player(user)

    #Handle additional checks required when a player quits the game. Override if needed.
    async def remove_player(self, session, user):
        session.remove_player(user)

    #Remove session on inactivity timeout. Override if needed.
    async def timeout_session(self, session):
        if session.message_join != None:
            msg = f"{self.game_name} room {session.room_id} has timed out due to inactivity."
            await session.message_join.edit(content=msg)
            await session.message_join.clear_reactions()
        self.game_sessions.remove(session)

    #Remove session for reasons other than timeout.
    def remove_session(self, session):
        session.inactivity_timer_cancel()
        self.game_sessions.remove(session)

    #Return the names of users in a game room.
    async def player_list(self, ctx, room_id):
        #In case of no room ID specified.
        if room_id == None:
            msg = f"Please specify a room ID to see its players as `!{self.game_abbrev} players XXXX`"
            await ctx.channel.send(content=msg, delete_after=15.0)
            return
        #Return player list of specified room.
        for session in self.game_sessions:
            if room_id.upper() == session.room_id:
                msg = f"**{self.game_name} Room {session.room_id} Players:** "
                for i, player in enumerate(session.players):
                    if i:
                        msg += ", "
                    msg += f"{player.user.name}"
                await ctx.channel.send(msg)
                return
        msg = f"{self.game_name} room {room_id} not found."
        await ctx.channel.send(msg)

    #Get room without having to specify room ID, if user is in a single room, or report error if they're not
    async def get_room_id(self, ctx, room_id):
        if room_id != None:
            return room_id
        for session in self.game_sessions:
            if ctx.author.id in [player.user.id for player in session.players]:
                if room_id == None:
                    room_id = session.room_id
                else:
                    msg = f"You are in multiple {self.game_name} rooms. Please specify a room ID by adding it to the end of your command."
                    await ctx.channel.send(content=msg, delete_after=15.0)
                    return None
        if room_id == None:
            msg = f"You are not in any {self.game_name} rooms."
            await ctx.channel.send(content=msg, delete_after=15.0)
            return None
        return room_id

    #Register a new game room.
    async def new(self, ctx, session, player):
        await self.add_player(session, player)
        self.game_sessions.append(session)
        #Send session's room ID
        msg = f"New {self.game_name} room created! Your room ID is: {session.room_id}.\n"
        if self.instant_start == False:
            msg += f"The game can be started typing `!{self.game_abbrev} start`\n"
        msg += f"Others can join by typing `!{self.game_abbrev} join {session.room_id}`"
        if ctx.guild != None:
            msg += " or by reacting to this message with ▶️."
            session.message_join = await ctx.channel.send(msg)
            await session.message_join.add_reaction("▶️")
            return
        await ctx.channel.send(msg)

    #Join an existing game room.
    async def join(self, ctx, room_id, player):
        #In case of joining through DMs.
        if ctx.guild == None and self.instant_start == True:
            msg = "Please join the game in a public channel."
            await ctx.channel.send(content=msg, delete_after=15.0)
            return
        #In case of no room ID specified.
        if room_id == None:
            msg = f"Please specify a room ID to join as `!{self.game_abbrev} join XXXX`"
            await ctx.channel.send(content=msg, delete_after=15.0)
            return
        #Attempt to join room.
        msg = f"{self.game_name} room {room_id} does not exist."
        for session in self.game_sessions:
            if room_id.upper() == session.room_id:
                #Check if player is already in room
                if any(active_player.user.id == player.user.id for active_player in session.players):
                    msg = f"{player.user.name} is already in {self.game_name} room {session.room_id}!"
                    break
                #Check if room is full
                max_players = self.get_max_players(session)
                if max_players > 0 and len(session.players) >= max_players:
                    msg = f"{self.game_name} room {session.room_id} is full."
                    break
                #Add player to room
                await self.add_player(session, player)
                if self.instant_start == True:
                    await self.setup_game(session, ctx.channel)
                    return
                msg = f"{player.user.name} joined {self.game_name} room {session.room_id}!"
                await ctx.channel.send(msg)
                return
        await ctx.channel.send(content=msg, delete_after=15.0)

    #Start a game.
    async def start(self, ctx, room_id):
        #In case of trying to start game in DMs.
        if self.instant_start == True:
            msg = f"{self.game_name} starts automatically when enough players join."
            await ctx.channel.send(content=msg, delete_after=15.0)
            return
        if ctx.guild == None:
            msg = "Please start the game in a public channel."
            await ctx.channel.send(content=msg, delete_after=15.0)
            return
        #In case of no room ID specified.
        room_id = await self.get_room_id(ctx, room_id)
        if room_id == None:
            return
        #Start game in specified room ID.
        msg = f"{self.game_name} room {room_id} not found."
        for session in self.game_sessions:
            if room_id.upper() == session.room_id:
                #Check if player is in room
                if any(ctx.author.id == player.user.id for player in session.players):
                    #Check if room has enough players
                    min_players = self.get_min_players(session)
                    if min_players > 0 and len(session.players) < min_players:
                        msg = f"{self.game_name} room {session.room_id} does not have enough players to start."
                        break
                    await self.setup_game(session, ctx.channel)
                    if ctx.guild == None:
                        print(f"{datetime.datetime.now()} - {self.game_name} room started in DMs by {ctx.author.name}.")
                    else:
                        print(f"{datetime.datetime.now()} - {self.game_name} room started in {ctx.guild.name} by {ctx.author.name}.")
                    return
                msg = f"You are not in {self.game_name} room {session.room_id}."
                break
        await ctx.channel.send(content=msg, delete_after=15.0)

    #Quit an existing room the player is in.
    async def quit(self, ctx, room_id):
        #In case of no room ID specified
        room_id = await self.get_room_id(ctx, room_id)
        if room_id == None:
            return
        #Quit all rooms a player is in.
        if room_id.lower() in ["all", "every", "everything"]:
            rooms_quit = 0
            for session in reversed(self.game_sessions):
                if any(ctx.author.id == player.user.id for player in session.players):
                    rooms_quit += 1
                    await self.remove_player(session, ctx.author)
            msg = f"{ctx.author.name} is not in any {self.game_name} rooms."
            if rooms_quit > 0:
                msg = f"Removed {ctx.author.name} from {rooms_quit} {self.game_name} room(s)."
            await ctx.channel.send(content=msg, delete_after=15.0)
            return
        #Quit a specific room
        msg = f"{self.game_name} room {room_id} not found."
        for session in self.game_sessions:
            if room_id.upper() == session.room_id:
                if any(ctx.author.id == player.user.id for player in session.players):
                    await self.remove_player(session, ctx.author)
                    msg = f"Removed {ctx.author.name} from {self.game_name} room {session.room_id}."
                    break
                msg = f"{ctx.author.name} is not in {self.game_name} room {session.room_id}."
                break
        await ctx.channel.send(content=msg, delete_after=15.0)
        return

    #Perform checks for setting changes that require a positive integer.
    async def set_new_value_positive(self, ctx, new_value, room_id):
        #In case of no room ID specified.
        room_id = await self.get_room_id(ctx, room_id)
        if room_id == None:
            return None
        #Check if value was supplied
        if new_value == None:
            msg = f"Please specify a new setting value to set."
            await ctx.channel.send(content=msg, delete_after=15.0)
            return None
        #Check if a positive integer was supplied.
        if new_value.isdigit() == False or int(new_value) <= 0:
            msg = "Please specify a positive integer as new setting value."
            await ctx.channel.send(content=msg, delete_after=15.0)
            return None
        #Check if settings can be changed in room.
        msg = f"{self.game_name} room {room_id} not found."
        for session in self.game_sessions:
            if room_id.upper() == session.room_id:
                if any(ctx.author.id == player.user.id for player in session.players):
                    if self.has_game_started(session) == True:
                        msg = "Cannot change settings after game has started."
                        break
                    return int(new_value)
                msg = f"You are not in {self.game_name} room {session.room_id}."
                break
        await ctx.channel.send(content=msg, delete_after=15.0)
        return None

    #Perform checks for setting changes that require an integer between 0-12 inclusive.
    async def set_new_value_within12(self, ctx, new_value, room_id):
        return_value = await self.set_new_value_positive(ctx, new_value, room_id)
        if return_value != None:
            #Check if an integer between 0-12 was supplied.
            if new_value.isdigit() == False or int(new_value) <= 0 or int(new_value) >= 12:
                msg = "Please specify an integer between 0 and 12 as new setting value."
                await ctx.channel.send(content=msg, delete_after=15.0)
                return None
        return return_value
