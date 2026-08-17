#include "opencuda/device_registry.hpp"

#include <cassert>

int main() {
    const auto devices = opencuda::DeviceRegistry::detect();
    assert(devices.empty());
    return 0;
}
