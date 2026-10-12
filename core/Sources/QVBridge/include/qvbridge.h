#ifndef QVBRIDGE_H
#define QVBRIDGE_H

// Plain C++ types shared between the Qt code and the Swift core (QVCore).
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

#endif // QVBRIDGE_H
