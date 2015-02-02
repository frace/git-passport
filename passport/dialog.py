# -*- coding: utf-8 -*-


# ..................................................................... Imports
import sys

from . import util


# ............................................................ Dialog functions
def get_input(pool):
    """ Prompt a user to select a number from a list of numbers representing
        available Git IDs. Optionally the user can choose `q` to quit the
        selection process.

        Args:
            pool (list): A list of numbers representing available Git IDs

        Returns:
            None (NoneType): If the user quits the selection dialog
            selection (int): A number representing a Git ID chosen by a user
    """
    while True:
        # Redirect sys.stdin to an open filehandle from which input()
        # is able to read
        sys.stdin = open("/dev/tty")
        selection = input("» Select an [ID] or enter «(q)uit» to exit: ")

        try:
            selection = int(selection)

            if selection in pool:
                return selection

        except ValueError:
            if selection == "q" or selection == "quit":
                return None
            continue

        # Reset sys.stdin to its default value, even if we return early
        # when an exception occurs
        finally:
            sys.stdin = sys.__stdin__


def print_choice(choice):
    """ Before showing the actual prompt by calling `get_user_input()` print a
        list of available Git IDs containing properties ID, «scope», name,
        email and service.

        Args:
            choice (dict): Contains a list of preselected Git ID candidates

        Returns:
            True (bool): On success
    """
    for key, value in choice.items():
        if value.get("flag") == "global":
            msg = """
                ~:Global passport:
                    . User:   {}
                    . E-Mail: {}
            """.format(
                value["name"],
                value["email"]
            )

            print(util.dedented(msg, "lstrip"))

        if value.get("service"):
            msg = """
                ~Passport:     {}
                    . User:    {}
                    . E-Mail:  {}
            """.format(
                value["service"],
                value["name"],
                value["email"]
            )

            print(util.dedented(msg, "lstrip"))

    return True
