#include <cuda_runtime.h>

#include <atomic>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

namespace {

__global__ void burn_kernel(float *data, std::size_t count, unsigned long long rounds) {
    const std::size_t index = blockIdx.x * blockDim.x + threadIdx.x;
    if (index >= count) {
        return;
    }

    float value = data[index];
    for (unsigned long long round = 0; round < rounds; ++round) {
        value = fmaf(value, 1.00000011920928955078125F, 0.00000011920928955078125F);
    }
    data[index] = value;
}

struct Options {
    int seconds = 60;
    int duty_percent = 100;
    int memory_mib = 512;
    std::string devices;
};

bool parse_int(const char *text, int minimum, int maximum, int *value) {
    char *end = nullptr;
    const long parsed = std::strtol(text, &end, 10);
    if (end == text || *end != '\0' || parsed < minimum || parsed > maximum) {
        return false;
    }
    *value = static_cast<int>(parsed);
    return true;
}

bool parse_options(int argc, char **argv, Options *options) {
    for (int index = 1; index < argc; index += 2) {
        if (index + 1 >= argc) {
            return false;
        }
        if (std::strcmp(argv[index], "--seconds") == 0) {
            if (!parse_int(argv[index + 1], 1, 86400, &options->seconds)) {
                return false;
            }
        } else if (std::strcmp(argv[index], "--duty") == 0) {
            if (!parse_int(argv[index + 1], 1, 100, &options->duty_percent)) {
                return false;
            }
        } else if (std::strcmp(argv[index], "--memory-mib") == 0) {
            if (!parse_int(argv[index + 1], 64, 8192, &options->memory_mib)) {
                return false;
            }
        } else if (std::strcmp(argv[index], "--devices") == 0) {
            options->devices = argv[index + 1];
        } else {
            return false;
        }
    }
    return true;
}

bool select_devices(const std::string &text, int device_count, std::vector<int> *devices) {
    if (text.empty()) {
        for (int device = 0; device < device_count; ++device) {
            devices->push_back(device);
        }
        return true;
    }

    std::stringstream stream(text);
    std::string token;
    while (std::getline(stream, token, ',')) {
        int device = -1;
        if (!parse_int(token.c_str(), 0, device_count - 1, &device)) {
            return false;
        }
        for (const int selected : *devices) {
            if (selected == device) {
                return false;
            }
        }
        devices->push_back(device);
    }
    return !devices->empty();
}

void worker(int device, const Options &options, std::atomic<bool> *failed) {
    if (cudaSetDevice(device) != cudaSuccess) {
        failed->store(true);
        return;
    }

    const std::size_t bytes = static_cast<std::size_t>(options.memory_mib) * 1024U * 1024U;
    const std::size_t count = bytes / sizeof(float);
    float *data = nullptr;
    if (cudaMalloc(&data, bytes) != cudaSuccess ||
        cudaMemset(data, 0x3f, bytes) != cudaSuccess) {
        std::fprintf(stderr, "device %d: allocation or initialization failed\n", device);
        if (data != nullptr) {
            cudaFree(data);
        }
        failed->store(true);
        return;
    }

    constexpr int threads = 256;
    const int blocks = static_cast<int>((count + threads - 1U) / threads);
    const auto deadline = std::chrono::steady_clock::now() +
                          std::chrono::seconds(options.seconds);

    while (std::chrono::steady_clock::now() < deadline && !failed->load()) {
        const auto active_start = std::chrono::steady_clock::now();
        const auto active_end = active_start + std::chrono::milliseconds(options.duty_percent * 10);
        while (std::chrono::steady_clock::now() < active_end && !failed->load()) {
            burn_kernel<<<blocks, threads>>>(data, count, 512);
            if (cudaGetLastError() != cudaSuccess || cudaDeviceSynchronize() != cudaSuccess) {
                std::fprintf(stderr, "device %d: kernel execution failed\n", device);
                failed->store(true);
                break;
            }
        }
        if (options.duty_percent < 100) {
            std::this_thread::sleep_until(active_start + std::chrono::seconds(1));
        }
    }

    if (cudaFree(data) != cudaSuccess) {
        failed->store(true);
    }
}

}  // namespace

int main(int argc, char **argv) {
    Options options;
    if (!parse_options(argc, argv, &options)) {
        std::fprintf(stderr,
                     "usage: %s [--seconds N] [--duty 1..100] [--memory-mib N] "
                     "[--devices 0,1,...]\n",
                     argv[0]);
        return 2;
    }

    int device_count = 0;
    if (cudaGetDeviceCount(&device_count) != cudaSuccess || device_count < 1) {
        std::fprintf(stderr, "no CUDA devices available\n");
        return 3;
    }

    std::vector<int> devices;
    if (!select_devices(options.devices, device_count, &devices)) {
        std::fprintf(stderr, "invalid CUDA device selection: %s\n", options.devices.c_str());
        return 4;
    }

    std::printf("loading %zu of %d CUDA device(s): %d seconds, %d%% duty, %d MiB/device\n",
                devices.size(), device_count, options.seconds, options.duty_percent,
                options.memory_mib);
    std::atomic<bool> failed{false};
    std::vector<std::thread> workers;
    workers.reserve(devices.size());
    for (const int device : devices) {
        workers.emplace_back(worker, device, options, &failed);
    }
    for (auto &thread : workers) {
        thread.join();
    }
    return failed.load() ? 1 : 0;
}
