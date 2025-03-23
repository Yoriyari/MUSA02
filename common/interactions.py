#===============================================================================
# Interactions v1.0
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 11 Oct 2022 - v1.0; Started and finished file. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# interactions.py contains common functions useful for Discord Interaction
# handling.
#===============================================================================

#Import Modules
import discord
from discord import ui

def slice_list_page(labels: list, page: int, max_options=25):
    '''Returns the labels that are on the given page of a list.
    '''
    labels_page = labels[max_options*(page-1):max_options*page]
    return labels_page

def generate_selectoptions(labels: list, values=None, max_options=25):
    '''Creates a list of up to 25 SelectOptions objects consisting of the given
    list of labels.
    '''
    options = []
    for i, label in enumerate(labels):
        option = None
        if values != None and i < len(values):
            option = discord.SelectOption(label=label, value=values[i])
        else:
            option = discord.SelectOption(label=label)
        options.append(option)
        if i+1 >= max_options:
            break
    return options

def generate_selectoptions_lists(labels: list, max_lists=5):
    '''Creates a list of up to five lists each containing up to 25 SelectOptions
    objects consisting of the given list of labels.
    '''
    options_lists = []
    labels_list = []
    for i, label in enumerate(labels):
        labels_list.append(label)
        if (i+1) % 25 == 0 or i+1 == len(labels):
            options = generate_selectoptions(labels_list)
            options_lists.append(options)
            labels_list = []
        if i+1 >= 25*max_lists:
            break
    return options_lists

def generate_selects(labels: list, max_selects=5, placeholder=None):
    '''Creates a list of up to five Select objects consisting of the given list
    of labels.
    '''
    selects = []
    options_lists = generate_selectoptions_lists(labels, max_lists=max_selects)
    for options in options_lists:
        select = ui.Select(placeholder=placeholder, options=options)
    return selects
