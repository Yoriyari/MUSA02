#===============================================================================
# JSON Handling v1.0
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 25 Jan 2022 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# json_handling.py takes care of json file handling.
#===============================================================================

#Import Modules
import json

def write_to_json(filename, input):
    j = json.dumps(input)
    with open(filename, "w", encoding="utf8") as f:
        f.write(j)

def read_from_json(filename):
    with open(filename, "r", encoding="utf8") as f:
        j = f.read()
    return json.loads(j)
