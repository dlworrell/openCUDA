#ifndef OPENCUDA_LEGACY_CUDA_H
#define OPENCUDA_LEGACY_CUDA_H

#include <stdint.h>
#include "opencuda.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct opencuda_kepler_summary {
    uint32_t visible_devices;
    uint32_t sm37_devices;
} opencuda_kepler_summary;

opencuda_status opencuda_kepler_probe(opencuda_kepler_summary *summary);

#ifdef __cplusplus
}
#endif

#endif
