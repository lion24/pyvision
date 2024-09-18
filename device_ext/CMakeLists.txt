set(DEVICE_C_EXT_SRCS
    "device.cpp"
)

add_library(device_ext SHARED ${DEVICE_C_EXT_SRCS})


set_target_properties(
    device_ext
    PROPERTIES
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED YES
        CXX_EXTENSIONS NO
        LINKER_LANGUAGE CXX
)


set_target_properties(
    device_ext
    PROPERTIES
        PREFIX ""
        OUTPUT_NAME ${DEVICE_C_EXT_NAME}
        LINKER_LANGUAGE CXX
)

target_include_directories(device_ext PRIVATE ${Python3_INCLUDE_DIRS})
target_link_libraries(device_ext PRIVATE Python3::Python)

# Force the use of release Python library even in debug mode on Windows
if(WIN32)
    # Define the Python extension file suffix for Windows
    set_target_properties(
        device_ext
        PROPERTIES
            SUFFIX ".pyd"
    )
else()
    # For Unix-based systems, set the suffix to `.so`
    set_target_properties(
        device_ext
        PROPERTIES
            SUFFIX ".so"
    )
endif()
