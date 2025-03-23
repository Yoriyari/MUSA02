#===============================================================================
# Monochrome Roles v1.1.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.1.1; Hid Discord user IDs and server IDs from file. Updated
#               error handling. -YY
# 27 Apr 2024 - v1.1.0; Moved named/coloured roles to the new personal roles
#               feature's automated presets, leaving only pronouns roles. -YY
# 23 Apr 2024 - v1.0.11; Split Azu role into white, green, and all. -YY
# 16 Mar 2024 - v1.0.10; Added Katya role. -YY
# 18 Jan 2024 - v1.0.9; Added Kira role. -YY
# 20 Dec 2023 - v1.0.8; Added Glitter role and "Holly" to Aries's names. -YY
# 30 Nov 2023 - v1.0.7; Added pronoun roles to every member and fusion. -YY
# 17 Nov 2023 - v1.0.6; Added Gaige role. -YY
# 26 Oct 2023 - v1.0.5; Extended function to Monochrome's alt account too. -YY
# 17 Oct 2023 - v1.0.4; Added Fang role. -YY
# 12 Sep 2023 - v1.0.3; Added Rosé role. -YY
# 29 Jul 2023 - v1.0.2; Added Poppy and Neon roles. -YY
# 21 Jul 2023 - v1.0.1; Removed Bot role on Azu's request. -YY
# 20 Jul 2023 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
# - Move role IDs per member to a data file? -YY
# - Save certain new roles if Monochrome receives any (e.g. pronouns). -YY
# - Let Monochrome alter their roles themselves. -YY
#===============================================================================
# Description
# ..............................................................................
# monochrome_roles.py gives Discord user Monochrome the pronouns roles
# corresponding to each headmate in the TITS server.
#===============================================================================

#Import Modules
import discord
from discord import Embed, ui
from discord.ext import commands

from common.private_ids import discord_id, guild_id
from common.error_message import send_error

#-------------------------------------------------------------------------------

#Define names and roles
class Monochrome:
    def __init__(self, names={}, roles={}):
        self.names = names
        self.roles = roles

#Cog Setup
class MonochromeRoles(commands.Cog):
    def __init__(self,client):
        self.client = client
        self.monochrome = discord_id("monochrome", "monochrome alt")
        self.whitelisted_server = guild_id("tits")
        self.roles = { 1034197313381470291, 1034197338266279976, 1034197359283949680, 1034197383933861898,
                       1034197390955130982, 1179824991194320946, 1179823318442967142, 1179823382611632220,
                       1218479394063122512
                     }
        self.system = { Monochrome({"Aries", "Anya", "Holly"}, {1034197338266279976, 1034197313381470291}), #Aries, She/her, He/him
                        Monochrome({"Azu", "Carnelian"}, {1034197359283949680}), #Azu (All), They/them
                        Monochrome({"Sera", "Serafina"}, {1034197359283949680, 1034197383933861898}), #Azu (White), They/them, It/its
                        Monochrome({"Ivy"}, {1034197359283949680}), #Azu (Green), They/them
                        Monochrome({"Aurora", "Day", "Nadia"}, {1179823318442967142, 1034197338266279976}), #Aurora, E/Eir, She/her
                        Monochrome({"Athame", "Dawn", "Ashley", "Ash"}, {1179823318442967142, 1034197359283949680}), #Athame, E/Eir, They/them
                        Monochrome({"Aeon", "Dusk", "Ace"}, {1179823318442967142, 1034197383933861898}), #Aeon, A/eir, It/its
                        Monochrome({"Ema"}, {1179824991194320946}), #Ema, She/Her (caps)
                        Monochrome({"Tempest", "Atmos"}, {1179823382611632220}), #Tempest, Ix/ix'
                        Monochrome({"Poppy"}, {1034197338266279976}), #Poppy, She/her
                        Monochrome({"Neon"}, {1034197383933861898}), #Neon, It/its
                        Monochrome({"Rosé"}, {1034197338266279976}), #Rosé, She/her
                        Monochrome({"Fang"}, {1034197359283949680}), #Fang, They/them
                        Monochrome({"Gaige"}, {1034197390955130982}), #Gaige, Any
                        Monochrome({"Glitter"}, {1034197338266279976}), #Glitter, She/her
                        Monochrome({"Kira"}, {1034197383933861898}), #Kira, It/its
                        Monochrome({"Skye"}, {1034197359283949680}), #[Skye], They/them
                        Monochrome({"Katya"}, {1034197338266279976}), #Katya, She/her
                        Monochrome({"Monochrome"}, {1034197359283949680}) #[Monochrome], They/them
                      }

    @commands.Cog.listener()
    async def on_ready(self):
        print("Monochrome Roles cog loaded.")

    @commands.Cog.listener()
    async def on_message(self, message):
        '''Detects if Monochrome's current roles reflect their display name
        and adds/removes the relevant roles if they do not.
        '''
        try:
            if message.guild and message.guild.id == self.whitelisted_server and message.author.id in self.monochrome:
                display_name = message.author.display_name.split(" ")[0]
                for headmate in self.system:
                    if display_name in headmate.names:
                        current_roles = {role.id for role in message.author.roles}
                        roles_to_remove = current_roles & self.roles - headmate.roles
                        roles = (discord.Object(role) for role in headmate.roles)
                        if roles:
                            await message.author.add_roles(*roles)
                        roles = (discord.Object(role) for role in roles_to_remove)
                        if roles:
                            await message.author.remove_roles(*roles)
                        break
        except Exception as e:
            await send_error(self.client, e, reference=message.jump_url)

async def setup(client):
    await client.add_cog(MonochromeRoles(client))
