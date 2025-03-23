#===============================================================================
# Prefix v1.0.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 23 Mar 2025 - v1.0.1; Moved database to secrets folder. -YY
# 21 Oct 2022 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# prefix.py returns a Discord server's prefixes. To change prefixes, see
# cogs/prefix.py.
#===============================================================================

PREFIXES_FILE = "secrets/musa_prefixes.txt"

##Get command prefix
def get_prefix_of_guild(guild):
    prefix = ["!"]
    if guild != None:
        with open(PREFIXES_FILE, "r") as file:
            lines = file.read().splitlines()
        for i, line in enumerate(lines):
            if i % 2 == 0:
                if guild.id == int(line):
                    prefix = [p for p in lines[i+1].split()]
                    break
    return prefix
