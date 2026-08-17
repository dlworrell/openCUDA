#include "opencuda/legacy_cuda.h"

#include <cuda_runtime_api.h>

extern "C" opencuda_status opencuda_kepler_probe(opencuda_kepler_summary *summary) {
    if (summary == nullptr) {
        return OPENCUDA_STATUS_INVALID_ARGUMENT;
    }

    summary->visible_devices = 0u;
    summary->sm37_devices = 0u;

    int device_count = 0;
    const cudaError_t count_status = cudaGetDeviceCount(&device_count);
    if (count_status != cudaSuccess) {
        return OPENCUDA_STATUS_UNAVAILABLE;
    }

    summary->visible_devices = static_cast<uint32_t>(device_count);
    for (int index = 0; index < device_count; ++index) {
        cudaDeviceProp properties{};
        if (cudaGetDeviceProperties(&properties, index) != cudaSuccess) {
            return OPENCUDA_STATUS_INTERNAL_ERROR;
        }
        if (properties.major == 3 && properties.minor == 7) {
            ++summary->sm37_devices;
        }
    }

    return OPENCUDA_STATUS_OK;
}
