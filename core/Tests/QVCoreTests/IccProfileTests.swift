@testable import QVCore
import Testing

/// Builds a profile: a 128-byte header, the tag count, then one 12-byte entry per tag
/// (signature, offset, data size). Only the data size matters to the code under test.
private func makeProfile(dataSizes: [UInt32], padding: Int = 0) -> [UInt8] {
    var bytes = [UInt8](repeating: 0xAB, count: 128)
    func append(_ value: UInt32) {
        bytes += [24, 16, 8, 0].map { UInt8(truncatingIfNeeded: value >> $0) }
    }
    append(UInt32(dataSizes.count))
    for (index, size) in dataSizes.enumerated() {
        append(0x7461_6700 + UInt32(index)) // "tag0", "tag1", ...
        append(0x1000)
        append(size)
    }
    return bytes + [UInt8](repeating: 0xCD, count: padding)
}

private func clean(_ profile: inout [UInt8]) -> Bool {
    // Array.mutableSpan needs macOS 26, so view the buffer the way the C++ entry point does
    profile.withUnsafeMutableBufferPointer { buffer in
        var span = unsafe MutableSpan(_unsafeElements: buffer)
        return removeTinyDataTags(in: &span)
    }
}

@Test func profileWithoutTinyTagsIsUnchanged() {
    var profile = makeProfile(dataSizes: [12, 100, 4000], padding: 8)
    let original = profile
    #expect(!clean(&profile))
    #expect(profile == original)
}

@Test func tinyTagsAreRemovedAndTableCompacted() {
    var profile = makeProfile(dataSizes: [100, 4, 200, 0, 300], padding: 8)
    #expect(clean(&profile))
    // Same size, remaining tags in order, freed entries zeroed, padding untouched
    var expected = makeProfile(dataSizes: [100, 200, 300])
    expected += [UInt8](repeating: 0, count: 24) + [UInt8](repeating: 0xCD, count: 8)
    // Entries keep their original signatures (tag0, tag2, tag4)
    expected[132 + 12 + 3] = 2
    expected[132 + 24 + 3] = 4
    #expect(profile == expected)
}

@Test func allTinyTagsLeavesEmptyTable() {
    var profile = makeProfile(dataSizes: [1, 2])
    #expect(clean(&profile))
    #expect(profile[128..<132].elementsEqual([0, 0, 0, 0]))
    #expect(profile[132...].allSatisfy { $0 == 0 })
}

@Test func truncatedOrImplausibleProfilesAreRejectedSafely() {
    var tooShort = [UInt8](repeating: 0, count: 131)
    #expect(!clean(&tooShort))

    // Claims 3 tags but only has room for 2
    var truncated = Array(makeProfile(dataSizes: [4, 4, 4]).dropLast(12))
    let original = truncated
    #expect(!clean(&truncated))
    #expect(truncated == original)

    var huge = makeProfile(dataSizes: [])
    huge[128..<132] = [0xFF, 0xFF, 0xFF, 0xFF]
    #expect(!clean(&huge))
}
