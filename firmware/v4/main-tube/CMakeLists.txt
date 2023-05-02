cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

set(PICO_BOARD adafruit_feather_rp2040)

project(firmware C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
pico_sdk_init()

add_executable(firmware
    firmware.c bno055.c
)

pico_enable_stdio_usb(firmware 1)
pico_enable_stdio_uart(firmware 0)

pico_add_extra_outputs(firmware)

target_link_libraries(firmware pico_stdlib hardware_gpio hardware_adc hardware_pwm hardware_i2c hardware_irq hardware_uart)
