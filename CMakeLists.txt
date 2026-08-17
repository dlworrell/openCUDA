cmake_minimum_required(VERSION 3.24)

project(openCUDA VERSION 0.1.0 LANGUAGES C CXX)

include(CheckLanguage)
include(CTest)

option(OPENCUDA_BUILD_TESTS "Build native tests" ON)
option(OPENCUDA_BUILD_SHARED "Build openCUDA libraries as shared libraries" OFF)
option(OPENCUDA_ENABLE_ASM "Enable architecture-specific assembly primitives" ON)
option(OPENCUDA_ENABLE_LEGACY_CUDA "Build the CUDA 11.x Kepler backend" OFF)
option(OPENCUDA_WARNINGS_AS_ERRORS "Treat compiler warnings as errors" OFF)

set(CMAKE_C_STANDARD 17)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(OPENCUDA_BUILD_SHARED)
  set(OPENCUDA_LIBRARY_TYPE SHARED)
else()
  set(OPENCUDA_LIBRARY_TYPE STATIC)
endif()

function(opencuda_target_warnings target)
  if(MSVC)
    target_compile_options(${target} PRIVATE
      $<$<COMPILE_LANGUAGE:C>:/W4>
      $<$<COMPILE_LANGUAGE:CXX>:/W4>
      $<$<COMPILE_LANGUAGE:CXX>:/permissive->
    )
    if(OPENCUDA_WARNINGS_AS_ERRORS)
      target_compile_options(${target} PRIVATE
        $<$<COMPILE_LANGUAGE:C>:/WX>
        $<$<COMPILE_LANGUAGE:CXX>:/WX>
      )
    endif()
  else()
    target_compile_options(${target} PRIVATE
      $<$<COMPILE_LANGUAGE:C>:-Wall>
      $<$<COMPILE_LANGUAGE:C>:-Wextra>
      $<$<COMPILE_LANGUAGE:C>:-Wpedantic>
      $<$<COMPILE_LANGUAGE:C>:-Wconversion>
      $<$<COMPILE_LANGUAGE:C>:-Wshadow>
      $<$<COMPILE_LANGUAGE:CXX>:-Wall>
      $<$<COMPILE_LANGUAGE:CXX>:-Wextra>
      $<$<COMPILE_LANGUAGE:CXX>:-Wpedantic>
      $<$<COMPILE_LANGUAGE:CXX>:-Wconversion>
      $<$<COMPILE_LANGUAGE:CXX>:-Wshadow>
    )
    if(OPENCUDA_WARNINGS_AS_ERRORS)
      target_compile_options(${target} PRIVATE
        $<$<COMPILE_LANGUAGE:C>:-Werror>
        $<$<COMPILE_LANGUAGE:CXX>:-Werror>
      )
    endif()
  endif()
endfunction()

set(OPENCUDA_ASM_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/asm/opencuda_cpu_relax_fallback.c")
set(OPENCUDA_ASM_KIND "portable-c-fallback")
string(TOLOWER "${CMAKE_SYSTEM_PROCESSOR}" OPENCUDA_PROCESSOR)

if(OPENCUDA_ENABLE_ASM)
  if(WIN32 AND MSVC AND OPENCUDA_PROCESSOR MATCHES "^(amd64|x86_64)$")
    check_language(ASM_MASM)
    if(CMAKE_ASM_MASM_COMPILER)
      enable_language(ASM_MASM)
      set(OPENCUDA_ASM_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/asm/x86_64/windows/opencuda_cpu_relax.asm")
      set(OPENCUDA_ASM_KIND "x86-64-masm")
    endif()
  elseif(UNIX AND OPENCUDA_PROCESSOR MATCHES "^(amd64|x86_64)$")
    enable_language(ASM)
    if(APPLE)
      set(OPENCUDA_ASM_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/asm/x86_64/macos/opencuda_cpu_relax.S")
      set(OPENCUDA_ASM_KIND "x86-64-clang-asm")
    else()
      set(OPENCUDA_ASM_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/asm/x86_64/linux/opencuda_cpu_relax.S")
      set(OPENCUDA_ASM_KIND "x86-64-gas")
    endif()
  elseif(UNIX AND OPENCUDA_PROCESSOR MATCHES "^(aarch64|arm64)$")
    enable_language(ASM)
    if(APPLE)
      set(OPENCUDA_ASM_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/asm/aarch64/macos/opencuda_cpu_relax.S")
      set(OPENCUDA_ASM_KIND "aarch64-clang-asm")
    else()
      set(OPENCUDA_ASM_SOURCE "${CMAKE_CURRENT_SOURCE_DIR}/src/asm/aarch64/linux/opencuda_cpu_relax.S")
      set(OPENCUDA_ASM_KIND "aarch64-gas")
    endif()
  endif()
endif()

message(STATUS "openCUDA assembly implementation: ${OPENCUDA_ASM_KIND}")

add_library(opencuda_core ${OPENCUDA_LIBRARY_TYPE}
  src/core/opencuda.c
  ${OPENCUDA_ASM_SOURCE}
)
add_library(openCUDA::core ALIAS opencuda_core)

target_include_directories(opencuda_core
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
target_compile_definitions(opencuda_core PRIVATE OPENCUDA_BUILDING_LIBRARY=1)
opencuda_target_warnings(opencuda_core)

add_library(opencuda_cpp ${OPENCUDA_LIBRARY_TYPE}
  src/cpp/device_registry.cpp
)
add_library(openCUDA::cpp ALIAS opencuda_cpp)
target_link_libraries(opencuda_cpp PUBLIC openCUDA::core)
target_include_directories(opencuda_cpp
  PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)
opencuda_target_warnings(opencuda_cpp)

if(OPENCUDA_ENABLE_LEGACY_CUDA)
  check_language(CUDA)
  if(NOT CMAKE_CUDA_COMPILER)
    message(FATAL_ERROR "OPENCUDA_ENABLE_LEGACY_CUDA=ON but no CUDA compiler was found")
  endif()

  enable_language(CUDA)
  find_package(CUDAToolkit REQUIRED)

  if(CUDAToolkit_VERSION VERSION_GREATER_EQUAL "12.0")
    message(FATAL_ERROR
      "Kepler sm_37 support is not available in CUDA 12+. "
      "Use a CUDA 11.x toolchain (CUDA 11.8 is recommended for the reference backend).")
  endif()

  if(CUDAToolkit_VERSION VERSION_LESS "11.0")
    message(WARNING "openCUDA is primarily validated against CUDA 11.x; found ${CUDAToolkit_VERSION}")
  endif()

  add_library(opencuda_kepler_backend ${OPENCUDA_LIBRARY_TYPE}
    src/legacy_cuda/kepler_probe.cu
  )
  add_library(openCUDA::kepler_backend ALIAS opencuda_kepler_backend)
  target_link_libraries(opencuda_kepler_backend PUBLIC openCUDA::core CUDA::cudart)
  target_include_directories(opencuda_kepler_backend PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
  set_target_properties(opencuda_kepler_backend PROPERTIES
    CUDA_ARCHITECTURES 37
    CUDA_STANDARD 14
    CUDA_STANDARD_REQUIRED ON
  )
endif()

if(BUILD_TESTING AND OPENCUDA_BUILD_TESTS)
  add_executable(opencuda_c_api_test tests/test_c_api.c)
  target_link_libraries(opencuda_c_api_test PRIVATE openCUDA::core)
  add_test(NAME c_api COMMAND opencuda_c_api_test)

  add_executable(opencuda_cpp_api_test tests/test_cpp_api.cpp)
  target_link_libraries(opencuda_cpp_api_test PRIVATE openCUDA::cpp)
  add_test(NAME cpp_api COMMAND opencuda_cpp_api_test)
endif()
