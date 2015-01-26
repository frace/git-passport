# -*- coding: utf-8 -*-


# ..................................................................... Imports
import time
import urllib.parse

from . import (
    configuration,
    dialog,
    util
)


# .............................................................. Case functions
def active_identity(config, email, name, url, style=None):
    """ Prints an existing ID of a local gitconfig.

        Args:
            config (dict): Contains validated configuration options
            email (str): An email address
            name (str): A name
            url (str): A remote.origin.url

        Returns:
            True (bool): If an active passport could be found
            False (bool): If an active passport could not be found
    """
    duration = config["sleep_duration"]
    strip = "strip" if style == "compact" else "lstrip"

    if not url:
        url = "Not set"

    if email and name:
        msg = """
            ~Active Passport:
                . User:   {}
                . E-Mail: {}
                . Remote: {}
        """.format(
            name,
            email,
            url
        )

        print(util.dedented(msg, strip))
    else:
        msg = "No passport set."

        print(msg)
        return False

    time.sleep(duration)
    return True


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

        print(util.dedented(msg, "lstrip"))
    else:
        candidates = local_passports
        msg = """
            Zero suitable passports found - listing all passports.
            remote.origin.url: {}
        """.format(url)

        print(util.dedented(msg, "lstrip"))
        configuration.add_global_id(config, candidates)

    dialog.print_choice(candidates)
    return candidates


def no_url_exists(config):
    """ If a local gitconfig does not contain a remote.origin.url add
        all available user defined Git IDs and the global Git ID as
        candidates.

        Args:
            config (dict): Contains validated configuration options

        Returns:
            candidates (dict): Contains preselected Git ID candidates
    """
    candidates = config["git_passports"]
    msg = "«remote.origin.url» is not set, listing all passports:\n"

    print(msg)
    configuration.add_global_id(config, candidates)
    dialog.print_choice(candidates)

    return candidates
