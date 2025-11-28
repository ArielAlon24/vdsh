#!/usr/bin/env bash

set -euo pipefail

source $(dirname $0)/lib/log.sh

PID=$$
PROC_PID_MAPS="/proc/$PID/maps"
PROC_PID_MEM="/proc/$PID/mem"
CLOCK_GETTIME_SYMBOL="__kernel_clock_gettime"
CLOCK_GETTIME_SHELLCODE_B64="KA6A0gEAANTAA1/W"
# CLOCK_GETTIME_SHELLCODE_B64="Ym9vbQ=="   # This shellcode is garbage and should trigger and error

mkdir -p ~/out

log debug "PID: $COLOR__BLUE$PID$COLOR__RESET"

# 1. Find [vdso]

vdso_line=$(grep '\[vdso\]' "$PROC_PID_MAPS")
[[ -z "$vdso_line" ]] && panic "Did not find the [vdso] line in $PROC_PID_MAPS"
log debug "[vdso] Map: $COLOR__BLUE$vdso_line$COLOR__RESET"

vdso_start_hex=$(echo "$vdso_line" | cut -d' ' -f1 | cut -d'-' -f1)
vdso_start=$((0x$vdso_start_hex))
log debug "[vdso] start: $COLOR__BLUE$vdso_start$COLOR__RESET"

vdso_end_hex=$(echo "$vdso_line" | cut -d' ' -f1 | cut -d'-' -f2)
vdso_end=$((0x$vdso_end_hex))
log debug "[vdso] end: $COLOR__BLUE$vdso_end$COLOR__RESET"

vdso_size=$((vdso_end - vdso_start))
log debug "[vdso] size: $COLOR__BLUE$vdso_size$COLOR__RESET"

log info "Found [vdso] Map: $COLOR__BLUE$vdso_start$COLOR__RESET - \
$COLOR__BLUE$vdso_end$COLOR__RESET ($COLOR__GRAY$vdso_size$COLOR__RESET Bytes)"

# 2. Dump [vdso]

vdso_b64=$(dd if="$PROC_PID_MEM" bs=1 skip="$vdso_start" count="$vdso_size" status=none | base64 -w0)
log debug "[vdso] data:\t$COLOR__BLUE${#vdso_b64}$COLOR__RESET bytes"

# 3. locate __kernel_clock_gettime symbol offset

symbol_line=$(
    echo "$vdso_b64" \
    | base64 --decode \
    | llvm-nm --dynamic - \
    | grep "$CLOCK_GETTIME_SYMBOL" \
)
log debug "[vdso] symbol:\t$COLOR__BLUE$symbol_line$COLOR__RESET"

symbol_offset_hex=$(echo "$symbol_line" | cut -d' ' -f1 | cut -d'-' -f1)
symbol_offset=$((0x$symbol_offset_hex))
symbol_address=$(($vdso_start + $symbol_offset))
log debug "Symbol offset:\t$COLOR__BLUE$symbol_offset$COLOR__RESET"
log debug "Symbol address:\t$COLOR__BLUE$symbol_address$COLOR__RESET"

log info "Found $CLOCK_GETTIME_SYMBOL symbol at: $COLOR__BLUE$symbol_address$COLOR__RESET"

# 4. patch bytes via /proc/$pid/mem

shellcode_size=$(echo $CLOCK_GETTIME_SHELLCODE_B64 | base64 --decode | wc -c)
log debug "Shellcode size:\t$COLOR__BLUE$shellcode_size$COLOR__RESET"

echo "$CLOCK_GETTIME_SHELLCODE_B64" \
    | base64 --decode \
    | dd of="$PROC_PID_MEM" bs=1 seek="$symbol_address" conv=notrunc status=none

log info "Wrote shellcode to $COLOR__BLUE$symbol_address$COLOR__RESET \
($COLOR__GRAY$shellcode_size$COLOR__RESET bytes)"

# 5. Dump [vdso] yet again

vdso_b64_2=$(dd if="$PROC_PID_MEM" bs=1 skip="$vdso_start" count="$vdso_size" status=none | base64 -w0)
echo "$vdso_b64_2" | base64 --decode > ~/out/dump2.bin
log info "Dumped new [vdso] to$COLOR__BLUE ~/out/dump2.bin$COLOR__RESET"

# 5. trigger a vDSO time user

log info "Triggering $COLOR__BLUE$CLOCK_GETTIME_SYMBOL$COLOR__RESET via \
$COLOR__BLUE\$EPOCHSECONDS$COLOR__RESET expansions"

for i in 1 2 3; do
    value=$EPOCHSECONDS
    log info "EPOCHSECONDS[$i]:\t$COLOR__BLUE$value$COLOR__RESET"
    sleep 1
done
