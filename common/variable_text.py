#===============================================================================
# Variable Text v1.0.1
# by Yoriyari
#===============================================================================
# Update History
# ..............................................................................
# 19 Oct 2022 - v1.0.1; Added fit_text_to_length. -YY
# 16 Oct 2022 - v1.0; Added get_closest_matches. -YY
#===============================================================================
# Notes
# ..............................................................................
#
#===============================================================================
# Description
# ..............................................................................
# variable_text.py handles various kinds of cases where you cannot be certain
# of what text input was given and conforming them to specification.
#===============================================================================

from fuzzywuzzy import fuzz, process
import textwrap, re

def get_closest_matches(word: str, list: list, max_matches=5):
    '''Returns either a single string if a perfect match was found, or a list
    of the closest matches that could be found for the input word in the input
    list.
    '''
    matches = process.extract(word, list, scorer=fuzz.token_set_ratio, limit=max_matches)
    matches = [match for match, _ in matches]
    for match in matches:
        if word.lower() == match.lower():
            return match
    return matches

def fit_text_to_length(text: str, max_length: int, delimiter=None, replacements=[], placeholder=" …"):
    '''Returns a shortened version of the input text that is made to barely fit
    within the given maximum length.
    If a delimiter is given, the shortening will occur to strings between
    occurrences of the delimiter.
    If a replacements list of tuples is given, each occurrence in the final
    text of the first element will be replaced with the second element. This is
    useful for restoring line breaks that are shortened away by textwrap...
    '''
    best_result = placeholder
    length = 1
    while True:
        substrings = text.split(delimiter) if delimiter != None else [text]
        substrings = [textwrap.shorten(s, length, placeholder=placeholder) for s in substrings]
        result = delimiter.join(substrings) if delimiter != None else "".join(substrings)
        for occur, replace in replacements:
            result = re.sub(occur, replace, result)
        if len(result) > max_length or length >= max_length:
            return best_result
        best_result = result
        length += 1
