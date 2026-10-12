# Swift core (QVCore): Qt-free logic written in Swift and called from the C++ code.
# The same sources also build standalone with SwiftPM (see Package.swift) for `swift test`.

set(QVCORE_BRIDGE_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/Sources/QVBridge/include")
set(QVCORE_GENERATED_INCLUDE_DIR "${CMAKE_CURRENT_BINARY_DIR}/include")
set(QVCORE_GENERATED_HEADER "${QVCORE_GENERATED_INCLUDE_DIR}/QVCore-Swift.h")

set(QVCORE_SOURCES
    Sources/QVCore/FolderSort.swift
)
list(TRANSFORM QVCORE_SOURCES PREPEND "${CMAKE_CURRENT_SOURCE_DIR}/")

set(QVCORE_SWIFT_FLAGS
    -cxx-interoperability-mode=default
    -Xcc -std=c++17
)

add_library(QVCore STATIC ${QVCORE_SOURCES})
set_target_properties(QVCore PROPERTIES
    Swift_MODULE_NAME QVCore
    AUTOMOC OFF
    AUTOUIC OFF
    AUTORCC OFF
)
target_compile_options(QVCore PRIVATE
    "$<$<COMPILE_LANGUAGE:Swift>:-cxx-interoperability-mode=default>"
    "$<$<COMPILE_LANGUAGE:Swift>:SHELL:-Xcc -std=c++17>"
)
target_include_directories(QVCore PUBLIC
    "${CMAKE_CURRENT_SOURCE_DIR}/include"
    "${QVCORE_BRIDGE_INCLUDE_DIR}"
    "${QVCORE_GENERATED_INCLUDE_DIR}"
)

# Generate the C++ header (QVCore-Swift.h) that exposes the Swift API to C++.
# This runs as a separate type-check so C++ sources can include the header before
# the Swift library itself has finished building.
if(CMAKE_Swift_COMPILER_TARGET)
    list(APPEND QVCORE_TARGET_FLAGS -target "${CMAKE_Swift_COMPILER_TARGET}")
endif()
if(APPLE AND CMAKE_OSX_SYSROOT)
    list(APPEND QVCORE_TARGET_FLAGS -sdk "${CMAKE_OSX_SYSROOT}")
endif()
add_custom_command(
    OUTPUT "${QVCORE_GENERATED_HEADER}"
    COMMAND "${CMAKE_Swift_COMPILER}" -typecheck
            -module-name QVCore
            ${QVCORE_SWIFT_FLAGS}
            ${QVCORE_TARGET_FLAGS}
            -I "${QVCORE_BRIDGE_INCLUDE_DIR}"
            -emit-clang-header-path "${QVCORE_GENERATED_HEADER}"
            ${QVCORE_SOURCES}
    DEPENDS ${QVCORE_SOURCES} "${QVCORE_BRIDGE_INCLUDE_DIR}/qvbridge.h"
    COMMENT "Generating QVCore-Swift.h"
    VERBATIM
)
add_custom_target(QVCoreHeader DEPENDS "${QVCORE_GENERATED_HEADER}")
add_dependencies(QVCore QVCoreHeader)
