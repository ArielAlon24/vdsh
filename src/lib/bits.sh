#!/bin/env bash

PID=$$

PROC_PID_MEM="/proc/$PID/mem"


## @brief Encode a 32-bit unsigned integer as little-endian hex.
##
## @param $1 32-bit integer value (decimal or shell-arithmetic compatible)
## @return Little-endian hexadecimal representation (no prefix, no newline)
##
## @example
##   u32_le_hex 0x12345678
##   # => 78563412
##
u32_le_hex() {
    local v="$1"
    local hex le=""

    printf -v hex '%08x' "$v"

    for ((i=6; i>=0; i-=2)); do
        le+="${hex:i:2}"
    done

    printf '%s' "$le"
}

## @brief Encode a 64-bit integer as little-endian hex.
##
## @param $1 64-bit integer value (decimal, hex, or negative)
## @return Little-endian hexadecimal representation (no prefix, no newline)
##
## @example
##   u64_le_hex 0x1122334455667788
##   # => 8877665544332211
##
## @example
##   u64_le_hex -1
##   # => ffffffffffffffff
##
u64_le_hex() {
    local v="$1"
    local hex le=""

    printf -v hex '%016x' "$v"

    for ((i=14; i>=0; i-=2)); do
        le+="${hex:i:2}"
    done

    printf '%s' "$le"
}

## @brief Convert an hex value into the raw bytes it represents
##
## @param $1 A string hex value without any prefix (e.g "12ab")
## @return The raw repsentation of the value
hex_to_raw() {
    local hex="$1"

    echo -n -e $(echo $hex | sed -u -E 's/([0-9,a-f,A-F][0-9,a-f,A-F])/\\x&/g')
}

write_hex() {
    local address="$1"
    local value="$2"

    hex_to_raw $value \
        | dd of="$PROC_PID_MEM" bs=1 seek="$address" conv=notrunc status=none

}

read_raw() {
    local address="$1"
    local size="$2"

    dd if="$PROC_PID_MEM" bs=1 skip="$address" count="$size" status=none
}

read_hex() {
    local address="$1"
    local size="$2"

    read_raw $address $size | xxd -ps -c 0
}

le_hex() {
    local h="$1"
    local out=""
    for ((i=${#h}-2; i>=0; i-=2)); do
        out+="${h:i:2}"
    done

    printf '%d\n' "0x$out"
}
