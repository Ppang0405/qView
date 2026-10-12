// Qt implementations of the functions the Swift core (core/) calls back into.

#include "qvbridge.h"

#include <QCollator>

int qvCompareStrings(const std::string &a, const std::string &b, bool numeric)
{
    // QCollator is expensive to create, so reuse one per thread
    thread_local QCollator collator;
    if (collator.locale() != QLocale())
        collator.setLocale(QLocale());
    if (collator.numericMode() != numeric)
        collator.setNumericMode(numeric);
    return collator.compare(QString::fromStdString(a), QString::fromStdString(b));
}
