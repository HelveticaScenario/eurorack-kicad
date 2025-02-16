# Generated Cmake Pico project file

cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Initialise pico_sdk from installed location
# (note this can come from environment, CMake cache etc)

# == DO NOT EDIT THE FOLLOWING LINES for the Raspberry Pi Pico VS Code Extension to work ==
if(WIN32)
    set(USERHOME $ENV{USERPROFILE})
else()
    set(USERHOME $ENV{HOME})
endif()
set(sdkVersion 2.0.0)
set(toolchainVersion 13_2_Rel1)
set(picotoolVersion 2.0.0)
set(picoVscode ${USERHOME}/.pico-sdk/cmake/pico-vscode.cmake)
if (EXISTS ${picoVscode})
    include(${picoVscode})
endif()
# ====================================================================================
set(PICO_BOARD pico_w CACHE STRING "Board type")

# Pull in Raspberry Pi Pico SDK (must be before project)
include(pico_sdk_import.cmake)

project(sequencer_switch C CXX ASM)

set(PICO_CXX_ENABLE_EXCEPTIONS 1)

set(PICO_CXX_ENABLE_RTTI 1)

# Initialise the Raspberry Pi Pico SDK
pico_sdk_init()

# Add executable. Default name is the project name, version 0.1

add_executable(sequencer_switch sequencer_switch.cpp )

pico_set_program_name(sequencer_switch "sequencer_switch")
pico_set_program_version(sequencer_switch "0.1")

# Modify the below lines to enable/disable output over UART/USB
pico_enable_stdio_uart(sequencer_switch 1)
pico_enable_stdio_usb(sequencer_switch 0)

pico_generate_pio_header(sequencer_switch ${CMAKE_CURRENT_LIST_DIR}/quadrature_encoder_substep.pio)
pico_generate_pio_header(sequencer_switch ${CMAKE_CURRENT_LIST_DIR}/quadrature_encoder.pio)
pico_generate_pio_header(sequencer_switch ${CMAKE_CURRENT_LIST_DIR}/ws2812.pio)

# Add the standard library to the build
target_link_libraries(sequencer_switch
        pico_stdlib
        pico_multicore
        hardware_pio
        hardware_pwm
        hardware_watchdog
        )

# Add the standard include files to the build
target_include_directories(sequencer_switch PRIVATE
  ${CMAKE_CURRENT_LIST_DIR}
)

pico_add_extra_outputs(sequencer_switch)

