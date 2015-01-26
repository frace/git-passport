# -*- coding: utf-8 -*-

# ..................................................................... Imports
import argparse


# .......................................................... Argparse functions
def release():
    """ Define available arguments for the command line usage.

        Returns:
            args (obj): An object containing predefined args
    """
    arg_parser = argparse.ArgumentParser(add_help=False)
    arg_parser.description = "manage multiple Git identities"
    arg_parser.usage = (
        "git passport (--select | --delete | --active | --passports)"
    )

    arg_group = arg_parser.add_mutually_exclusive_group()
    arg_group.add_argument(
        "-h",
        action="help",
        help="show this help message and exit"
    )

    arg_group.add_argument(
        "-s",
        "--select",
        action="store_true",
        help="select a passport"
    )

    arg_group.add_argument(
        "-d",
        "--delete",
        action="store_true",
        help="delete the active passport in .git/config"
    )

    arg_group.add_argument(
        "-a",
        "--active",
        action="store_true",
        help="print the active passport in .git/config"
    )

    arg_group.add_argument(
        "-p",
        "--passports",
        action="store_true",
        help="print all passports in ~/.gitpassport"
    )

    args = arg_parser.parse_args()
    return args
