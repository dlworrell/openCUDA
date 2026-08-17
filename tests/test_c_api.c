#include "opencuda/opencuda.h"

#include <assert.h>
#include <string.h>

int main(void) {
    const opencuda_version version = opencuda_get_version();
    assert(version.abi == OPENCUDA_ABI_VERSION);
    assert(version.major == 0u);
    assert(strcmp(opencuda_status_string(OPENCUDA_STATUS_OK), "ok") == 0);
    opencuda_cpu_relax();
    return 0;
}
