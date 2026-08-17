#ifndef OPENCUDA_DEVICE_REGISTRY_HPP
#define OPENCUDA_DEVICE_REGISTRY_HPP

#include <cstdint>
#include <string>
#include <vector>

namespace opencuda {

struct DeviceInfo {
    std::uint32_t logical_index{};
    std::string backend;
    std::string name;
    std::string uuid;
    std::uint32_t compute_major{};
    std::uint32_t compute_minor{};
    std::uint64_t memory_bytes{};
};

class DeviceRegistry {
  public:
    [[nodiscard]] static std::vector<DeviceInfo> detect();
};

} // namespace opencuda

#endif
