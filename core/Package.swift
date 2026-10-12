// swift-tools-version:6.0
// Standalone package for building and testing the Swift core without Qt.
// The app itself compiles these same sources through CMake.

import PackageDescription

let package = Package(
    name: "QVCore",
    targets: [
        .target(name: "QVBridge"),
        .target(
            name: "QVCore",
            dependencies: ["QVBridge"],
            swiftSettings: [.interoperabilityMode(.Cxx)]
        ),
        .testTarget(
            name: "QVCoreTests",
            dependencies: ["QVCore"],
            swiftSettings: [.interoperabilityMode(.Cxx)]
        ),
    ],
    cxxLanguageStandard: .cxx17
)
