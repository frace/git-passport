#!/usr/bin/env python3
# -*- coding: utf-8 -*-


""" git-passport is a Git pre-commit hook written in Python to manage
    multiple Git user identities.
"""


# ..................................................................... Imports
import configparser
import os.path
import subprocess
import sys
import textwrap
import time
import urllib.parse


# ............................................................ Config functions
def config_create(filename):
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
        sys.exit("\n~Quitting~")


def config_read(filename):
    """ Read a provided configuration file and «import» allowed sections and
        their keys/values into a dictionary.

        Args:
            filename (str): The complete `filepath` of the configuration file

        Returns:
            config (dict): Contains all allowed configuration sections
    """
    raw_config = configparser.ConfigParser()
    raw_config.read(filename)

    # Match an arbitrary number of sections starting with pattern
    pattern = "Passport"

    # A generator to filter matching sections:
    # Let's see if user defined config sections match a pattern
    def generate_matches():
        for section in raw_config.items():
            if pattern in section[0]:
                yield dict(section[1])

    # Construct a custom dict containing allowed sections
    config = dict(raw_config.items("General"))
    config["git_local_ids"] = dict(enumerate(generate_matches()))

    return config


def config_validate(config):
    """ Validate and convert certain keys and values of a given dictionary
        containing a set of configuration options. If unexpected values are
        found we quit the script and notify the user what went wrong.

        Since ``ConfigParser`` only accepts strings when setting up a default
        config it is necessary to convert some values to numbers and boolean.

        Args:
            config (dict): Contains all allowed configuration sections

        Returns:
            config (dict): Contains valid and converted configuration options
    """
    for key, value in config.items():
        if key == "enable_hook":
            if value == "True":
                config[key] = True
            elif value == "False":
                config[key] = False
            else:
                msg = "E > Settings > {}: Expecting True or False."
                sys.exit(msg).format(key)

        elif key == "sleep_duration":
            try:
                config[key] = float(value)
            except ValueError:
                msg = "E > Settings > {}: Expecting float or number."
                sys.exit(msg).format(key)

        # Here the values could really be anything...
        elif key == "git_local_ids":
            pass

        else:
            msg = "E > Settings > {}: Section/key unknown."
            sys.exit(msg).format(key)

    return config


# ............................................................... Git functions
def infected():
    """ Checks if the current directory is under Git version control."""
    if os.path.exists("./.git/HEAD"):
        return

    msg = """
        The current directory does not seem to be a Git repository.
        Nothing to do.
    """

    print(dedented(msg, "strip"))
    sys.exit("\n~Quitting~")


def git_get_id(config, scope, property):
    """ Get the email address or username of the global or local Git ID.

        Args:
            config (dict): Contains validated configuration options
            scope (str): Search inside a `global` or `local` scope
            property (str): Type of `email` or `name`

        Returns:
            git_id (str): A name or email address

        Raises:
            Exception: If subprocess.Popen() fails
    """
    try:
        git_process = subprocess.Popen([
            "git",
            "config",
            "--get",
            "--" + scope,
            "user." + property
        ], stdout=subprocess.PIPE)

        git_id = git_process.communicate()[0].decode("utf-8")
        return git_id.replace("\n", "")

    except Exception as error:
        raise error


def git_get_url():
    """ Get the local remote.origin.url of a Git repository.

        Returns:
            git_url (str): The local and active remote.origin.url

        Raises:
            Exception: If subprocess.Popen() fails
    """
    try:
        git_process = subprocess.Popen([
            "git",
            "config",
            "--get",
            "--local",
            "remote.origin.url"
        ], stdout=subprocess.PIPE)

        git_url = git_process.communicate()[0].decode("utf-8")
        return git_url.replace("\n", "")

    except Exception as error:
        raise error


def git_set_id(config, value, property):
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

    except Exception as error:
        raise error


# ............................................................ Helper functions
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
                sys.exit("\n~Quitting~\n")
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
            """
            print(dedented(msg, "lstrip").format(
                key,
                value["name"],
                value["email"])
            )
        elif not value.get("service"):
            msg = """
                ~:Passport ID: {}
                    . User:   {}
                    . E-Mail: {}
            """
            print(dedented(msg, "lstrip").format(
                key,
                value["name"],
                value["email"])
            )
        else:
            msg = """
                ~Passport ID: {}
                    . User:    {}
                    . E-Mail:  {}
                    . Service: {}
            """
            print(dedented(msg, "lstrip").format(
                key,
                value["name"],
                value["email"],
                value["service"])
            )


def add_global_id(config, target):
    """ If available add the global Git ID as a fallback ID to a
        dictionary containing potential preselected candidates.

        Args:
            config (dict): Contains validated configuration options
            target (dict): Contains preselected local Git IDs
    """
    global_email = git_get_id(config, "global", "email")
    global_name = git_get_id(config, "global", "name")
    local_ids = config["git_local_ids"]

    if global_email and global_name:
        position = len(local_ids)
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
def identity_exists(config, email, name, url):
    """ Prints an existing ID of a local gitconfig.

        Args:
            config (dict): Contains validated configuration options
            email (str): An email address
            name (str): A name
            url (str): A remote.origin.url
    """
    duration = config["sleep_duration"]

    if not url:
        url = "«remote.origin.url» is not set."

    msg = """
        ~Intermission~

        ~Active Passport:
            . User:   {}
            . E-Mail: {}
            . Remote: {}
    """

    print(dedented(msg, "lstrip").format(name, email, url))
    time.sleep(duration)
    sys.exit()


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
    local_ids = config["git_local_ids"]
    netloc = urllib.parse.urlparse(url)[1]

    # A generator to filter matching sections:
    # Let's see if user defined IDs match remote.origin.url
    def generate_candidates():
        for key, value in local_ids.items():
            if value.get("service") == netloc:
                yield (key, value)

    candidates = dict(generate_candidates())

    if len(candidates) >= 1:
        msg = """
            ~Intermission~
                One or more identities match your current git provider.
                remote.origin.url: {}
        """
        print(dedented(msg, "lstrip").format(url))
    else:
        candidates = local_ids
        msg = """
            ~Intermission~
                Zero passports matching - listing all passports.
                remote.origin.url: {}
        """

        print(dedented(msg, "lstrip").format(url))
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
    candidates = config["git_local_ids"]
    msg = """
        ~Intermission~
            «remote.origin.url» is not set, listing all IDs:
    """

    print(dedented(msg, "lstrip"))
    add_global_id(config, candidates)
    print_choice(candidates)
    return candidates


# ........................................................................ Glue
def main():
    infected()

    config_file = os.path.expanduser("~/.git_passport")
    config_create(config_file)

    config = config_validate(config_read(config_file))

    if config["enable_hook"]:
        local_email = git_get_id(config, "local", "email")
        local_name = git_get_id(config, "local", "name")
        local_url = git_get_url()

        if local_email and local_name:
            identity_exists(config, local_email, local_name, local_url)
        elif local_url:
            candidates = url_exists(config, local_url)
        else:
            candidates = no_url_exists(config, local_url)

        selected_id = get_user_input(candidates.keys())
        git_set_id(config, candidates[selected_id]["email"], "email")
        git_set_id(config, candidates[selected_id]["name"], "name")
        print("\n~Done~\n")


if __name__ == "__main__":
    main()
