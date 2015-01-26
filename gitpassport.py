#!/usr/bin/env python3
# -*- coding: utf-8 -*-


""" git-passport is a Git command and hook written in Python to manage multiple
    Git users / user identities.
"""

import passport
# ........................................................................ Glue
if __name__ == "__main__":
    args = args_release()
    config_file = os.path.expanduser("~/.gitpassport")

    if (
        not config_preset(config_file) or
        not config_validate_scheme(config_file) or
        not config_validate_values(config_file) or
        not git_infected()
    ):
        sys.exit(1)
    else:
        config = config_release(config_file)

    if config["enable_hook"]:
        local_email = git_config_get(config, "local", "email")
        local_name = git_config_get(config, "local", "name")
        local_url = git_config_get(config, "local", "url")

        if args.select:
            local_name = None
            local_email = None
            git_config_remove(verbose=False)

        if args.delete:
            git_config_remove()
            sys.exit(0)

        if args.active:
            active_identity(
                config,
                local_email,
                local_name,
                local_url,
                style="compact"
            )
            sys.exit(0)

        if args.passports:
            print_choice(config["git_passports"])
            exit(0)

        if local_email and local_name:
            active_identity(
                config,
                local_email,
                local_name,
                local_url
            )
            sys.exit(0)

        if local_url:
            candidates = url_exists(config, local_url)
        else:
            candidates = no_url_exists(config)

        selected_id = get_user_input(candidates.keys())
        if selected_id is not None:
            git_config_set(config, candidates[selected_id]["email"], "email")
            git_config_set(config, candidates[selected_id]["name"], "name")
            sys.exit(0)
    else:
        print("git-passport is currently disabled.")
        sys.exit(1)
