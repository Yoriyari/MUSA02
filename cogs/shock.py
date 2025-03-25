#===============================================================================
# Shock v1.2.12
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 25 Mar 2025 - v1.2.12; Fixed update_forgot_timer invoking the old cache. -YY
# 23 Mar 2025 - v1.2.11; Separated PiShock info to a JSON including usernames,
#               device codes, API keys, long-term toggles. Created a Collar
#               class. Centralized servers whitelisted for NSFW commands. -YY
# 20 Mar 2025 - v1.2.10; Made strings with escape characters raw strings. -YY
# 10 Jan 2024 - v1.2.9; Added Arora's shock collar. -YY
# 13 Nov 2024 - v1.2.8; Fixed a wrong function call in the forgot timer. -YY
# 12 Nov 2024 - v1.2.7; Fixed keywordless intensity incorrectly parsing decimal
#               values. -YY
# 10 Nov 2024 - v1.2.6; Parallelized the shocker API calls. Added caching for
#               collar toggles to cut down file operations. Added a timeout
#               timer for forgotten enabled collars. -YY
# 26 Oct 2024 - v1.2.5; Added Monochrome's shock collar. -YY
# 05 Jul 2024 - v1.2.4; Accepts appending duration after intensity without
#               preceding keyword now too. Silently passes errors for trying to
#               add a reaction to a deleted message (e.g. due to PluralKit). -YY
# 05 May 2024 - v1.2.3; Reworked help message import and error handling. Also
#               added terminal prints for enabling/disabling collars. -YY
# 28 Apr 2024 - v1.2.2; Limited command to servers I whitelisted. -YY
# 25 Nov 2023 - v1.2.1; Added Saffron's shock collar. Converted bytes string to
#               standard string for error messages. -YY
# 18 Nov 2023 - v1.2; Added Roxy's shock collar. Commands control both Yori's
#               and Roxy's collar simultaneously. Removed the collar permission
#               toggle and aliased it to the collar online/offline toggle as the
#               distinction was confusing anyway. Also made decimal input
#               without keywords properly default to time instead of power. -YY
# 30 Jun 2022 - v1.1; Added manual toggle for collar Online status. Moved API
#               request code to its own function and added two aliases. Made
#               numbers without preceding keyword in input default to
#               determining the intensity. -YY
# 25 Jun 2022 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Set up an interface for users to manually set up their own shocker(s),
#   rather than me having to hardcode them every time. -YY
# - Implement a queue to prevent operations getting lost when one is already
#   running. -YY
# - Make error messages specify which collar is giving the error message. -YY
# - Set up a way for users to disable "social shocking", e.g. only shock
#   commands that have their username appended will go through to them, or at
#   least only shock commands from the server they're in the members list of or
#   toggled their collar in. -YY
# - Consider a MUSA-side way to set intensity/duration range limits which do
#   not forward to PiShock's app, as PiShock just silently clamps them. -YY
#===============================================================================
# Description
# ..............................................................................
# shock.py allows users to submit PiShock shock collar commands to various shock
# collars, if any are online. This includes shocks, vibrations, and beeps.
# Intensity can be set from 1-100 and duration can be set from 0.1-15 seconds.
# Chosen privileged users can enable/disable their respective collars.
#===============================================================================

#Import Modules
import discord
from discord import Embed, ui
from discord.ext import commands, tasks

from common.json_handling import write_to_json, read_from_json
from common.private_ids import discord_id, guilds_whitelisted_for_nsfw
from common.error_message import send_error
from common.help_message import send_help

import re, json, datetime, asyncio, aiohttp

PISHOCK_DATA_FILE = "secrets/pishock_data.json"

#-------------------------------------------------------------------------------
#Custom Class

class Collar():
    def __init__(self, owner_name, pishock_username, privileged_names, device_codes, api_key, enabled):
        self.owner_name = owner_name
        self.privileged_names = privileged_names
        self.privileged_ids = [discord_id(name) for name in privileged_names]
        self.pishock_username = pishock_username
        self.device_codes = device_codes
        self.api_key = api_key
        self.enabled = enabled

#-------------------------------------------------------------------------------
#Cog Setup

class Shock(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.collars = self.initialize_collars()
        self.intensity_aliases = ["int", "pow", "str", "lev", "lvl"]
        self.duration_aliases = ["dur", "len", "tim", "for"]
        self.intensity_default = "25"
        self.duration_default = "1"

    @tasks.loop(hours=24.0, count=2)
    async def forgot_timer(self):
        '''Turns off all collars after no interactions have happened in 24 hours,
        assuming that any that're still on were simply forgotten about.
        '''
        try:
            if self.forgot_timer.current_loop != 0:
                for collar in self.collars:
                    collar.enabled = False
                self.write_cache_to_database()
        except Exception as e:
            await send_error(self.client, e)
            print("Error in the PiShock forgotten timer.")

    @commands.Cog.listener()
    async def on_ready(self):
        print("Shock cog loaded.")

    @commands.command(aliases=["collardisable", "shock_disable", "shockdisable", "disable_collar", "disablecollar", "disable_shock", "disableshock", "disableshocker", "disable_shocker", "shockerdisable", "shocker_disable", "collaroffline", "shock_offline", "shockoffline", "offline_collar", "offlinecollar", "offline_shock", "offlineshock", "offlineshocker", "offline_shocker", "shockeroffline", "shocker_offline", "collaroff", "shock_off", "shockoff", "off_collar", "offcollar", "off_shock", "offshock", "offshocker", "off_shocker", "shockeroff", "shocker_off", "collarstop", "shock_stop", "shockstop", "stop_collar", "stopcollar", "stop_shock", "stopshock", "stopshocker", "stop_shocker", "shockerstop", "shocker_stop", "collar_off", "pishockdisable", "pishock_disable", "pishockoffline", "pishock_offline", "pishockoff", "pishock_off", "pishockstop", "pishock_stop", "disablepishock", "disable_pishock", "offlinepishock", "offline_pishock", "offpishock", "off_pishock", "stoppishock", "stop_pishock"], case_insensitive=True, invoke_without_command=True)
    async def collar_disable(self, ctx):
        try:
            if ctx.guild and not ctx.guild.id in guilds_whitelisted_for_nsfw():
                return
            if ctx.author.id not in self.all_privileged_ids():
                await ctx.message.add_reaction("⛔")
                return
            for collar in self.collars:
                if ctx.author.id in collar.privileged_ids:
                    collar.enabled = False
                    print(f"{datetime.datetime.now()} - {collar.owner_name}'s PiShock has been disabled.")
            await ctx.message.add_reaction("👍")
            self.update_forgot_timer()
            self.write_cache_to_database()
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.command(aliases=["collarenable", "shock_enable", "shockenable", "enable_collar", "enablecollar", "enable_shock", "enableshock", "enableshocker", "enable_shocker", "shockerenable", "shocker_enable", "collaronline", "shock_online", "shockonline", "online_collar", "onlinecollar", "online_shock", "onlineshock", "onlineshocker", "online_shocker", "shockeronline", "shocker_online", "collaron", "shock_on", "shockon", "on_collar", "oncollar", "on_shock", "onshock", "onshocker", "on_shocker", "shockeron", "shocker_on", "collarstart", "shock_start", "shockstart", "start_collar", "startcollar", "start_shock", "startshock", "startshocker", "start_shocker", "shockerstart", "shocker_start", "collar_on", "pishockenable", "pishock_enable", "pishockonline", "pishock_online", "pishockon", "pishock_on", "pishockstart", "pishock_start", "enablepishock", "enable_pishock", "onlinepishock", "online_pishock", "onpishock", "on_pishock", "startpishock", "start_pishock"], case_insensitive=True, invoke_without_command=True)
    async def collar_enable(self, ctx):
        try:
            if ctx.guild and not ctx.guild.id in guilds_whitelisted_for_nsfw():
                return
            if ctx.author.id not in self.all_privileged_ids():
                await ctx.message.add_reaction("⛔")
                return
            for collar in self.collars:
                if ctx.author.id in collar.privileged_ids:
                    collar.enabled = True
                    print(f"{datetime.datetime.now()} - {collar.owner_name}'s PiShock has been enabled.")
            await ctx.message.add_reaction("👍")
            self.update_forgot_timer()
            self.write_cache_to_database()
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.command(aliases=["shocker", "pishock", "zap"], case_insensitive=True, invoke_without_command=True)
    async def shock(self, ctx, *arg):
        '''Shocks all online collars. Sends a message if none are online.
        Can be set to various intensities and durations.
        '''
        try:
            if ctx.guild and not ctx.guild.id in guilds_whitelisted_for_nsfw():
                return
            await self.shock_collar_operation(ctx, arg, "0")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.command(aliases=["vibe", "buzz"], case_insensitive=True, invoke_without_command=True)
    async def vibrate(self, ctx, *arg):
        '''Vibrates all online collar. Sends a message if none are online.
        Can be set to various intensities and durations.
        '''
        try:
            if ctx.guild and not ctx.guild.id in guilds_whitelisted_for_nsfw():
                return
            await self.shock_collar_operation(ctx, arg, "1")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.command(aliases=["sound"], case_insensitive=True, invoke_without_command=True)
    async def beep(self, ctx, *arg):
        '''Beeps all online collars. Sends a message if none are online.
        Can be set to various durations.
        '''
        try:
            if ctx.guild and not ctx.guild.id in guilds_whitelisted_for_nsfw():
                return
            await self.shock_collar_operation(ctx, arg, "2")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

#-------------------------------------------------------------------------------
#Auxiliary functions

    def initialize_collars(self):
        '''Returns a list of Collar objects created from the long-term database.
        '''
        data = read_from_json(PISHOCK_DATA_FILE)
        return [Collar(key, value["username"], value["privileged names"], value["device codes"],
                value["api key"], value["enabled"]) for key, value in data.items()]

    def collars_to_dict(self):
        '''Returns a dict of all Collar objects in cache.
        '''
        collars_dict = {}
        for collar in self.collars:
            collars_dict[collar.owner_name]: {
                    "username": collar.pishock_username,
                    "privileged names": collar.privileged_names,
                    "device codes": collar.device_codes,
                    "api key": collar.api_key,
                    "enabled": collar.enabled
            }
        return collars_dict

    def all_privileged_ids(self):
        '''Returns a list of all privileged IDs across all collars in cache.
        '''
        privileged_ids = []
        for collar in self.collars:
            privileged_ids += collar.privileged_ids
        return privileged_ids

    def write_cache_to_database(self):
        '''Writes all Collar objects in cache to the long-term database.
        '''
        write_to_json(PISHOCK_DATA_FILE, self.collars_to_dict())

    def is_any_collar_online(self):
        '''Returns True if any collar in cache is enabled.
        Returns False otherwise.
        '''
        for collar in self.collars:
            if collar.enabled:
                return True
        return False

    def update_forgot_timer(self):
        '''Ensures the forgot timer is restarted or stopped for each
        interaction.
        '''
        if not self.is_any_collar_online():
            self.forgot_timer.cancel()
            return
        if self.forgot_timer.is_running():
            self.forgot_timer.restart()
            return
        self.forgot_timer.start()

    async def shock_collar_operation(self, ctx, arg, op):
        '''Processes the input arg and sends the corresponding collar API
        request, given that collar permissions check out.
        '''
        if not self.is_any_collar_online():
            await ctx.channel.send("Device is currently set offline.")
            return
        intensity, duration = self.get_intensity_and_duration(arg)
        query_data = self.prepare_data_for_queries(op, intensity, duration)
        reqs = []
        async with aiohttp.ClientSession() as session:
            reqs = await asyncio.gather(*(self.post_to_api(query, session) for query in query_data))
        await self.acknowledge_operation(ctx, reqs)
        self.update_forgot_timer()

    async def post_to_api(self, data, session):
        '''Sends a POST request to the PiShock server with the given query data.
        Returns the PiShock server's response.
        '''
        url = "https://do.pishock.com/api/apioperate"
        headers = {"Content-Type":"application/json"}
        async with session.post(url=url, data=data, headers=headers) as response:
            data = json.loads(data)
            print(f"{datetime.datetime.now()} - Sent Shocker ID {data['Code']}: Op {data['Op']}, Int {data['Intensity']}, Dur {data['Duration']}")
            return response

    async def acknowledge_operation(self, ctx, reqs):
        '''Sends a message or reaction to the triggering message, giving
        feedback to how the shock collar(s) responded.
        '''
        for req in reqs:
            if not req:
                await ctx.channel.send("Unknown error occurred. Contact yoriyari.")
                return
            if req.status != 200:
                await ctx.channel.send(f"Couldn't contact PiShock server. Error code: {req.status}")
                return
            ## The section beneath has been commented out during parallelization,
            ## but if we fail to parse an error please look into this first. -YY
            #body = req.content.decode("utf-8")
            #if body != "Operation Succeeded." and body != "Operation Attempted.":
            #    await ctx.channel.send(f"Error: {body}")
            #    return
        try:
            await ctx.message.add_reaction("👍")
        except discord.HTTPException as e:
            if e.code != 10008:
                raise e

    def prepare_data_for_queries(self, op, intensity, duration):
        '''Returns a list of JSON dumps data, each prepared with the necessary
        info for a query to the PiShock server for each online collar.
        '''
        data = []
        for collar in self.collars:
            if not collar.enabled:
                continue
            for device_code in collar.device_codes:
                data.append(json.dumps({
                        "Username": collar.pishock_username,
                        "Name": "MUSA02",
                        "Code": device_code,
                        "Apikey": collar.api_key,
                        "Op": op,
                        "Intensity": intensity,
                        "Duration": duration
                }))
        return data

    def get_intensity_and_duration(self, arg):
        '''Returns the intensity and duration from the provided input arg list.
        '''
        arg = " ".join(arg)
        #Intensity
        intensity = self.get_first_digit_following_substrings(arg, self.intensity_aliases)
        intensity_end_index = None
        if not intensity:
            keywordless = re.search(r"^[\d.,]+", arg)
            if keywordless:
                intensity_end_index = keywordless.end()
                intensity = keywordless.group()
                if float(intensity) > 0.0 and float(intensity) < 1.0:
                    intensity = "1"
                else:
                    intensity = str(round(float(intensity)))
            else:
                intensity = self.intensity_default
        if float(intensity) > 100:
            intensity = "100"
        #Duration
        duration = self.get_first_digit_following_substrings(arg, self.duration_aliases)
        if not duration:
            if intensity_end_index != None:
                arg = arg[intensity_end_index:].strip()
            keywordless = re.search(r"^[\d.,]+", arg)
            if keywordless:
                duration = keywordless.group()
            else:
                duration = self.duration_default
        if float(duration) > 15:
            duration = "15"
        elif re.search("[.,]", duration):
            if float(duration) >= 0.1 and float(duration) <= 1.5:
                duration = str(int(float(duration)*1000))
            else:
                duration = str(round(float(duration)))
        return intensity, duration

    def get_first_digit_following_substrings(self, arg, substrings):
        '''Returns the first digit following any matching substring of text
        provided in a list. Returns None is not found.
        '''
        aliases = "({})".format(")|(".join(substrings))
        parameter = re.search(r"({})\S* [\d.,]+".format(aliases), arg)
        if not parameter:
            return None
        return re.search(r"[\d.,]+", parameter.group()).group()

async def setup(client):
    await client.add_cog(Shock(client))
