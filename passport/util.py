# -*- coding: utf-8 -*-


# ..................................................................... Imports
import textwrap


# ........................................................... Utility functions
def dedented(message, strip_type):
    """ Dedents a multiline string and strips leading (lstrip)
        or leading and trailing characters (strip).

        Args:
            message (str): An arbitrary string
            strip_type (str): Defines the type of strip()

        Returns:
            string (str): A stripped and dedented string
    """
    if strip_type == "strip":
        string = textwrap.dedent(message).strip()
    elif strip_type == "lstrip":
        string = textwrap.dedent(message).lstrip()

    return string
