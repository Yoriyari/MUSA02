#===============================================================================
# Mastermind v1.3.2
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.3.2; Moved database to secrets folder. -YY
# 02 May 2024 - v1.3.1; Reworked help message import and error handling. -YY
# 20 Nov 2023 - v1.3; Added lifetime scores with leaderboard. -YY
# 19 Nov 2023 - v1.2; Added global leaderboard and personal highscores. Added
#               persistent score memory for ongoing games across reboots. -YY
# 17 Apr 2022 - v1.1; Centralized help messages to one importable file. -YY
# 04 May 2020 - v1.0; Finished file. -YY
# 28 Apr 2020 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Rewrite to utilize command infrastructure instead of parameter strings. -YY
# - Allow players to guess just a four-digit code without preceding command. -YY
#===============================================================================
# Description
# ..............................................................................
# mastermind.py plays a one-player game of Mastermind. A four-digit code is
# generated and the player must guess it within ten guesses, only getting the
# feedback of how many digits were in the code and in the correct position.
# Score is awarded relative to how few guesses it took and we keep a leaderboard
# for best streak and highest lifetime score.
#===============================================================================

#Import Modules
import discord
from discord import ui
from discord.ext import commands

from common.json_handling import write_to_json, read_from_json
from common.error_message import send_error
from common.help_message import send_help

import random
import os
import datetime

scores_file = "secrets/mastermind_scores.json"
view_timeout = 86400 # 24 hours

#-------------------------------------------------------------------------------

#Auxiliary functions
def save_active_game(id, name, score):
    '''Saves ongoing scores to disk. Updates username.
    '''
    id = str(id)
    scores = read_from_json(scores_file)
    if id not in scores:
        scores[id] = {"high_score": 0, "current_score": score, "name": name, "lifetime_score": 0}
    else:
        scores[id]["current_score"] = score
        scores[id]["name"] = name
    write_to_json(scores_file, scores)

def end_active_game(id):
    '''Sets the high score to the current score and resets the current score
    to zero.
    '''
    id = str(id)
    scores = read_from_json(scores_file)
    if id not in scores:
        scores[id] = {"high_score": 0, "current_score": 0, "name": name, "lifetime_score": 0}
    else:
        if "lifetime_score" not in scores[id]:
            scores[id]["lifetime_score"] = scores[id]["high_score"]
        if scores[id]["high_score"] < scores[id]["current_score"]:
            scores[id]["high_score"] = scores[id]["current_score"]
        scores[id]["lifetime_score"] += scores[id]["current_score"]
        scores[id]["current_score"] = 0
    write_to_json(scores_file, scores)

def check_personal_best(id):
    '''Checks if someone's current score is greater than their high score.
    '''
    id = str(id)
    scores = read_from_json(scores_file)
    if id not in scores:
        return False
    if scores[id]["current_score"] > scores[id]["high_score"]:
        return True
    return False

def get_current_score(id):
    '''Returns the current score of the specified user.
    '''
    id = str(id)
    scores = read_from_json(scores_file)
    if id not in scores:
        return 0
    if "current_score" not in scores[id]:
        return 0
    return scores[id]["current_score"]

def get_highscore():
    '''Returns the highest high_score integer from disk.
    '''
    scores = read_from_json(scores_file)
    hiscore = 0
    for entry in scores.values():
        score = entry["high_score"]
        if score > hiscore:
            hiscore = score
    return hiscore

def generate_highscores_message():
    '''Returns a string giving the top ten users' high scores.
    '''
    scores = read_from_json(scores_file)
    leaderboard = []
    for entry in scores.values():
        score = max(entry["high_score"], entry["current_score"])
        new_slot = {"name": entry["name"], "score": score}
        leaderboard = insert_leaderboard_slot_in_sorted_position(leaderboard, new_slot)
    msg = "**Top 10 Mastermind High Scores**"
    msg += generate_leaderboard_listing(leaderboard)
    return msg

def generate_lifetime_scores_message():
    '''Returns a string giving the top ten users' lifetime scores.
    '''
    scores = read_from_json(scores_file)
    leaderboard = []
    for entry in scores.values():
        if "lifetime_score" in entry:
            score = entry["lifetime_score"] + entry["current_score"]
        else:
            score = entry["high_score"] + entry["current_score"]
        new_slot = {"name": entry["name"], "score": score}
        leaderboard = insert_leaderboard_slot_in_sorted_position(leaderboard, new_slot)
    msg = "**Top 10 Mastermind Lifetime Scores**"
    msg += generate_leaderboard_listing(leaderboard)
    return msg

def insert_leaderboard_slot_in_sorted_position(leaderboard, new_slot, max_size=10):
    '''Returns the given leaderboard with new_slot inserted above the first
    slot it finds to be of lower score. Optionally specify max_size to limit
    the maximum slots on the leaderboard, or set to None for no limit.
    Default leaderboard size is 10.
    '''
    for i, slot in enumerate(leaderboard):
        if max_size != None and i >= max_size:
            return leaderboard
        if new_slot["score"] > slot["score"]:
            leaderboard.insert(i, new_slot)
            return slice_list_to_size(leaderboard, max_size)
    leaderboard.append(new_slot)
    return slice_list_to_size(leaderboard, max_size)

def slice_list_to_size(list, size):
    '''Returns the given list sliced to the given size.
    '''
    if len(list) > size:
        return list[:size]
    return list

def generate_leaderboard_listing(leaderboard):
    '''Returns a Discord code listing of the supplied leaderboard array.
    '''
    msg = "```\n"
    largest_num_len = len(str(leaderboard[0]["score"]))
    for slot in leaderboard:
        current_num_len = len(str(slot["score"]))
        msg += " " * (largest_num_len-current_num_len)
        msg += f"{slot['score']} │ {slot['name']}\n"
    msg += "```"
    return msg

#-------------------------------------------------------------------------------

#Cog Setup
class Mastermind(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.game_players = [] #Players running an active game.
        self.game_points = 0 #Points total for current game.
        self.game_round = 1 #Current guessing round.
        self.game_maxrounds = 10 #Maximum amount of guesses before you lose the game.
        self.game_secretcode = [] #The code you have to guess each round.
        self.game_lastguess = [] #Most recent code guess.
        self.game_playercodes = [] #Collection of player IDs with their current secret codes.
        self.game_playerrounds = [] #Collection of player IDs with their current guessing round.
        self.game_playerpoints = [] #Collection of player IDs with their current game score.

    @commands.Cog.listener()
    async def on_ready(self):
        print("Mastermind cog loaded.")

    #Define check_valid_guess(guess)
    def check_valid_guess(self, action):
        if len(action) != 4:
            return False
        self.game_lastguess = list(action)
        for index, entry in enumerate(self.game_lastguess):
            if entry.isdecimal() == False:
                return False
            self.game_lastguess[index] = int(entry)
        return True

    #Define end_game(player)
    def end_game(self, player):
        for index, entry in enumerate(self.game_playercodes): #Find and delete player's codes
            if entry == player:
                del self.game_playercodes[index]
                del self.game_playercodes[index]
                break
        for index, entry in enumerate(self.game_playerrounds): #Find and delete player's rounds
            if entry == player:
                del self.game_playerrounds[index]
                del self.game_playerrounds[index]
                break
        for index, entry in enumerate(self.game_playerpoints): #Find, retrieve and delete player's points. And update the saved high score.
            if entry == player:
                del self.game_playerpoints[index]
                del self.game_playerpoints[index]
                break

    #Define check_new_highscore():
    def check_new_highscore(self):
        hiscore = get_highscore()
        if self.game_points > hiscore:
            return True
        else:
            return False

    #Define generate_secret_code():
    def generate_secret_code(self):
        self.game_secretcode = []
        for _ in range(4):
            self.game_secretcode.append(random.randint(0, 9))

    def setup_game(self, user_id, score):
        '''Sets up the architecture for a new active game for a given user.
        '''
        self.game_players.append(user_id)
        self.generate_secret_code()
        self.game_playercodes.append(user_id)
        self.game_playercodes.append(self.game_secretcode)
        self.game_playerrounds.append(user_id)
        self.game_playerrounds.append(1)
        self.game_playerpoints.append(user_id)
        self.game_playerpoints.append(score)

    ##New Game
    @commands.command(aliases=["mm"])
    async def mastermind(self, ctx, action=""):
        try:
            if action == "new" or action == "newgame" or action == "game" or action == "start" or action == "begin":
                player = ctx.author.id
                if player in self.game_players:
                    score = get_current_score(player)
                    if score > 0:
                        self.setup_game(player, score)
                        await ctx.channel.send("Recovered score from an unfinished game prior to bot reboot. New game started with old score.\n__Round 1:__")
                    player = 0
                if player != 0: #Set up new game for new player
                    self.setup_game(player, 0)
                    await ctx.channel.send("New game started. Guess the code by typing `!mm ####` with digits in place of the `#`s.\n__Round 1:__")
                    if ctx.guild == None:
                        print(f"{datetime.datetime.now()} - Mastermind room started in DMs by {ctx.author.name}.")
                    else:
                        print(f"{datetime.datetime.now()} - Mastermind room started in {ctx.guild.name} by {ctx.author.name}.")
                else: #Player is already in game
                    await ctx.channel.send("You're already in a game. End it with `!mm quit` to restart.")

        ##Help
            elif action == "help" or action == "?":
                await send_help(ctx.channel.send, "mastermind")

        ##Display High Score
            elif action == "highscore" or action == "hiscore" or action == "high" or action == "score" or action == "points" or action == "highscores" or action == "hiscores" or action == "scores" or action == "leaderboard" or action == "leaderboards" or action == "high_score" or action == "high_scores" or action == "hi_score" or action == "hi_scores" or action == "lifetime" or action == "lifetimescore" or action == "lifetimescores" or action == "lifetime_score" or action == "lifetime_scores":
                msg = generate_highscores_message()
                view = ViewMM(page=0)
                await ctx.channel.send(msg, view=view)

        ##Quit Game
            elif action == "quit" or action == "stop" or action == "exit" or action == "leave" or action == "end" or action == "done":
                player = ctx.author.id
                areyouplaying = False
                for index, entry in enumerate(self.game_players): #Find and delete player ID
                    if entry == player:
                        del self.game_players[index]
                        areyouplaying = True
                        break
                if areyouplaying:
                    for index, entry in enumerate(self.game_playerpoints): #Retrieve final score
                        if entry == player:
                            self.game_points = self.game_playerpoints[index+1]
                    self.end_game(player)
                    await ctx.channel.send("Game quit. Final Score: {} points.".format(self.game_points))
                    msg = ""
                    if check_personal_best(player):
                        msg += "**New Personal Best!** "
                    if self.check_new_highscore():
                        msg += "**New High Score!**"
                    if msg != "":
                        await ctx.channel.send(msg)
                    save_active_game(ctx.author.id, ctx.author.name, self.game_points)
                    end_active_game(ctx.author.id)
                else:
                    await ctx.channel.send("You're not in a game. Start one with `!mm new`")

        ##Just !mm
            elif action == "":
                player = ctx.author.id #Check if author is actually playing
                for entry in self.game_players:
                    if entry == player:
                        await ctx.channel.send("Invalid guess or command.")
                        return
                await ctx.channel.send("You're not in a game. Start one with `!mm new`")

        ##Guessing
            elif self.check_valid_guess(action):
                player = ctx.author.id #Check if author is actually playing
                areyouplaying = False
                if player in self.game_players:
                    areyouplaying = True
                else:
                    score = get_current_score(player)
                    if score > 0:
                        self.setup_game(player, score)
                        await ctx.channel.send("Recovered score from an unfinished game prior to bot reboot. New game started with old score.")
                        areyouplaying = True
                if areyouplaying: #Retrieve secret code for this particular player
                    for index, entry in enumerate(self.game_playercodes):
                        if entry == player:
                            self.game_secretcode = self.game_playercodes[index+1].copy()
                    inplaces = 0 #Calculate how correct the guess was
                    outofplaces = 0
                    for index, entry in enumerate(self.game_lastguess):
                        if entry == self.game_secretcode[index]:
                            inplaces += 1
                            self.game_secretcode[index] = 10
                            self.game_lastguess[index] = 11
                            continue
                    for index, entry in enumerate(self.game_lastguess):
                        for position, value in enumerate(self.game_secretcode):
                            if value == entry:
                                outofplaces += 1
                                self.game_secretcode[position] = 10
                                break
                    for index, entry in enumerate(self.game_playerrounds): #Retrieve rounds and score for this particular player
                        if entry == player:
                            self.game_round = self.game_playerrounds[index+1]
                    for index, entry in enumerate(self.game_playerpoints):
                        if entry == player:
                            self.game_points = self.game_playerpoints[index+1]
                    if inplaces == 4: #Feedback on correct guess
                        self.game_points += (self.game_maxrounds - self.game_round + 1)
                        save_active_game(ctx.author.id, ctx.author.name, self.game_points)
                        await ctx.channel.send("Correct! You cracked the code in {} rounds!\nCurrent Score: {} points.\nGenerating new code.\n__Round 1:__".format(self.game_round, self.game_points))
                        self.game_round = 1
                        self.generate_secret_code()
                        for index, entry in enumerate(self.game_playercodes): #Store new code, round and score (when correct)
                            if entry == player:
                                self.game_playercodes[index+1] = self.game_secretcode
                        for index, entry in enumerate(self.game_playerrounds):
                            if entry == player:
                                self.game_playerrounds[index+1] = self.game_round
                        for index, entry in enumerate(self.game_playerpoints):
                            if entry == player:
                                self.game_playerpoints[index+1] = self.game_points
                    elif self.game_round < self.game_maxrounds: #Feedback on wrong guess
                        self.game_round += 1
                        await ctx.channel.send(":red_circle: {} numbers in the correct position.\n:yellow_circle: {} numbers in code, but out of position.\nGuess again!\n__Round {}:__".format(inplaces, outofplaces, self.game_round))
                        for index, entry in enumerate(self.game_playerrounds): #Store new round (when incorrect)
                            if entry == player:
                                self.game_playerrounds[index+1] = self.game_round
                    else: #Wrong guess and exceeding maximum guesses
                        for index, entry in enumerate(self.game_playerpoints): #Retrieve final code and score
                            if entry == player:
                                self.game_points = self.game_playerpoints[index+1]
                        for index, entry in enumerate(self.game_playercodes):
                            if entry == player:
                                self.game_secretcode = self.game_playercodes[index+1].copy()
                                self.game_lastguess = [str(integ) for integ in self.game_secretcode]
                                self.game_secretcode = "".join(self.game_lastguess)
                        for index, entry in enumerate(self.game_players): #Find and delete player ID
                            if entry == player:
                                del self.game_players[index]
                                break
                        self.end_game(player)
                        await ctx.channel.send(":red_circle: {} numbers in the correct position.\n:yellow_circle: {} numbers in code, but out of position.\nYou're out of guesses! The code was {}. Thanks for playing!\nFinal Score: {} points.".format(inplaces, outofplaces, self.game_secretcode, self.game_points))
                        save_active_game(ctx.author.id, ctx.author.name, self.game_points)
                        msg = ""
                        if check_personal_best(player):
                            msg += "**New Personal Best!** "
                        if self.check_new_highscore():
                            msg += "**New High Score!**"
                        if msg != "":
                            await ctx.channel.send(msg)
                        end_active_game(ctx.author.id)
                else:
                    await ctx.channel.send("You're not in a game. Start one with `!mm new`")

        ##Invalid Command
            else:
                await ctx.channel.send("Invalid guess or command.")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.command()
    async def mastermind_print_cache(self, ctx):
        print(f"mm: {self.game_playerpoints}")

#-------------------------------------------------------------------------------

class ViewMM(ui.View):
    def __init__(self, page=None):
        super().__init__(timeout=view_timeout)
        self.add_item(ButtonHigh(disabled=(page==0)))
        self.add_item(ButtonLifetime(disabled=(page==1)))

class ButtonHigh(ui.Button):
    def __init__(self, disabled):
        super().__init__(label="High Scores", style=discord.ButtonStyle.blurple, disabled=disabled)
    async def callback(self, interaction):
        '''Turns the interaction message into the high scores leaderboard.
        '''
        try:
            msg = generate_highscores_message()
            view = ViewMM(page=0)
            await interaction.response.edit_message(content=msg, view=view)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonLifetime(ui.Button):
    def __init__(self, disabled):
        super().__init__(label="Lifetime Scores", style=discord.ButtonStyle.blurple, disabled=disabled)
    async def callback(self, interaction):
        '''Turns the interaction message into the high scores leaderboard.
        '''
        try:
            msg = generate_lifetime_scores_message()
            view = ViewMM(page=1)
            await interaction.response.edit_message(content=msg, view=view)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

async def setup(client):
    await client.add_cog(Mastermind(client))
