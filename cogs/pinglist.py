#===============================================================================
# PingList v1.3.6
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 09 May 2025 - v1.3.6; Hardcoded new free react ID in Stonecutters. -YY
# 23 Mar 2025 - v1.3.5; Hid Mudae's Discord ID from file. Moved database to
#               secrets folder. -YY
# 20 Mar 2025 - v1.3.4; Made strings with escape characters raw strings. -YY
# 04 Mar 2025 - v1.3.3; Amended claim/rank filtering for series names to reflect
#               Mudae including commas in large numbers now. -YY
# 26 Feb 2025 - v1.3.2; Removed free reacts from chaos key pings. -YY
# 22 Feb 2025 - v1.3.1; Fixed chaos key pings not actually working. -YY
# 21 Feb 2025 - v1.3; Added !chaosping to allow users to opt into being pinged
#               for characters with chaos keys they own. -YY
# 05 Feb 2025 - v1.2; Added !clearpings. Removed markdown-sensitivity from
#               !removeping, particularly for removing preciseping entries. -YY
# 05 May 2024 - v1.1.4; Reworked help message import. Added error handling. -YY
# 30 Jun 2022 - v1.1.3; Fixed secondary aliases and wishprotect emoji not being
#               filtered out of the series title detection. -YY
# 22 Apr 2022 - v1.1.2; Included messages without "React to claim" text and
#               without "button react". Also allowed for itacilizing with _ when
#               removing pings. -YY
# 21 Apr 2022 - v1.1.1; Included messages with Mudae's optional "button react"
#               enabled, excluding wishlisted and owned characters. Also allowed
#               for itacilizing precise pings with _ in addition to *. Also now
#               includes character name when pinging. -YY
# 20 Apr 2022 - v1.1; Added asterisk filter for perfect title matches only.
#               Also fixed non-server members being pinged and made series title
#               detection more precise. -YY
# 18 Apr 2022 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Scrape whatever free react emoji is being used rather than hardcoding it,
#   such that it dynamically updates for each server. -YY
#===============================================================================
# Description
# ..............................................................................
# pinglist.py automatically pings users if the bot Mudae sends a message which
# contains a series title that that user opted into being pinged for, or if the
# character belongs to them and has a chaos key and they opted into those pings.
# Users can add and remove titles, including multiple at once separated by $
# symbols. Users can see their own and others' full lists. When Mudae posts a
# claimable character from a matching series, all users with matching pinglist
# entries get pinged. The title does not have to be a perfect match: a substring
# match is sufficient. Optional perfect matches are available by italicization.
#===============================================================================

#Import Modules
import discord
from discord import Embed, ui
from discord.ext import commands

from common.json_handling import write_to_json, read_from_json
from common.interactions import slice_list_page
from common.private_ids import discord_id
from common.error_message import send_error
from common.help_message import send_help

import re, math

PINGLIST_FILE = "secrets/pinglist_series.json"
CHAOS_PINGS_FILE = "secrets/pinglist_chaos.json"
VIEW_TIMEOUT = 600 # 10 minutes
PAGINATION_LENGTH = 15
MUDAE_ID = discord_id("mudae")

#-------------------------------------------------------------------------------

#Cog Setup
class PingList(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ping List cog loaded.")

    @commands.group(name="addping", aliases=["ap", "ping", "pingfor", "ping4", "add_ping", "ping_for", "pingadd", "ping_add", "pa"], case_insensitive=True, invoke_without_command=True)
    async def addping(self, ctx, *series):
        '''Allows user to add a series title to their pings list.
        '''
        try:
            if not series or series == ("help",) or series == ("info",):
                await send_help(ctx.channel.send, "addping")
                return
            series = self.get_series_from_command(series)
            user_id = str(ctx.author.id)
            self.add_pings_to_list(series, user_id)
            await ctx.message.add_reaction("👍")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.group(name="preciseping", aliases=["pp", "addpreciseping", "perfectping", "specificping", "add_precise_ping", "add_perfect_ping", "app", "precisepingadd", "perfectpingadd", "specificpingadd", "ppa", "spa", "asp"], case_insensitive=True, invoke_without_command=True)
    async def preciseping(self, ctx, *series):
        '''Allows user to add a series title to their pings list with precision
        filter enabled, without the user having to manually add itacilization.
        '''
        try:
            if not series or series == ("help",) or series == ("info",):
                await send_help(ctx.channel.send, "preciseping")
                return
            series = self.get_series_from_command(series)
            series = [f'*{title}*' for title in series]
            user_id = str(ctx.author.id)
            self.add_pings_to_list(series, user_id)
            await ctx.message.add_reaction("👍")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.group(name="removeping", aliases=["rp", "remove_ping", "pingremove", "ping_remove", "pr"], case_insensitive=True, invoke_without_command=True)
    async def removeping(self, ctx, *series):
        '''Allows user to remove a series title from their pings list.
        '''
        try:
            if not series or series == ("help",) or series == ("info",):
                await send_help(ctx.channel.send, "removeping")
                return
            series = self.get_series_from_command(series)
            user_id = str(ctx.author.id)
            unrecognized, unsubscribed = self.remove_pings_from_list(series, user_id)
            if unrecognized or unsubscribed:
                msg = ""
                if unrecognized:
                    msg += f"Series not found: **{', '.join(unrecognized)}**\n"
                if unsubscribed:
                    msg += f"You aren't on the ping list for: **{', '.join(unsubscribed)}**\n"
                if len(series) > len(unrecognized)+len(unsubscribed):
                    msg += "Other series have successfully been removed from your pinglist."
                await ctx.channel.send(msg)
            await ctx.message.add_reaction("👍")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.group(name="clearpings", aliases=["clear_pings", "clearping", "clear_ping", "pingclear", "ping_clear", "pingsclear", "pings_clear", "clearpinglist", "clear_pinglist", "clearpl", "clear_pl"], case_insensitive=True, invoke_without_command=True)
    async def clearpings(self, ctx, arg=None):
        '''Clears a user's pinglist after confirmation.
        '''
        try:
            if arg in ["help", "info"]:
                await send_help(ctx.channel.send, "clearpings")
                return
            msg = f"**{ctx.author.name}**, this will remove all entries from your pinglist. Please confirm."
            user_id = str(ctx.author.id)
            view = ViewClearPinglist(user_id)
            await ctx.channel.send(msg, view=view)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.group(name="pinglist", aliases=["pl", "apl", "ping_list", "pingslist", "pings_list", "pings"], case_insensitive=True, invoke_without_command=True)
    async def pinglist(self, ctx, user_id=None):
        '''Shows user a message with all entries on the pinglist of themself or
        a mentioned user.
        '''
        try:
            if user_id == ("help") or user_id == ("info"):
                await send_help(ctx.channel.send, "pinglist")
                return
            if user_id == None:
                user_id = str(ctx.author.id)
            user_id = user_id.lstrip("<@").rstrip(">")
            pinglist = read_from_json(PINGLIST_FILE)
            pings = []
            for title, users in pinglist.items():
                if user_id in users:
                    pings.append(title)
            username = self.client.get_user(int(user_id)).name
            title = f"**{username}'s pinglist:**"
            pings.sort()
            embed = generate_paginated_pings_embed(title, pings)
            await ctx.channel.send(embed=embed, view=ViewPinglistButtons(title, pings))
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.group(name="chaosping", aliases=["chaos_ping", "chaospings", "chaos_pings", "keyping", "key_ping", "keypings", "key_pings", "togglechaos", "togglekey", "togglekeys", "toggle_chaos", "toggle_key", "toggle_keys", "chaostoggle", "keytoggle", "keystoggle", "chaos_toggle", "key_toggle", "keys_toggle", "togglechaospings", "toggle_chaos_pings", "togglechaosping", "toggle_chaos_ping", "chaospingtoggle", "chaospingstoggle", "chaos_ping_toggle", "chaos_pings_toggle", "togglekeypings", "toggle_key_pings", "togglekeyping", "toggle_key_ping", "keypingtoggle", "keypingstoggle", "key_ping_toggle", "key_pings_toggle", "togglereact", "togglereacts", "toggle_react", "toggle_reacts", "reacttoggle", "reactstoggle", "react_toggle", "reacts_toggle"], case_insensitive=True, invoke_without_command=True)
    async def chaosping(self, ctx):
        '''Opts a user into being pinged for owned chaos keyed characters.
        '''
        try:
            database = read_from_json(CHAOS_PINGS_FILE)
            user_id = str(ctx.author.id)
            server_id = str(ctx.guild.id)
            if server_id not in database:
                database[server_id] = {"opted_in_users": [], "chaos_keyed_characters": []}
            if user_id in database[server_id]["opted_in_users"]:
                database[server_id]["opted_in_users"].remove(user_id)
                msg = "Pings for characters with chaos keys are now DISABLED for YOUR claims!"
            else:
                database[server_id]["opted_in_users"].append(user_id)
                msg = "Pings for characters with chaos keys are now ENABLED for YOUR claims!"
            await ctx.channel.send(msg)
            write_to_json(CHAOS_PINGS_FILE, database)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @chaosping.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def chaosping_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "chaosping")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @addping.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def addping_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "addping")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @removeping.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def removeping_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "removeping")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @preciseping.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def preciseping_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "preciseping")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @pinglist.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def pinglist_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "pinglist")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @clearpings.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def clearpings_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "clearpings")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            await self.add_chaos_chars_to_database(message)
            await self.ping_for_series(message)
            await self.ping_for_chaos(message)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        try:
            await self.add_chaos_chars_to_database(after)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    async def add_chaos_chars_to_database(self, message):
        '''If a card explicitly shows a character having 10+ keys, add the
        character's name to the chaos key database.
        '''
        if not self.message_contains_chaos_key(message):
            return
        charnames = self.get_charnames_from_chaos_key_marker(message)
        if not charnames:
            return
        database = read_from_json(CHAOS_PINGS_FILE)
        server_id = str(message.guild.id)
        if server_id not in database:
            database[server_id] = {"opted_in_users": [], "chaos_keyed_characters": []}
        database.get("server_id", {}).get("chaos_keyed_characters", [])
        for charname in charnames:
            if charname in database[server_id]["chaos_keyed_characters"]:
                continue
            database[server_id]["chaos_keyed_characters"].append(charname)
        write_to_json(CHAOS_PINGS_FILE, database)

    async def ping_for_series(self, message):
        '''Pings users if Mudae posts a ping-listed series.
        '''
        if not self.message_is_an_unclaimed_character_roll(message):
            return
        charname = self.get_charname_from_embed(message)
        series = self.get_series_from_embed(message)
        pinglist = read_from_json(PINGLIST_FILE)
        msg = f"**{charname}** from **{series}**"
        guild_ids = [str(member.id) for member in message.guild.members]
        for ping, users in pinglist.items():
            if re.search(r"^\*.+\*$", ping):
                if f"*{series.upper()}*" == ping:
                    msg = self.add_mentions_to_message(msg, users, guild_ids)
            elif ping in series.upper():
                msg = self.add_mentions_to_message(msg, users, guild_ids)
        if re.search(r"<@\d+>", msg):
            await message.reply(msg)

    async def ping_for_chaos(self, message):
        '''Pings users if one of their chaos keyed characters showed up and
        they're opted into pings for chaos keyed characters.
        '''
        if not self.message_is_a_claimed_character_roll(message):
            return
        if not message.components:
            return
        if self.are_all_reacts_free(message):
            return
        charname = self.get_charname_from_embed(message)
        server_id = str(message.guild.id)
        database = read_from_json(CHAOS_PINGS_FILE)
        chaos_chars = database.get(server_id, {}).get("chaos_keyed_characters", [])
        if charname not in chaos_chars:
            return
        username = self.get_owner_username_from_embed(message)
        if not username:
            return
        user_id = None
        async for member in message.guild.fetch_members():
            if username == member.name:
                user_id = str(member.id)
                break
        opted_in_users = database.get(server_id, {}).get("opted_in_users", [])
        if not user_id or user_id not in opted_in_users:
            return
        msg = f"**{charname}**'s kakera react has halved cost for <@{user_id}>"
        await message.reply(msg)

    def are_all_reacts_free(self, message):
        '''Returns True is all buttons on a message have the Kurt emoji.
        Returns False otherwise.
        '''
        for component in message.components: # Halt if all reacts are free
            if type(component) == discord.ActionRow and component.children:
                for child in component.children:
                    if (type(child) == discord.Button and child.emoji and
                            child.emoji.id not in [609264156347990016, 513832682485055509, 1308044033519652894]):
                        return False
        return True

    def add_mentions_to_message(self, msg, users, guild_ids=[]):
        '''Returns a string of user IDs appended to the given message as
        mentions. Optional parameter guild_ids is a whitelist filter, only
        adding a mention if the user ID is on it.
        '''
        for user in users:
            if f"<@{user}>" not in msg and user in guild_ids:
                msg += f" <@{user}>"
        return msg

    def add_pings_to_list(self, series, user_id):
        '''Adds new entries of a user to the pinglist json file.
        '''
        pinglist = read_from_json(PINGLIST_FILE)
        for title in series:
            if re.search(r"^(_|\*)\s*.+\s*(_|\*)$", title):
                title = self.italicize_title(title)
            if title in pinglist:
                if user_id not in pinglist[title]:
                    pinglist[title].append(user_id)
            else:
                pinglist[title] = [user_id]
        write_to_json(PINGLIST_FILE, pinglist)

    def italicize_title(self, title):
        '''Returns a given title bordered by one asterisk, with removed existing
        bordering asterisks, underscores, and whitespace from the given title.
        '''
        title = title.strip("*_ ")
        title = f"*{title}*"
        return title

    def remove_pings_from_list(self, series, user_id):
        '''Removes existing entries of a user from the pinglist json file.
        '''
        pinglist = read_from_json(PINGLIST_FILE)
        unrecognized_series = []
        already_unsubscribed_series = []
        for title in series:
            precise_title = f"*{title}*"
            if title not in pinglist and precise_title not in pinglist:
                unrecognized_series.append(title)
                continue
            if ((precise_title not in pinglist or (precise_title in pinglist and user_id not in pinglist[precise_title])) and
                    (title not in pinglist or (title in pinglist and user_id not in pinglist[title]))):
                already_unsubscribed_series.append(title)
                continue
            if title in pinglist:
                if user_id in pinglist[title]:
                    pinglist[title].remove(user_id)
                    if not pinglist[title]:
                        pinglist.pop(title)
            if precise_title in pinglist:
                if user_id in pinglist[precise_title]:
                    pinglist[precise_title].remove(user_id)
                    if not pinglist[precise_title]:
                        pinglist.pop(precise_title)
        write_to_json(PINGLIST_FILE, pinglist)
        return (unrecognized_series, already_unsubscribed_series)

    def message_is_an_unclaimed_character_roll(self, message):
        '''Returns boolean giving whether a message is a Mudae message with an
        unclaimed character roll.
        '''
        if message.author.id != MUDAE_ID:
            return False #Message not from Mudae
        if message.guild == None:
            return False #Message not in a server
        if not message.embeds:
            return False #Message has no Embed
        if not message.embeds[0].description:
            return False #Embed has no description
        if "React with any emoji to claim!" in message.embeds[0].description:
            return True #Claimable character! If this doesn't pass, user may have at some point enabled optional heart button react
        if not message.embeds[0].image:
            return False #Embed has no character portrait
        if message.embeds[0].footer and message.embeds[0].footer.text and "Belongs to " in message.embeds[0].footer.text:
            return False #Don't ping for owned characters
        if message.content and "Wished by " in message.content:
            return False #Don't ping for wishlisted characters
        if message.embeds[0].footer and message.embeds[0].footer.text and re.search(r"^\d+ / \d+$", message.embeds[0].footer.text):
            return False #Embed is a lookup, judging by image page footer
        if re.search(r"<:(fe)?male:\d+>", message.embeds[0].description):
            return False #Embed is a lookup or a newly added custom character, judging by Mudae's custom (fe)male emoji
        if re.search(r"((Claim)|(Like)) Rank: #[\d,]+", message.embeds[0].description):
            return False #Embed is a lookup, judging by ranks
        if re.search(" roulette*", message.embeds[0].description):
            return False #Embed is a lookup, judging by pool category marker
        if re.search(r"((Claim)|(Like))s: #[\d,]+", message.embeds[0].description):
            return True #Embed is a character roll with rank(s) enabled
        if message.components and len(message.components) == 1 and message.components[0].type == discord.ComponentType.action_row and message.components[0].children and len(message.components[0].children) == 1 and message.components[0].children[0].type == discord.ComponentType.button:
            return True #Probably using optional heart button react
        return True #Whatever

    def message_is_a_claimed_character_roll(self, message):
        '''Returns True if the a message is a Mudae message with a claimed
        character roll.
        '''
        if message.author.id != MUDAE_ID:
            return False #Message not from Mudae
        if message.guild == None:
            return False #Message not in a server
        if not message.embeds:
            return False #Message has no Embed
        if not message.embeds[0].description or not message.embeds[0].footer:
            return False #Embed has no description or footer
        if re.search(r"Belongs to [.\w]+", message.embeds[0].footer.text):
            if not re.search("<:female:452463537508450304>|<:male:452470164529872899>", message.embeds[0].description):
                return True #Claimed character card without gender marker indicates a roll
        return False

    def message_contains_chaos_key(self, message):
        '''Returns True if the message has a Mudae Embed with a chaos key.
        '''
        if message.author.id != MUDAE_ID:
            return False #Message not from Mudae
        if message.guild == None:
            return False #Message not in a server
        if not message.embeds:
            return False #Message has no Embed
        if not message.embeds[0].description:
            return False #Embed has no description
        if "<:chaoskey:690110264166842421>" in message.embeds[0].description:
            return True #Chaos key is present
        return False

    def get_series_from_command(self, series):
        '''Returns a list of strings giving series names.
        Receives a list of words and $ separators. Returned list consists of
        those words concatenated with space separators, split upon where
        the original list had $ separators.
        '''
        series = " ".join(series)
        series = series.split("$")
        for i, title in enumerate(series):
            series[i] = title.strip().upper()
        return series

    def get_series_from_embed(self, message):
        '''Returns the series name from an Embed of a message by filtering out
        irrelevant parts of roll Embeds.
        '''
        try:
            desc = message.embeds[0].description
            series = desc.splitlines()
            series = [line for line in series if not re.search(r"(^Claims: #[\d,]+$)|(^Likes: #[\d,]+$)|(^\*\*[\d,]+\*\*<:.+:\d+>$)|(^\*|_.+\*|_$)|(^React with any emoji to claim!$)", line)]
            series = " ".join(series)
            series = re.sub(r"\s<:wishprotect:\d+>$", "", series)
            return series
        except:
            return None

    def get_charnames_from_chaos_key_marker(self, message):
        '''Returns the character name near a chaos key emoji.
        '''
        try:
            embed = message.embeds[0]
            if re.search(r"Belongs to [.\w]+", embed.footer.text):
                return [embed.author.name] #Only infomarry and rolls have this footer, so return Embed header
            lines = embed.description.split("\n")
            charnames = []
            for line in lines:
                match = re.search(r"^(\*\*#[\d,]+\*\* - \*\*)?([^💞]+) ( 💞\*\* - .+ )?·.*<:chaoskey:690110264166842421>", line)
                if match: #This is for commands $mmy= and $topy=
                    charname = match.group(2)
                    charnames.append(charname)
                    continue
                match = re.search(r"^<:chaoskey:690110264166842421> \([\d,]+\) \*\*(.+)\*\* => .+$", line)
                if match: #This is for command $tsy=
                    charname = match.group(1)
                    charnames.append(charname)
            return charnames
        except:
            return None

    def get_charname_from_embed(self, message):
        '''Returns the header of an Embed of a message.
        '''
        try:
            name = message.embeds[0].author
            if name:
                name = name.name
            return name
        except:
            return None

    def get_owner_username_from_embed(self, message):
        '''Returns the username in the ownership footer of a message Embed.
        '''
        try:
            footer = message.embeds[0].footer.text
            match = re.search(r"Belongs to ([.\w]+)", footer)
            name = match.group(1)
            return name
        except:
            return None

#-------------------------------------------------------------------------------

def generate_paginated_pings_embed(title: str, pings: list, page=1):
    '''Returns an Embed supporting large lists of ping titles by only
    rendering a portion of the list
    '''
    sliced_pings = slice_list_page(pings, page, PAGINATION_LENGTH)
    desc = "(no series found)"
    if pings:
        desc = "\n".join(sliced_pings)
    embed = Embed(title=title, description=desc)
    if len(pings) > PAGINATION_LENGTH:
        total = math.ceil(len(pings)/PAGINATION_LENGTH)
        embed.set_footer(text=f"Page {page}/{total}")
    return embed

#Select item to show details of menu
class ViewPinglistButtons(ui.View):
    def __init__(self, title=None, pings=[], page=1):
        super().__init__(timeout=VIEW_TIMEOUT)
        if len(pings) > PAGINATION_LENGTH*2:
            self.add_item(ButtonPinglistBack(title, pings, page))
            self.add_item(ButtonPinglistForward(title, pings, page))
        elif len(pings) > PAGINATION_LENGTH:
            if page == 2:
                self.add_item(ButtonPinglistBack(title, pings, page))
            else:
                self.add_item(ButtonPinglistForward(title, pings, page))

#Select item to show details of menu
class ViewClearPinglist(ui.View):
    def __init__(self, user_id: str):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.add_item(ButtonClearConfirm(user_id))
        self.add_item(ButtonClearCancel(user_id))

class ButtonPinglistBack(ui.Button):
    def __init__(self, title: str, pings: list, page: int):
        self.title = title
        self.pings = pings
        self.prev_page = math.ceil(len(pings)/PAGINATION_LENGTH) if page<=1 else page-1
        super().__init__(label=f"← Page {self.prev_page}", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction):
        try:
            embed = generate_paginated_pings_embed(self.title, self.pings, self.prev_page)
            view = ViewPinglistButtons(self.title, self.pings, self.prev_page)
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonPinglistForward(ui.Button):
    def __init__(self, title: str, pings: list, page: int):
        self.title = title
        self.pings = pings
        self.next_page = 1 if PAGINATION_LENGTH*page>=len(pings) else page+1
        super().__init__(label=f"Page {self.next_page} →", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction):
        try:
            embed = generate_paginated_pings_embed(self.title, self.pings, self.next_page)
            view = ViewPinglistButtons(self.title, self.pings, self.next_page)
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonClearConfirm(ui.Button):
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(label=f"Clear Pinglist", style=discord.ButtonStyle.red)

    async def callback(self, interaction):
        try:
            if str(interaction.user.id) != self.user_id:
                await interaction.response.send_message("Only the pinglist owner may confirm.", ephemeral=True)
                return
            msg = interaction.message.content + "\nPinglist cleared."
            await interaction.response.edit_message(content=msg, view=None)
            pinglist = read_from_json(PINGLIST_FILE)
            emptied_titles = []
            for title, users in pinglist.items():
                if self.user_id in users:
                    pinglist[title].remove(self.user_id)
                    if not pinglist[title]:
                        emptied_titles.append(title)
            for title in emptied_titles:
                pinglist.pop(title)
            write_to_json(PINGLIST_FILE, pinglist)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

class ButtonClearCancel(ui.Button):
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(label=f"Cancel", style=discord.ButtonStyle.blurple)

    async def callback(self, interaction):
        try:
            if str(interaction.user.id) != self.user_id:
                await interaction.response.send_message("Only the pinglist owner may cancel.", ephemeral=True)
                return
            msg = interaction.message.content + "\nProcess cancelled."
            await interaction.response.edit_message(content=msg, view=None)
        except Exception as e:
            await send_error(interaction.client, e, reference=interaction.message.jump_url)

async def setup(client):
    await client.add_cog(PingList(client))
