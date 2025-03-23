#===============================================================================
# Cards Against Humanity v1.1.3
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.1.3; Backed up and removed the Gang Plays friends deck. -YY
# 20 Mar 2025 - v1.1.2; Made strings with escape characters raw strings. -YY
# 02 May 2024 - v1.1.1; Reworked help message import. Added error handling. -YY
# 17 Apr 2022 - v1.1; Centralized help messages to one importable file. -YY
# 09 Jan 2021 - v1.0; Finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Update for concurrent games. Currently supports only a single game. -YY
# - Update command infrastructure. -YY
# - Separate decks into a database instead of a huge hardcoded array. -YY
#===============================================================================
# Description
# ..............................................................................
# cah.py plays a game of Cards Against Humanity.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.error_message import send_error
from common.help_message import send_help

 #from asyncio import gather
import random

#Cog Setup
class CAH(commands.Cog):

    def __init__(self,client):
        self.client = client
        self.deck_blacks = [] #Black Cards, the ones prompting player input.
        self.deck_whites = [] #White Cards, the ones players answer with.
        self.emojis = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        self.game_blacks = [] #For copying the black base deck and shuffling.
        self.game_whites = [] #For copying the white base deck and shuffling.
        self.game_discards = [] #Discard pile of white cards, in case they run out.
        self.game_hands = [] #Lists containing the player Member type and the cards List type they've drawn.
        self.game_players = [] #Players' Member types.
        self.game_handmessages = [] #Player hand Message types collection.
        self.game_blackmessages = [] #Player's black card Message types collection.
        self.game_whitepicks = [] #Lists containing the player Member type and chosen white card String type.
        self.game_score = [] #Lists containing the player Member type and their score Integer type.
        self.game_scoremessages = [] #Player's score Message types collection.
        self.game_emojipicks = [] #For preventing picking the same card, but allowing duplicates. If it works right.
        self.game_handsize = 10 #Amount of white cards a player gets.
        self.game_round = 1 #Round number.
        self.game_threshold = 8 #Points threshold for winning.
        self.game_queue = 0 #Amount of players that have yet to respond.
        self.turn_preczar = False #Whether it's the player white card-picking turn right before czar.
        self.turn_czar = False #Whether it's the czar's turn to pick their favourite white card.

    def number_emoji(self, argument):
        if argument == 0:
            return "0️⃣"
        if argument == 1:
            return "1️⃣"
        if argument == 2:
            return "2️⃣"
        if argument == 3:
            return "3️⃣"
        if argument == 4:
            return "4️⃣"
        if argument == 5:
            return "5️⃣"
        if argument == 6:
            return "6️⃣"
        if argument == 7:
            return "7️⃣"
        if argument == 8:
            return "8️⃣"
        if argument == 9:
            return "9️⃣"

    def emoji_number(self, argument):
        if argument == "0️⃣":
            return 0
        if argument == "1️⃣":
            return 1
        if argument == "2️⃣":
            return 2
        if argument == "3️⃣":
            return 3
        if argument == "4️⃣":
            return 4
        if argument == "5️⃣":
            return 5
        if argument == "6️⃣":
            return 6
        if argument == "7️⃣":
            return 7
        if argument == "8️⃣":
            return 8
        if argument == "9️⃣":
            return 9

    def reset_game(self):
        self.game_round = 1
        self.deck_blacks = []
        self.deck_whites = []
        self.game_blacks = []
        self.game_whites = []
        self.game_discards = []
        self.game_hands = []
        self.game_players = []
        self.game_handmessages = []
        self.game_blackmessages = []
        self.game_whitepicks = []
        self.game_score = []
        self.game_scoremessages = []
        self.game_emojipicks = []
        self.turn_preczar = False
        self.turn_czar = False

    ##The first black card message. For use in black_card()
    async def send_black_card_queue(self):
        blackmessage = "**Round " + str(self.game_round) + "'s Black Card:**\n" + self.game_blacks[0]
        for index, player in enumerate(self.game_players):
            if index != 0:
                nonczar_message = await player.send(blackmessage + "\n**" + self.game_players[0].name + " is the czar this round. " + str(self.game_queue) + " player(s) have not picked a white card yet!**")
                self.game_blackmessages.append(nonczar_message)
            else:
                anim = "<a:danceY:799433527580950529><a:danceO:799433527761698836><a:danceU:799433528277860424>         <a:danceA:799433527309107234><a:danceR:799433527800102922><a:danceE:799433527871537162>         <a:danceT:799433527669555221><a:danceH:799433527783456768><a:danceE:799433527871537162>         <a:danceC:799433527716216903><a:danceZ:799433527677550593><a:danceA:799433527309107234><a:danceR:799433527800102922>"
                czar_message = await player.send(anim + "\n" + blackmessage + "\n**You are the czar this round. " + str(self.game_queue) + " player(s) have not picked a white card yet!**\n" + anim)
                self.game_blackmessages.append(czar_message)

    ##Updating the count of players that haven't picked yet, in white_card().
    async def update_black_card_queue(self):
        blackmessage = "**Round " + str(self.game_round) + "'s Black Card:**\n" + self.game_blacks[0]
        for index, msg in enumerate(self.game_blackmessages):
            if index != 0:
                nonczar_message = await msg.edit(content = blackmessage + "\n**" + self.game_players[0].name + " is the czar this round. " + str(self.game_queue) + " player(s) have not picked a white card yet!**")
            else:
                anim = "<a:danceY:799433527580950529><a:danceO:799433527761698836><a:danceU:799433528277860424>         <a:danceA:799433527309107234><a:danceR:799433527800102922><a:danceE:799433527871537162>         <a:danceT:799433527669555221><a:danceH:799433527783456768><a:danceE:799433527871537162>         <a:danceC:799433527716216903><a:danceZ:799433527677550593><a:danceA:799433527309107234><a:danceR:799433527800102922>"
                czar_message = await msg.edit(content = anim + "\n" + blackmessage + "\n**You are the czar this round. " + str(self.game_queue) + " player(s) have not picked a white card yet!**\n" + anim)

    ##Display Black Card, Await Player's White Cards
    async def black_card(self):
        #Show each player the black card for this round, starting the pre-czar turn.
        self.game_blackmessages = []
        self.game_queue = len(self.game_players)-1
        await self.send_black_card_queue()
        self.turn_preczar = True

    async def white_card(self, user, reaction):
        #Starts processing when detecting a reaction in the on_reaction_add function.
        #If reaction detected, add appropriate white card to stack of picks.
        #Show czar picks once all non-czar players reacted, and start the czar turn.
        ###Check if the player's already submitted a white card before. If yes, extend the picks, if not, create new picks entry.
        pick = []
        playercount = -1
        for count, entry in enumerate(self.game_whitepicks):
            if user.id == entry[0].id:
                playercount = count
                pick = entry
                self.game_emojipicks[count][1].append(self.emoji_number(reaction.emoji))
                break
        if pick == []:
            pick.append(user)
            pick.append([])
        for playerhand in self.game_hands:
            if playerhand[0].id == user.id:
                pick[1].append(playerhand[1][self.emoji_number(reaction.emoji)])
                break
        if playercount == -1:
            self.game_whitepicks.append(pick)
            self.game_emojipicks.append([user,[self.emoji_number(reaction.emoji)]])
        else:
            self.game_whitepicks[playercount] = pick
        ###Check if the amount of submitted white cards matches the blanks in the black card, continue round.
        if len(pick[1]) == self.game_blacks[0].count(r"\_\_\_"):
            self.game_queue -= 1
            if self.game_queue <= 0:
                self.turn_preczar = False
                all_sentences = "**Round " + str(self.game_round) + "'s Answers:**"
                random.shuffle(self.game_whitepicks)
                for count, picks in enumerate(self.game_whitepicks):
                    sentence = self.game_blacks[0]
                    for word in picks[1]:
                        sentence = sentence.replace(r"\_\_\_", "__" + word + "__", 1)
                    all_sentences += "\n" + self.number_emoji(count) + " " + sentence
                for index, msg in enumerate(self.game_blackmessages):
                    if index != 0:
                        await msg.edit(content = all_sentences + "\n**Wait for the czar to choose their favorite answer.**")
                    else:
                        anim = "<a:danceY:799433527580950529><a:danceO:799433527761698836><a:danceU:799433528277860424>         <a:danceA:799433527309107234><a:danceR:799433527800102922><a:danceE:799433527871537162>         <a:danceT:799433527669555221><a:danceH:799433527783456768><a:danceE:799433527871537162>         <a:danceC:799433527716216903><a:danceZ:799433527677550593><a:danceA:799433527309107234><a:danceR:799433527800102922>"
                        await msg.edit(content = anim + "\n" + all_sentences + "\n**You are the czar this round. Choose your favorite answer!**\n" + anim)
                        for i in range(len(self.game_whitepicks)):
                            await msg.add_reaction(self.number_emoji(i))
                        self.turn_czar = True
            else:
                await self.update_black_card_queue()

    async def czar_pick(self, reaction):
        #Starts processing when detecting a reaction from the czar in the on_reaction_add function.
        #If reaction detected, add point to correct player and let all players know of the round winner.
        #Then either declare game winner or continue to next round, depending on score standings.
        self.turn_czar = False
        winner = self.game_whitepicks[self.emoji_number(reaction.emoji)]
        score = 0
        for points in self.game_score:
            if winner[0].id == points[0].id:
                points[1] += 1
                score = points[1]
                break
        winning_line = self.game_blacks[0]
        for word in winner[1]:
            winning_line = winning_line.replace(r"\_\_\_", "__" + word + "__", 1)
        notification = "**The czar chose " + winner[0].name + "'s answer!**\n" + winning_line
        ###Update everyone's scoreboard messages
        scoremessage = "**Scoreboard (play until " + str(self.game_threshold) + ")**```css\n"
        for point in self.game_score:
            if point[0].id == self.game_players[1].id:
                scoremessage += str(point[1]) + " - [" + point[0].name + "]\n"
            else:
                scoremessage += str(point[1]) + " - " + point[0].name + "\n"
        scoremessage += "```"
        for msg in self.game_scoremessages:
            await msg.edit(content = scoremessage)
        ###Reset game, either entirely or just the round
        if score >= self.game_threshold:
            notification += "\n" + winner[0].name + " has won the game!"
            for msg in self.game_blackmessages:
                await msg.edit(content = notification)
            self.reset_game()
        else:
            self.game_round += 1
            #Update black card with victor and put in the new black card.
            for msg in self.game_blackmessages:
                await msg.edit(content = notification, delete_after = 16.0)
            del self.game_blacks[0]
            if len(self.game_blacks) <= 0:
                self.game_blacks = self.deck_blacks.copy()
                random.shuffle(self.game_blacks)
            for hand in self.game_hands:
                #Remove picked card from non-czar player's hands.
                for pick in self.game_whitepicks:
                    if pick[0].id == hand[0].id:
                        for strng in pick[1]:
                            for num, card in enumerate(hand[1]):
                                if card == strng:
                                    self.game_discards.append(card)
                                    del hand[1][num]
                                    break
                        break
                #Give every non-czar player a new card.
                if self.game_players[0].id != hand[0].id:
                    for _ in range(len(self.game_whitepicks[0][1])):
                        if len(self.game_whites) == 0:
                            self.game_whites = self.game_discards.copy()
                            self.deck_discards = []
                            random.shuffle(self.game_whites)
                        hand[1].append(self.game_whites[0])
                        del self.game_whites[0]
                    #Update the hand messages.
                    privatemessage = "**Your White Cards:**"
                    for number, card in enumerate(hand[1]):
                        privatemessage += "\n" + self.number_emoji(number) + " " + card
                    for hand_msg in self.game_handmessages:
                        if hand_msg.channel.recipient.id == hand[0].id:
                            await hand_msg.edit(content = privatemessage)
                            break
            #Move czar to back of the player queue and wipe picks.
            self.game_players.append(self.game_players[0])
            del self.game_players[0]
            self.game_whitepicks = []
            self.game_emojipicks = []
            await self.black_card()

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        try:
            #Check if reaction is a valid number by a non-czar player that hasn't answered yet on their hand message.
            #If it is, then process the white_card function.
            if self.turn_preczar == True:
                if reaction.emoji not in self.emojis or self.emoji_number(reaction.emoji) >= self.game_handsize or user.id == self.game_players[0].id:
                    return
                for picks in self.game_whitepicks:
                    if picks[0].id == user.id and len(picks[1]) == self.game_blacks[0].count(r"\_\_\_"):
                        return
                for emote in self.game_emojipicks:
                    if emote[0].id == user.id:
                        for num in emote[1]:
                            if num == self.emoji_number(reaction.emoji):
                                return
                for msg in self.game_handmessages:
                    if msg.id == reaction.message.id:
                        await self.white_card(user, reaction)
            #Check if reaction is a valid number by the czar on their answer message.
            #If it is, then process the czar_pick function.
            elif self.turn_czar == True:
                if reaction.emoji not in self.emojis or self.emoji_number(reaction.emoji) >= len(self.game_whitepicks):
                    return
                if self.game_players[0].id == user.id and self.game_blackmessages[0].id == reaction.message.id:
                    await self.czar_pick(reaction)
        except Exception as e:
            await send_error(self.client, e, reference=reaction.message.jump_url)

    @commands.Cog.listener()
    async def on_ready(self):
        print("CAH cog loaded.")

    #Decks
    @commands.command(aliases=["cardsagainsthumanity"])
    async def cah(self, ctx, action, *decks):
        try:
            ##Join CAH Game
            if action == "join":
                invalid_join = False
                join_messages = [" has joined CAH!",                        " has joined the party!",
                                 " has entered the game!",                  " has joined the battle!",
                                 " came into the game!",                    " has come aboard!",
                                 " has entered the ring!",                  " is here to win!",
                                 " is ready to play!",                      " is raring to go!",
                                 " will face everyone else!",               " has signed in!",
                                 " is on the scene!",                       " is all fired up!",
                                 " hungers for battle!",                    " will face the competition!"
                                 ]
                for player in self.game_players:
                    if player.id == ctx.author.id:
                        invalid_join = True
                        await ctx.channel.send("You already joined, silly " + ctx.author.name + ".")
                if invalid_join == False:
                    self.game_players.append(ctx.author)
                    await ctx.channel.send(ctx.author.name + random.choice(join_messages))

            ##Start CAH Game
            if action == "start" or action == "begin":
                ###Pick Deck
                if len(decks) == 0:
                    decks = ["default"]
                for deck in decks:
                    extension_blacks = []
                    extension_whites = []
                    if deck == "default":
                        extension_blacks = [r"Hey Reddit! I'm \_\_\_. Ask Me Anything.", r"Introducing X-treme Baseball! It's Like Baseball, But With \_\_\_!", r"What Is Batman's Guilty Pleasure? \_\_\_.",
                                            r"TSA Guidelines Now Prohibit \_\_\_ On Airplanes.", r"Next From J.K. Rowling: *Harry Potter and the Chamber of* \_\_\_.",
                                            r"I'm Sorry, Professor, But I Couldn't Complete My Homework Because Of \_\_\_.", r"Dude, *Do Not* Go In That Bathroom. There's \_\_\_ In There.",
                                            r"How Did I Lose My Virginity? \_\_\_.", r"It's A Pity That Kids These Days Are All Getting Involved With \_\_\_.", r"\_\_\_. Betcha Can't Have Just One!",
                                            r"Kids, I Don't Need Drugs To Get High. I'm High On \_\_\_.",
                                            r"While The United States Raced The Soviet Union to The Moon, The Mexican Government Funneled Millions Of Pesos Into Research On \_\_\_.",
                                            r"In The Disney Channel Original Movie, Hannah Montana Struggles With \_\_\_ For The First Time", r"Whats My Secret Power? \_\_\_.",
                                            r"I'm Going On A Cleanse This Week. Nothing But Kale Juice And \_\_\_.", r"When Pharaoh Remains Unmoved, Moses Called Down A Plague Of \_\_\_.",
                                            r"Just Once, I'd Like To Hear You Say 'Thanks, Mom. Thanks For \_\_\_.'", r"Daddy, Why Is Mommy Crying? \_\_\_.", r"50% Of All Marriages End In \_\_\_.",
                                            r"My Fellow Americans: Before This Decade Is Out, We *Will* Have \_\_\_ On The Moon!",
                                            r"This Season At Steppenwolf, Samuel Beckett's Classic Existential Play: *Waiting For* \_\_\_.", r"Instead Of Coal, Santa Now Gives Bad Children \_\_\_.",
                                            r"Life For American Indians Was Forever Changed When The White Man Introduced Them To \_\_\_.",
                                            r"What's Teach For America Using To Inspire Inner City Students To Succeed? \_\_\_.", r"Maybe She's Born With It. Maybe It's \_\_\_.",
                                            r"What Is George W. Bush Thinking About Right Now? \_\_\_.", r"White People Like \_\_\_.", r"Why Do I Hurt All Over? \_\_\_.",
                                            r"A Romantic Candlelit Dinner Would Be Incomplete Without \_\_\_.", r"Just Saw This Upsetting Video! Please Retweet!! #stop\_\_\_",
                                            r"Fun Tip! When Your Man Asks You To Down On Him, Try Surprising Him With \_\_\_ Instead.", r"The Class Field Trip Was Completely Ruined By \_\_\_.",
                                            r"What's A Girl's Best Friend? \_\_\_.", r"Dear Abby, I'm Having Some Trouble With \_\_\_ And Would Like Your Advice.",
                                            r"When I Am President, I Will Create The Deparment Of \_\_\_.", r"What Are My Parents Hiding From Me?", r"What Never Fails To Liven Up The Party? \_\_\_.",
                                            r"IF You Like \_\_\_, YOU MIGHT BE A REDNECK.", r"What Made My First Kiss So Awkward? \_\_\_.",
                                            r"Hey Guys, Welcome To Chili's! Would You Like To Start The Night Off Right With \_\_\_?", r"I Got 99 Problems But \_\_\_ Ain't One.", r"\_\_\_. It's A Trap!",
                                            r"Bravo's New Reality Show Features Eight Washed-Up Celebrities Living With \_\_\_.", r"What Would Grandma Find Disturbing, Yet Oddly Charming? \_\_\_.",
                                            r"\_\_\_. That Was So Metal.", r"During Sex, I Like To Think About \_\_\_.", r"What Ended My Last Relationship? \_\_\_.", r"What's That Sound? \_\_\_.",
                                            r"Uh, Hey Guys, I Know This Was My Idea, But I'm Having Serious Doubts About \_\_\_.", r"Why Am I Sticky? \_\_\_.",
                                            r"I'm No Doctor But I'm Pretty Sure What You're Suffering from Is Called '\_\_\_.'", r"What's There A Ton Of In Heaven? \_\_\_.",
                                            r"After Four Platinum Albums And Three Grammys, It's Time To Get Back To My Roots, To What Inspired My To Make Music In The First Place: \_\_\_.",
                                            r"What Will Always Get You Laid? \_\_\_.", r"\_\_\_: Kid-Tested, Mother-Approved.", r"Why Can't I Sleep At Night? \_\_\_.", r"What's That Smell? \_\_\_.",
                                            r"After Eight Years In The White House, How Is Obama Finally Letting Loose? \_\_\_.", r"This Is The Way The World Ends. Not With A Bang But With \_\_\_.",
                                            r"Coming To Broadway This Season, \_\_\_: The Musical", r"Here Is The Church, Here Is The Steeple, Open The Doors, And There Is \_\_\_.",
                                            r"But Before I Kill You, Mr. Bond, I Must Show You \_\_\_.", r"A Recent Laboratory Study Shows That Undergraduates Have 50% Less Sex After Being Exposed To \_\_\_.",
                                            r"Next On ESPN2: The World Series Of \_\_\_.", r"When I Am A Billionaire, I Shall Erect A 50-Foot Statue To Commemorate \_\_\_.",
                                            r"Military Historians Remember Alexander The Great For His Brilliant Use Of \_\_\_ Against The Persians.", r"War! What Is It Good For? \_\_\_.", #End Of Single-A's
                                            r"That's Right, I Killed \_\_\_. How, You Ask? \_\_\_.", r"And The Academy Award For \_\_\_ Goes To \_\_\_.", r"Step 1: \_\_\_. Step 2: \_\_\_. Step 3: Profit.",
                                            r"For My Next Trick, I Will Pull \_\_\_ Out Of \_\_\_.", r"\_\_\_ + \_\_\_ = \_\_\_.", r"When I Was Tripping On Acid, \_\_\_ Turned Into \_\_\_.",
                                            r"\_\_\_ Is A Slippery Slope That Leads To \_\_\_.", r"In M. Night Shyamalan's New Movie, Bruce Willis Discovers That \_\_\_ Had Really Been \_\_\_ All Along.",
                                            r"Make A Haiku. \_\_\_ / \_\_\_ / \_\_\_.", r"I Never Truly Understood \_\_\_ Until I Encountered \_\_\_.",
                                            r"They Said We Were Crazy. They Said We Couldn't Put \_\_\_ Inside Of \_\_\_. They Were Wrong.", r"Lifetime® Presents '\_\_\_: The Story Of \_\_\_.",
                                            r"Introducing The Amazing Superhero/Sidekick Duo! It's \_\_\_ And \_\_\_!"
                                            ]
                        extension_whites = ["Silence", "The Illusion Of Choice In A Late-Stage Capitalist Society", "Many Bats", "Famine", "Flesh-Eating Bacteria", "Flying Sex Snakes",
                                            "Not Giving A Shit About The Third World", "Magnets", "Shapeshifters", "Seeing What Happens When You Lock People In A Room With Hungry Seagulls", "A Crucifixion",
                                            "Jennifer Lawrence", "72 Virgins", "A Live Studio Audience", "A Time Travel Paradox", "Authentic Mexican Cuisine", "Doing Crimes", "Synergistic Management Solutions",
                                            "Crippling Debt", "Daddy Issues", "Used Panties", "A Fart So Powerful That It Wakes Giants From Their Thousand-Year Slumber", "Former President George W. Bush",
                                            "Full Frontal Nudity", "Covering Myself With Parmesan Cheese And Chili Flakes Because I Am Pizza", "Laying An Egg", "Getting Naked And Watching Nickelodeon",
                                            "Pretending To Care", "Having Big Dreams But No Realistic Way To Achieve Them", "Seeing Grandma Naked", "Boogers", "The Inevitable Heat Death Of The Universe",
                                            "The Miracle Of Childbirth", "The Rapture", "Whipping It Out", "White Privilege", "Emerging From The Sea And Rampaging Through Tokyo", "The Hamburglar",
                                            "AXE Body Spray", "The Blood Of Christ", "Soft, Kissy Missionary Sex", "BATMAN!", "Agriculture", "Barely Making $25,000 A Year", "Natural Selection",
                                            "Coat Hanger Abortions", "Sex With Patrick Stewart", "My Abusive Boyfriend Who Really Isn't So Bad Once You Get To Know Him", "Prescription Pain Killers", "Swooping",
                                            "Mansplaining", "A Homoerotic Volleyball Montage", "Alexandria Ocasio-Cortez", "Putting Things Where They Go", "Fragile Masculinity",
                                            "All-You-Can-Eat Shrimp For $8.99", "An Old Guy Who's Almost Dead", "Kanye West", "Hot Cheese", "Raptor Attacks", "Seven Dead And Three In Critical Condition",
                                            "Smegma", "Alcoholism", "A Middle-Aged Man On Roller Skates", "Looking In The Mirror, Applying Lipstick, And Whispering 'Tonight, You Will Have Sex With Tom Cruise.'",
                                            "Bingeing And Purging", "An Oversized Lollipop", "Self-Loathing", "Sitting On My Face And Telling Me I'm Garbage", "Half-Assed Foreplay", "The Holy Bible",
                                            "German Dungeon Porn", "Being On Fire", "Teenage Pregnancy", "Gandhi", "Your Weird Brother", "A Fleshlight®", "A Pyramid Of Severed Heads",
                                            "An Erection That Lasts Longer Than Four Hours", "A Three-Way With My Wife And Shaquille O'Neal", "The Past", "My Genitals", "An Endless Stream Of Diarrhea",
                                            "Science", "Not Reciprocating Oral Sex", "Flightless Birds", "A Good Sniff", "50,000 Volts Straight To The Nipples", "A Balanced Breakfast", "Dead Birds Everywhere",
                                            "The Arrival Of The Pizza", "Permanent Orgasm-Face Disorder", "The Cool, Refreshing Taste Of Pepsi®", "Chemical Weapons", "Oprah",
                                            "Wondering If It's Possible To Get Some Of That Salsa To Go", "Bananas", "Passive Aggressive Post-It Notes", "Hillary Clinton's Emails", "Switching To Geico®",
                                            "Peeing A Little Bit", "Wet Dreams", "The Jews", "My Cheating Son-Of-A-Bitch Husband", "Powerful Thighs", "These Hoes", "The Only Gay Person In A Hundred Miles",
                                            "Having Sex For The First Time", "Donald J. Trump", "Kissing Grandma On The Forehead And Turning Off Her Life Support", "Sexual Tension", "An AR-15 Assault Rifle",
                                            "My Good Bra", "Punching A Congressman In The Face", "Fancy Feast®", "Being Rich", "Sweet, Sweet Vengeance", "Republicans", "Sniffing And Kissing My Feet",
                                            "A Much Younger Woman", "Poverty", "Kamikaze Pilots", "Committing Suicide", "The Homosexual Agenda", "A Mexican", "A Falcon With A Cap On Its Head", "Wizard Music",
                                            "The Kool-Aid Man", "Juuling", "Free Samples", "Hurting Those Closest To Me", "Doing The Right Thing", "The Three-Fifths Compromise", "Lactation", "World Peace",
                                            "Shutting Up So I Can Watch The Game", "Eating A Hard Boiled Egg Out Of My Husband's Asshole", "RoboCop", "One Titty Hanging Out", "Justin Bieber", "Oompa-Loompas",
                                            "Inappropriate Yodeling", "Puberty", "Ghosts", "50 mg Of Zoloft Daily", "Fucking My Sister", "Braiding Three Penises Into A Twizzler", "Vigorous Jazz Hands",
                                            "Getting Fingered", "My Uber Driver, Pavel", "GoGurt®", "Police Brutality", "Filling My Briefcase With Business Stuff", "Preteens", "My Fat Daughter", "Rap Music",
                                            "Fading Away Into Nothingness", "Darth Vader", "A Sad Handjob", "Exactly What You'd Expect", "Expecting A Burp And Vomiting On The Floor", "Adderall®",
                                            "The Red Hot Chili Peppers", "Sideboob", "An Octopus Giving Seven Handjobs And Smoking A Cigarette", "My Neck, My Back, My Pussy, And My Crack",
                                            "J.D. Powers And His Associates", "Mouth Herpes", "Sperm Whales", "Women Of Color", "Men Discussing Their Feelings In An Emotionally Healthy Way", "Incest",
                                            "Pac-Man Uncontrollably Guzzling Cum", "Casually Suggesting A Threesome", "Running Out Of Semen", "God", "The Wonders Of The Orient", "Sexual Peeing", "Emotions",
                                            "Licking Things To Claim Them As Your Own", "Jobs", "The Placenta", "Spontaneous Human Combustion", "*The Bachelorette* Season Finale",
                                            "Throwing Grapes At A Man Until He Loses Touch With Reality", "Establishing Dominance", "Finger Painting", "Old-People Smell",
                                            "Getting Crushed By A Vending Machine", "My Inner Demons", "A Super Soaker™️ Full Of Cat Pee", "Aaron Burr", "Cuddling", "However Much Weed $20 Can Buy",
                                            "Battlefield Amputations", "Spaghetti? Again?", "Ronald Reagan", "A Disappointing Birthday Party", "Nachos For The Table", "Becoming A Blueberry", "A Tiny Horse",
                                            "William Shatner", "Selling Crack To Children", "An M. Night Shyamalan Plot Twist", "Brown People", "Mutually Assured Destruction", "Pedophiles", "Yeast",
                                            "How Bad My Daughter Fucked Up Her Dance Recital", "Rectangles", "Catapults", "Poor People", "Only Dating Asian Women", "The Hustle", "The Force",
                                            "How Amazing It Is To Be On Mushrooms", "Judging Everyone", "Kourtney, Kim, Khloe, Kendall, And Kylie",
                                            "Getting Married, Having A Few Kids, Buying Some Stuff, Retiring To Florida, And Dying", "Some God Damn Peace And Quiet", "AIDS", "Pictures Of Boobs",
                                            "Strong Female Characters", "Some Foundation, Mascara, And A Touch Of Blush", "Hospice Care", "Getting Really High", "The Opiod Epidemic", "Penis Envy",
                                            "Gay Conversion Therapy", "Ruth Bader Ginsburg Brutally Gaveling Your Penis", "German Chancellor Angela Merkel", "The KKK",
                                            "A Pangender Octopus Who Roams The Cosmos In Search Of Love", "Meth", "Serfdom", "Holding Down A Child And Farting All Over Him", "A Bop It™️",
                                            "A Whole Thing Of Butter", "Still Being A Virgin", "Solving Problems With Violence", "Getting Cummed On", "Pixelated Bukkake", "A Lifetime Of Sadness",
                                            "Going An Entire Day Without Masturbating", "Dick Pics", "Racism", "Menstrual Rage", "Sunshine And Rainbows", "Radical Islamic Terrorism",
                                            "Huge Biceps", "My Little Boner", "Dry Heaving", "A Gossamer Stream Of Jizz That Catches The Light As It Arcs Through The Morning Air",
                                            "Executing A Hostage Every Hour", "The Rhythms Of Africa", "Breaking Out Into Song And Dance", "Leprosy", "Gloryholes", "Nipple Blades", "The Heart Of A Child",
                                            "Puppies", "Fellowship In Christ", "Little Boy Penises", "Waking Up Half-Naked In A Denny's Parking Lot", "An Older Woman Who Knows Her Way Around The Penis",
                                            "Getting Drugs Off The Street And Into My Body", "Daniel Radcliffe's Delicious Asshole", "Active Listening", "Ethnic Cleansing", "Itchy Pussy",
                                            "Blowing My Boyfriend So Hard He Shits", "A Fuck-Ton Of Almonds", "A Salad For Men That's Made Of Metal", "Waiting Till Marriage", "Unfathomable Stupidity",
                                            "Shiny Objects", "The Devil Himself", "Autocannibalism", "Erectile Dysfunction", "My Collection Of Japanese Sex Toys", "The Pope", "White People", "Tentacle Porn",
                                            "My Bright Pink Fuckhole", "How Far I Can Get My Own Penis Up My Butt", "Having Anuses For Eyes", "The Penny Whistle Solo From 'My Heart Will Go On'", "Seppuku",
                                            "Danny DeVito", "The Magic Of Live Theatre", "Throwing A Virgin Into A Volcano", "Dwayne 'The Rock' Johnson", "Accepting The Way Things Are",
                                            "NBA Superstar LeBron James", "Listening To Her Problems Without Trying To Solve Them", "Therapy", "Being Fat And Stupid", "Pooping Back And Forth. Forever",
                                            "Tearing That Ass Up Like Wrapping Paper On Christmas Morning", "More Elephant Cock Than I Bargained For", "A Salty Surprise", "The South",
                                            "The Violation Of Our Most Basic Human Rights", "Tap Dancing Like There's No Tomorrow", "Consensual Sex", "Telling A Shitty Story That Goes Nowhere",
                                            "A Good, Strong Gorilla", "Seeing My Father Cry", "Necrophilia", "Being A Woman", "Getting Into A Pretty Bad Car Accident", "Bill Nye The Science Guy",
                                            "Black People", "The Boy Scouts Of America", "Lunchables™️", "Bitches", "Some Punk Kid Who Stole My Turkey Sandwich", "Heartwarming Orphans", "Spirit Airlines",
                                            "Bubble Butt Bottom Boys", "A Bowl Of Mayonnaise And Human Teeth", "Fiery Poops", "Saying 'I Love You.'", "Inserting A Mason Jar Into My Anus",
                                            "The True Meaning Of Christmas", "Some Of The Best Rappers In The Game", "Owning And Operating A Chili's Franchise", "Estrogen", "Girls", "The Russians",
                                            "A Bleached Asshole", "Fucking The Weatherman On Live Television", "PTSD", "Dark And Mysterious Forces Beyond Our Control", "Smallpox Blankets", "Masturbating",
                                            "Hobos", "Queefing", "The Guys From *Queer Eye*", "Cardi B", "Viagra®", "Soup That Is Too Hot", "Muhammad (Peace Be Upon Him)", "Explaining How Vaginas Work",
                                            "Academy Award Winner Meryl Streep", "Drinking Alone", "Dick Fingers", "Multiple Stab Wounds", "Poopy Diapers", "Child Abuse", "Anal Beads",
                                            "Slaughtering Innocent Civilians", "Pulling Out", "Being Able To Talk To Elephants", "Horse Meat", "A Really Cool Hat", "Stalin", "A Stray Pube",
                                            "Worshipping That Pussy", "Completely Unwarranted Confidence", "Doin' It In The Butt", "My Ex-Wife", "Teaching A Robot To Love",
                                            "Touching A Pug Right On His Penis", "A Windmill Full Of Corpses", "Count Chocula", "Vladimir Putin", "The Patriarchy", "The Glass Ceiling",
                                            "Vomiting Seafoood And Bleeding Anally", "The American Dream", "Not Wearing Pants", "My Balls On Your Face", "Popping In A Laptop And Closing It", "Dead Babies",
                                            "Foreskin", "A Saxophone Solo", "Italians", "A Fetus", "Firing A Rifle Into The Air While Balls Deep In A Squealing Hog", "Mike Pence", "10,000 Syrian Refugees",
                                            "Forced Sterilization", "My Relationship Status", "An Unwanted Pregnancy", "Diversity", "A White Ethnostate", "Bees?", "Harry Potter Erotica",
                                            "Giving Birth To The Antichrist", "Three Dicks At The Same Time", "Nazis", "8 oz. Of Sweet Mexican Black-Tar Heroin", "What That Mouth Do", "Dead Parents",
                                            "Object Permanence", "Opposable Thumbs", "Racially-Biased SAT Questions", "The Great Depression", "Chainsaws For Hands", "Nicolas Cage", "Child Beauty Pageants",
                                            "Explosions", "Not Vaccinating My Children Because I Am Stupid", "Lena Dunham", "Huffing Spray Paint", "A Man On The Brink Of Orgasm", "Repression", "Invading Poland",
                                            "My Vagina", "Assless Chaps", "Murder", "Giving 110%", "Her Majesty, Queen Elizabeth II", "The Trail Of Tears", "Memes", "Sex With Animals", "Being Marginalized",
                                            "Goblins", "Hope", "Liberals", "A Micropenis", "My Soul", "A Ball Of Earwax, Semen, And Toenail Clippings", "A Horde Of Vikings", "Hot People",
                                            "Seething With Quiet Resentment", "An Oedipus Complex", "Geese", "Extremely Tight Pants", "Fox News", "A Little Boy Who Won't Shut The Fuck Up About Dinosaurs",
                                            "Making A Pouty Face", "Vehicular Manslaughter", "Women's Suffrage", "Some Guy", "Judge Judy", "African Children", "This Month's Mass Shooting", "Barack Obama",
                                            "Illegal Immigrants", "Elderly Japanese Men", "The Female Orgasm", "Heteronormativity", "Crumbs All Over The God Damn Carpet", "Arnold Schwarzenegger",
                                            "The Wifi Password", "Spectacular Abs", "A Bird That Shits Human Turds", "A Mopey Zoo Lion", "A Bag Of Magic Beans", "Poor Life Choices", "My Sex Life", "Auschwitz",
                                            "A Snapping Turtle Biting The Tip Of Your Penis", "All The Dudes I've Fucked", "The Clitoris", "The Big Bang", "Land Mines", "The Entire Mormon Tabernacle Choir",
                                            "A Micropig Wearing A Tiny Raincoat And Booties", "Penis Breath", "Jerking Off Into A Pool Of Children's Tears", "Man Meat", "Me Time", "The Underground Railroad",
                                            "Poorly-Timed Holocaust Jokes", "A Sea Of Troubles", "Lumberjack Fantasies", "Morgan Freeman's Voice", "Women In Yogurt Commercials", "Natural Male Enhancement",
                                            "Being A Motherfucking Sorcerer", "My Black Ass", "Genuine Human Connection", "Announcing That I Am About To Cum", "Balls", "Grandma", "Friction",
                                            "Chunks Of A Dead Hitchhiker", "Farting And Walking Away", "Being A Dick To Children", "One Trillion Dollars", "Drowning The Kids In The Bathtub", "Dying",
                                            "Drinking Out Of The Toilet And Eating Garbage", "The Gays", "The Screams... The Terrible Screams", "Men", "The Bombing Of Nagasaki", "Fake Tits", "The Amish",
                                            "David Bowie Flying In On A Tiger Made Of Lightning", "My Ugly Face And Bad Personality", "A Bitch Slap", "A Brain Tumor", "Fear Itself",
                                            "Jews, Gypsies, And Homosexuals", "The Milkman", "Cards Against Humanity"
                                            ]
                    elif deck == "red":
                        extension_blacks = [r"\_\_\_ Would Be Woefully Incomplete Without \_\_\_.", r"\_\_\_: Hours Of Fun. Easy To Use. Perfect For \_\_\_!", r"\_\_\_. Awesome In Theory, Kind Of A Mess In Practice.",
                                            r"A Remarkable New Study Has Shown That Chimps Have Evolved Their Own Primitive Version Of \_\_\_.", r"A Successful Job Interview Begins With A Firm Handshake And Ends With \_\_\_.",
                                            r"After Months Of Practice With \_\_\_, I Think I'm Finally Ready For \_\_\_.", r"And I Would Have Gotten Away With It, Too, If It Hadn't Been For \_\_\_!",
                                            r"And What Did You Bring For Show And Tell? \_\_\_.", r"As Part Of His Daily Regimen, Anderson Cooper Sets Aside 15 Minutes For \_\_\_.",
                                            r"Awww, Sick! I Just Say This Skater Do A 720 Kickflip Into \_\_\_!", r"Before \_\_\_, All We Had Was \_\_\_.",
                                            r"Before I Run For President, I Must Destroy All Evidence Of My Involvement With \_\_\_.",
                                            r"Call The Law Offices Of Goldstein & Goldstein, Because No One Should Have To Tolerate \_\_\_ In The Workplace.",
                                            r"Charades Was Ruined For Me Forever When My Mom Had To Act Out \_\_\_.", r"Dear Sir Or Madam, We Regret To Inform You That The Office Of \_\_\_ Has Denied Your Request For \_\_\_.",
                                            r"Doctor, You've Gone Too Far! The Human Body Wasn't Meant To Withstand That Amount Of \_\_\_!", r"During High School I Never Really Fit In Until I Found \_\_\_ Club.",
                                            r"During His Midlife Crisis, My Dad Got Really Into \_\_\_.", r"Finally! A Service That Delivers \_\_\_ Right To Your Door.",
                                            r"Future Historians Will Agree That \_\_\_ Marked The Beginning Of America's Decline.", r"Having Problems With \_\_\_? Try \_\_\_!",
                                            r"Hey Baby, Come Back To My Place And I'll Show You \_\_\_.", r"I Learned The Hard Way That You Can't Cheer Up A Grieving Friend With \_\_\_.",
                                            r"I Love Being A Mom. But It's Tough When My Kids Come Home Filthy From \_\_\_. That's Why There's Tide®.",
                                            r"I Spent My Whole Life Working Toward \_\_\_, Only To Have It Ruined By \_\_\_.", r"I Went From \_\_\_ To \_\_\_, All Thanks To \_\_\_.",
                                            r"I'm Not Like The Rest Of You. I'm Too Rich And Busy For \_\_\_.", r"If God Didn't Want Us To Enjoy \_\_\_, He Wouldn't Have Given Us \_\_\_.",
                                            r"In A Pinch, \_\_\_ Can Be A Suitable Substitute For \_\_\_.", r"In His New Self-Produced Album, Kanye West Raps Over The Sounds Of \_\_\_.",
                                            r"In His Newest And Most Difficult Stunt, David Blaine Must Escape From \_\_\_.", r"In Its New Tourism Campaign, Detroit Proudly Proclaims That It Has Finally Eliminated \_\_\_.",
                                            r"In Rome, There Are Whisperings That The Vatican Has A Secret Room Devoted To \_\_\_.", r"In The Seventh Circle Of Hell, Sinners Must Endure \_\_\_ For All Eternity.",
                                            r"Legend Has It Prince Wouldn't Perform Without \_\_\_ In His Dressing Room.", r"Listen, Son. If You Want To Get Involved With \_\_\_, I Won't Stop You. Just Steer Clear Of \_\_\_.",
                                            r"Little Miss Muffet Sat On A Tuffet, Eating Her Curds And \_\_\_.", r"Lovin' You Is Easy 'Cause You're \_\_\_.",
                                            r"Members Of New York's Social Elite Are Paying Thousands Of Dollars Just To Experience \_\_\_.", r"Michael Bay's New Three-Hour Action Epic Pits \_\_\_ Against \_\_\_.",
                                            r"Money Can't Buy Me Love, But It Can Buy Me \_\_\_.", r"My Country, 'Tis Of Thee, Sweet Land Of \_\_\_.", r"My Gym Teacher Got Fired For Adding \_\_\_ To The Obstacle Course.",
                                            r"My Life Is Ruled By A Vicious Cycle Of \_\_\_ And \_\_\_.", r"My Mom Freaked Out When She Looked At My Browser History And Found \_\_\_.com/\_\_\_.",
                                            r"My New Favorite Porn Star Is Joey '\_\_\_' Mcgee.", r"My Plan For World Domination Begins With \_\_\_.", r"Next Time On Dr. Phil: How To Talk To Your Child About \_\_\_.",
                                            r"Next Week On The Discovery Channel, One Man Must Survive In The Depths Of The Amazon With Only \_\_\_ And His Wits.", r"Only Two Things In Life Are Certain: Death And \_\_\_.",
                                            r"Science Will Never Explain \_\_\_.", r"The Blind Date Was Going Horribly Until We Discovered Our Shared Interest In \_\_\_.",
                                            r"The CIA Now Interrogates Enemy Agents By Repeatedly Subjecting Them To \_\_\_.", r"The Five Stages Of Grief: Denial, Anger, Bargaining, \_\_\_, Acceptance.",
                                            r"The Healing Process Began When I Joined A Support Group For Victims Of \_\_\_.", r"The Secret To A Lasting Marriage Is Communication, Communication, And \_\_\_.",
                                            r"This Is Your Captain Speaking. Fasten Your Seatbelts And Prepare For \_\_\_.", r"This Month's Cosmo: 'Spice Up Your Sex Life By Bringing \_\_\_ Into The Bedroom.'",
                                            r"To Prepare For His Upcoming Role, Daniel Day-Lewis Immersed Himself In The World Of \_\_\_.", r"Tonight On 20/20: What You Don't Know About \_\_\_ Could Kill You.",
                                            r"Turns Out That \_\_\_-Man Was Neither The Hero We Needed Nor Wanted.", r"Welcome To Señor Frog's! Would You Like To Try Our Signature Cocktail, '\_\_\_ On The Beach?'",
                                            r"What Brought The Orgy To A Grinding Halt? \_\_\_.", r"What Has Been Making Life Difficult At The Nudist Colony? \_\_\_.", r"What Left This Stain On My Couch? \_\_\_.",
                                            r"What's Harshing My Mellow, Man? \_\_\_.", r"When All Else Fails, I Can Always Masturbate To \_\_\_.", r"When I Pooped, What Came Out Of My Butt? \_\_\_.",
                                            r"When You Get Right Down To It, \_\_\_ Is Just \_\_\_.", r"With Enough Time And Pressure, \_\_\_ Will Turn Into \_\_\_.",
                                            r"You Haven't Truly Lived Until You've Experienced \_\_\_ And \_\_\_ At The Same Time.", r"Your Persistence Is Admirable, My Dear Prince. But You Cannot Win My Heart With \_\_\_ Alone."
                                            ]
                        extension_whites = ["24-Hour Media Coverage", "A 55-Gallon Drum Of Lube", "A Big Black Dick", "A Bigger, Blacker Dick", "A Black-Owned And Operated Business", "A Bloody Pacifier", "A Boo-Boo",
                                            "A Botched Circumcision", "A Burmese Tiger Pit", "A Cat Video So Cute That Your Eyes Roll Back And Your Spine Slides Out Of Your Anus", "A Complicated Relationship With Food",
                                            "A Cop Who Is Also A Dog", "A Crappy Little Hand", "A Dollop Of Sour Cream", "A Fat Bald Man From The Internet", "A Fortuitous Turnip Harvest", "A Greased-Up Matthew McConaughey",
                                            "A Japanese Toaster You Can Fuck", "A Japanese Tourist Who Wants Something Very Badly But Cannot Communicate It", "A Lamprey Swimming Up The Toilet And Latching Onto Your Taint",
                                            "A Low Standard Of Living", "A Magic Hippie Love Cloud", "A Man In Yoga Pants With A Ponytail And Feather Earrings", "A Nautical Theme", "A Nuanced Critique",
                                            "A Passionate Latino Lover", "A Phantasmagoria Of Anal Delights", "A Pile Of Squirming Bodies", "A Piñata Full Of Scorpions", "A Plunger To The Face", "A Powerpoint Presentation",
                                            "A Sad Fat Dragon With No Friends", "A Sales Team Of Clowns And Pedophiles", "A Slightly Shittier Parallel Universe",
                                            "A Smiling Black Man, A Latina Businesswoman, A Cool Asian, And Some Whites", "A Sofa That Says 'I Have Style, But I Like To Be Comfortable.'", "A Spontaneous Conga Line",
                                            "A Squadron Of Moles Wearing Aviator Goggles", "A Surprising Amount Of Hair", "A Sweaty, Panting Leather Daddy", "A Sweet Spaceship", "A Vagina That Leads To Another Dimension",
                                            "A Web Of Lies", "Actually Getting Shot, For Real", "All My Friends Dying", "All Of This Blood", "An All-Midget Production Of Shakespeare's Richard III", "An Army Of Skeletons",
                                            "An Ass Disaster", "An Ether-Soaked Rag", "An Etsy Steampunk Strap-On", "An Evil Man In Evil Clothes", "An Unhinged Ferris Wheel Rolling Toward The Sea",
                                            "An Unstoppable Wave Of Fire Ants", "André The Giant's Enormous, Leathery Scrotum", "Another Shot Of Morphine", "Basic Human Decency",
                                            "Being A Busy Adult With Many Important Things To Do", "Being A Dinosaur", "Being A Hideous Beast That No One Could Love", "Being Awesome At Sex", "Being Black",
                                            "Being Fat From Noodles", "Being White", "Big Bad Mama Nipples", "Big Bird's Brown, Crusty Asshole", "Big Ol' Floppy Titties",
                                            "Bill Clinton, Naked On A Bearskin Rug With A Saxophone", "Blood Farts", "Blowing Some Dudes In An Alley", "Boris The Soviet Love Hammer", "Bosnian Chicken Farmers", "Bullshit",
                                            "Buying The Right Pants To Be Cool", "Catastrophic Urethral Trauma", "Chugging A Lava Lamp", "Clams", "Clenched Butt Cheeks", "Cock", "Consent", "Converting To Islam",
                                            "Crabapples All Over The Fucking Sidewalk", "Crushing Mr. Peanut's Brittle Body", "Crying Into The Pages Of Sylvia Plath", "Cumming Deep Inside My Best Bro", "Dad's Funny Balls",
                                            "Daddy's Belt", "Death By Steven Seagal", "Deflowering The Princess", "Demonic Possession", "Dining With Cardboard Cutouts Of The Cast Of *Friends*", "Disco Fever", "Dorito Breath",
                                            "Double Penetration", "Drinking My Bro's Pee-Pee Right Out Of His Peen", "Drinking Ten 5-Hour ENERGYs® To Get Fifty Continuous Hours Of Energy", "Dying Alone And In Pain",
                                            "Eating An Albino", "Eating Tom Selleck's Mustache To Gain His Powers", "Emotional Baggage", "Enormous Scandinavian Women", "Existing", "Fabricating Statistics",
                                            "Fetal Alcohol Syndrome", "Filling Every Orifice With Butterscotch Pudding", "Filling My Son With Spaghetti", "Finding Waldo", "Fisting", "Flying Robots That Kill People",
                                            "Four Hours Of Truly Goofy Sex With The Blue Man Group", "Fuck Mountain", "Gandalf", "Gargling Jizz", "Gay Aliens", "Generational Wealth", "Genetically Engineered Super-Soldiers",
                                            "George Clooney's Musk", "Getting Abducted By Peter Pan", "Getting Your Dick Stuck In A Chinese Finger Trap With Another Dick", "Gladiatorial Combat", "Going Around Punching People",
                                            "Grandpa's Ashes", "Graphic Violence, Adult Language, And Some Sexual Content", "Having $57 In The Bank", "Having A Penis", "Having Sex On Top Of A Pizza", "Having Shotguns For Legs",
                                            "Hillary Clinton", "Hipsters", "Historical Revisionism", "Hot Brown Piss", "Hot Doooooooogs", "How Awesome It Is To Be White", "How Wet My Pussy Is", "Huge Tits And A Can-Do Attitude",
                                            "Indescribable Loneliness", "Insatiable Bloodlust", "Intimacy Problems", "Jafar", "Jeff Goldblum", "Jesus", "Jumping Out At People", "Just The Tip", "Kim Jong-Un",
                                            "Letting Everyone Down", "Leveling Up", "Literally Eating Shit", "Living In A Trash Can", "Loki, The Trickster God", "Mad Hacky-Sack Skills",
                                            "Maintaining Eye Contact With A Grown Man While He Takes A Shit", "Making A Friend", "Making Shit Up", "Making The Penises Kiss", "Masturbating In A Robe Like A Rich Person",
                                            "Maximal Insertion", "Me", "Medieval Times® Dinner & Tournament", "Mild Autism", "Mom", "Mooing", "Moral Ambiguity", "Mufasa's Death Scene", "Multiple Orgasms",
                                            "My Father, Who Died When I Was Seven", "My First Kill", "My Machete", "My Manservant, Claude", "Neil Patrick Harris", "Not Contributing To Society In Any Meaningful Way",
                                            "Not Having Sex", "Nothing", "Nubile Slave Boys", "Nunchuck Moves", "Ominous Background Music", "Oncoming Traffic", "One Ring To Rule Them All", "One Thousand Slim Jims",
                                            "Our Mutual Friend Brad", "Overpowering Your Father", "Power", "Pretty Pretty Princess Dress-Up Board Game®", "Pumping Out A Baby Every Nine Months",
                                            "Putting An Entire Peanut Butter And Jelly Sandwich Into The VCR", "Quiche", "Racial Profiling", "Revenge Fucking", "Reverse Cowgirl", "Rich People",
                                            "Ripping Open A Man's Chest And Pulling Out His Still-Beating Heart", "Rising From The Grave", "Roland The Farter, Flatulist To The King",
                                            "Running Naked Through A Mall, Pissing And Shitting Everywhere", "Ryan Gosling Riding In On A White Horse", "Samuel L. Jackson", "Sanding Off A Man's Nose", "Santa Claus",
                                            "Savagely Beating A Mascot", "Screaming Like A Maniac", "Scrotal Frostbite", "Scrotum Tickling", "Self-Flagellation", "Sexual Humiliation", "Sexual Intercourse", "Shaft",
                                            "Shitting Out A Screaming Face", "Shutting The Fuck Up", "Sitting On A Dick And Sipping Green Tea", "Slapping A Racist Old Lady", "Sneezing, Farting, And Cumming At The Same Time",
                                            "Some Douche With An Acoustic Guitar", "Some Kind Of Bird-Man", "Some Really Fucked-Up Shit", "Sorcery", "Special Musical Guest, Cher", "Spending Lots Of Money",
                                            "Staring At A Painting And Going 'Hmmmmmm...'", "Statistically Validated Stereotypes", "Stockholm Syndrome", "Subduing A Grizzly Bear And Making Her Your Wife",
                                            "Sudden Poop Explosion Disease", "Suicidal Thoughts", "Suicide Bombers", "Survivor's Guilt", "Swiftly Achieving Orgasm", "Syphilitic Insanity",
                                            "Taking A Man's Eyes And Balls Out And Putting His Eyes Where His Balls Go And Then His Balls In The Eye Holes", "That Ass", "The Baby That Ruined My Pussy",
                                            "The Black Power Ranger", "The Boners Of The Elderly", "The Day The Birds Attacked", "The Economy", "The Entire Internet", "The Flute", "The Four Arms Of Vishnu", "The Gulags",
                                            "The Harlem Globetrotters", "The Harsh Light Of Day", "The Hiccups", "The Hose", "The Human Body", "The Land Of Chocolate", "The Lingering Scent Of Gardenias",
                                            "The Mere Concept Of Applebee's®", "The Milk That Comes Out Of A Person", "The Mixing Of The Races", "The Moist, Demanding Chasm Of His Mouth", "The New Radiohead Album",
                                            "The Ooze", "The People Of Florida", "The Primal, Ball-Slapping Sex Your Parents Are Having Right Now", "The Prunes I've Been Saving For You In My Armpits",
                                            "The Quesadilla Explosion Salad™ From Chili's®", "The Shambling Corpse Of Larry King", "The Systematic Destruction Of An Entire People And Their Way Of Life",
                                            "The Thin Veneer Of Situational Causality That Underlies Porn", "The Total Collapse Of The Global Financial System", "The Way White People Is",
                                            "The Worst Pain Imaginable. Times Two!", "Three Months In The Hole", "Tiny Nipples", "Tongue", "Tripping Balls", "Unlimited Soup, Salad, And Breadsticks", "Velcro™",
                                            "Vietnam Flashbacks", "Vomiting Mid-Blowjob", "Walking In On Dad Peeing Into Mom's Mouth", "Warm, Velvety Muppet Sex", "Weapons-Grade Plutonium", "Wearing An Octopus For A Hat",
                                            "Wet Butt", "Whining Like A Little Bitch", "Whipping A Disobedient Slave", "White Power", "Words, Words, Words", "Zeus's Sexual Appetites"
                                            ]
                    elif deck == "blue":
                        extension_blacks = [r"\_\_\_ May Pass, But \_\_\_ Will Last Forever.", r"\_\_\_ Will Never Be The Same After \_\_\_.", r"*'This Is Madness.' 'No, THIS IS* \_\_\_!'",
                                            r"2 AM In The City That Never Sleeps. The Door Swings Open And She Walks In, Legs Up To Here. Something In Her Eyes Tells Me She's Looking For \_\_\_.",
                                            r"Adventure. Romance. \_\_\_. From Paramount Pictures, '\_\_\_.'", r"And Today's Soup Is Cream Of \_\_\_.", r"And Would You Like Those Buffalo Wings Mild, Hot, Or \_\_\_?",
                                            r"Armani Suit: $1,000. Dinner For Two At That Swanky Restaurant: $300. The Look On Her Face When You Surprise Her With \_\_\_: Priceless.",
                                            r"As King, How Will I Keep The Peasants In Line? \_\_\_.", r"Behind Every Powerful Man Is \_\_\_.",
                                            r"Come To Dubai, Where You Can Relax In Our World-Famous Spas, Experience The Nightlife, Or Simply Enjoy \_\_\_ By The Poolside.",
                                            r"Dammit Gary. You Can't Just Solve Every Problem With \_\_\_.", r"Dear Leader Kim Jong-Un, Our Village Praises Your Infinite Wisdom With A Humble Offering Of \_\_\_.",
                                            r"Do *Not* Fuck With Me! I Am Literally \_\_\_ Right Now.", r"Do The Dew With Our Most Extreme Flavor Yet! Get Ready For Mountain Dew \_\_\_!",
                                            r"Do You Lack Energy? Does It Sometimes Feel Like The Whole World Is \_\_\_ ? Ask Your Doctor About Zoloft®.",
                                            r"Don't Forget! Beginning This Week, Casual Friday Will Officially Become '\_\_\_ Friday.'", r"Don't Worry Kid. It Gets Better. I've Been Living With \_\_\_ For 20 Years.",
                                            r"Every Step Towards \_\_\_ Gets Me A Little Bit Closer To \_\_\_.", r"Everybody Join Hands And Close Your Eyes. Do You Sense That? That's The Presence Of \_\_\_ In This Room.",
                                            r"Forget Everything You Know About \_\_\_, Because Now We've Supercharged It With \_\_\_!",
                                            r"Get Ready For The Movie Of The Summer! One Cop Plays By The Book. The Other's Only Interested In One Thing: \_\_\_.", r"Having The Worst Day Ever. #\_\_\_",
                                            r"Heed My Voice, Mortals! I Am The God Of \_\_\_ , And I Will Not Tolerate \_\_\_!", r"Help Me Doctor, I've Got \_\_\_ In My Butt!",
                                            r"Here At The Academy For Gifted Children, We Allow Students To Explore \_\_\_ At Their Own Pace.",
                                            r"Hi MTV! My Name Is Kendra, I Live In Malibu, I'm Into \_\_\_, And I Love To Have A Good Time.",
                                            r"Hi, This Is Jim From Accounting. We Noticed A $1,200 Charge Labeled '\_\_\_.' Can You Explain?",
                                            r"Honey, I Have A New Role-Play I Want To Try Tonight! You Can Be \_\_\_, And I'll Be \_\_\_.",
                                            r"How Am I Compensating For My Tiny Penis? \_\_\_.", r"I Am Become \_\_\_, Destroyer Of \_\_\_!", r"I Don't Mean To Brag, But They Call Me The Micheal Jordan Of \_\_\_.",
                                            r"I Have A Strict Policy. First Date, Dinner. Second Date, Kiss. Third Date, \_\_\_.", r"I Work My Ass Off All Day For This Family, And This Is What I Come Home To? \_\_\_!?",
                                            r"I'm Miss Tennessee, And If I Could Make The World Better By Changing One Thing, I Would Get Rid Of \_\_\_.",
                                            r"I'm Pretty Sure I'm High Right Now, Because I'm Absolutely Mesmerized By \_\_\_.",
                                            r"I'm Sorry, Mrs. Chen, But There Was Nothing We Could Do. At 4:15 This Morning, Your Son Succumbed To \_\_\_.", r"I'm Sorry, Sir, But We Don't Allow \_\_\_ At The Country Club.",
                                            r"If You Can't Handle \_\_\_, You'd Better Stay Away From \_\_\_.", r"If You Had To Describe The Card Czar, Using Only One Of The Cards In Your Hand, Which One Would It Be? \_\_\_.",
                                            r"In His Farewell Address, George Washington Famously Warned Americans About The Dangers Of \_\_\_.",
                                            r"In His New Action Comedy, Jackie Chan Must Fend Off Ninjas While Also Dealing With \_\_\_.", r"In Return For My Soul, The Devil Promised Me \_\_\_, But All I Got Was \_\_\_.",
                                            r"In The Beginning, There Was \_\_\_. And The Lord Said, 'Let There Be \_\_\_.'", r"It Lurks In The Night. It Hungers For Flesh. This Summer, No One Is Safe From \_\_\_.",
                                            r"James Is A Lonely Boy. But When He Discovers A Secret Door In His Attic, He Meets A Magical New Friend: \_\_\_.",
                                            r"Life's Pretty Tough In The Fast Lane. That's Why I Never Leave The House Without \_\_\_.",
                                            r"Listen Gary, I Like You. But If You Want That Corner Office, You're Going To Have To Show Me \_\_\_.", r"Man, This Is Bullshit. Fuck \_\_\_.",
                                            r"My Grandfather Worked His Way Up From Nothing. When He Came To This Country, All He Had Was The Shoes On His Feet And \_\_\_.",
                                            r"Now In Bookstores: 'The Audacity Of \_\_\_' By Barack Obama.", r"Oprah's Book Of The Month Is '\_\_\_ For \_\_\_: A Story Of Hope.'",
                                            r"Patient Presents With \_\_\_. Likely A Result Of \_\_\_.",
                                            r"Puberty Is A Time Of Change. You Might Notice Hair Growing In New Places. You Might Develop An Intrest In \_\_\_. This Is Normal.",
                                            r"She's Up All Night For Good Fun. I'm Up All Night For \_\_\_.", r"The Japanese Have Developed A Smaller, More Efficient Version Of \_\_\_.",
                                            r"The Six Things I Could Never Do Without: Oxygen, Facebook, Chocolate, Netflix, Friends, And \_\_\_ LOL!",
                                            r"This Is America. If You Don't Work Hard, You Don't Succeed. I Don't Care If You're Black, White, Purple, Or \_\_\_.",
                                            r"This Is The Prime Of My Life. I'm Young, Hot, And Full Of \_\_\_.", r"This Year's Hottest Album Is '\_\_\_' By \_\_\_.",
                                            r"To Become A True Yanomami Warrior, You Must Prove That You Can Withstand \_\_\_ Without Crying Out.",
                                            r"Tonight We Will Have Sex. And Afterwards, If You'd Like, A Little Bit Of \_\_\_.", r"We Never Did Find \_\_\_, But Along The Way We Sure Learned A Lot About \_\_\_.",
                                            r"Well If \_\_\_ Is Good Enough For \_\_\_, It's Good Enough For Me.",
                                            r"Well What Do You Have To Say For Yourself, Casey? This Is The Third Time You've Been Sent To The Principal's Office For \_\_\_.",
                                            r"Wes Anderson's New Film Tells The Story Of A Precocious Child Coming To Terms With \_\_\_.", r"What Killed My Boner? \_\_\_.", r"What's Fun Until It Gets Weird? \_\_\_.",
                                            r"What's Making Things Awkward In The Sauna? \_\_\_.", r"When I Was A Kid, We Used To Play Cowboys And \_\_\_.", r"WHOOO! God Damn I Love \_\_\_!",
                                            r"Why Am I Broke? \_\_\_.", r"Why Won't You Make Love To Me Anymore? Is It \_\_\_?", r"Y'all Ready To Get This Thing Started? I'm Nick Cannon, And This Is America's Got \_\_\_.",
                                            r"Yo' Mama's So Fat She \_\_\_!", r"You Are Not Alone. Millions Of Americans Struggle With \_\_\_ Every Day.",
                                            r"You Guys, I Saw This Crazy Movie Last Night. It Opens On \_\_\_, And Then There's Some Stuff About \_\_\_, And Then It Ends With \_\_\_.",
                                            r"You Know, Once You Get Past \_\_\_, \_\_\_ Ain't So Bad.", r"You Won't Believe These 15 Hilarious \_\_\_ Bloopers!",
                                            r"You've Seen The Bearded Lady! You've Seen The Ring Of Fire! Now, Ladies And Gentlemen, Feast Your Eyes Upon \_\_\_!"
                                            ]
                        extension_whites = ["10 Incredible Facts About The Anus", "40 Acres And A Mule", "A Bass Drop So Huge It Tears The Starry Vault Asunder To Reveal The Face Of God",
                                            "A Bunch Of Idiots Playing A Card Game Instead Of Interacting Like Normal Humans", "A Buttload Of Candy", "A Chimpanzee In Sunglasses Fucking Your Wife",
                                            "A Constant Need For Validation", "A Crazy Little Thing Called Love", "A Dance Move That's Just Sex", "A Disappointing Salad", "A Face Full Of Horse Cum","A Fart",
                                            "A For-Real Lizard That Spits Blood From Its Eyes", "A Gender Identity That Can Only Be Conveyed Through Slam Poetry","A Giant Powdery Manbaby", "A Hopeless Amount Of Spiders",
                                            "A Horse With No Legs", "A Kiss On The Lips", "A Lil' Stupid Ass Bitch", "A Man Who Is So Cool That He Rides On A Motorcycle", "A Manhole", "A Mouthful Of Potato Salad",
                                            "A Native American Who Solves Crimes By Going Into The Spirit World", "A One-Way Ticket To Gary, Indiana", "A Peyote-Fueled Vision Quest", "A Pizza Guy Who Fucked Up",
                                            "A Possible Muslim", "A Reason Not To Commit Suicide", "A Self-Microwaving Burrito", "A Sex Comet From Neptune That Plunges The Earth Into Eternal Sexiness",
                                            "A Sex Goblin With A Carnival Penis", "A Shiny Rock That Proves I Love You", "A Team Of Lawyers", "A Thrilling Chase Over The Rooftops Of Rio De Janeiro", "A Turd",
                                            "A Ugandan Warlord", "A Whole Lotta Woman", "A Whole New Kind Of Porn", "A Woman", "A Zero-Risk Way To Make $2,000 From Home",
                                            "Actual Mutants With Medical Conditions And No Superpowers", "Africa", "Aids Monkeys", "All The Single Ladies", "All These Decorative Pillows",
                                            "Almost Giving Money To A Homeless Person", "Ambiguous Sarcasm", "An Inability To Form Meaningful Relationships", "An Interracial Handshake",
                                            "An Oppressed People With A Vibrant Culture", "An Overwhelming Variety Of Cheeses", "An Unforgettable Quinceañera", "An Uninterrupted History Of Imperialism And Exploitation",
                                            "Anal Fissures Like You Wouldn't Believe", "Ancient Athenian Boy-Fucking",
                                            "Angelheaded Hipsters Burning For The Ancient Heavenly Connection To The Starry Dynamo In The Machinery Of Night", "Ass To Mouth", "Backwards Knees",
                                            "Bathing In Moonsblood And Dancing Around The Ancient Oak", "Being A Terrible Mother", "Being John Malkovich", "Being Nine Years Old", "Being Paralyzed From The Neck Down",
                                            "Being Popular And Good At Sports", "Being Worshipped As The One True God", "Beloved Television Star Bill Cosby", "Blackface", "Blackula", "Blowjobs For Everyone",
                                            "Boring Vaginal Sex", "Bouncing Up And Down", "Breastfeeding A Ten-Year-Old", "Bullets", "Butt Stuff", "Calculating Every Mannerism So As Not To Suggest Homosexuality",
                                            "Cancer", "Changing A Person's Mind With Logic And Facts", "Child Protective Services", "Child Support Payments", "Common-Sense Gun Control Legislation",
                                            "Cool, Relatable Cancer Teens", "Crazy Opium Eyes", "Crippling Social Anxiety", "Crying And Shitting And Eating Spaghetti", "Cute Boys",
                                            "Cutting Off A Flamingo's Legs With Garden Shears", "Daddy", "Daddy's Credit Card", "Deez Nuts", "Dem Titties", "Depression", "Doing The Right Stuff To Her Nipples", "Doo-Doo",
                                            "Drinking Responsibly", "Eating Together Like A God Damn Family For Once", "Eggs", "Ejaculating Inside Another Man's Wife", "Ejaculating Live Bees And The Bees Are Angry",
                                            "Ennui", "Every Ounce Of Charisma Left In Mick Jagger's Tired Body", "Exploding Pigeons", "Falling Into The Toilet", "Figuring Out How To Have Sex With A Dolphin",
                                            "Filling A Man's Anus With Concrete", "Finally Finishing Off The Indians", "Free Ice Cream, Yo", "Fresh Dill From The Patio", "Fucking A Corpse Back To Life",
                                            "Generally Having No Idea What's Going On", "Genghis Khan's DNA", "Getting All Offended", "Getting Caught By The Police And Going To Jail",
                                            "Getting Down To Business To Defeat The Huns", "Getting Drive-By Shot", "Getting Eaten Alive By Guy Fieri", "Getting Offended", "Getting Shot By The Police",
                                            "Getting Shot Out Of A Cannon", "Giant Sperm From Outer Space", "Going Down On A Woman, Discovering That Her Vagina Is Filled With Eyeballs, And Being Totally Into That",
                                            "Going Inside At Some Point Because Of The Mosquitoes", "Going To A High School Reunion On Ketamine", "Grammar Nazis Who Are Also Regular Nazis",
                                            "Growing Up Chained To A Radiator In Perpetual Darkness", "Gwyneth Paltrow's Opinions", "Having Been Dead For A While", "How Awesome I Am", "Immortality Cream",
                                            "Important News About Taylor Swift", "Injecting Speed Into One Arm And Horse Tranquilizer Into The Other", "Interspecies Marriage", "Irrefutable Evidence That God Is Real","Jizz",
                                            "Kale", "Khakis", "Letting Out 20 Years' Worth Of Farts", "Like A Million Alligators", "Lots And Lots Of Abortions", "Meaningless Sex", "Mediocrity",
                                            "Moderate-To-Severe Joint Pain", "Mom's New Boyfriend", "Morpheus", "My Boyfriend's Stupid Penis", "My Dad's Dumb Fucking Face", "My Dead Son's Baseball Glove", "My First Period",
                                            "My Sex Dungeon", "My Worthless Son", "Neil Diamond's Greatest Hits", "Never Having Sex Again", "No Clothes On, Penis In Vagina",
                                            "No Longer Finding Any Cards Against Humanity Card Funny", "Not Believing In Giraffes", "Oil!", "One Unforgettable Night Of Passion", "Our New Buffalo Chicken Dippers®!",
                                            "Out-Of-This-World Bazongas", "Owls, The Perfect Predator", "P.F. Chang Himself", "Party Mexicans", "Peeing Into A Girl's Butt To Make A Baby", "Potato",
                                            "Prince Ali, Fabulous He, Ali Ababwa", "Pussy", "Rabies", "Reading The Entire End-User License Agreement", "Ripping A Dog In Half", "Robots Who Just Want To Party",
                                            "Russian Super-Tuberculosis", "Seeing My Village Burned And My Family Slaughtered Before My Eyes", "Seeing Things From Hitler's Perspective", "September 11th, 2001",
                                            "Setting My Balls On Fire And Cartwheeling To Ohio", "Shapes And Colors", "Sharks With Legs", "Shitting All Over The Floor Like A Bad, Bad Girl",
                                            "Slowly Easing Down Onto A Cucumber", "Smoking Crack, For Instance", "Snorting Coke Off A Clown's Boner", "Social Justice Warriors With Flamethrowers Of Compassion",
                                            "Some Shit-Hot Guitar Licks", "Some Sort Of Asian", "Sports", "Storing A Bunch Of Acorns In My Pussy", "Stuffing A Child's Face With Fun Dip® Until He Starts Having Fun",
                                            "Stupid", "Such A Big Boy", "Sucking All The Milk Out Of A Yak", "Sudden Penis Loss", "Teaching A Girl How To Handjob The Penis", "Texas", "The Abercrombie & Fitch Lifestyle",
                                            "The All-New Nissan Pathfinder With 0.9% APR Financing!", "The Amount Of Gay I Am", "The Basic Suffering That Pervades All Of Existence", "The Best Taquito In The Galaxy",
                                            "The Black Half Of Barack Obama", "The Color 'Puce'", "The Complex Geopolitical Quagmire That Is The Middle East", "The Dentist",
                                            "The Eight Gay Warlocks Who Dictate The Rules Of Fashion", "The Eighth Graders", "The Euphoric Rush Of Strangling A Drifter", "The Ghost Of Marlon Brando",
                                            "The Haunting Stare Of An Iraqi Child", "The Inability To Form Meaningful Relationships", "The Male Gaze", "The Passage Of Time", "The Peaceful And Nonthreatening Rise Of China",
                                            "The Power Of The Dark Side", "The Right Amount Of Cocaine", "The Safe Word", "The Secret Formula For Ultimate Female Satisfaction", "The Size Of My Penis",
                                            "The Sweet Song Of Sword Against Sword And The Braying Of Mighty War Beasts", "The Swim Team, All At Once", "The Tiger That Killed My Father",
                                            "The Tiniest Shred Of Evidence That God Is Real", "The Unbelievable World Of Mushrooms", "The White Half Of Barack Obama", "Three Consecutive Seconds Of Happiness",
                                            "Throwing Stones At A Man Until He Dies", "Too Much Cocaine", "Total Fucking Chaos", "Treasures Beyond Your Wildest Dreams", "Turning The Rivers Red With The Blood Of Infidels",
                                            "Two Whales Fucking The Shit Out Of Each Other", "Unquestioning Obedience", "Unrelenting Genital Punishment", "Unsheathing My Massive Horse Cock", "Vegetarian Options",
                                            "Walking Into A Glass Door", "Wearing Glasses And Sounding Smart", "Western Standards Of Beauty", "What Jesus Would Do", "Whatever A McRib® Is Made Of",
                                            "Whatever You Wish, Mother", "Whispering All Sexy"
                                            ]
                    elif deck == "green":
                        extension_blacks = [r"\_\_\_ Be All Like \_\_\_.", r"\_\_\_: Brought To You By \_\_\_.", r"Art Isn't Just A Painting In A Stuffy Museum. Art Is Alive. Art Is \_\_\_.",
                                            r"As Reparations For Slavery, All African Americans Will Receive \_\_\_.", r"As Teddy Roosevelt Said, The Four Manly Virtues Are Honor, Temperance, Industry, And \_\_\_.",
                                            r"Best You Go Back Where You Came From, Now. We Don't Take Too Kindly To \_\_\_ In These Parts.", r"CNN Breaking News! Scientists Discover \_\_\_.",
                                            r"Coming To Red Lobster® This Month, \_\_\_.",
                                            r"Congratulations! You Have Been Selected For Our Summer Internship Program. While We Are Unable To Offer A Salary, We Can Offer You \_\_\_.",
                                            r"Dance Like There's Nobody Watching, Love Like You'll Never Be Hurt, And Live Like You're \_\_\_.", r"Errbody In The Club \_\_\_.", r"Feeling So Grateful! #Amazing #MyLife #\_\_\_.",
                                            r"Girls Just Wanna Have \_\_\_.", r"Google Calendar Alert: \_\_\_ In 10 Minutes.", r"I Don't Believe In God. I Believe In \_\_\_.",
                                            r"I Got Rhythm, I've Got Music, I've Got \_\_\_. Who Could Ask For Anything More?", r"I May Not Be Much To Look At, But I Fuck Like \_\_\_.",
                                            r"I Tell You, It Was A Non-Stop Fuckfest. When It Was Over, My Asshole Looked Like \_\_\_.", r"I'll Take The BBQ Bacon Burger With Friend Egg And Fuck It How About \_\_\_.",
                                            r"I'm Sorry, Sir, But Your Insurance Plan Doesn't Cover Injuries Caused By \_\_\_.",
                                            r"I've Had A Horrible Vision, Father. I Saw Mountains Crumbling, Stars Falling From The Sky. I Saw \_\_\_.", r"If At First You Don't Succeed, Try \_\_\_.",
                                            r"In The 1950s, Psychologists Prescribed \_\_\_ As A Cure For Homosexually.", r"LSD + \_\_\_ = Really Bad Time.",
                                            r"Mom's To-Do List: Buy Groceries, Clean Up \_\_\_, Soccer Practice.", r"Most Americans Would Not Vote For A Candidate Who Is Openly \_\_\_.",
                                            r"No, No, No, No, No, No, NO! I Will NOT Let \_\_\_ Ruin This Wedding.", r"Oh No! Siri, How Do I Fix \_\_\_?",
                                            r"One More Thing. Watch Out For Big Mike. They Say He Killed A Man With \_\_\_.", r"Ooo, Daddy Like \_\_\_.",
                                            r"Poor Brandon, Still Living In His Parent's Basement. I Heard He Never Got Over \_\_\_.", r"Run, Run, As Fast As You Can! You Can't Catch Me, I'm \_\_\_!",
                                            r"She's A Lady In The Streets, \_\_\_ In The Sheets.", r"She's Just One Of The Guys, You Know? She Likes Beer, And Football, And \_\_\_.",
                                            r"Son, Take It From Someone Who's Been Around The Block A Few Times. Nothin' Puts Her In The Mood Like \_\_\_.", r"Summer Lovin', Had Me A Blast. \_\_\_, Happened So Fast.",
                                            r"The Top Google Auto-Complete Results For 'Barack Obama': Barack Obama Height, Barack Obama Net Worth, Barack Obama \_\_\_.",
                                            r"Then The Princess Kissed The Frog, And All Of A Sudden The Frog Was \_\_\_!", r"There Is No God. It's Just \_\_\_ And Then You Die.",
                                            r"This Friday At The Liquid Lounge, It's \_\_\_ Night! Ladies Drink Free.", r"We Do Not Shake With Our Left Hands In This Country. That Is The Hand We Use For \_\_\_.",
                                            r"Well If \_\_\_ Is A Crime, Then Lock Me Up!", r"Well, Shit. My Eyes Ain't So Good, But I'll Eat My Own Boot If That Ain't \_\_\_!",
                                            r"What Are All Those Whales Singing About? \_\_\_.", r"What Sucks Balls? \_\_\_.", r"What Totally Destroyed My Asshole? \_\_\_.", r"What Turned Me Into A Republican? \_\_\_.",
                                            r"What Will End Racism Once And For All? \_\_\_.", r"What's A Total Waste Of Hillary Clinton's Time? \_\_\_.", r"What's About To Take Dance Floor To The Next Level? \_\_\_.",
                                            r"What's The Gayest? \_\_\_.", r"What's The Most Problematic? \_\_\_.", r"Why Am I Laughing And Crying And Taking Off My Clothes? \_\_\_.",
                                            r"With A One-Time Gift Of Just $10, You Can Save This Child From \_\_\_.", r"You Know Who Else Liked \_\_\_? Hitler.", r"You Won't Believe What's In My Pussy. It's \_\_\_."
                                            ]
                        extension_whites = ["10 Football Players With Erections Barrelling Towards You At Full Speed", "10,000 Shrieking Teenage Girls", "A Big Ol' Plate Of Fettuccini Alfredo",
                                            "A Big, Beautiful Mouth Packed To The Brim With Sparkling White Teeth", "A Black Friend", "A Burrito That's Just Sour Cream",
                                            "A Cheerfulness That Belies A Deep-Seated Self-Loathing", "A Cold And Indifferent Universe", "A Creature Made Of Penises That Must Constantly Arouse Itself To Survive",
                                            "A Creepy Child Singing A Nursery Rhyme", "A Dolphin That Learns To Talk And Becomes The Dean Of Harvard Law School", "A Duffel Bag Full Of Lizards", "A Finger Up The Butt",
                                            "A Genetic Predisposition For Alcoholism", "A Gun That Shoots Cobras", "A Hug", "A Long Business Meeting With No Obvious Purpose",
                                            "A Man In A Suit With Perfect Hair Who Tells You Beautiful Lies", "A Man With The Head Of A Goat And The Body Of A Goat", "A Massive Collection Of Child Pornography",
                                            "A Medium Horchata", "A Negative Body Image That Is Totally Justified", "A Slowly Encroaching Circle Of Wolves", "A Strong Horse And Enough Rations For Thirty Days",
                                            "A Terrified Fat Child Who Won't Come Out Of The Bushes", "A Tiny Fireman Who Puts Out Tiny Fires", "A Weird Guy Who Says Weird Stuff And Weirds Me Out", "A Woman's Perspective",
                                            "A Woman's Right To Choose", "Aborting The Shit Out Of A Fetus", "Albert Einstein But If He Had Huge Muscles And A Rhinoceros Cock", "All The People I've Killed",
                                            "An Arrangement Wherein I Give A Person Money And They Have Sex With Me", "An Empowered Woman", "An Incurable Homosexual", "An Old Dog Dragging Its Anus Across The Floor",
                                            "An Old Dog Full Of Tumors", "An Older Man", "An X-Man Whose Power Is That He Has Sex With Dogs And Children", "Anal", "Antidepressants", "Art", "Assassinating The President",
                                            "Awesome Pictures Of Planets And Stuff", "Bad Emotions I Don't Want", "Becoming The President Of The United States", "Being Sexually Attracted To Children",
                                            "Being Turned Into Sausages", "Beyoncé", "Big, Smart Money Boys Tap-Tapping On Their Keyboards", "Blossoming Into A Beautiful Young Woman",
                                            "Breastfeeding In Public Like A Radiant Earth Goddess", "Brunch", "Catching A Live Salmon In Your Mouth", "Child Labor", "China", "Chipotle", "Chris Hemsworth",
                                            "Comprehensive Immigration Reform", "Condoleezza Rice", "Consensual, Nonreproductive Incest", "Content", "Crazy Anal Orgasms", "Creamy Slices Of Real, California Avocado",
                                            "Critical Thinking", "Crushing The Patriarchy", "Daddy Going Away Forever", "Defeating A Gorilla In Single Combat", "Denying The Holocaust", "Dis Bitch",
                                            "Discovering That What I Really Want In Life Is To Kill People And Have Sex With Their Corpses", "Doing A Somersault And Barfing", "Dominating A Man By Peeing On His Eldest Son",
                                            "Doritos And A Fruit Roll-Up", "Dropping Dead In A Sbarro's Bathroom And Not Being Found For 72 Hours", "Dumpster Juice", "Eating Ass",
                                            "Eating Pebbles, Shitting The Pebbles, The Eating The Shit-Pebbles, And Then Shitting Those Pebbles Again", "Eating People",
                                            "Eating Too Many Cinnabons And Then Vomiting And Then Eating The Vomit", "Ejaculating At The Apex Of A Cartwheel", "Esmeralda, My Most Beautiful Daughter",
                                            "Eternal Screaming Madness", "Every Man's Ultimate Fantasy: A Perfectly Cylindrical Vagina", "Everything", "Exploring Each Other's Buttholes",
                                            "Facilitating Dialogue And Deconstructing Binaries", "Falling Into A Pit Of Waffles", "Farting A Huge Shit Out Of My Pussy",
                                            "Farting All Over My Face With Your Tight Little Asshole", "Feeling The Emotion Of Anger", "Feminism", "Film Roles For Actresses Over 40", "Finding A Nice Elevator To Poop In",
                                            "Forty-Five Minutes Of Finger Blasting", "Founding A Major World Religion", "Fucking Me Good And Taking Me To Red Lobster®", "Fucking My Therapist", "Gary", "Gay Thoughts",
                                            "Gayle From HR", "Gazpacho", "Getting Aborted", "Getting Blasted In The Face By A T-Shirt Cannon", "Getting Eaten Out By A Dog", "Getting High With Mom",
                                            "Getting Killed And Dragged Up A Tree By A Leopard", "Getting Laid Like All The Time", "Getting Naked Too Soon", "Getting Pegged", "Getting The Dorito Crumbs Out Of My Pubes",
                                            "Getting This Party Started!", "Getting Trapped In A Conversation About Ayn Rand", "Going Around Pulling People's Tampons Out", "Going To Bed At A Reasonable Hour",
                                            "Gregor, My Largest Son", "Grunting For Ten Minutes And Then Peeing Sand", "Guns", "Happy Daddies With Happy Sandals", "Hating Jews", "Having A Vagina",
                                            "Having An Awesome Time Drinking And Driving", "Having Sex With A Beautiful Person", "Having Sex With A Man And Then Eating His Head", "Having Sex With Your Mom",
                                            "Holding The Proper Political Beliefs Of My Time To Attract A Mate", "Homework", "Hot Lettuce", "How Good Lead Paint Taste", "How Great My Ass Looks In These Jeans",
                                            "How Sad It Will Be When Morgan Freeman Dies", "How Strange It Is To Be Anything At All", "Huge Big Balls Full Of Jizz", "Informing You That I Am A Registered Sex Offender",
                                            "ISIS", "It Being Too Late To Stop Having Sex With A Horse", "Jason, The Teen Mayor", "Jazz", "Jeff Bezos", "Just Now Finding Out About The Armenian Genocide",
                                            "Late-Stage Dementia", "Libertarians", "Loud, Scary Thunder", "Making Out And Stuff", "Math", "Meatloaf, The Food", "Meatloaf, The Man", "Melanin", "Menopause", "Mental Illness",
                                            "Microaggressions", "Misogyny", "Mixing M&Ms And Skittles Like Some Kind Of Psychopath", "Mommy And Daddy Fighting All The Time", "Moon People", "Munchin' Puss",
                                            "My Brother's Hot Friends", "My Dog Dying", "My Huge Penis And Substantial Fortune", "Objectifying Women", "One Of Them Big-City Jew Lawyers",
                                            "One Of Those 'Blow Jobs' I've Been Hearing So Much About", "Onions", "Opening Your Mouth To Talk And A Big Penis Flops Out", "Our Baby", "Out-Of-Control Teenage Blowjob Parties",
                                            "Overthrowing The Democratically-Elected Government Of Chile", "Participating", "Period Poops", "Picking Up A Glass Of Water And Taking A Sip And Being The President",
                                            "Playing My Asshole Like A Trumpet", "Plowing That Ass Like A New England Corn Farmer", "Political Correctness", "Pooping In A Leotard And Hoping No One Notices",
                                            "Pooping In The Potty", "Prematurely Ejaculating Like A Total Loser", "Pretending To Be One Of The Guys But Actually Being The Spider God", "Putting More Black People In Jail",
                                            "Quacking Like A Duck In Lieu Of A Cogent Argument", "Quinoa", "Raising Three Kids On Minimum Wage", "Reaching An Age Where Barbecue Chips Are Better Than Sex",
                                            "Regurgitating A Half-Digested Sparrow", "Restoring Germany To Its Former Glory", "Rock-Hard Tits And A Huge Vagina", "Rolling So Hard", "Rubbing My Bush All Over Your Bald Head",
                                            "Salsa Night At Dave's Cantina", "Scissoring, If That's A Thing", "Seizing Control Of The Means Of Production", "Self-Identifying As A DJ",
                                            "Showering Praise Upon The Sultan's Hideous Daughters", "Showing All The Boys My Pussy", "Slamming A Dunk", "Smashing My Balls At The Moment Of Climax", "Some Of That Good Dick",
                                            "Some Real Spicy Shrimps", "Starting A Shitty Podcast", "Straight Blazin' 24/7", "Sucking Each Other's Penises For Hours On End", "Sudden And Unwanted Slam Poetry",
                                            "Systems And Policies Designed To Preserve Centuries-Old Power Structures", "Tables", "Taking The Form Of A Falcon", "Tender Chunks Of All-White-Meat Chicken", "That Bitch, Stacy",
                                            "That Chicken From Popeyes ®", "The Amount Of Baby Carrots I Can Fit Up My Ass", "The Best, Deepest Quotes From The Dark Knight", "The Body Of A 46-Year-Old Man",
                                            "The Bond Between A Woman And Her Horse", "The Clown That Followed Me Home From The Grocery Store", "The Fear And Hatred In Men's Hearts",
                                            "The Feeling Of Going To McDonald's As A 6-Year-Old", "The Flaming Wreckage Of The International Space Station", "The Full Force Of The American Military",
                                            "The Full-Blown Marginalization Of Ugly People", "The Government", "The Graceful Path Of An Autumn Leaf As It Falls To Its Earthen Cradle", "The Hottest Milf In Dallas",
                                            "The LGBT Community", "The Lived Experience Of African Americans", "The Mysterious Fog Rolling Into Town", "The Ol' Penis-In-The-Popcorn Surprise", "The Rwandan Genocide",
                                            "The Secret To Truly Resilient Hair", "The Sweet, Forbidden Meat Of The Monkey", "The Wind", "Thinking About What Eating Even Is", "Three Hours Of Nonstop Penetration",
                                            "Tiny, Rancid Girl Farts", "Trees", "Trevor, The World's Greatest Boyfriend", "Turning 32", "Twenty Bucks", "Twenty Cheerleaders Laughing At Your Tiny Penis",
                                            "Twisting My Cock And Balls Into A Balloon Poodle", "Two Beautiful Pig Sisters","Two Shitty Kids And A Garbage Husband", "Waking Up Inside Of A Tornado",
                                            "Watching A Hot Person Eat", "Watching You Die", "Water", "When The Big Truck Goes 'Toot! Toot!'", "Who Really Did 9/11", "Whomsoever Let The Dogs Out",
                                            "Whooping Your Ass At Mario Kart", "Working So Hard To Have Muscles And Then Having Them", "You"
                                            ]
                    elif deck == "crabs":
                        extension_blacks = [r"\_\_\_: Just Sayin'.", r"\_\_\_: Not Even Once.", r"According To A New UN Treaty, \_\_\_ Now Qualifies As A Weapon Of Mass Destruction.",
                                            r"Ever Since 'The Incident,' Every Time I Close My Eyes, I Still See \_\_\_.",
                                            r"Gentlemen, I'm Sure You're Wondering Why I Asked You Here This Evening. It's A Long Story, But It All Began With \_\_\_.", r"How Did I Get This Restraining Order? \_\_\_.",
                                            r"How Did I Hurt My Back? \_\_\_.", r"How Did My Grandparents Make It Through The Great Depression? \_\_\_.", r"I Am Become \_\_\_, The Destroyer Of Worlds.",
                                            r"I Love The Smell Of \_\_\_ In The Morning.", r"I'm So Hungry, I Could Eat \_\_\_.", r"If You Want A Picture Of The Future, Imagine A Boot Stamping On \_\_\_ - Forever.",
                                            r"In A Move That Has Hollywood Insiders Baffled, The Producers Of American Idol Have Decided To Replace Host Ryan Seacrest With \_\_\_.",
                                            r"In My Opinion, \_\_\_ Is Grounds For Justifiable Homicide.", r"It Took Seven Years In A Remote Tibetan Monastery, But I Finally Learned The Art Of \_\_\_.",
                                            r"Like Midas Reborn, Everything She Touches Turns To \_\_\_.", r"Oh My God! They Killed \_\_\_! You Bastards!", r"The Best Part Of Waking Up Is \_\_\_.",
                                            r"Tonight On 'My Super Sweet 16,' Stephani's Parents Give Her \_\_\_.", r"What Do We Want? \_\_\_! When Do We Want It? Now!",
                                            r"What Was One Of The Rejected Flavors For Bertie Bott's Every Flavour Beans™️? \_\_\_.", r"Why Won't They Let Me In Chuck E. Cheese's® Anymore? \_\_\_.",
                                            r"William Shatner's Shocking New Autobiography Is Titled '\_\_\_: The Final Frontier.'", #End of Volume 1 One-Answer Black Cards
                                            r"\_\_\_: It's Magically Delicious.", r"\_\_\_? That's What She Said.", r"'You Have My Sword.' 'And You Have My Bow.' 'And My \_\_\_!'",
                                            r"A New Russian Dash-Cam Video Shows \_\_\_, Right There In The Middle Of The Street!",
                                            r"Apple® Has Announced A New Device That Promises To Revolutionize The Way We Think About \_\_\_.",
                                            r"Audiences At Sundance Were Traumatized By Lars Von Trier's Controversial New Film, '\_\_\_.'", r"Dear Dan Savage, Please Help. I Am Unable To Achieve Orgasm Without \_\_\_.",
                                            r"Experts Say That Without Careful Management And Conservation, \_\_\_ Will Disappear Within Our Lifetimes.",
                                            r"From The People Who Brought You Sharktopus And Sharknado, Syfy's® Next Horror Film Combines Sharks With \_\_\_.",
                                            r"Having Abandoned His Pleas For A Return To The Gold Standard, Ronn Paul Is Now Promoting A \_\_\_-Based Economy.",
                                            r"Hey Man, You Gonna Come Check Out My Show Tonight? My New Band Is Called '\_\_\_.'", r"I Don't Care What People Say, \_\_\_ Is Not A Crime.",
                                            r"I Have To Admit... It Took Me A While To Agree To It, But Incorporating \_\_\_ Into Our Wedding Cerenomy Is A Decision I Will Never Regret.",
                                            r"I Quit My Job As A Bartender The Night Some Jackass Left Me \_\_\_ As A Tip.", r"I Think I Need To Take Fluffums To Puppy Training: He Has This Terrible Habit Of \_\_\_.",
                                            r"I Wish It Were Something Simple - Like Peanuts Or Shellfish - But My Doctor Tells Me I'm Actually Allergic To \_\_\_.",
                                            r"If People Wouldn't Be So Quick To Judge, I Would Give \_\_\_ To The Last Czar In A Heartbeat.",
                                            r"Michelle Obama Outraged Conservatives When She Implied That \_\_\_ Maybe Wasn't Such A Bad Thing",
                                            r"My Tour Of The White House Radically Escalated When Secret Service Caught A Glimpse Of \_\_\_ In My Bag.",
                                            r"Now That He Has Retired, Pope Benedict Can Finally Devote Time To His True Passion: \_\_\_.", r"Oh, So You Think You're Too Good For Us Now, Little 'Miss \_\_\_!'",
                                            r"WANTED: A Clean, Well-Lit Place For \_\_\_.", r"What I Gotta Give My Boo To Get Outta The Doghouse? \_\_\_.", r"When You Play The Game Of \_\_\_, You Win Or You Die.",
                                            r"Why Won't Anyone Sit With Me? \_\_\_.", #End of Volume 2 One-Answer Black Cards
                                            r"\_\_\_, Just For A Second. Just To See How It Feels.", r"\_\_\_: Ain't Nobody Got Time For That!", r"\_\_\_: I Volunteer As Tribute!",
                                            r"\_\_\_: Provided By The Management For Your Protection.", r"\_\_\_: Your Ideas Are Intriguing To Me And I Wish To Subscribe To Your Newsletter.",
                                            r"Before I Got Laid Off, I Never Pictured A Career In \_\_\_.", r"How Did I Get Through College? \_\_\_.", r"I Do Declare, In Times Of Distress I Have Always Relied On \_\_\_.",
                                            r"I Do Wish The Newspapers Hadn't Mentioned \_\_\_ In Grandpa's Obituary.", r"In Valhalla, It Is Said That All Brave Warriors Are Given \_\_\_.",
                                            r"Old Willy Used To Be Just Like You Or Me, Before \_\_\_ Got Ahold Of Him.", r"Rumor Is, Kim Jong-Un Is Executing Prisoners With \_\_\_.",
                                            r"Utah Is Considering The Legalization Of \_\_\_.", r"What Made Me This Way? \_\_\_.", r"What *Really* Gave Superman His Powers? \_\_\_.", r"What Should I Be For Halloween? \_\_\_.",
                                            r"What Will They Carve On My Tombstone? \_\_\_.", r"What's This Town's Best-Kept Secret? \_\_\_.",
                                            r"While Officially Still Frowned On, \_\_\_ Is Now Permitted In The US Armed Forces.", r"Who Will Be First Against The Wall When The Revolution Comes? \_\_\_.",
                                            r"Who's *Really* To Blame? \_\_\_.", r"Yes, It Is I, The World's Most Dangerous Supervillain: Baron Von \_\_\_!", #End of Volume 3 One-Answer Black Cards
                                            r"\_\_\_, You Da Real MVP.", r"\_\_\_: Boil 'Em, Mash 'Em, Stick 'Em In A Stew!", r"\_\_\_: Just Another Way That God Shows Us He Loves Us.", r"\_\_\_: Just Girly Things.",
                                            r"9-1-1, What's Your Emergency? \_\_\_.", r"Bowing To Years Of Pressure, The Washington Redskins Have Officially Been Renamed The Washington \_\_\_.",
                                            r"Coming Soon From Pixar: \_\_\_.", r"During The Lunch Meeting, We Were Shocked To Hear The Boss Reveal Her Obsession With \_\_\_.",
                                            r"From The Producers Of Shark Week... Coming This Fall, \_\_\_ Week.", r"Fuddruckers® Is Secretly Testing A Burger Made With \_\_\_.", r"Go-Go-Gadget \_\_\_!",
                                            r"If Laughter Is The Best Medicine, The Second Best Is \_\_\_.", r"If You Wanna Be My Lover, You Gotta Get With \_\_\_.",
                                            r"In A New Novel By Nicholas Sparks, A Young Girl Tragically Falls In Love With \_\_\_.", r"In His Final Interview, Robin Williams Discussed His Private Battle With \_\_\_.",
                                            r"My Psychic Warns That My Future Is Filled With \_\_\_.", r"Ooooooohh Yeah, Baby You Know What I Like. Gimmie \_\_\_.",
                                            r"Scientists Have Discovered The True Cause Of Autism: \_\_\_.", r"Sweet, I Just Got A Groupon For \_\_\_.", r"Thank You Mario! But \_\_\_ Is In Another Castle!",
                                            r"The Restaurant Was Nice, But I Was Surprised To See \_\_\_ On The Menu.", r"The Road To Hell Is Paved With \_\_\_.",
                                            r"There's A New Anime About Four Magical High School Students And Their Adventures With \_\_\_.", r"Today, Amazon.com® Received A Patent On \_\_\_.",
                                            r"What *Exactly* Is Up My Ass? \_\_\_.", r"What's My Safe Word? \_\_\_.", r"You People Are Sick! There's *Nothing* Funny About \_\_\_.", #End of Volume 4 One-Answer Black Cards
                                            r"\_\_\_ Is Many Things To Many People, As You Will See And Learn.", r"\_\_\_: Evidence That *This* Is The Darkest Timeline.", r"\_\_\_: It Even Makes Its Own Gravy!",
                                            r"\_\_\_: My Body Is Ready.", r"\_\_\_: The Struggle Is Real", r"\_\_\_: Wake Up Sheeple!", r"'\_\_\_ Spice' Was One Of The Lesser-Known Spice Girls.",
                                            r"As A Staunch Libertarian, I Believe The Only Role For Government Is \_\_\_.", r"Code Three, Request Backup! I'm Surrounded By \_\_\_!",
                                            r"Could A Brother Get \_\_\_ Up In This Bitch?", r"Forget *Fifty Shades Of Grey...* Give Me *Fifty Shades Of* \_\_\_!",
                                            r"I Never Karaoke, Because I Always End Up Getting Drunk And Singing A Song About \_\_\_.", r"I'm Finally Writing That Book, It's Titled *'Zen And The Art Of* \_\_\_.'",
                                            r"Instructions Unclear: Dick Stuck In \_\_\_.", r"Let It Go! Let It Go! \_\_\_ Never Bothered Me Anyway...", r"My Therapist Says I Have An Unhealthy Attitude About \_\_\_.",
                                            r"Thank You Alex, I'll Take \_\_\_ For 800.", r"Turn Down For What? \_\_\_.", r"What Really Brings Out The Child In Me? \_\_\_.", r"What Would *You* Do For A Klondike® Bar? \_\_\_.",
                                            r"Whatever Else May Change, One Thing Is Certain: You Can't Unfuck \_\_\_.", r"When I Was Young, The Only Thing That Kept Me Off The Streets Was \_\_\_.",
                                            r"Why Do I Need Feminism? \_\_\_.", r"Why Is Jon Stewart *Really* Retiring? \_\_\_.", r"Why So Salty? \_\_\_.", r"Yo Bro, You Tried \_\_\_? Shit's Straight Fire.",
                                            r"You Kids With Your Fancy Degrees... They Don't Teach Ya' Nothin' 'Bout \_\_\_ In School.", #End of Volume 5 One-Answer Black Cards
                                            r"\_\_\_: Not Only, Like, Super Gross? But Like, From A Feminist Standpoint? Totallyproblematic.", r"\_\_\_? Thanks Obama.",
                                            r"'The Time Has Come,' The Walrus Said, 'To Talk Of Many Things: Of Shoes, And Ships, And Sealing-Wax. Of Cabbages, And \_\_\_.",
                                            r"Although \_\_\_ Provided Excellent Results, The Ethics Committee Has Decided That The Practice Can No Longer Continue.", r"Amazon Prime Membership Now Includes \_\_\_.",
                                            r"Chilean Seabass: $29. Caribbean Spiny Lobster: $38. \_\_\_: Market Price.", r"Citing Demographics, Playboy Has Replaced Nudity With \_\_\_.",
                                            r"Come With Me On An Adventure To The Land Of \_\_\_.", r"George RR Martin Says That \_\_\_ Is Preventing Him From Finishing His Epic Fantasy Saga.",
                                            r"Grandma Told Me 'Child, Everyone On This Earth Was Born With A Skill, And Yours Is \_\_\_... So Don't You Never Do It For Free.",
                                            r"If He Were Elected President, What Would Bernie Sanders Bring To The White House? \_\_\_.",
                                            r"If You Enjoy \_\_\_, It's Because You Are Weak, Your Bloodline Is Weak, And You Will Not Survive The Winter.",
                                            r"In His New Book, Author David Sedaris Details His Life-Long Love Affair With \_\_\_.", r"In Order To Stop My Family From Talking Politics, I Distract Them With \_\_\_.",
                                            r"In The Years Ahead, Pundits Will Debate The Impact Of The \_\_\_-Gate Scandal On Obama's Legacy.",
                                            r"In Today's News Conference, Donald Trump Made Headlines When He Denounced \_\_\_.",
                                            r"In What Some Are Calling An Act Of Desperation, The Conservative Billionaire Koch Brothers Are Funding \_\_\_.", r"Mmmmm, \_\_\_! ...And It's Still Warm!",
                                            r"My Uncle Has A Wardrobe In His House That Leads To \_\_\_.", r"New Kicks, New Clothes, \_\_\_ On Fleek: Friday Night, Here I Come.",
                                            r"Pardon Me, May I Have A Moment Of Your Time To Talk To You About \_\_\_?", r"SHOW ME WHAT YOU GOT. \_\_\_.", r"That's My Secret, I'm Always \_\_\_.",
                                            r"We Found Out What's Causing Your Chest Pain. We Think It's A Direct Result Of \_\_\_.", r"What Am I Waiting For? \_\_\_.", r"What do I See In This Inkblot? \_\_\_.",
                                            r"What's In The Box? \_\_\_.", r"What's My Go-To Baby Shower Gift? \_\_\_.", r"Where Were You When I Needed You? \_\_\_.", r"Without Doubt, This Is The Golden Age Of \_\_\_.", #End of Volume 6 One-Answer Black Cards
                                            r"\_\_\_, I Choose You!", r"After Years Of Study, I Finally Received My Doctorate In \_\_\_.",
                                            r"Before I Go, I Check The List: Rubber Tubing, Gas, Saw, Gloves, Cuffs, Razor Wire, Hatchet, \_\_\_, And My Mitts.", r"Choosy Moms Choose \_\_\_.",
                                            r"Fridays This Fall: *CSI:* \_\_\_.", r"General, It Appears That Instead Of Brains, These Zombies Want \_\_\_.", r"Hear My Words, \_\_\_ Will Rise Again!",
                                            r"I See London, I See France, I See \_\_\_.", r"I Struggle To Maintain A Healthy Weight, But My Problem Isn't Glandular, It's \_\_\_.",
                                            r"If The Eyes Are The Windows To The Soul, Then Why Are Mine Filled With \_\_\_?", r"In The Days Before Her Death, Maya Angelou Wrote A Moving Essay About \_\_\_.",
                                            r"It Is Pitch Black. You Are Likely To Be Eaten By \_\_\_.", r"Mother, Father, Today I Am A Man. Fetch Me \_\_\_.", r"New From DC Comics®: Batman Vs. \_\_\_.",
                                            r"New To The 2020 Summer Olympics, \_\_\_.", r"Purists Agree: A True Philly Cheesesteak Must Contain \_\_\_.", r"Run, Toto! It's The Wicked Witch Of \_\_\_!",
                                            r"Soylent Pink Is \_\_\_!", r"The CIA Reports That Russia Is Spending Billions To Influence \_\_\_.", r"The Curse! The Child Has Been Born With The Mark Of \_\_\_!",
                                            r"The Hills Are Alive, With The Sound Of \_\_\_!", r"'There's Nothing To Worry About,' The Doctor Said 'It's Just A Simple Routine Check For \_\_\_.'",
                                            r"What Is Hillary's New Hobby In Retirement? \_\_\_.", r"What Is The White House Press Secretary Trying To Explain?", r"What Would It Take To Get Me Back Into Church? \_\_\_.",
                                            r"What's Andy Serkis Pretending To Be Now? \_\_\_.", r"What's Barron Trump Googling At This Very Moment? \_\_\_.", r"Why Don't I Date Online Anymore? \_\_\_.",
                                            r"You've Never Seen Adam Sandler Like This Before! This Summer, '\_\_\_.'", #End of Volume 7 One-Answer Black Cards
                                            r"A Wild \_\_\_ Appears! You Used \_\_\_! It's Super Effective!", r"I Was Once Sent To The HR Department For An Incident Involving \_\_\_, \_\_\_, And (Allegedly) \_\_\_.",
                                            r"I'm Gonna Go Build My *Own* Theme Park! With \_\_\_! And \_\_\_!", r"PornHub.com's Single Most Popular Video Features \_\_\_ And \_\_\_.",
                                            r"So Then He Says, 'If You Want To Make This Relationship Work, You Need To Give Up \_\_\_ And \_\_\_.' As. *If.*", r"Thanks To \_\_\_, I Now Have A Crippling Fear Of \_\_\_.",
                                            r"The Last Three Items On My 'Bucket List': \_\_\_, \_\_\_, \_\_\_.", r"Three Bullet Points From My OKCupid® Profile: \_\_\_, \_\_\_, And (Most Importantly) \_\_\_.",
                                            r"Tonight On 'Supernatural,' Sam And Dean Are Forced To Confront \_\_\_ Using Only \_\_\_.",
                                            r"When I'm Dating Somebody, I Can Overlook \_\_\_ And \_\_\_, But \_\_\_ Is A Deal-Breaker", #End of Volume 1 Multi-Answer Black Cards
                                            r"An Ounce Of \_\_\_ Is Worth A Pound Of \_\_\_.", r"Bentley's® Latest Ultra-High-End Luxury Sedan Comes Complete With \_\_\_, \_\_\_, And \_\_\_.",
                                            r"Dear, Your Father And I Found \_\_\_ And \_\_\_ In Your Bedroom. I'm Shocked, And Frankly Just A Little Disappointed.",
                                            r"I Got Some Strange Looks In The Checkout Line When The Cashier Noticed \_\_\_, \_\_\_, And \_\_\_ In My Cart.",
                                            r"Netflix's® New Original Series Is A Sitcom Based Around \_\_\_ And \_\_\_.",
                                            r"The NSA Wants To Talk To Me About An Email I Sent Containing These Key Phrases: \_\_\_, \_\_\_, \_\_\_.",
                                            r"When I've Seriously Fucked Up And Need To Make Amends, What Can I Give My Significant Other To Show Them I Am Truly Remorseful? \_\_\_, \_\_\_.",
                                            r"Yea, Though I Walk Through The Valley Of \_\_\_, I Will Fear No \_\_\_.", #End of Volume 2 Multi-Answer Black Cards
                                            r"Good News, Everyone! I'm Giving A TED Talk On The Subject Of How \_\_\_ Will Transform \_\_\_.", r"How Did I Spent My Inheritance? \_\_\_, \_\_\_.",
                                            r"I Have This Recurring Dream Where I'm \_\_\_, And I'm Giving \_\_\_ To \_\_\_.", r"I've Designed A Spaceship Powered By The Energy Released When You Combine \_\_\_ And \_\_\_.",
                                            r"The Night Before A Blizzard, Always Stock Up On \_\_\_ And \_\_\_.", r"This Bottle Of 1961 Château Cheval Blanc Has Notes Of \_\_\_ And \_\_\_.",
                                            r"This Film Has Been Rated 'NC-17' For Graphic Depictions Of \_\_\_ And \_\_\_.", r"Topping This Week's Non-Fiction Best-Sellers: '\_\_\_: The Art Of Living With \_\_\_.'",
                                            r"What Do I Have Rotting Away In A Storage Unit? \_\_\_, \_\_\_.", r"Who's Got \_\_\_, \_\_\_, And Two Thumbs? This Guy!", #End of Volume 3 Multi-Answer Black Cards
                                            r"Ancient Chinese Proverb Say: \_\_\_ Is Just \_\_\_ Without \_\_\_.", r"I Am \_\_\_. I Speak For \_\_\_.", r"In A Groundbreaking Experiment, \_\_\_ Has Given Birth To \_\_\_.",
                                            r"Ultimate Deathmatch: \_\_\_ Vs. \_\_\_.", r"You Got Your \_\_\_ In My \_\_\_!", #End of Volume 4 Multi-Answer Black Cards
                                            r"And Behold, The Fifth Seal Opened, And There Was \_\_\_ And With It Came \_\_\_.", r"Baby, I'm \_\_\_ On The Streets, \_\_\_ In The Sheets.",
                                            r"I'm Constantly Confusing \_\_\_ And \_\_\_.", r"It's All About \_\_\_ - No \_\_\_.", r"Next On Adult Swim™️: *The Adventures Of* \_\_\_ *And* \_\_\_.", #End of Volume 5 Multi-Answer Black Cards
                                            r"Concerned About Diabetes? Watch For Symptoms Like \_\_\_ And \_\_\_.", r"The Presidential Election Came Down To A Choice Of Either \_\_\_ Or \_\_\_.", #End of Volume 6 Multi-Answer Black Cards
                                            r"Hey, Perverts! It's 'Adam And Eve,' Not '\_\_\_ And \_\_\_.'", r"No Stranger, Here We Worship \_\_\_: The God Of \_\_\_.",
                                            r"Tonight On Public Access Channel 16, \_\_\_, A Student Film About \_\_\_." #End of Volume 7 Multi-Answer Black Cards
                                            ]
                        extension_whites = ["A $50 Cup Of Coffee Literally Made From Cat Shit", "A Beard Longer Than 12 Inches", "A Four-Inch Clit", "A Hamster With A Throbbing Erection",
                                            "A Mazel Tov Cocktail", "A Nugget Of Poo Roughly The Size And Shape Of A Crouton", "A Prehensile Penis", "A Sexually Aggressive Koala",
                                            "A Shockingly Flatulent Bobcat", "A Strong, Independent Woman Who Don't Need No Man", "A Tossed Salad", "Affirmative Action", "An Asexual Bonobo",
                                            "An Entire Bottle Of Jägermeister®", "An Extra-Large Can Of Bone Bashful™ Brand Chinchilla Pudding Sauce",
                                            "An Oosik, Or Inuit War Club Made From The Penis Bone Of A Walrus", "An Overly-Enthusiastic Prostate Exam", "An Unsurprising Rash", "Axl Rose", "Bacne",
                                            "Bacon That Can Feel Pain", "Bacon-Flavored Lube", "Being Born With A Tail", "Being Kicked In The Ovaries", "Being Punk In Drublic",
                                            "Being Raped To Sleep By Dickwolves", "Belching Out The Lyrics To 'Hey Jude'", "Bono. Just... Bono", "Bronies", "Cockasaurus Rex: The Horniest Dinosaur Of Them All",
                                            "Cocktimus Prime: The Laser-Guided Dildo Rocket", "Costco® Food Samples", "Death By Snu-snu", "Droppin' The Mic", "Enrolling In Clown School",
                                            "Erotic Balloon Animals", "Explaining How I Got The Nickname 'Nibbleberries'",
                                            "Ezekiel 23:20 'There She Lusted After Her Lovers, Whose Genitals Were Like Those Of Donkeys And Whose Emission Was Like That Of Horses.'", "Flop Sweat",
                                            "Gilbert Gottfried's Voice", "Giving Anne Frank A Drum Kit For Her Birthday", "Giving The Tumor A Cutesy Name", "Googling 'Betty White Nude'",
                                            "Grandma's Wet, Sloppy Kisses", "Honey Boo Boo Shotgunning A 2-Litre Bottle Of 'Go-Go Juice'", "Insisting That Jesus Is Technically A Zombie",
                                            "JJ Abrams Putting Lens Flares All Over Everything", "Joe Biden Getting His Freak On", "Joffrey Baratheon, The Loathsome Little Shit",
                                            "LEGO® Recreations Of Classic Pornos", "Logic", "Michele Bachmann Furiously Masturbating With A Coathanger",
                                            "Mitt Romney Doing A Burlesque Routine In A Giant Champagne Glass", "Monkey Torture", "My Level 90 Night Elf, Leafshit Puddingsbane",
                                            "Natalie Portman Naked, Petrified, And Covered In Hot Grits", "Officially No Longer Giving A Shit", "Plato's Allegory Of The Cave Or Some Other Pretentious Bullshit",
                                            "Posting On www.reddit.com/r/gonewild/", "Pretending To Be A Malfunctioning Robot", "Pretending To Have The Hiccups", "Pronouncing 'Quinoa' Properly",
                                            "Racist Ninjas", "Raptor Jesus", "Reluctant Anal", "S'more Schnapps", "Selling Out", "Sexy Witches", "Slightly More Than 3 Ounces Of Cum", "Steaming Hot Lemonade",
                                            "Struggle Snuggles", "That 'Not-So-Fresh' Feeling", "The Combined Fat From All The Kardashian Family Liposuctions", "The Fabled Mongolian Death Worm",
                                            "The Green Apple Splatters", "The Slender Man", "The Tardis", "Touching Each Other's Butts", "Thirty Pieces Of Silver", "Using Teeth", "Van Gogh's Severed Ear",
                                            "Weaponized Ebola", "Wielding A Toddler As A Weapon", "WINNING!!", "Yoga Pants", #End of Volume 1 White Cards
                                            "A 5 lb. Bag Of Gummy Bears", "A Bachelor's Degree In Communication", "A Bit O' The Ol' Slap And Tickle", "A Bitchin' Camaro", "A Blanket With A Hole In It",
                                            "A Breakfast Sausage With Serious Emotional Problems", "A Chair That Likes To Rape People", "A Cunning Stunt", "A Good Schtupping",
                                            "A Gratuitous Claymation Sequence", "A Hairshirt", "A Husband Bulge", "A Jury Of Your Peers", "A Sense Of Resignation", "A Slack-Jawed Yokel", "A Stinky Pinky",
                                            "A Tender Rodgering", "A Warm, Gently Fragrant Biscuit", "A Were-Salmon", "A Younger, Vastly More Attractive Spouse", "Agent Orange", "An Angry Little Man",
                                            "An Effeminate Southern Homophobe", "Applying To A New Guild", "Barfing Into A Tiny, Bejeweled Handbag", "Being Able To Name *All* The Different Kinds Of Olives",
                                            "Being Circumcised With A Deli Slicer", "Being Small But Perfectly Well Formed", "Bitch Tits", "Biting My Toenails", "Blistering Barnacles!", "Bourbon Pong",
                                            "Choking", "Cockissimo Fantastico, The Legendary Lover With The Wondrous Wang", "Cockulous Maximus, Tremendous Tallywacker Of Tripoli", "Firm Buttocks",
                                            "Gazpacho Tactics", "Giving Your Pet Lamb A Brazilian", "*Hakuna Matata,* Motherfucker", "Her Dry, Scaly Hands", "Hiroshima",
                                            "Hooking Up At A Tegan And Sarah Concert", "Japanese Rope Technique", "Kentucky Fried Children", "Killing Hobos",
                                            "Making Vigorous Love To A Taco Bell® Beefy 5-Layer Burrito™", "Mesothelioma", "Minimum Wage", "Mongolian 'Beef'", "More Dots!", "My Evil Twin",
                                            "Not Being Too Smelly, You Know, In The Cellar. Down Below", "One Direction",
                                            "One Whose Nether Regions Are Vast And Beckoning, Like Unto A Corridor Down Which A Frankfurter Might Be Thrown", "Opening For Sigur Rós", "Painal",
                                            "Paula Deen's Dietitian", "Poop Soup", "Pooping In Public", "Reptilians", "Rich Corinthian Leather", "Rock Bottom",
                                            "Running Around Like A Guy With His Chicken Cut Off", "Self-Medicating", "Self-Replicating Fudge", "Slowly Waving An Oversized Jamaican Flag", "Some Minor Bruising",
                                            "Something Elon Musk Thought Up While Floating Six Inches Above The Floor In A Meditative Trance", "Spiking The Juice At AA", "Sploosh!", "Swallowing A Cue Ball",
                                            "Tacos", "Ted Nugent's Cold, Dead Hands", "That Thing With The Spoon", "The Cliterati", "The Creative Use Of A Pool Noodle", "The French", "The Reek Of Shame",
                                            "The Smooth, Unblemished Skin Of A Child", "The Soft Love-Honks Of A Lusty Goose", "The Whole Goddamned Thing", "The WNBA", "Those Creamy Atheist Thighs",
                                            "Titty Sprinkles", "Treason", "Tufted Ears", "Uncontrollably Retching At The Mere Mention Of Mayonnaise", "Using A Zip-Tie As An Impromptu Cock-Ring",
                                            "Using Tears As Lubricant", "Wearing A Blue Fox Fursuit On Casual Friday", "Wearing Your IUD Into An MRI", #End of Volume 2 White Cards
                                            "A Ball Pit Filled With Testicles", "A Banana. You Know, For Scale", "A Benedict Cumberbatch RealDoll™", "A Black Fly In Your Chardonnay", "A Braille Vajazzling",
                                            "A Bunch Of Snot-Nosed, Know-It-All Twentysomethings", "A Butt-Plug In The Shape Of A Rolled-Up Copy Of The US Constitution", "A Cage Fight With Nicolas Cage",
                                            "A Combination Bounce House And Fumigation Tent", "A Donkey Show", "A Fleshlight®", "A Fluffy Little Butt", "A Literal Shaved Beaver", "A Meat Popsicle",
                                            "A Silly Old Sea Captain Who's Just *Full* Of Stories", "A Song About How Great Nebraska Is", "A Stripper Named 'Anchovy'", "A Tongue Punch In The Ol' Fart Box",
                                            "A Whole Lot Of Donuts", "An Emergency Root Canal", "An Emperor Penguin With *No* Sense Of Shame", "An Erotic Novel About The Loch Ness Monster",
                                            "An Unexpected Finger In The Anus", "Baby Carrots", "Being Heteroflexible", "Being So Far In The Closet, You Can See Narnia",
                                            "Being Waterboarded With Wild Turkey® 101", "Charles Darwin", "Chasing Waterfalls", "Chemtrails", "Chloroform", "Combing Out The Dingleberries",
                                            "Crabs Adjust Humidity", "Dennis Rodman, Professional Diplomat", "Double Vaginal, Double Anal",
                                            "Erotic Star Trek Fan Fiction Where All The Characters Are Furries, Like Kirk Is An Ocelot Or Something",
                                            "Gettin' Down There And Bein' All Like 'This Shit Is Nasty, Yo. Fuck This, Yo.'", "Getting Ganked", "Hookers And Blow", "Jennifer Lawrence", "Juggalos",
                                            "Korean Jesus", "Lebron James' Vast, Enveloping Hands", "Living Among Us... Learning Our Ways. Watching. Waiting", "Low-Hanging Fruit",
                                            "Lt. Worf's Naturally-Ribbed Klingon Schlong", "Lucky Pierre", "Making Airplane Noises", "Mr. Right Now", "My Apparent Inability To Read A Few Simple Words Out Loud",
                                            "Nazi Unicorns", "Neil Degrasse Tyson", "Obamacare", "Peanut Butter Jelly Time", "Primo Shlick Material", "Rainbow Cumdrops", "Realistic Expectations",
                                            "Robin Thicke", "Scissoring", "September 11th", "Six Pounds Of Raw, Peeled Garlic", "Some Punk-Ass Little Bitch", "Sriracha", "Susan, That Bitch",
                                            "The (Technically) Virgin Mary", "The Crotches Of Strangers", "The Express Written Consent Of Major League Baseball",
                                            "The Few Shreds Of Tinsel Still Clinging To My Asshole", "The Irish", "The Ol' Reach-Around", "The Sound Of One Hand Fapping", "The Sticky Icky",
                                            "The Sweet Release Of Death", "The Taste Of Human Flesh", "Turning It All Into A Sexy Dance", "Twenty Million US Dollars", "Using A Live Squid As A Condom",
                                            "Wanghis Kahn, Cocklord Of The Mongols", "What Jesus Would Do", "Wiggling", "Wuv", "Yiffing", "You Know, One Of Them Sorts Of Things", #End of Volume 3 White Cards
                                            "A Burning Sensation", "A Category 5 Assnado", "A Crusty Old Sock", "A Fear-Boner", "A Fishy Taste", "A History Of Abuse", "A Moist Towlette",
                                            "A Pineapple With Chlamydia", "A Powerful Gag Reflex", "A Purple Nurple", "A *Really* Bad Yeast Infection", "A Secret Blend Of Eleven Herbs And Spices",
                                            "A Shit-Ton Of Glitter", "A Single, Shiny Bitcoin", "A Thirsty, Sperm-Jacking Wanna-Be Baby Mama", "A Tip Of My Fedora", "A Urine-Filled Bong",
                                            "A Waco, Texas-Themed Novelty Barbecue Pit And Smoker", "Africans, The Racist White Kind", "An Absinthe Enema", "An Actual Gravy Train",
                                            "An Actual Invisible Knapsack", "An Adorable Baby Sloth", "An Itsy-Bitsy Teeny Weenie", "An Obscene Amount Of Butter", "An Orcgasm", "Anything With A Hole",
                                            "Asian Girls With Names Like 'Christina' Or 'Elizabeth'", "Auto-Erotic Asphyxiation", "Bitchy Resting Face", "Cake Farts", "Chesticles", "Child-Sized Coffins",
                                            "Cumalot", "Curb-Stomping", "Danger Pheromones", "DOOOOOMM!!!!!!!", "Dr. Jellyfinger", "Duchess Von Fingerbang", "Fat Man And Little Boy", "Felching",
                                            "Front Row Seats To The Shit Show", "Gargling Noises", "Ham Night!", "Hey, Fuck You Buddy", "Hilarious Foreigners!", "Hulking Out", "Long Schlong Silver", "M'lady",
                                            "Making Sweet, Sweet Love All Night Long", "My Big Juicy Fuck Potatoes", "My Silent Twin, The Afterbirth", "OH EM GEE, TOTES ADORBS!!!", "Origami Erotica",
                                            "Pelvic Sorcery", "Protective Custody", "Putting Baby In A Corner", "Romantic Cancer", "Something So Offensive, I Don't Even Want To Say It",
                                            "State-Of-The-Art Animatronics", "Taking One For The Team", "Tampons In Every Hole", "The Age Of Consent", "The Chronicles Of Red-Dick",
                                            "The Echoing Silence Left By SIDS", "The Gaza Strip", "The Graveyard Shift At 7-Eleven®", "The Hole In My Chest Where My Heart Used To Be",
                                            "The Large Hard-On Collider", "The Love That Dare Not Speak Its Name", "The Noise A Cat Makes Before Vomiting",
                                            "The Patriarchal Social Construct Of Physical Genitalia", "Trickle-Down Economics", "Trouser Chili", "Welfare", "What Happens In Vegas", "Whatever Is Left",
                                            "www.clownpenis.fart", "Zatopeepee, The Blind Fucksman", "Ze Germans", #End of Volume 4 White Cards
                                            "A Bag Of Doorknobs", "A Bag Of Pickled Socks", "A Bucket Of Dicks", "A Few Sharp Tugs", "A Girl-Child", "A Lemon-Stealing Whore", "A Meat Tornado", "A Miscarriage",
                                            "A *Nice* Boy Who Never Did *Anyone* Any Harm", "A Pattern Of Defensive Wounds", "A Racist Toddler", "A Shallow Grave", "A Soggy Biscuit", "A Special Snowflake",
                                            "A Sternly-Worded Letter", "A Tablespoon Of Thick, Custardy Puss",
                                            "A Turbo-Encabulator, Complete With Pre-Famulated Amulite Surmounted By A Malleable Logarithmic Casing", "A Whole Baby", "ALLAH HU AKBAR!", "Alzheimer's",
                                            "An Amber Alert", "An Asshole That Tastes Like Vanilla Ice Cream", "Area 69", "Battle-Tested Period Panties", "Being A Size Queen", "Being Catfished",
                                            "Being Judged Not By The Color Of Your Skin, But By The Content Of Your Character", "Being Raped To Sleep By Dickwolves", "Bill Cosby's Chocolate Pudding Pop",
                                            "Booklearnin'", "Brojobs", "Crotchfruit", "Crushing Your Enemies, Seeing Them Driven Before You, And Hearing The Lamentations Of Their Women",
                                            "Diamond-Studded Tampons", "Dick Nipples", "Dickbutt <:dickbutt:797599374548402197>", "Doggy-Style With A Real Doggy", "Doing The Waffle Stomp", "Freedom",
                                            "Getting White Girl Wasted", "Going Potty", "Hillary Clinton's Triumphant Patriotic Cock", "Hot Singles In Your Area", "Iggy Azalea", "Irony", "It", "Kinky Fuckery",
                                            "Me Lucky Charms®!", "Mortal Kombat™", "Nutella®", "One More Fucking Word", "Only Traveling By Rickshaw", "Poking It With A Stick", "Quietly Ovulating",
                                            "Santorum, Everywhere", "Sharia Law", "Shenanigans", "Shit-Filled Raviolis", "Shub-Niggurath, The Black Goat Of The Woods With A Thousand Young",
                                            "Sitting Alone In The Dark, Listening To Drake", "Skanky Smurf", "Spelunking", "Stank Dick", "Sugar And Spice And Everything Nice", "The Cockpocalypse",
                                            "The Difference Between 'Good Touch' And 'Bad Touch'", "The Muffled Cries Of An Asian Baby Girl", "The Poophole Loophole", "The Scientific Method",
                                            "The Sound Of A Toddler's Skull Cracking Against The Pavement", "The Third Trimester", "The Wet Spot", "The Yellow Dick Road", "These Strange Human Urges",
                                            "This Motherfucker Right Here", "Tinder™", "Type 2 Diabetes", "Wink Wink, Nudge Nudge!", "You Know Who", "Your Bourgeois Morality", #End of Volume 5 White Cards
                                            "3.7 Billion Women", "A 3-1/2 Pound Shit Baby", "A Blue Waffle", "A Chronic Colonic", "A Cleveland Steamer", "A Cock-Gobbling Cock-Goblin", "A Dumpster Fire",
                                            "A Hoo-Hoo That Bites Your Ding-Dong", "A Lemon Party", "A Little Bit Of Spit-Up", "A NEWWWW CAR!", "A Planned Parenthood® Clinic And Non-Kosher Deli",
                                            "A Positive Pregnancy Test From Craigslist", "Acknowledging That None Of The Dreams That You Had As A Child Have Come True", "Adele", "Agreeing With Donald Trump",
                                            "An Ancient, Malevolent Entity", "Ariana Grande And Her Sisters Ariana Tall And Ariana Venti", "Asparagus Pee", "Barbecuing What's Left Of The Fetus",
                                            "Being A 'Gold Star' Lesbian", "Benghazi!", "Bernie Sanders' Sexy Tickles!", "Bristol Palin", "Brovaries", "Burning Man", "Cock Cancer", "Dank Memes",
                                            "Dem Lil' Critters", "Dickin'", "Eating Pussy With A Knife And Fork", "El Niño", "Getting Head From Kevin Spacey", "Ghost Babies", "Hepatitis C",
                                            "Hillary Clinton's Kevlar-Lined Pantsuit", "Hitler? Hitler! Hitler Hitler Hitler ᴴⁱᵗˡᵉʳ ᴴⁱᵗˡᵉʳ", "Huge, Wobbly Meat-Curtains",
                                            "I Would Like To Add You To My Professional Network On Linkedin®", "Jared's Six-Inch Kiddie Meal", "Jesus H. Christ", "Jihotties", "Literally, Anything Else",
                                            "Making America Great Again", "Manspreading", "Mouth Sounds", "My Own Two Hands", "Nonstop Helicoptering", "Nuking Gay Baby Whales For Jesus", "Nun Chunks",
                                            "Pegging", "Pissing In The Popcorn", "Placenta Polenta", "Profound Autism", "Pungent Butt-Burps", "Pure Evil", "Putting The Pussy On The Chainwax",
                                            "Releasing The Kraken", "Riding The Struggles Bus", "Rough, Anonymous Sex", "Scrotemeal", "Shia LeBeouf", "Sleep Fapnia", "Smirnoff® The Wizard",
                                            "Someone Who Isn't Me", "Sweater Puppies", "Ten Points For Gryffindor!", "That Woman", "The Academy Of Fine Farts", "The Dewey Decimal System", "The Hostages",
                                            "The Other, Other, Otherwhite Meat", "The Person Mr. Rogers Thought I Could Be", "The Shortbus", "This. This Right Here. So. Much. This", "Touching The Poop",
                                            "Trademark Infringement", "Twincest", "Unspeakable Atrocities", "Waiting For The Bar To Open", #End of Volume 6 White Cards
                                            "A 5-Gallon Bucket Of Used Condoms", "A Bull Dyke In A China Shop", "A Bulldog Eating Mayonnaise", "A Burkini",
                                            "A County Fair Goldfish Who Has Seen Things No Goldfish Should Ever See", "A Cry For Help", "A Hasidic Hillbilly With A Snootful Of Honeybees",
                                            "A Journey Of Self-exploration", "A Pale Rider, And His Name Was Death", "A Pickup Truck, A Good Dog, And My Woman", "A Really Stupid Mustache",
                                            "A Schlong Of Ice And Fire", "A Shoehorn, The Kind With Teeth", "A Twatadile", "A Well-Regulated Militia", "A-Rabs", "Additional Lubrication, Stat!",
                                            "All My Worldly Possessions, Piled In The Street And Set Alight", "All That And A Bag Of Chips", "Alternative Facts", "Balthus, The Blue-Balled Barbarian",
                                            "Behold! The Majestic Sequoia", "Boom Shakalaka", "Bursting Through The Back Door", "Cankles", "*Casu Marzu,* The Famed Sardinian Maggot Cheese",
                                            "Clowns That Lure Children Into The Woods", "Cockhenge", "Dick Cheese Cheesecake", "Dildo Saggins", "Dropping The Soap", "Falling Into The Zoo Enclosure",
                                            "Family Fun Fecal Face Painting", "Fidget Spinners", "Fracking", "Fruit Leather Bondage Gear", "Getting A Bit 'Rapey' At Night Sometimes", "Good Boy Points",
                                            "Grab-Ass", "Grabbing Them By The Pussy", "Granny's Nooks And Crannies", "Gravity", "Harambe",
                                            "Having So Little Hope For Your Child's Future That You Name Him 'Jathan'", "Hot Topic®", "Impeachment", "Jack The Stripper", "Just Doing My Fucking Job, Asshole",
                                            "Leaving The European Union", "Lord Xenu", "*Mesonychoteuthis Hamiltoni,* The Colossal Squid And One Hell Of A Fucking Metaphor", "My Druncle", "My Will To Live",
                                            "Not Knowing When To Stop", "Obsessive Compulsive Disorder", "Optional Lumbar Support", "Prescription Drugs", "Repressed Scout-Leader Memories",
                                            "Ringo, The Last Surviving Beatle", "Safe, Low-Voltage Stimulation", "Sharron's Shitty, Seashell-Shaped, Chartreuse She-Shed By The Seashore",
                                            "Some Kind Of Infestation", "Steve From *Blue's Clues*", "The Fear That Senpai Will Never Notice Me",
                                            "The Great Black Wolf Fenrir, Eater Of Odin And Harbinger Of Ragnarök", "The Ladies Of The Women's Auxiliary",
                                            "The Maddening CLICK CLICK CLICK Of Fingernails On iPhone®", "The Naughty Nuns Of North Nottingham", "The Smell", "The Sound Of My Vagina", "The Yakuza",
                                            "Thinkin' 'Bout Them Beans", "This Silly 'Consent' Nonsense", "Throwing Another Pidgey In The Wood Chipper", "Throwing Shade", "Turning It Off And On Again",
                                            "Vaping", "Weasels Ripping My Flesh", "White Girl Dreads", "Yanking On The Clitoris" #End of Volume 7 White Cards
                                            ]
                    else:
                        await ctx.channel.send(deck + " is not a known deck.")
                    self.deck_blacks.extend(extension_blacks)
                    self.deck_whites.extend(extension_whites)
                ###Shuffle Decks
                self.game_blacks = self.deck_blacks.copy()
                random.shuffle(self.game_blacks)
                self.game_whites = self.deck_whites.copy()
                random.shuffle(self.game_whites)
                ###Create Player Score and Hands messages
                scoremessage = "**Scoreboard (play until " + str(self.game_threshold) + ")**```css\n"
                for index, player in enumerate(self.game_players):
                    if index == 0:
                        scoremessage += "0 - [" + player.name + "]\n"
                    else:
                        scoremessage += "0 - " + player.name + "\n"
                scoremessage += "```"
                for player in self.game_players:
                    hand = self.game_whites[0:self.game_handsize]
                    privatemessage = "**Your White Cards:**"
                    for number, card in enumerate(hand):
                        privatemessage += "\n" + self.number_emoji(number) + " " + card
                    self.game_whites = self.game_whites[self.game_handsize:]
                    self.game_hands.append([player, hand])
                    self.game_score.append([player, 0])
                    pointmessage = await player.send(scoremessage)
                    reactmessage = await player.send(privatemessage)
                    self.game_scoremessages.append(pointmessage)
                    self.game_handmessages.append(reactmessage)
                    for num in range(self.game_handsize):
                        await reactmessage.add_reaction(self.number_emoji(num))
                await ctx.channel.send("Ready to play CAH! Let's take this to DMs.")
                ###Start Gameplay Loop
                await self.black_card()

            ##Quit CAH Game
            if action == "quit" or action == "stop" or action == "end":
                if len(self.game_players) > 0:
                    for player in self.game_players:
                        await player.send("Game forcefully stopped by " + ctx.author.name + ".")
                    self.reset_game()
                else:
                    await ctx.channel.send("No game running!")

            ##Describe Decks
            if action == "decks" or action == "deck":
                await ctx.channel.send("`default`: The standard base game Cards Against Humanity deck.\n"
                                    "`red`: The official Red Box Expansion for Cards Against Humanity.\n"
                                    "`blue`: The official Blue Box Expansion for Cards Against Humanity.\n"
                                    "`green`: The official Green Box Expansion for Cards Against Humanity.\n"
                                    "`crabs`: Every card from the unofficial Crabs Adjust Humidity packs.")

            ##Help Info
            if action == "help" or action == "info":
                await send_help(ctx.channel.send, "cah")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

async def setup(client):
    await client.add_cog(CAH(client))
