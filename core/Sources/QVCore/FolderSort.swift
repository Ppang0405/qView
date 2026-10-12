import CxxStdlib
import Foundation
import QVBridge

/// Values of the "sortmode" setting.
public enum FolderSortMode: Int32 {
    case natural = 0
    case dateModified = 1
    case dateCreated = 2
    case size = 3
    case type = 4
    case random = 5
}

public struct FolderEntry {
    public var fileName: String
    public var mimeType: String
    public var lastModified: Int64
    public var lastCreated: Int64
    public var size: Int64

    public init(fileName: String, mimeType: String = "", lastModified: Int64 = 0,
                lastCreated: Int64 = 0, size: Int64 = 0) {
        self.fileName = fileName
        self.mimeType = mimeType
        self.lastModified = lastModified
        self.lastCreated = lastCreated
        self.size = size
    }
}

/// Returns the display order of `entries` as indices into `entries`.
///
/// Date and size modes put the newest/largest file first unless `descending` is set,
/// matching qView's historical behavior.
public func folderSortOrder(of entries: [FolderEntry], mode: FolderSortMode,
                            descending: Bool) -> [Int] {
    let indices = Array(entries.indices)

    func sorted(by areInIncreasingOrder: (FolderEntry, FolderEntry) -> Bool) -> [Int] {
        indices.sorted { areInIncreasingOrder(entries[$0], entries[$1]) }
    }

    let wantedOrder: ComparisonResult = descending ? .orderedDescending : .orderedAscending
    switch mode {
    case .natural:
        return sorted { $0.fileName.localizedStandardCompare($1.fileName) == wantedOrder }
    case .dateModified:
        return sorted { descending ? $0.lastModified < $1.lastModified : $0.lastModified > $1.lastModified }
    case .dateCreated:
        return sorted { descending ? $0.lastCreated < $1.lastCreated : $0.lastCreated > $1.lastCreated }
    case .size:
        return sorted { descending ? $0.size < $1.size : $0.size > $1.size }
    case .type:
        return sorted { $0.mimeType.localizedCompare($1.mimeType) == wantedOrder }
    case .random:
        return indices.shuffled()
    }
}

/// C++ entry point, called from QVImageCore::updateFolderInfo.
/// An unknown `mode` leaves the order unchanged.
///
/// int64_t imports as Int64 on macOS/Windows but Int on Linux, hence the explicit conversions.
public func sortFolderEntries(_ entries: QVFolderEntryList, _ mode: Int32,
                              _ descending: Bool) -> QVIndexList {
    let swiftEntries = entries.map {
        FolderEntry(fileName: String($0.fileName), mimeType: String($0.mimeType),
                    lastModified: Int64($0.lastModified), lastCreated: Int64($0.lastCreated),
                    size: Int64($0.size))
    }
    let order = FolderSortMode(rawValue: mode).map {
        folderSortOrder(of: swiftEntries, mode: $0, descending: descending)
    } ?? Array(swiftEntries.indices)

    var result = QVIndexList()
    result.reserve(order.count)
    for index in order {
        result.push_back(QVIndexList.value_type(index))
    }
    return result
}
