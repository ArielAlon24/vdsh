#!/usr/bin/env bash

set -euo pipefail

source $(dirname $0)/lib/log.sh
source $(dirname $0)/lib/string.sh
source $(dirname $0)/lib/bits.sh

PID=$$
PROC_PID_MAPS="/proc/$PID/maps"
PROC_PID_MEM="/proc/$PID/mem"
CLOCK_GETTIME_SYMBOL="__kernel_clock_gettime"
CLOCK_GETTIME_SHELLCODE_B64="KA6A0gEAANTAA1/W"

ANY_SYSCALL_SHELLCODE_B64=$(remove_whitespace "
    FAAAFB8gA9UAAAAAAAAAAHEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAoDoDSAQAA1PMDAKpp/f8Q
    KgFAueoBADRJ/f8QKAFA+Un9/xAgAUD5IQVA+SIJQPkjDUD5JBFA+SUVQPkBAADU
    yf3/ECoBQPlKAAC0QAEA+eADE6rAA1/W
")

mkdir -p ~/out

log info "PID: $COLOR__BLUE$PID$COLOR__RESET"

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

log info $(remove_whitespace_keep_spaces "
    Found [vdso] Map: $COLOR__BLUE$vdso_start$COLOR__RESET -
    $COLOR__BLUE$vdso_end$COLOR__RESET ($COLOR__GRAY$vdso_size$COLOR__RESET Bytes)
")

# 1.5. Find [stack]

stack_line=$(grep '\[stack\]' "$PROC_PID_MAPS")
[[ -z "$stack_line" ]] && panic "Did not find the [stack] line in $PROC_PID_MAPS"
log debug "[stack] Map: $COLOR__BLUE$stack_line$COLOR__RESET"

stack_start_hex=$(echo "$stack_line" | cut -d' ' -f1 | cut -d'-' -f1)
stack_start=$((0x$stack_start_hex))
log debug "[stack] start: $COLOR__BLUE$stack_start$COLOR__RESET"

stack_end_hex=$(echo "$stack_line" | cut -d' ' -f1 | cut -d'-' -f2)
stack_end=$((0x$stack_end_hex))
log debug "[stack] end: $COLOR__BLUE$stack_end$COLOR__RESET"

stack_size=$((stack_end - stack_start))
log debug "[stack] size: $COLOR__BLUE$stack_size$COLOR__RESET"

log info $(remove_whitespace_keep_spaces "
    Found [stack] Map: $COLOR__BLUE$stack_start$COLOR__RESET -
    $COLOR__BLUE$stack_end$COLOR__RESET ($COLOR__GRAY$stack_size$COLOR__RESET Bytes)
")

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

shellcode_size=$(echo $ANY_SYSCALL_SHELLCODE_B64 | base64 --decode | wc -c)
log debug "Shellcode size:\t$COLOR__BLUE$shellcode_size$COLOR__RESET"

echo "$ANY_SYSCALL_SHELLCODE_B64" \
    | base64 --decode \
    | dd of="$PROC_PID_MEM" bs=1 seek="$symbol_address" conv=notrunc status=none

log info $(remove_whitespace_keep_spaces "
    Wrote shellcode to $COLOR__BLUE$symbol_address$COLOR__RESET
    ($COLOR__GRAY$shellcode_size$COLOR__RESET bytes)
")

# 5. Dump [vdso] yet again

vdso_b64_2=$(dd if="$PROC_PID_MEM" bs=1 skip="$vdso_start" count="$vdso_size" status=none | base64 -w0)
echo "$vdso_b64_2" | base64 --decode > ~/out/dump2.bin
log info "Dumped new [vdso] to$COLOR__BLUE ~/out/dump2.bin$COLOR__RESET"

# 6. Filling the `g_syscall_config` with `getpid` syscall

syscall_config_mode="$(u32_le_hex 1)"
syscall_config_padding="$(u32_le_hex 0)"
syscall_config_number="$(u64_le_hex 172)"

syscall_config_argument0="$(u64_le_hex 0)"
syscall_config_argument1="$(u64_le_hex 0)"
syscall_config_argument2="$(u64_le_hex 0)"
syscall_config_argument3="$(u64_le_hex 0)"
syscall_config_argument4="$(u64_le_hex 0)"
syscall_config_argument5="$(u64_le_hex 0)"

syscall_config_result_address="$(u64_le_hex $stack_start)"

g_syscall_config_address=$(($symbol_address + 8))
write_hex $(($g_syscall_config_address +  0)) $syscall_config_mode
write_hex $(($g_syscall_config_address +  4)) $syscall_config_padding
write_hex $(($g_syscall_config_address +  8)) $syscall_config_number
write_hex $(($g_syscall_config_address + 16)) $syscall_config_argument0
write_hex $(($g_syscall_config_address + 24)) $syscall_config_argument1
write_hex $(($g_syscall_config_address + 32)) $syscall_config_argument2
write_hex $(($g_syscall_config_address + 40)) $syscall_config_argument3
write_hex $(($g_syscall_config_address + 48)) $syscall_config_argument4
write_hex $(($g_syscall_config_address + 56)) $syscall_config_argument5
write_hex $(($g_syscall_config_address + 64)) $syscall_config_result_address


log info "Dumping 'g_syscall_config':"
read_raw $g_syscall_config_address 70 | xxd

# 5. Trigger a vDSO time syscall + `getpid`

log info "Triggering $COLOR__BLUE$CLOCK_GETTIME_SYMBOL$COLOR__RESET via \
$COLOR__BLUE\$EPOCHSECONDS$COLOR__RESET expansion"
log info "EPOCHSECONDS:\t$COLOR__BLUE$EPOCHSECONDS$COLOR__RESET"

syscall_result_hex="$(read_hex $stack_start 8)"

log info "Syscall Result vs PID: $COLOR__GREEN$(le_hex $syscall_result_hex)$COLOR__RESET vs $COLOR__BLUE$PID$COLOR__RESET"

