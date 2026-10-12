#ifndef QVBRIDGE_H
#define QVBRIDGE_H

// Plain C++ types and functions shared between the Qt code and the Swift core (QVCore).
// Keep this header free of Qt so it can be imported into Swift and built standalone.

#include <cstdint>
#include <string>
#include <vector>

struct QVFolderEntry
{
    std::string fileName; // UTF-8
    std::string mimeType; // UTF-8, only populated when sorting by type
    int64_t lastModified;
    int64_t lastCreated;
    int64_t size;
};

using QVFolderEntryList = std::vector<QVFolderEntry>;
using QVIndexList = std::vector<int64_t>;

// Locale-aware comparison of two UTF-8 strings, returning <0, 0 or >0. With `numeric`,
// digit runs compare by value ("img2" < "img10"). The app implements this with QCollator
// (src/qvcorebridge.cpp) so Swift doesn't need Foundation's bundled ICU on Linux/Windows;
// standalone SwiftPM builds use a simpler fallback (Sources/QVBridge/standalone.cpp).
int qvCompareStrings(const std::string &a, const std::string &b, bool numeric);

#endif // QVBRIDGE_H
