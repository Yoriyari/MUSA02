#===============================================================================
# YAML Handling v1.0
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 01 May 2024 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# yaml_handling.py takes care of YAML file handling.
#===============================================================================

#Import Modules
import yaml

def write_to_yaml(filename, input, encoding="utf8"):
    with open(filename, "w", encoding=encoding) as f:
        yaml.dump(input, f)

def read_from_yaml(filename, encoding="utf8"):
    with open(filename, "r", encoding=encoding) as f:
        return yaml.safe_load(f)
