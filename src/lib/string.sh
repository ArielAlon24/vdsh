#!/bin/env bash

# @brief Remove all whitespace characters from input
#
# @note Input can be passed from stdin and as arguments
#
remove_whitespace() {
    if [[ $# -gt 0 ]]; then
        printf "%s" "$*"
    else
        cat
    fi | tr -d '[:space:]'
}

# @brief Remove all whitespace except spaces
#
# @note Tabs, newlines and carriage returns are removed.
#       Spaces are preserved.
#
remove_whitespace_keep_spaces() {
    if [[ $# -gt 0 ]]; then
        printf "%s" "$*"
    else
        cat
    fi | tr -d '\t\r\n\f\v'
}
