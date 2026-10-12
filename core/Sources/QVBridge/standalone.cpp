// Fallback implementations of the bridge functions for standalone SwiftPM builds (swift test).
// The app uses the Qt implementations in src/qvcorebridge.cpp instead.

#include "qvbridge.h"

#include <cctype>

// Not locale-aware: compares ASCII case-insensitively and digit runs by value.
int qvCompareStrings(const std::string &a, const std::string &b, bool numeric) noexcept
{
    size_t i = 0, j = 0;
    while (i < a.size() && j < b.size()) {
        const auto ca = static_cast<unsigned char>(a[i]);
        const auto cb = static_cast<unsigned char>(b[j]);
        if (numeric && std::isdigit(ca) && std::isdigit(cb)) {
            while (i < a.size() && a[i] == '0')
                ++i;
            while (j < b.size() && b[j] == '0')
                ++j;
            const size_t startA = i, startB = j;
            while (i < a.size() && std::isdigit(static_cast<unsigned char>(a[i])))
                ++i;
            while (j < b.size() && std::isdigit(static_cast<unsigned char>(b[j])))
                ++j;
            if (i - startA != j - startB)
                return i - startA < j - startB ? -1 : 1;
            const int digits = a.compare(startA, i - startA, b, startB, j - startB);
            if (digits != 0)
                return digits;
            continue;
        }
        const int la = std::tolower(ca), lb = std::tolower(cb);
        if (la != lb)
            return la < lb ? -1 : 1;
        ++i;
        ++j;
    }
    if (i < a.size())
        return 1;
    if (j < b.size())
        return -1;
    return 0;
}
