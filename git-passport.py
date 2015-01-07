#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# ..................................................................... Imports
import configparser
import os.path
import subprocess
import sys
import textwrap
import time
import urllib.parse


# ............................................................ Config functions
def config_generate(filename):
    preset = configparser.ConfigParser()

    preset["General"] = {}
    preset["General"]["enable_hook"] = "True"
    preset["General"]["devel_debug"] = "False"
    preset["General"]["sleep_duration"] = "1"

    preset["Git ID 0"] = {}
    preset["Git ID 0"]["email"] = "email_0@example.com"
    preset["Git ID 0"]["name"] = "name_0"
    preset["Git ID 0"]["service"] = "github.com"

    preset["Git ID 1"] = {}
    preset["Git ID 1"]["email"] = "email_1@example.com"
    preset["Git ID 1"]["name"] = "name_1"
    preset["Git ID 1"]["service"] = "gitlab.com"

    with open(filename, "w") as configfile:
        preset.write(configfile)


def config_read(filename):
    data = configparser.ConfigParser()
    data.read(filename)

    pattern = "Git ID"
    matches = []

    for section in data.items():
        if pattern in section[0]:
            matches.append(dict(section[1]))

    config = dict(data.items("General"), git_local_id={})
    config["git_local_id"] = dict(enumerate(matches))

    return config


def config_validate(config):
    for key, value in config.items():
        if key == "enable_hook" or key == "devel_debug":
            if value == "True":
                config[key] = True
            elif value == "False":
                config[key] = False
            else:
                msg = "E > Settings > %s: Expecting True or False." % (key)
                sys.exit(msg)

        elif key == "sleep_duration":
            try:
                config[key] = int(value)
            except ValueError:
                msg = "E > Settings > %s: Expecting a number." % (key)
                sys.exit(msg)

        elif key == "git_local_id":
            pass

        else:
            msg = "E > Settings > %s: Section/key unknown." % (key)
            sys.exit(msg)


# ............................................................... Git functions
def git_get_id(config, scope, property):
    """Returns the global or local git ID (email and username)."""

    if config["devel_debug"]:
        valid_args = ("global", "local", "email", "name")
        fname = sys._getframe().f_code.co_name

        if scope not in valid_args:
            msg = "E > %s(scope): arg must be «%s» or «%s»." % (
                fname,
                valid_args[0],
                valid_args[1]
            )
            sys.exit(msg)

        if property not in valid_args:
            msg = "E > %s(property): arg must be «%s» or «%s»." % (
                fname,
                valid_args[2],
                valid_args[3]
            )
            sys.exit(msg)

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
        return error


def git_get_url():
    """ Returns the local remote.origin.url of a git repository """

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
        return error


def git_set_id(config, data, property):
    """Sets the local ID (email and username) of a local git repository."""

    if config["devel_debug"]:
        valid_args = ("email", "name")
        fname = sys._getframe().f_code.co_name

        if property not in valid_args:
            msg = "E > %s(property): arg must be «%s» or «%s»." % (
                fname,
                valid_args[0],
                valid_args[1]
            )
            sys.exit(msg)

    try:
        subprocess.Popen([
            "git",
            "config",
            "--local",
            "user." + property,
            data
        ], stdout=subprocess.PIPE)

    except Exception as error:
        return error


# ............................................................ Helper functions
def get_user_input(pool):
    while True:
        selected = input("» Please select a valid [ID] or type «q» to quit: ")

        try:
            selected = int(selected)
        except ValueError:
            if selected == "q":
                sys.exit("\n~Quitting~\n")
            continue

        if selected not in pool:
            continue
        break
    return selected


def print_choice(choice):
    for key, value in choice.items():
        if value.get("flag") == "global":
            msg = """
                ~:Global ID: [%s]
                    . User: %s
                    . Mail: %s
            """
            print(textwrap.dedent(msg).lstrip() % (
                key,
                value["name"],
                value["email"])
            )
        else:
            msg = """
                ~Local ID: [%s]
                    . User: %s
                    . Mail: %s
                    . Service: %s
            """
            print(textwrap.dedent(msg).lstrip() % (
                key,
                value["name"],
                value["email"],
                value["service"])
            )


def add_global_id(config, target):
    global_email = git_get_id(config, "global", "email")
    global_name = git_get_id(config, "global", "name")
    local_id = config["git_local_id"]

    if global_email and global_name:
        pointer = len(local_id)
        target[pointer] = {}
        target[pointer]["email"] = global_email
        target[pointer]["name"] = global_name
        target[pointer]["flag"] = "global"


# .............................................................. Implementation
def identity_exists(config, email, name, url):
    duration = config["sleep_duration"]

    if not url:
        url = "«remote.origin.url» is not set."

    msg = """
        ~Intermission~
            Current local ID is already set:
            . User: %s
            . Mail: %s
            . Remote: %s
    """
    print(textwrap.dedent(msg).lstrip() % (name, email, url))
    sys.exit(time.sleep(duration))


def url_exists(config, url):
    candidates = {}
    local_id = config["git_local_id"]
    netloc = urllib.parse.urlparse(url)[1]

    for key, value in local_id.items():
        if value.get("service") == netloc:
            candidates[key] = value

    if len(candidates) >= 1:
        msg = """
            ~Intermission~
                One or more identities match your current git provider.
                remote.origin.url: %s
        """
        print(textwrap.dedent(msg).lstrip() % (url))
    else:
        candidates = local_id
        msg = """
            ~Intermission~
                Zero identities match your git provider, listing all IDs.
                remote.origin.url: %s
        """

        print(textwrap.dedent(msg).lstrip() % (url))
        add_global_id(config, candidates)

    print_choice(candidates)
    return candidates


def no_url_exists(config, url):
    candidates = {}
    candidates = config["git_local_id"]
    msg = """
        ~Intermission~
            «remote.origin.url» is not set, listing all IDs:
    """

    add_global_id(config, candidates)
    print(textwrap.dedent(msg).lstrip())
    print_choice(candidates)
    return candidates


# ........................................................................ Glue
def main():
    config_file = os.path.expanduser("~/.git_passport")

    if not os.path.exists(config_file):
        config_generate(config_file)

    config = config_read(config_file)
    config_validate(config)

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

        pointer = get_user_input(candidates.keys())
        git_set_id(config, candidates[pointer]["email"], "email")
        git_set_id(config, candidates[pointer]["name"], "name")
        sys.exit("\n~Done~\n")


if __name__ == "__main__":
    main()
