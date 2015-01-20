#!/usr/bin/env python3
# -*- coding: utf-8 -*-


""" git-passport is a Git command and hook written in Python to manage multiple
    Git users / user identities.
"""


# ..................................................................... Imports
import argparse
import configparser
import os.path
import re
import subprocess
import sys
import textwrap
import time
import urllib.parse


# .......................................................... Argparse functions
def args_release():
    """ Define available arguments for the command line usage.

        Returns:
            args (obj): An object containing predefined args
    """
    arg_parser = argparse.ArgumentParser(add_help=False)
    arg_parser.description = "manage multiple Git identities"
    arg_parser.usage = "git passport (-h | --choose | --remove | --show)"

    arg_group = arg_parser.add_mutually_exclusive_group()
    arg_group.add_argument("-h",
                           action="help",
                           help="show this help message and exit")
    arg_group.add_argument("-c",
                           "--choose",
                           action="store_true",
                           help="choose a passport")
    arg_group.add_argument("-r",
                           "--remove",
                           action="store_true",
                           help="remove a passport from a .git/config")
    arg_group.add_argument("-s",
                           "--show",
                           action="store_true",
                           help="show the active passport set in .git/config")

    args = arg_parser.parse_args()
    return args


# ............................................................ Config functions
def config_preset(filename):
    """ Create a configuration file containing sample data inside the home
        directory if none exists yet.

        Args:
            filename (str): The complete `filepath` of the configuration file
    """
    if os.path.exists(filename):
        return

    preset = configparser.ConfigParser()

    preset["General"] = {}
    preset["General"]["enable_hook"] = "True"
    preset["General"]["sleep_duration"] = "0.75"

    preset["Passport 0"] = {}
    preset["Passport 0"]["email"] = "email_0@example.com"
    preset["Passport 0"]["name"] = "name_0"
    preset["Passport 0"]["service"] = "github.com"

    preset["Passport 1"] = {}
    preset["Passport 1"]["email"] = "email_1@example.com"
    preset["Passport 1"]["name"] = "name_1"
    preset["Passport 1"]["service"] = "gitlab.com"

    try:
        msg = """
            No configuration file found.
            Generating a sample configuration file.
        """
        print(dedented(msg, "strip"))
        with open(filename, "w") as configfile:
            preset.write(configfile)
        sys.exit("\n~Done~")

    except Exception:
        raise


def config_validate_scheme(filename):
    """ Validate section and option names of a provided configuration file.
        Quit the script and tell the user if we find false names.

        Args:
            filename (str): The complete `filepath` of the configuration file
    """
    raw_config = configparser.ConfigParser()
    raw_config.read(filename)

    whitelist = [{"General", "Passport"},
                 {"email", "enable_hook", "name", "service", "sleep_duration"}]

    # Create a list containing non-whitelisted section and option names
    pattern_section = r"^(Passport)\s[0-9]+$"
    false_scheme = [[section  # Validate sections
                     for section in raw_config.sections()
                     if section not in whitelist[0]
                     if not re.match(pattern_section, section)],
                    [option  # Validate options
                     for section in raw_config.sections()
                     for option in raw_config.options(section)
                     if option not in whitelist[1]]]

    # Quit if we have wrong section names
    if len(false_scheme[0]):
        msg = """
            E > Configuration > Invalid sections:
            >>> {}

            Allowed sections (Passport sections scheme: "Passport 0"):
            >>> {}
        """.format(", ".join(false_scheme[0]),
                   ", ".join(whitelist[0]))
        print(dedented(msg, "strip"))
        sys.exit()

    # Quit if we have wrong option names
    if len(false_scheme[1]):
        msg = """
            E > Configuration > Invalid options:
            >>> {}

            Allowed options:
            >>> {}
        """.format(", ".join(false_scheme[1]),
                   ", ".join(whitelist[1]))
        print(dedented(msg, "strip"))
        sys.exit()


def config_validate_values(filename):
    """ Validate certain values of a provided configuration file.
        Quit the script and tell the user if we find false values.

        Values to be validated:
            email: E-Mail scheme
            sleep_duration: Float
            enable_hook: Boolean

        Args:
            filename (str): The complete `filepath` of the configuration file
    """
    def filter_email(config):
        pattern_section = r"^(Passport)\s[0-9]+$"
        pattern_email = r"[^@]+@[^@]+\.[^@]+"
        for section in config.sections():
            if re.match(pattern_section, section):
                email = config.get(section, "email")
                if not re.match(pattern_email, email):
                    yield email

    raw_config = configparser.ConfigParser()
    raw_config.read(filename)

    false_email = list(filter_email(raw_config))

    # Quit if we have wrong email addresses
    if len(false_email):
        msg = """
            E > Configuration > Invalid email address:
            >>> {}
        """.format(", ".join(false_email))
        print(dedented(msg, "strip"))
        sys.exit()

    # Quit if we have wrong boolean values
    try:
        raw_config.getboolean("General", "enable_hook")
    except ValueError:
        msg = "E > Configuration > enable_hook: Expecting True or False."
        print(msg)
        sys.exit()

    # Quit if we have wrong float values
    try:
        raw_config.getfloat("General", "sleep_duration")
    except ValueError:
        msg = "E > Configuration > sleep_duration: Expecting float or number."
        print(msg)
        sys.exit()


def config_release(filename):
    """ Read a provided configuration file and «import» sections and their
        validated keys/values into a dictionary.

        Args:
            filename (str): The complete `filepath` of the configuration file

        Returns:
            config (dict): Contains all allowed configuration sections
    """
    def passport(config):
        pattern_section = r"^(Passport)\s[0-9]+$"
        for passport in config.items():
            if re.match(pattern_section, passport[0]):
                yield dict(passport[1])

    raw_config = configparser.ConfigParser()
    raw_config.read(filename)

    config = {}
    config["enable_hook"] = raw_config.getboolean("General", "enable_hook")
    config["sleep_duration"] = raw_config.getfloat("General", "sleep_duration")
    config["git_passports"] = dict(enumerate(passport(raw_config)))

    return config


# ............................................................... Git functions
def git_infected():
    """ Checks if the current directory is under Git version control.

        Raises:
            Exception: If subprocess.Popen() fails
    """
    try:
        git_process = subprocess.Popen([
            "git",
            "rev-parse",
            "--is-inside-work-tree"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Captures the git return code
        exit_status = git_process.wait()

    except Exception:
        raise

    if exit_status == 0:
        return
    elif exit_status == 128:
        msg = "The current directory does not seem to be a Git repository."
        print(msg)
        sys.exit()


def git_config_get(config, scope, property):
    """ Get the email address, username of the global or local Git ID.
        Also gets the local remote.origin.url of a Git repository.

        Args:
            config (dict): Contains validated configuration options
            scope (str): Search inside a `global` or `local` scope
            property (str): Type of `email` or `name` or `url`

        Returns:
            value (str): A name, email address or url

        Raises:
            Exception: If subprocess.Popen() fails
    """
    git_args = "remote.origin.url" if property == "url" else "user." + property

    try:
        git_process = subprocess.Popen([
            "git",
            "config",
            "--get",
            "--" + scope,
            git_args
        ], stdout=subprocess.PIPE)

        value = git_process.communicate()[0].decode("utf-8")
        return value.replace("\n", "")

    except Exception:
        raise


def git_config_set(config, value, property):
    """ Set the email address or username as a local Git ID for a repository.

        Args:
            config (dict): Contains validated configuration options
            value (str): A name or email address
            property (str): Type of `email` or `name`

        Raises:
            Exception: If subprocess.Popen() fails
    """
    try:
        subprocess.Popen([
            "git",
            "config",
            "--local",
            "user." + property,
            value
        ], stdout=subprocess.PIPE)

    except Exception:
        raise


def git_config_remove(silent=True):
    """ Remove an existing Git identity.

        Raises:
            Exception: If subprocess.Popen() fails
    """
    try:
        git_process = subprocess.Popen([
            "git",
            "config",
            "--local",
            "--remove-section",
            "user"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Captures the git return code
        exit_status = git_process.wait()

    except Exception:
        raise

    if not silent:
        if exit_status == 0:
            msg = "Passport removed."
        elif exit_status == 128:
            msg = "No passport set."

        print(msg)


# ............................................................ Dialog functions
def get_user_input(pool):
    """ Prompt a user to select a number from a list of numbers representing
        available Git IDs. Optionally the user can choose `q` to quit the
        selection process.

        Args:
            pool (list): A list of numbers representing available Git IDs

        Returns:
            selection (int): A number representing a Git ID chosen by a user
    """
    while True:
        #  Redirect sys.stdin to an open filehandle from which input() can read
        sys.stdin = open("/dev/tty")
        selection = input("» Select an [ID] or enter «(q)uit» to exit: ")
        sys.stdin = sys.__stdin__  # Reset the stdin to its default value

        try:
            selection = int(selection)
        except ValueError:
            if selection == "q" or selection == "quit":
                sys.exit()
            continue

        if selection in pool:
            return selection


def print_choice(choice):
    """ Before showing the actual prompt by calling `get_user_input()` print a
        list of available Git IDs containing properties ID, «scope», name,
        email and service.

        Args:
            choice (dict): Contains a list of preselected Git ID candidates
    """
    for key, value in choice.items():
        if value.get("flag") == "global":
            msg = """
                ~:Global ID: {}
                    . User:   {}
                    . E-Mail: {}
            """.format(
                key,
                value["name"],
                value["email"]
            )
            print(dedented(msg, "lstrip"))
        elif not value.get("service"):
            msg = """
                ~:Passport ID: {}
                    . User:   {}
                    . E-Mail: {}
            """.format(
                key,
                value["name"],
                value["email"]
            )
            print(dedented(msg, "lstrip"))
        else:
            msg = """
                ~Passport ID: {}
                    . User:    {}
                    . E-Mail:  {}
                    . Service: {}
            """.format(
                key,
                value["name"],
                value["email"],
                value["service"]
            )
            print(dedented(msg, "lstrip"))


# ........................................................... Utility functions
def dedented(message, strip_type):
    """ Dedents a multiline string and strips leading (lstrip),
        trailing (rstrip) or leading and trailing characters (strip).

        Args:
            message (str): An arbitrary string
            strip_type (str): Defines the type of strip()

        Returns:
            A stripped and dedented string
    """
    if strip_type == "strip":
        return textwrap.dedent(message).strip()
    elif strip_type == "lstrip":
        return textwrap.dedent(message).lstrip()
    elif strip_type == "rstrip":
        return textwrap.dedent(message).rstrip()
    else:
        return


# .............................................................. Implementation
def active_identity(config, email, name, url):
    """ Prints an existing ID of a local gitconfig.

        Args:
            config (dict): Contains validated configuration options
            email (str): An email address
            name (str): A name
            url (str): A remote.origin.url
    """
    duration = config["sleep_duration"]

    if not url:
        url = "Not set"

    if email and name:
        msg = """
            ~Active Passport:
                . User:   {}
                . E-Mail: {}
                . Remote: {}
        """.format(name, email, url)
        print(dedented(msg, "strip"))
    else:
        msg = "No passport set."
        print(msg)

    time.sleep(duration)


def url_exists(config, url):
    """ If a local gitconfig contains a remote.origin.url add all user defined
        Git IDs matching remote.origin.url as a candidate. However if there is
        not a single match then add all available user defined Git IDs and the
        global Git ID as candidates.

        Args:
            config (dict): Contains validated configuration options
            url (str): A remote.origin.url

        Returns:
            candidates (dict): Contains preselected Git ID candidates
    """
    # A generator to filter matching sections by options:
    # Let's see if user defined IDs match remote.origin.url
    def gen_candidates(ids, url):
        for key, value in ids.items():
            if value.get("service") == url:
                yield (key, value)

    local_passports = config["git_passports"]
    netloc = urllib.parse.urlparse(url)[1]

    candidates = dict(gen_candidates(local_passports, netloc))

    if len(candidates) >= 1:
        msg = """
            One or more passports match your current Git provider.
            remote.origin.url: {}
        """.format(url)
        print(dedented(msg, "lstrip"))
    else:
        candidates = local_passports
        msg = """
            Zero suitable passports found - listing all passports.
            remote.origin.url: {}
        """.format(url)
        print(dedented(msg, "lstrip"))
        add_global_id(config, candidates)

    print_choice(candidates)
    return candidates


def no_url_exists(config, url):
    """ If a local gitconfig does not contain a remote.origin.url add
        all available user defined Git IDs and the global Git ID as
        candidates.

        Args:
            config (dict): Contains validated configuration options
            url (str): A remote.origin.url

        Returns:
            candidates (dict): Contains preselected Git ID candidates
    """
    candidates = config["git_passports"]
    msg = "«remote.origin.url» is not set, listing all passports:\n"

    print(msg)
    add_global_id(config, candidates)
    print_choice(candidates)
    return candidates


def add_global_id(config, target):
    """ If available add the global Git ID as a fallback ID to a
        dictionary containing potential preselected candidates.

        Args:
            config (dict): Contains validated configuration options
            target (dict): Contains preselected local Git IDs
    """
    global_email = git_config_get(config, "global", "email")
    global_name = git_config_get(config, "global", "name")
    local_passports = config["git_passports"]

    if global_email and global_name:
        position = len(local_passports)
        target[position] = {}
        target[position]["email"] = global_email
        target[position]["name"] = global_name
        target[position]["flag"] = "global"
    else:
        msg = """
            ~Note
                Tried to add your global Git ID as a passport candidate but
                couldn't find one.
                Consider to setup a global Git ID in order to get it listed
                as a fallback passport.
        """
        print(dedented(msg, "lstrip"))


# ........................................................................ Glue
def main():
    args = args_release()
    config_file = os.path.expanduser("~/.gitpassport")
    config_preset(config_file)
    config_validate_scheme(config_file)
    config_validate_values(config_file)
    config = config_release(config_file)

    if config["enable_hook"]:
        git_infected()

        local_email = git_config_get(config, "local", "email")
        local_name = git_config_get(config, "local", "name")
        local_url = git_config_get(config, "local", "url")

        if args.choose:
            git_config_remove(silent=True)
            local_name = None
            local_email = None
        elif args.remove:
            git_config_remove(silent=False)
            sys.exit()
        elif args.show:
            active_identity(config, local_email, local_name, local_url)
            sys.exit()

        if local_email and local_name:
            active_identity(config, local_email, local_name, local_url)
            sys.exit()
        elif local_url:
            candidates = url_exists(config, local_url)
        elif not local_url:
            candidates = no_url_exists(config, local_url)

        selected_id = get_user_input(candidates.keys())
        git_config_set(config, candidates[selected_id]["email"], "email")
        git_config_set(config, candidates[selected_id]["name"], "name")
    else:
        print("git-passport is currently disabled.")


if __name__ == "__main__":
    main()
