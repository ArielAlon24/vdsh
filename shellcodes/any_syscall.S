.text
.global _start

/**
 * @brief A `clock_gettime` hook which let's a user run an arbitrary additional
 * syscall by placing a `syscal_config_t` in `symbol + word_size`.
 *
 * Where `syscall_config_t` is:
 *
 * ```c
 * typedef enum syscall_config_mode {
 *     SYSCALL_CONFIG_MODE__DEFAULT = 0,
 *     SYSCALL_CONFIG_MODE__ARBITRARY = 1,
 * } syscall_config_mode_t;
 *
 * typedef struct syscall_config {
 *     uint32_t mode;            // 0x00
 *     uint32_t _padding;        // 0x04
 *     uint64_t number;          // 0x08
 *     uint64_t argument0;       // 0x10
 *     uint64_t argument1;       // 0x18
 *     uint64_t argument2;       // 0x20
 *     uint64_t argument3;       // 0x28
 *     uint64_t argument4;       // 0x30
 *     uint64_t argument5;       // 0x38
 *     uint64_t *result_address; // 0x40
 * } syscall_config_t;
 * ```
 *
 * @brief This is done like so:
 *
 * 1. First run the `gettime` syscall and store the value in `x19`
 * 2. If, `SYSCALL_CONFIG_MODE__DEFAULT == mode` continue to (4)
 * 3. Otherwise, execute the syscall `config->number` with the provided arguments
 *    and store the return value in `result_address`.
 * 4. Move `x19` (`clock_gettime` return value) back `x0` and return
 */

_start:
    /* Skip the `syscall_config_t` inilined value */
    b       2f

    .align  3
g_mode:
    .word   0
    .word   0

g_number:
    .quad   113

g_arguments:
    .quad   0
    .quad   0
    .quad   0
    .quad   0
    .quad   0
    .quad   0

g_result_address:
    .quad   0

2:
    /* Execute `clock_gettime` */
    mov     x8, #113
    svc     #0

    /* Store syscall return value in `x19` */
    mov     x19, x0

    /* If `SYSCALL_CONFIG_MODE__DEFAULT == mode` continue to execute an arbitrary syscall */
    adr     x9, g_mode
    ldr     w10, [x9]
    cbz     w10, 1f

    /* Load `g_syscall_config->number` */
    adr     x9, g_number
    ldr     x8, [x9]

    /* Load `g_syscall_config->arguments */
    adr     x9, g_arguments
    ldr     x0, [x9]
    ldr     x1, [x9, #8]
    ldr     x2, [x9, #16]
    ldr     x3, [x9, #24]
    ldr     x4, [x9, #32]
    ldr     x5, [x9, #40]

    svc     #0

    /* Save arbitrary syscall return value in `g_syscall_config->result_address` */
    adr     x9, g_result_address
    ldr     x10, [x9]
    cbz     x10, 1f
    str     x0, [x10]

1:
    /* Retrieve `clock_gettime` syscall retunr values */
    mov     x0, x19
    ret
