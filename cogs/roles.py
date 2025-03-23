#===============================================================================
# Roles v1.1.5
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 20 Mar 2025 - v1.1.5; Made strings with escape characters raw strings. -YY
# 08 Sep 2024 - v1.1.4; Removed 'self' parameter dependency from functions that
#               didn't use any client calls. -YY
# 07 May 2024 - v1.1.3; Moved UserError to a common error file. -YY
# 05 May 2024 - v1.1.2; Reworked help message import and error handling. -YY
# 24 Mar 2024 - v1.1.1; Raised required permission to create/edit role-giving
#               messages to admin rather than role management. -YY
# 01 Dec 2023 - v1.1.0; Added roles_edit to change the description or roles of
#               existing emoji and to append new roles to an existing role
#               assignment message. -YY
# 25 Jun 2023 - v1.0.1; Errors are now DMd to Yori instead of the user causing
#               the error. -YY
# 26 Apr 2023 - v1.0; Finished file. -YY
# 25 Apr 2023 - Started file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Make it possible to remove emoji/roles from an existing role assignment
#   message too. -YY
# - Make error handling ignore 500 errors. -YY
# - 404 error handling for removing reactions from members that left. -YY
#===============================================================================
# Description
# ..............................................................................
# roles.py allows admins to make MUSA post a message with reaction prompts that,
# once pressed, give the pressing user a specified role.
#===============================================================================

#Import Modules
import discord
from discord.ext import commands

from common.error_message import send_error, UserError
from common.help_message import send_help

from emoji import emoji_list as search_emoji
import re

#-------------------------------------------------------------------------------
#Cog Setup
class Roles(commands.Cog):
    def __init__(self,client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Roles cog loaded.")

    @commands.group(name="roles", aliases=["role"], case_insensitive=True, invoke_without_command=True)
    async def roles(self, ctx, *input):
        '''Posts a roles self-assignment message. Input has to include an emoji
        followed by a role, with optional text.
        '''
        try:
            if not ctx.channel.guild:
                raise UserError("There are no roles to add in DMs.")
                return
            if not ctx.channel.permissions_for(ctx.author).administrator:
                raise UserError("You need to be an administrator to give or remove roles.")
                return
            input = " ".join(input)
            msg, reactions = generate_role_assignment_message(input)
            message = None
            if ctx.message.reference:
                reference_id = ctx.message.reference.message_id
                message = await ctx.channel.fetch_message(reference_id)
                if not self.is_message_role_assignment(message):
                    return
                await message.edit(content=msg)
                await message.clear_reactions()
            else:
                message = await ctx.channel.send(msg)
            for reaction in reactions:
                await message.add_reaction(reaction)
            await ctx.message.delete()
        except UserError as e:
            await ctx.channel.send(e, delete_after=15.0)
            await ctx.message.delete(delay=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.group(name="roles_edit", aliases=["role_edit", "rolesedit", "roleedit", "edit_roles", "edit_role", "editroles", "editrole", "roles_add", "role_add", "rolesadd", "roleadd", "add_roles", "add_role", "addroles", "addrole"], case_insensitive=True, invoke_without_command=True)
    async def roles_edit(self, ctx, *input):
        '''Appends new emoji and roles to an existing role assignment message.
        Input has to be replying to an existing role assignment message and
        include an emoji followed by a role, with optional text.
        '''
        try:
            if not ctx.channel.guild:
                raise UserError("There are no roles to add in DMs.")
            if not ctx.channel.permissions_for(ctx.author).administrator:
                raise UserError("You need to be an administrator to give or remove roles.")
            if not ctx.message.reference:
                raise UserError("Please use this command in reply to an existing role assignment message in order to edit or add roles to that message.")
            reference_id = ctx.message.reference.message_id
            message = await ctx.channel.fetch_message(reference_id)
            if not self.is_message_role_assignment(message):
                raise UserError("Please use this command in reply to an existing role assignment message in order to edit or add roles to that message.")
            input = " ".join(input)
            content, reactions = edit_existing_message(message.content, input)
            await message.edit(content=content)
            for reaction in reactions:
                await message.add_reaction(reaction)
            await ctx.message.delete()
        except UserError as e:
            await ctx.channel.send(e, delete_after=15.0)
            await ctx.message.delete(delay=15.0)
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @roles.command(aliases=["help", "info"], case_insensitive=True, invoke_without_command=True)
    async def roles_help(self, ctx):
        try:
            await send_help(ctx.channel.send, "roles")
        except Exception as e:
            await send_error(self.client, e, reference=ctx.message.jump_url)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        '''Checks whether a reaction was added to one of the bot's role-giving
        messages and gives the appropriate role to the reacting user.
        '''
        try:
            message = await self.get_message_from_payload(payload)
            if self.is_reaction_for_role_assignment(payload, message):
                role = await self.get_role_from_payload(payload, message)
                if not role:
                    return
                member = await self.get_member_from_payload(payload)
                await member.add_roles(role)
        except Exception as e:
            message = await self.get_message_from_payload(payload)
            await send_error(self.client, e, reference=message.jump_url)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        '''Checks whether a reaction was removed from one of the bot's role-
        giving messages and removes the appropriate role from the reacting user.
        '''
        try:
            message = await self.get_message_from_payload(payload)
            if self.is_reaction_for_role_assignment(payload, message):
                role = await self.get_role_from_payload(payload, message)
                if not role:
                    return
                member = await self.get_member_from_payload(payload)
                await member.remove_roles(role)
        except Exception as e:
            message = await self.get_message_from_payload(payload)
            await send_error(self.client, e, reference=message.jump_url)

    async def get_message_from_payload(self, payload):
        '''Returns the message object from the payload.
        '''
        channel = self.client.get_partial_messageable(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        return message

    def is_reaction_for_role_assignment(self, payload, message):
        '''Returns a boolean stating whether to ignore a reaction or act on it.
        '''
        return self.is_message_role_assignment(message) and payload.user_id != self.client.user.id

    def is_message_role_assignment(self, message):
        '''Returns a boolean stating whether a message is a role assignment
        message.
        '''
        return message.author.id == self.client.user.id and message.content.startswith("**MUSA02 Role Assignment**")

    async def get_role_from_payload(self, payload, message=None):
        '''Returns a role Object based off of the payload. Include message for
        optimization.
        '''
        if message == None:
            message = await self.get_message_from_payload(payload)
        emoji = get_emoji_string_from_partial_emoji(payload.emoji)
        role_id = get_role_id_from_payload(message.content, emoji)
        if role_id == None:
            return None
        role = discord.Object(role_id)
        return role

    async def get_member_from_payload(self, payload):
        '''Returns the triggering member object from the payload.
        '''
        guild = self.client.get_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        return member

def get_emoji_followup_tuples(input):
    '''Returns a list of tuples formatted as (emoji, followup) where the
    first element is an emoji from the input, and the second element is the
    plaintext that follows the corresponding emoji. The list is sorted in
    the order in which they appear in the input.
    '''
    emoji_list = get_emoji_indices_from_message(input)
    tuples = []
    for i, match in enumerate(emoji_list):
        emoji = match["emoji"]
        if emoji in [e for e, _ in tuples]:
            continue
        followup = get_text_after_emoji_match(input, emoji_list, i).strip()
        tuples.append((emoji, followup))
    return tuples

def get_edited_preface(old_content, new_input):
    '''Returns the new preface is the new input defines one. Returns the old
    preface if the new input does not define a preface but does define
    emoji. Returns just the assignment title if the new input is empty.
    '''
    old_first_emoji = get_first_emoji_indices(old_content)
    new_first_emoji = get_first_emoji_indices(new_input)
    if not new_first_emoji:
        return "**MUSA02 Role Assignment**\n" + new_input
    if new_first_emoji["match_start"] > 0:
        return "**MUSA02 Role Assignment**\n" + new_input[:new_first_emoji["match_start"]]
    elif old_first_emoji:
        return old_content[:old_first_emoji["match_start"]-1]
    return old_content

def get_edited_old_roles(old_emoji_n_followup, new_emoji_n_followup):
    '''Returns the list of old emoji-and-followups, except any emoji that
    also appears in the new emoji-and-followups has its followup replaced
    by the new one. The old role is prefixed to the new followup if no new
    role is specified in the new followup.
    '''
    new_tuples = []
    for old_emoji, old_followup in old_emoji_n_followup:
        followup = old_followup
        for new_emoji, new_followup in new_emoji_n_followup:
            if old_emoji == new_emoji:
                if get_first_role_in_string(new_followup):
                    followup = new_followup
                else:
                    followup = get_first_role_in_string(old_followup) + " " + new_followup
                break
        new_tuples.append((old_emoji, followup))
    return new_tuples

def cull_overlapping_emoji(old_emoji_n_followup, new_emoji_n_followup):
    '''Returns new_emoji_n_followup after removing the entries that have
    emoji in common with old_emoji_n_followup.
    '''
    new_tuples = []
    all_old_emoji = [e for e, _ in old_emoji_n_followup]
    for emoji, followup in new_emoji_n_followup:
        if emoji not in all_old_emoji:
            new_tuples.append((emoji, followup))
    return new_tuples

def edit_existing_message(old_content, input):
    '''Edits an existing role assignment message. If a new preface is given
    in the input, replaces the old preface. If an existing emoji is given
    without defining a role, leaves the old role assigned to the same emoji
    but replaces the new text after the emoji and role. If an existing emoji
    is given with a new role, the role is redefined as well. If a new emoji
    is given with a role, appends the new emoji and role to the end.
    '''
    new_content = get_edited_preface(old_content, input)
    new_emoji_n_followup = get_emoji_followup_tuples(input)
    old_emoji_n_followup = get_emoji_followup_tuples(old_content)
    new_roles = get_edited_old_roles(old_emoji_n_followup, new_emoji_n_followup)
    new_roles += cull_overlapping_emoji(old_emoji_n_followup, new_emoji_n_followup)
    if len(new_roles) > 20:
        raise UserError("The maximum number of roles per message is 20.")
    for emoji, followup in new_roles:
        if not followup:
            raise UserError("Please specify a role after an emoji to associate them.")
        new_content += f"\n{emoji} {followup}"
    new_reactions = [e for e, _ in new_emoji_n_followup]
    return new_content, new_reactions

def generate_role_assignment_message(input):
    '''Returns a tuple containing the role self-assignment message string
    generated from the input string and a list of emoji to add as reactions
    to that message, given that the input string matches the required
    emoji-role format.
    '''
    emoji_n_followup = get_emoji_followup_tuples(input)
    if not emoji_n_followup:
        raise UserError("Please post emoji followed by the role they correspond to.")
    first_emoji = emoji_n_followup[0][0]
    match = re.search(first_emoji, input)
    first_emoji_index, _ = match.span()
    contents = input[:first_emoji_index]
    if len(emoji_n_followup) > 20:
        raise UserError("The maximum number of roles per message is 20.")
    for emoji, followup in emoji_n_followup:
        if not followup:
            raise UserError("Please specify a role after an emoji to associate them.")
        contents += f"\n{emoji} {followup}"
    msg = "**MUSA02 Role Assignment**\n"
    msg += contents
    distinct_emoji = [e for e, _ in emoji_n_followup]
    return msg, distinct_emoji

def get_first_emoji_indices(input):
    '''Returns the starting and ending indices of the first emoji in the
    input, including isolated regional indicators and custom Discord emoji.
    Returns None if there are no emoji in the input.
    '''
    all_emoji_indices = get_emoji_indices_from_message(input)
    if not all_emoji_indices:
        return None
    return all_emoji_indices[0]

def get_emoji_indices_from_message(input):
    '''Returns a list of dicts giving the starting position and ending
    position of every emoji, including isolated regional indicators and
    custom Discord emoji.
    '''
    emoji_list = search_emoji(input)
    valid_emoji = emoji_list
    regional_indicators = create_dict_of_regex_matches("[\U0001f1e6-\U0001f1ff]", input)
    for regional_indicator in regional_indicators:
        if not is_regional_indicator_part_of_emoji(regional_indicator, emoji_list):
            valid_emoji.append(regional_indicator)
    custom_emoji_list = create_dict_of_regex_matches(r"<a?:\w+:\d+>", input)
    valid_emoji += custom_emoji_list
    valid_emoji = sorted(valid_emoji, key=lambda dict: dict["match_start"])
    return valid_emoji

def is_regional_indicator_part_of_emoji(regional_indicator, emoji_list):
    '''Returns boolean value giving whether the regional indicator is
    included in a multi-part emoji symbol in the given emoji list.
    '''
    for emoji in emoji_list:
        if regional_indicator["match_start"] >= emoji["match_start"] and regional_indicator["match_start"] < emoji["match_end"]:
            return True
    return False

def create_dict_of_regex_matches(regex_expression, text):
    '''Returns a list of dicts giving the span as match_start and match_end,
    and the group as emoji, from all regex matches of a given expression.
    '''
    matches = re.finditer(regex_expression, text)
    entries = []
    for match in matches:
        start, end = match.span()
        emoji = match.group()
        entry = {"match_start": start, "match_end": end, "emoji": emoji}
        entries.append(entry)
    return entries

def get_text_after_emoji_match(input, emoji_list, index):
    '''Returns a string giving the text between the current index of the
    emoji_list match and the next emoji_list match or the end of input.
    '''
    start_index = emoji_list[index]["match_end"]
    if index+1 < len(emoji_list):
        end_index = emoji_list[index+1]["match_start"]
    else:
        end_index = len(input)
    text = input[start_index:end_index]
    return text

def get_first_role_in_string(text):
    '''Returns a string giving the first role that appears in the input
    string.
    '''
    match = re.search(r"<@&\d+>", text)
    if not match:
        return None
    return match.group()

def get_emoji_string_from_partial_emoji(emoji: discord.PartialEmoji):
    '''Returns a string representation of a partial emoji.
    '''
    if emoji.is_unicode_emoji():
        return emoji.name
    representation = "<"
    if emoji.animated:
        representation += "a"
    representation += f":{emoji.name}:{emoji.id}>"
    return representation

def get_role_id_from_payload(content, emoji: str):
    '''Returns the first role ID number found in the given content after the
    first occurrence of the given emoji.
    '''
    match = re.search(emoji, content)
    if not match:
        return None
    _, end_index = match.span()
    full_role = get_first_role_in_string(content[end_index:])
    role_id = re.search(r"\d+", full_role).group()
    return int(role_id)

async def setup(client):
    await client.add_cog(Roles(client))
