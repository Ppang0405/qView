#ifndef QVBRIDGE_H
#define QVBRIDGE_H

// Plain C++ types and functions shared between the Qt code and the Swift core (QVCore).
// Keep this header free of Qt so it can be imported into Swift and built standalone.

#include <cstdint>
#include <span>
#include <string>
#include <vector>

// Marks a type as safe to use from Swift under strict memory safety. Equivalent to
// SWIFT_ESCAPABLE from <swift/bridging>, without needing that header's include path.
// (Swift 6.4 already infers this for structs of std::string and integers; 6.3 doesn't.)
#if defined(__has_attribute) && __has_attribute(swift_attr)
#  define QV_SWIFT_ESCAPABLE __attribute__((swift_attr("Escapable")))
#else
#  define QV_SWIFT_ESCAPABLE
#endif

struct QV_SWIFT_ESCAPABLE QVFolderEntry
{
    std::string fileName; // UTF-8
    std::string mimeType; // UTF-8, only populated when sorting by type
    int64_t lastModified;
    int64_t lastCreated;
    int64_t size;
};

using QVFolderEntryList = std::vector<QVFolderEntry>;
using QVIndexList = std::vector<int64_t>;

// A mutable view of bytes owned by the caller (e.g. a QByteArray). Swift accesses it as a
// bounds-checked MutableSpan without copying.
using QVMutableBytes = std::span<uint8_t>;

// Bridge functions are noexcept: a C++ exception propagating into Swift terminates the program.

// Locale-aware comparison of two UTF-8 strings, returning <0, 0 or >0. With `numeric`,
// digit runs compare by value ("img2" < "img10"). The app implements this with QCollator
// (src/qvcorebridge.cpp) so Swift doesn't need Foundation's bundled ICU on Linux/Windows;
// standalone SwiftPM builds use a simpler fallback (Sources/QVBridge/standalone.cpp).
int qvCompareStrings(const std::string &a, const std::string &b, bool numeric) noexcept;

#endif // QVBRIDGE_H
