#Import Modules
import discord
from discord.ext import commands
import random
import os
import datetime

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
        self.game_highscore = [] #High score. Points first, then record holder name.

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
        for index, entry in enumerate(self.game_playerpoints): #Find, retrieve and delete player's points
            if entry == player:
                del self.game_playerpoints[index]
                del self.game_playerpoints[index]
                break

    #Define get_highscore():
    def get_highscore(self):
        with open("musa_mastermind_highscore.txt", "r") as file_score:
            self.game_highscore = file_score.readlines()
            self.game_highscore[0] = self.game_highscore[0].rstrip()

    #Define check_new_highscore():
    def check_new_highscore(self):
        if self.game_points > int(self.game_highscore[0]):
            return True
        else:
            return False

    #Define set_new_highscore(points, player):
    def set_new_highscore(self, points, player):
        with open("musa_mastermind_highscore.txt", "w") as file_score:
            file_score.write("{}\n{}".format(str(points), player))

    #Define generate_secret_code():
    def generate_secret_code(self):
        self.game_secretcode = []
        for _ in range(4):
            self.game_secretcode.append(random.randint(0, 9))

    ##New Game
    @commands.command(aliases=["mm"])
    async def mastermind(self, ctx, action):
        if action == "new" or action == "newgame" or action == "game" or action == "start" or action == "begin":
            player = ctx.author.id
            for entry in self.game_players: #Iterate over all active players
                if entry == player:
                    player = 0
                    break
            if player != 0: #Set up new game for new player
                self.game_players.append(player)
                self.generate_secret_code()
                self.game_playercodes.append(player)
                self.game_playercodes.append(self.game_secretcode)
                self.game_playerrounds.append(player)
                self.game_playerrounds.append(1)
                self.game_playerpoints.append(player)
                self.game_playerpoints.append(0)
                await ctx.channel.send("New game started. Guess the code by typing `!mm ####` with digits in place of the `#`s.\n__Round 1:__")
                if ctx.guild == None:
                    print(f"{datetime.datetime.now()} - Mastermind room started in DMs by {ctx.author.name}.")
                else:
                    print(f"{datetime.datetime.now()} - Mastermind room started in {ctx.guild.name} by {ctx.author.name}.")
            else: #Player is already in game
                await ctx.channel.send("You're already in a game. End it with `!mm quit` to restart.")

    ##Help
        elif action == "help" or action == "?":
            await ctx.channel.send("**Mastermind Help:**\nIn this game, it is your job to deduce a secret four-digit code by guessing four-digit codes. Your only hint to the correct code is feedback on which guessed digits are in the secret code, and how many of those are in the correct position. The same digit can appear multiple times. You have {} rounds to guess the secret code. The game continues until you're out of rounds. The rounds get reset when you guess the code, and a new code gets generated. Try to get the high score!\n__Commands:__\n`!mm new`: Start a new game.\n`!mm quit`: Ends your game early.\n`!mm highscore`: Displays current high score.\n`!mm ####`: Guess codes by typing four digits in place of the `#`s.".format(self.game_maxrounds))

    ##Display High Score
        elif action == "highscore" or action == "hiscore" or action == "high score" or action == "high" or action == "score" or action == "points":
            self.get_highscore()
            await ctx.channel.send("**High Score:**\n{} points by {}".format(self.game_highscore[0], self.game_highscore[1]))

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
                self.get_highscore()
                if self.check_new_highscore():
                    await ctx.channel.send("**New High Score!**".format(self.game_points))
                    self.set_new_highscore(self.game_points, ctx.author.name)
            else:
                await ctx.channel.send("You're not in a game. Start one with `!mm new`")

    ##Guessing
        elif self.check_valid_guess(action):
            player = ctx.author.id #Check if author is actually playing
            areyouplaying = False
            for entry in self.game_players:
                if entry == player:
                    areyouplaying = True
                    break
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
                    self.get_highscore()
                    if self.check_new_highscore():
                        await ctx.channel.send("**New High Score!**".format(self.game_points))
                        self.set_new_highscore(self.game_points, ctx.author.name)
            else:
                await ctx.channel.send("You're not in a game. Start one with `!mm new`")

    ##Invalid Command
        else:
            await ctx.channel.send("Invalid guess or command.")

    @commands.command()
    async def mastermind_print_cache(self, ctx):
        print(f"mm: {self.game_playerpoints}")

def setup(client):
    client.add_cog(Mastermind(client))
