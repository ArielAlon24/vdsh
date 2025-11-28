#!/bin/env bash

if [[ -t 1 ]]; then
    COLOR__RESET="\033[0m"
    COLOR__GRAY="\033[90m"
    COLOR__RED="\033[31m"
    COLOR__GREEN="\033[32m"
    COLOR__YELLOW="\033[33m"
    COLOR__BLUE="\033[34m"
else
    COLOR__RESET=""
    COLOR__GRAY=""
    COLOR__RED=""
    COLOR__GREEN=""
    COLOR__YELLOW=""
    COLOR__BLUE=""
fi

MINIMUM_LOG_LEVEL="3"

log() {
    local level="$1"; shift

    local color="" symbol="" value=""
    case "$level" in
        error) color="$COLOR__RED" symbol="!" value="1";;
        warn)  color="$COLOR__YELLOW" symbol="-" value="2";;
        info)  color="$COLOR__GREEN" symbol="+" value="3";;
        debug) color="$COLOR__BLUE" symbol="?" value="4";;
        *) ;;
    esac

    (( $value > MINIMUM_LOG_LEVEL )) && return 0

    echo -e "$color[$symbol] $COLOR__RESET$*"
}

panic() {
    log error $0
    exit 1
}
