# -*- coding: utf-8 -*-


# ..................................................................... Imports
import subprocess

from . import util


# ............................................................... Git functions
def infected():
    """ Checks if the current directory is under Git version control.

        Returns:
            True (bool): If the current directory is a Git repository
            False (bool): If the current directory is not a Git repository

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

        if exit_status == 0:
            return True
        elif exit_status == 128:
            msg = "The current directory does not seem to be a Git repository."

            print(msg)
            return False

    except Exception:
        raise


def config_get(config, scope, property):
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


def config_set(config, value, property):
    """ Set the email address or username as a local Git ID for a repository.

        Args:
            config (dict): Contains validated configuration options
            value (str): A name or email address
            property (str): Type of `email` or `name`

        Returns:
            True (bool): On success

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

    return True


def config_remove(verbose=True):
    """ Remove an existing Git identity.

        Returns:
            True (bool): On success

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

        if verbose:
            if exit_status == 0:
                msg = "Passport removed."
            elif exit_status == 128:
                msg = "No passport set."

            print(msg)

    except Exception:
        raise

    return True


def add_global_id(config, target):
    """ If available add the global Git ID as a fallback ID to a
        dictionary containing potential preselected candidates.

        Args:
            config (dict): Contains validated configuration options
            target (dict): Contains preselected local Git IDs

        Returns:
            True (bool): If a global Git ID could be found
            False (bool): If a global Git ID could not be found
    """
    global_email = config_get(config, "global", "email")
    global_name = config_get(config, "global", "name")
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

        print(util.dedented(msg, "lstrip"))
        return False

    return True
