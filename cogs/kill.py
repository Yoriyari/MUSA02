#===============================================================================
# Kill v1.1.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 20 Mar 2025 - v1.1.1; Made strings with escape characters raw strings. -YY
# 18 Feb 2025 - v1.1; Altered phrase detection to permit nested phrases, adding
#               support for putting causes of death within a cause of death.
#               Rduimentary rammar support for targets literally named
#               "she"/"her", "he"/"him" or "it"/"its". -YY
# 05 May 2024 - v1.0.1; Reworked help message import and error handling. -YY
# 25 Sep 2023 - v1.0; Finished file. -YY
# 23 Sep 2023 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# kill.py generates a random cause of death of whoever was given as parameter.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.json_handling import read_from_json
from common.error_message import send_error
from common.help_message import send_help

from numpy import random
import re

causes_of_death_file = "data/causes_of_death.json"
terms_file = "data/terms.json"

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

#Auxiliary functions
def get_eligible_terms(terms_list, tag):
    '''Returns a list of terms with the matching tag
    '''
    return [t[0] for t in terms_list.items() if tag in t[1]]

def remove_ineligible_terms(terms_list, tag):
    '''Returns a list of terms without the matching tag
    '''
    return [t[0] for t in terms_list.items() if not tag in t[1]]

def integer_to_word(number):
    '''Returns the English variant of an integer above 1.
    '''
    if number == 2:
        return "two"
    if number == 3:
        return "three"
    if number == 4:
        return "four"
    if number == 5:
        return "five"
    if number == 6:
        return "six"
    if number == 7:
        return "seven"
    if number == 8:
        return "eight"
    if number == 9:
        return "nine"
    if number == 10:
        return "ten"
    if number == 11:
        return "eleven"
    if number == 12:
        return "twelve"
    return "several"

def pick_term(terms_list, tag):
    '''Returns a random string of a term corresponding to the provided tag.
    '''
    if tag == "number": # Special case 1: digit
        weighted_max = 101
        for _ in range(3):
            weighted_max = random.randint(3, weighted_max)+1
        weighted_max = random.randint(2, weighted_max)
        if weighted_max < 13 and random.random() <= 0.75:
            return integer_to_word(weighted_max)
        return str(weighted_max)
    elif tag == "any": # Special case 2: anything
        eligible_terms = remove_ineligible_terms(terms_list, "location")
        term = random.choice(eligible_terms)
        return fill_in_tags(terms_list, term)
    elif tag == "cause": # Special case 3: cause of death
        return generate_causes_of_death_string(terms_list=terms_list)
    else: # General case
        eligible_terms = get_eligible_terms(terms_list, tag)
        term = random.choice(eligible_terms)
        return fill_in_tags(terms_list, term)

def pick_causes(causes_list):
    '''Returns a list of randomly picked string(s) describing causes of death
    '''
    deaths_count = 1
    deaths_limit = len(causes_list)
    survival = random.random()
    while survival <= 0.2:
        if deaths_count >= deaths_limit:
            break
        deaths_count += 1
        survival = random.random()
    return random.choice(causes_list, deaths_count, False)

def fill_in_tags(terms_list, phrase):
    '''Replaces the tags in phrase string with corresponding terms.
    '''
    match = re.search(r"<\S+>", phrase)
    while match != None:
        tag = match.group().strip("<>")
        term = pick_term(terms_list, tag)
        start, end = match.span()
        phrase = phrase[:start] + term + phrase[end:]
        match = re.search(r"<\S+>", phrase)
    return phrase

def get_optional_fragments(text):
    '''Returns a list of tuples containing the probability and sub-phrase of
    an optional fragment set.
    Input format: "[1st float:1st phrase|2nd float:2nd phrase]"
    Output format: [(1st float, "1st phrase"), (2nd float, "2nd phrase")]
    '''
    fragments = [f.split(":") for f in text.strip("[]").split("|")]
    return [(float(f[0]), f[1]) for f in fragments]

def pick_optional_fragment(fragments):
    '''Returns a string randomly picked from the list of fragments, weighted by
    their given probabilities. If the probabilities don't add up to 1.0, the
    returned string may be empty. If the probabilities exceed 1.0, those
    fragments bringing the sum over 1.0 are ignored.
    '''
    p = random.random()
    for fragment in fragments:
        p -= fragment[0]
        if p <= 0:
            return fragment[1]
    return ""

def fill_in_optional_fragments(phrase):
    '''Replaces the tags in phrase string with corresponding terms.
    '''
    match = re.search(r"\[([.\d]+:[^\[\]|]+\|?)+\]", phrase)
    while match != None:
        fragments = get_optional_fragments(match.group())
        fragment = pick_optional_fragment(fragments)
        start, end = match.span()
        if phrase[start-1] == " " and fragment == "":
            start -= 1 #edge case where text gets double-spaced
        phrase = phrase[:start] + fragment + phrase[end:]
        match = re.search(r"\[([.\d]+:[^\[\]|]+\|?)+\]", phrase)
    return phrase

def fill_in_causes(terms_list, causes):
    '''Replaces the tags in cause of death strings with corresponding terms and
    determines optional random sentence parts.
    '''
    return [fill_in_single_cause(terms_list, cause) for cause in causes]

def fill_in_single_cause(terms_list, cause):
    '''Repalces the tags in a single cause of death string with corresponding
    terms and determines optional random sentence parts.
    '''
    cause = fill_in_optional_fragments(cause)
    cause = fill_in_tags(terms_list, cause)
    return cause

def generate_causes_of_death_string(terms_list=None):
    causes_list = read_from_json(causes_of_death_file)
    if not terms_list:
        terms_list = read_from_json(terms_file)
    causes = pick_causes(causes_list)
    causes = fill_in_causes(terms_list, causes)
    causes = " and ".join(causes)
    return causes

#---------------------------------------------------------------------------------------------------------------------------------------------------------------

#Cog Setup
class Kill(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Kill cog loaded.")

    @commands.group(name="kill", aliases=["murder", "assassinate", "death", "die"], case_insensitive=True, invoke_without_command=True)
    async def kill(self, ctx, *target):
        try:
            terms_list = read_from_json(terms_file)
            if not target:
                target = pick_term(terms_list, "individual")
                target = target[0].upper() + target[1:]
            else:
                target = " ".join(target)
                target = target[0].upper() + target[1:]
            causes = generate_causes_of_death_string(terms_list=terms_list)
            msg = ""
            survival = random.random()
            if survival <= 0.001:
                msg = f" [0.01:accidentally] managed to survive {causes} [0.1:with the power of <induces_madness>]."
            else:
                msg = f" [0.01:accidentally] [0.8:been killed|0.2:died] [0.05:<time>][0.001:.|0.999: after {causes}.] [0.005:The last thought going through their mind was of <any>.|0.005:Their last thoughts were of <any>.]"
            msg = fill_in_optional_fragments(msg)
            msg = fill_in_tags(terms_list, msg)
            opener = f"{target} has"
            if target.lower() in ["you", "me", "myself"]:
                opener = "You have"
                msg = msg.replace(" their ", " your ").replace(" themselves ", " yourself ").replace(" them ", " you ").replace(" them.", " you.")
            elif target.lower() in ["musa", "musa02", "musa 02", "musa2", "musa 2", "<@703563719879163914>"]:
                opener = "I have"
                msg = msg.replace(" their ", " my ").replace(" themselves ", " myself ").replace(" them ", " me ").replace(" them.", " me.")
            elif target.lower() in ["she", "her"]:
                opener = "She has"
                msg = msg.replace(" their ", " her ").replace(" themselves ", " herself ").replace(" them ", " her ").replace(" them.", " her.")
            elif target.lower() in ["he", "him"]:
                opener = "He has"
                msg = msg.replace(" their ", " his ").replace(" themselves ", " himself ").replace(" them ", " him ").replace(" them.", " him.")
            elif target.lower() in ["it"]:
                opener = "It has"
                msg = msg.replace(" their ", " its ").replace(" themselves ", " itself ").replace(" them ", " it ").replace(" them.", " it.")
            elif target.lower() in ["they", "them"]:
                opener = "They have"
            msg = f"{opener}{msg}"
            await ctx.channel.send(msg)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

async def setup(client):
    await client.add_cog(Kill(client))
