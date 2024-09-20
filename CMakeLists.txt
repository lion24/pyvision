cmake_minimum_required(VERSION 3.10)
project(pyvision)

find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

set(DEVICE_C_EXT_NAME "device" CACHE STRING "Name of the device extension module")

add_subdirectory(device_ext)
