#!/usr/bin/env bash

# Patterns to match a repo's "remote.origin.url" - a part of the url string
git_remotes[0]="Github"
git_remotes[1]="Gitlab"

local_id_0[0]="my_username_0"
local_id_0[1]="email_0@example.com"

local_id_1[0]="my_username_1"
local_id_1[1]="email_1@example.com"

local_fallback_id[0]="${local_id_1[0]}"
local_fallback_id[1]="${local_id_1[1]}"


_setIdentity()
{
    local current_id local_id

    current_id[0]="$(git config --get --local user.name)"
    current_id[1]="$(git config --get --local user.email)"

    local_id=("$@")

    if [[ "${current_id[0]}" == "${local_id[0]}" &&
          "${current_id[1]}" == "${local_id[1]}" ]]; then
        printf "%1sLocal identity is:\n" ""
        printf "%4s. User: %s\n" "" "${current_id[0]}"
        printf "%4s. Mail: %s\n\n" "" "${current_id[1]}"
    else
        printf "%1sSetting local identity to:\n" ""
        printf "%4s. User: %s\n" "" "${local_id[0]}"
        printf "%4s. Mail: %s\n\n" "" "${local_id[1]}"

        git config --local user.name "${local_id[0]}"
        git config --local user.email "${local_id[1]}"
    fi

    return 0
}


{
    current_remote_url="$(git config --get --local remote.origin.url)"

    if [[ "$current_remote_url" ]]; then

        for service in "${git_remotes[@]}"; do

            # Disable case sensitivity for regex matching
            # since Bash 3 does not support case modification
            shopt -s nocasematch

            if [[ "$current_remote_url" =~ $service ]]; then
                case "$service" in

                    "${git_remotes[0]}" )
                        printf "\n~Intermission~\n"
                        printf "%4s. %s repository found." "" "${git_remotes[0]}"
                        _setIdentity "${local_id_0[@]}"
                        exit 0
                        ;;

                    "${git_remotes[1]}" )
                        printf "\n~Intermission~\n"
                        printf "%4s. %s repository found." "" "${git_remotes[1]}"
                        _setIdentity "${local_id_1[@]}"
                        exit 0
                        ;;

                    * )
                        printf "\n~Intermission~\n"
                        printf "%4s. pre-commit hook: unknown error\n» Quitting.\n" ""
                        exit 1
                        ;;

                esac
            fi
        done
    else
        printf "\n~Intermission~\n"
        printf "%4s. No remote repository set. Using local fallback identity:\n" ""
        printf "%4s. User: %s\n" "" "${local_fallback_id[0]}"
        printf "%4s. Mail: %s\n\n" "" "${local_fallback_id[1]}"

        # Get the user's attention for a second
        sleep 2

        git config --local user.name "${local_fallback_id[0]}"
        git config --local user.email "${local_fallback_id[1]}"
    fi
}

exit 0
