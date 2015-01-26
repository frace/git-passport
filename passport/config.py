# -*- coding: utf-8 -*-


# ..................................................................... Imports
import configparser
import os.path
import re


# ............................................................ Config functions
def preset(filename):
    """ Create a configuration file containing sample data inside the home
        directory if none exists yet.

        Args:
            filename (str): The complete `filepath` of the configuration file

        Returns:
            True (bool): If the configfile exists already
            False (bool): If a new configfile was successfully created
    """
    if os.path.exists(filename):
        return True

    preset = configparser.ConfigParser()

    preset["general"] = {}
    preset["general"]["enable_hook"] = "True"
    preset["general"]["sleep_duration"] = "0.75"

    preset["passport 0"] = {}
    preset["passport 0"]["email"] = "email_0@example.com"
    preset["passport 0"]["name"] = "name_0"
    preset["passport 0"]["service"] = "github.com"

    preset["passport 1"] = {}
    preset["passport 1"]["email"] = "email_1@example.com"
    preset["passport 1"]["name"] = "name_1"
    preset["passport 1"]["service"] = "gitlab.com"

    try:
        msg = """
            No configuration file found ~/.
            Generating a sample configuration file.
        """

        print(dedented(msg, "strip"))

        with open(filename, "w") as configfile:
            preset.write(configfile)
        return False

    except Exception:
        raise

    finally:
        configfile.close()


def validate_scheme(filename):
    """ Validate section and option names of a provided configuration file.
        Quit the script and tell the user if we find false names.

        Args:
            filename (str): The complete `filepath` of the configuration file

        Returns:
            True (bool): If the configfile contains valid sections and options
            False (bool): If the configfile contains false sections or options
    """
    raw_config = configparser.ConfigParser()
    raw_config.read(filename)

    pattern_section = r"^(passport)\s[0-9]+$"
    whitelist_sections = frozenset([
        "general",
        "passport"
    ])

    whitelist_options = frozenset([
        "email",
        "enable_hook",
        "name",
        "service",
        "sleep_duration"
    ])

    # Create sets containing non-whitelisted section and option names
    false_sections = set([
        section
        for section in raw_config.sections()
        if section not in whitelist_sections
        if not re.match(pattern_section, section)
    ])

    false_options = set([
        option
        for section in raw_config.sections()
        for option in raw_config.options(section)
        if option not in whitelist_options
    ])

    # Quit if we have wrong section names
    if len(false_sections):
        msg = """
            E > Configuration > Invalid sections:
            >>> {}

            Allowed sections (Passport sections scheme: "passport 0"):
            >>> {}
        """.format(
            ", ".join(false_sections),
            ", ".join(whitelist_sections)
        )

        print(dedented(msg, "strip"))
        return False

    # Quit if we have wrong option names
    if len(false_options):
        msg = """
            E > Configuration > Invalid options:
            >>> {}

            Allowed options:
            >>> {}
        """.format(
            ", ".join(false_options),
            ", ".join(whitelist_options)
        )

        print(dedented(msg, "strip"))
        return False

    return True


def validate_values(filename):
    """ Validate certain values of a provided configuration file.
        Quit the script and tell the user if we find false values.

        Values to be validated:
            email: E-Mail scheme
            sleep_duration: Float
            enable_hook: Boolean

        Args:
            filename (str): The complete `filepath` of the configuration file

        Returns:
            True (bool): If the configfile contains valid values
            False (bool): If the configfile contains invalid values
    """
    def filter_email(config):
        pattern_section = r"^(passport)\s[0-9]+$"
        pattern_email = r"[^@]+@[^@]+\.[^@]+"
        for section in config.sections():
            if re.match(pattern_section, section):
                email = config.get(section, "email")
                if not re.match(pattern_email, email):
                    yield email

    raw_config = configparser.ConfigParser()
    raw_config.read(filename)

    false_email = set(filter_email(raw_config))

    # Quit if we have wrong email addresses
    if len(false_email):
        msg = """
            E > Configuration > Invalid email address:
            >>> {}
        """.format(", ".join(false_email))

        print(dedented(msg, "strip"))
        return False

    # Quit if we have wrong boolean values
    try:
        raw_config.getboolean("general", "enable_hook")
    except ValueError:
        msg = "E > Configuration > enable_hook: Expecting True or False."

        print(msg)
        return False

    # Quit if we have wrong float values
    try:
        raw_config.getfloat("general", "sleep_duration")
    except ValueError:
        msg = "E > Configuration > sleep_duration: Expecting float or number."

        print(msg)
        return False

    return True


def release(filename):
    """ Read a provided configuration file and «import» sections and their
        validated keys/values into a dictionary.

        Args:
            filename (str): The complete `filepath` of the configuration file

        Returns:
            config (dict): Contains all allowed configuration sections
    """
    def passport(config):
        pattern_section = r"^(passport)\s[0-9]+$"
        for passport in config.items():
            if re.match(pattern_section, passport[0]):
                yield dict(passport[1])

    raw_config = configparser.ConfigParser()
    raw_config.read(filename)

    config = {}
    config["enable_hook"] = raw_config.getboolean("general", "enable_hook")
    config["sleep_duration"] = raw_config.getfloat("general", "sleep_duration")
    config["git_passports"] = dict(enumerate(passport(raw_config)))

    return config
