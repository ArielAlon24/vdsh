    .text
    .global _start

_start:
    mov x8, #113    // __NR_clock_gettime
    svc #0
    ret

