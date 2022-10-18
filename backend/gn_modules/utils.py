"""
    utils, patch, etc...
"""


import unicodedata


def unaccent(input_str):
    """
    remove accent
    https://stackoverflow.com/a/517974
    """
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])
