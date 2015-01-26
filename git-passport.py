#!/usr/bin/env python3
# -*- coding: utf-8 -*-


""" git-passport is a Git command and hook written in Python to manage multiple
    Git users / user identities.
"""

if __name__ == "__main__":
    import os.path
    import sys

    from passport import (
        arg,
        case,
        configuration,
        dialog,
        git
    )

    args = arg.release()
    config_file = os.path.expanduser("~/.gitpassport")

    if (
        not configuration.preset(config_file) or
        not configuration.validate_scheme(config_file) or
        not configuration.validate_values(config_file) or
        not git.infected()
    ):
        sys.exit(1)
    else:
        config = configuration.release(config_file)

    if config["enable_hook"]:
        local_email = git.config_get(config, "local", "email")
        local_name = git.config_get(config, "local", "name")
        local_url = git.config_get(config, "local", "url")

        if args.select:
            local_name = None
            local_email = None
            git.config_remove(verbose=False)

        if args.delete:
            git.config_remove()
            sys.exit(0)

        if args.active:
            case.active_identity(
                config,
                local_email,
                local_name,
                local_url,
                style="compact"
            )
            sys.exit(0)

        if args.passports:
            dialog.print_choice(config["git_passports"])
            exit(0)

        if local_email and local_name:
            case.active_identity(
                config,
                local_email,
                local_name,
                local_url
            )
            sys.exit(0)

        if local_url:
            candidates = case.url_exists(config, local_url)
        else:
            candidates = case.no_url_exists(config)

        selected_id = dialog.get_input(candidates.keys())
        if selected_id is not None:
            git.config_set(config, candidates[selected_id]["email"], "email")
            git.config_set(config, candidates[selected_id]["name"], "name")
            sys.exit(0)
    else:
        print("git-passport is currently disabled.")
        sys.exit(1)
