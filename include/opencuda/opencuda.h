#ifndef OPENCUDA_OPENCUDA_H
#define OPENCUDA_OPENCUDA_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define OPENCUDA_ABI_VERSION 1u

typedef enum opencuda_status {
    OPENCUDA_STATUS_OK = 0,
    OPENCUDA_STATUS_UNAVAILABLE = 1,
    OPENCUDA_STATUS_UNSUPPORTED = 2,
    OPENCUDA_STATUS_INVALID_ARGUMENT = 3,
    OPENCUDA_STATUS_INTERNAL_ERROR = 4
} opencuda_status;

typedef struct opencuda_version {
    uint32_t major;
    uint32_t minor;
    uint32_t patch;
    uint32_t abi;
} opencuda_version;

opencuda_version opencuda_get_version(void);
const char *opencuda_status_string(opencuda_status status);
void opencuda_cpu_relax(void);

/* Internal assembly entry point exposed for low-level tests. */
void opencuda_asm_cpu_relax(void);

#ifdef __cplusplus
}
#endif

#endif
