import CxxStdlib
import QVBridge

/// Workaround for QTBUG-125241: Qt 5.14 through 6.7.1 reject ICC profiles containing tags
/// whose data is smaller than 12 bytes. Removes those tags from the profile in place by
/// compacting the tag table and zero-filling the freed entries; the size never changes.
/// Returns whether any tag was removed.
///
/// C++ entry point, called from QVImageCore with the profile's QByteArray storage.
public func removeTinyDataTagsFromIccProfile(_ profile: QVMutableBytes) -> Bool {
    // The only unsafe step: viewing the caller's buffer, which outlives this call.
    // Everything after it is bounds-checked.
    var bytes = unsafe MutableSpan<UInt8>(_unsafeCxxSpan: profile)
    return removeTinyDataTags(in: &bytes)
}

private let tagCountOffset = 128
private let tagEntrySize = 12

func removeTinyDataTags(in profile: inout MutableSpan<UInt8>) -> Bool {
    guard profile.count - tagCountOffset >= 4 else { return false }
    var tagCount = Int(readBigEndianUInt32(profile, at: tagCountOffset))
    // Small enough that the size arithmetic below can't overflow
    guard tagCount <= 99999 else { return false }
    var offset = tagCountOffset + 4
    guard profile.count - offset >= tagCount * tagEntrySize else { return false }

    var foundTinyData = false
    while tagCount > 0 {
        tagCount -= 1
        let dataSize = readBigEndianUInt32(profile, at: offset + 8)
        if dataSize >= 12 {
            // This tag is fine
            offset += tagEntrySize
            continue
        }
        // Qt will fail on this tag, so remove it: shift the remaining tags back...
        foundTinyData = true
        for index in offset..<(offset + tagCount * tagEntrySize) {
            profile[index] = profile[index + tagEntrySize]
        }
        // ...zero-fill the freed entry at the end...
        let freedEntry = offset + tagCount * tagEntrySize
        for index in freedEntry..<(freedEntry + tagEntrySize) {
            profile[index] = 0
        }
        // ...and decrement the tag count in the header
        let newCount = readBigEndianUInt32(profile, at: tagCountOffset) - 1
        writeBigEndianUInt32(newCount, to: &profile, at: tagCountOffset)
    }
    return foundTinyData
}

private func readBigEndianUInt32(_ bytes: borrowing MutableSpan<UInt8>, at offset: Int) -> UInt32 {
    (0..<4).reduce(0) { value, index in (value << 8) | UInt32(bytes[offset + index]) }
}

private func writeBigEndianUInt32(_ value: UInt32, to bytes: inout MutableSpan<UInt8>,
                                  at offset: Int) {
    for index in 0..<4 {
        bytes[offset + index] = UInt8(truncatingIfNeeded: value >> (24 - 8 * index))
    }
}
