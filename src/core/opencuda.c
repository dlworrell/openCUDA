#include "opencuda/opencuda.h"

opencuda_version opencuda_get_version(void) {
    const opencuda_version version = {0u, 1u, 0u, OPENCUDA_ABI_VERSION};
    return version;
}

const char *opencuda_status_string(opencuda_status status) {
    switch (status) {
    case OPENCUDA_STATUS_OK:
        return "ok";
    case OPENCUDA_STATUS_UNAVAILABLE:
        return "unavailable";
    case OPENCUDA_STATUS_UNSUPPORTED:
        return "unsupported";
    case OPENCUDA_STATUS_INVALID_ARGUMENT:
        return "invalid argument";
    case OPENCUDA_STATUS_INTERNAL_ERROR:
        return "internal error";
    default:
        return "unknown status";
    }
}

void opencuda_cpu_relax(void) { opencuda_asm_cpu_relax(); }
