#include "opencuda/device_registry.hpp"

namespace opencuda {

std::vector<DeviceInfo> DeviceRegistry::detect() {
    // The portable core intentionally reports no accelerator devices.
    // Backend-specific discovery will be registered here as backends mature.
    return {};
}

} // namespace opencuda
