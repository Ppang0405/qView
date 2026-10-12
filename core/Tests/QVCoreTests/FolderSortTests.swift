import CxxStdlib
import QVBridge
@testable import QVCore
import Testing

private func names(_ entries: [FolderEntry], _ mode: FolderSortMode, descending: Bool = false) -> [String] {
    folderSortOrder(of: entries, mode: mode, descending: descending).map { entries[$0].fileName }
}

@Test func naturalSortOrdersNumbersByValue() {
    let entries = ["img10.png", "img2.png", "img1.png"].map { FolderEntry(fileName: $0) }
    #expect(names(entries, .natural) == ["img1.png", "img2.png", "img10.png"])
    #expect(names(entries, .natural, descending: true) == ["img10.png", "img2.png", "img1.png"])
}

@Test func naturalSortIgnoresCase() {
    let entries = ["b.png", "A.png", "c.png"].map { FolderEntry(fileName: $0) }
    #expect(names(entries, .natural) == ["A.png", "b.png", "c.png"])
}

@Test func dateAndSizeModesPutLargestFirstByDefault() {
    let entries = [
        FolderEntry(fileName: "old", lastModified: 1, lastCreated: 1, size: 1),
        FolderEntry(fileName: "new", lastModified: 3, lastCreated: 3, size: 3),
        FolderEntry(fileName: "mid", lastModified: 2, lastCreated: 2, size: 2),
    ]
    for mode in [FolderSortMode.dateModified, .dateCreated, .size] {
        #expect(names(entries, mode) == ["new", "mid", "old"])
        #expect(names(entries, mode, descending: true) == ["old", "mid", "new"])
    }
}

@Test func typeSortOrdersByMimeType() {
    let entries = [
        FolderEntry(fileName: "a.png", mimeType: "image/png"),
        FolderEntry(fileName: "b.gif", mimeType: "image/gif"),
        FolderEntry(fileName: "c.jpg", mimeType: "image/jpeg"),
    ]
    #expect(names(entries, .type) == ["b.gif", "c.jpg", "a.png"])
}

@Test func randomSortIsAPermutation() {
    let entries = (0..<50).map { FolderEntry(fileName: "\($0)") }
    let order = folderSortOrder(of: entries, mode: .random, descending: false)
    #expect(order.sorted() == Array(0..<50))
}

@Test func cxxEntryPointRoundTrips() {
    var list = QVFolderEntryList()
    for name in ["img10.png", "img2.png"] {
        list.push_back(QVFolderEntry(fileName: std.string(name), mimeType: std.string(),
                                     lastModified: 0, lastCreated: 0, size: 0))
    }
    #expect(Array(sortFolderEntries(list, .natural, false)) == [1, 0])
}
