from PyQt6.QtCore import QDir, QElapsedTimer, QFileInfo, QObject, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QImage, QImageReader, QMovie, QPixmap, QPixmapCache, QTransform


class QVImageCore(QObject):
    animatedFrameChanged = pyqtSignal(object)  # QRect
    updateLoadedPixmapItem = pyqtSignal()
    fileChanged = pyqtSignal()

    class CompatibleFile:
        def __init__(self, absoluteFilePath, fileName):
            self.absoluteFilePath = absoluteFilePath
            self.fileName = fileName
            self.lastModified = 0
            self.lastCreated = 0
            self.size = 0
            self.mimeType = ""

    class ErrorData:
        def __init__(self):
            self.hasError = False
            self.errorNum = 0
            self.errorString = ""

    class FileDetails:
        def __init__(self):
            self.fileInfo = QFileInfo()
            self.folderFileInfoList = []
            self.loadedIndexInFolder = -1
            self.isLoadRequested = False
            self.isPixmapLoaded = False
            self.isMovieLoaded = False
            self.baseImageSize = QSize()
            self.loadedPixmapSize = QSize()
            self.timeSinceLoaded = QElapsedTimer()
            self.errorData = QVImageCore.ErrorData()

        def updateLoadedIndexInFolder(self):
            if not self.folderFileInfoList:
                return

            for i, file in enumerate(self.folderFileInfoList):
                if file.absoluteFilePath == self.fileInfo.absoluteFilePath():
                    self.loadedIndexInFolder = i
                    break

    class ReadData:
        def __init__(self):
            self.image = QImage()
            self.absoluteFilePath = ""
            self.fileSize = 0
            self.imageSize = QSize()
            self.targetColorSpace = None
            self.errorData = QVImageCore.ErrorData()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loadedPixmap = QPixmap()
        self.loadedMovie = QMovie()
        self.currentFileDetails = self.FileDetails()
        self.currentRotation = 0

        # Supported formats
        self.supportedFormats = QImageReader.supportedImageFormats()
        self.supportedMimeTypes = QImageReader.supportedMimeTypes()

        # Cache settings
        QPixmapCache.setCacheLimit(512 * 1024)  # 512 MB cache

    def loadFile(self, fileName, isReloading=False):
        """Load an image file and prepare it for display"""
        if not fileName:
            return

        fileInfo = QFileInfo(fileName)
        if not fileInfo.exists():
            self.currentFileDetails.errorData.hasError = True
            self.currentFileDetails.errorData.errorString = "File does not exist"
            return

        # Reset current state
        self.closeImage()

        # Update file details
        self.currentFileDetails.fileInfo = fileInfo
        self.currentFileDetails.isLoadRequested = True
        self.currentFileDetails.timeSinceLoaded.start()

        # Read the image
        readData = self.readFile(fileName, None)
        if readData.errorData.hasError:
            self.currentFileDetails.errorData = readData.errorData
            return

        # Load pixmap or movie
        if self._isAnimatedFormat(fileName):
            self._loadMovie(readData)
        else:
            self.loadPixmap(readData)

        # Update folder info
        self.updateFolderInfo(fileInfo.absolutePath())

        # Emit signals
        self.fileChanged.emit()

    def readFile(self, fileName, targetColorSpace):
        """Read image file and return ReadData"""
        readData = self.ReadData()
        readData.absoluteFilePath = fileName

        try:
            # Check file size
            fileInfo = QFileInfo(fileName)
            readData.fileSize = fileInfo.size()

            # Create image reader
            reader = QImageReader(fileName)

            # Set format if needed
            if not reader.format():
                # Try to determine format from extension
                ext = fileInfo.suffix().lower()
                if ext in ["jpg", "jpeg"]:
                    reader.setFormat(b"jpeg")
                elif ext == "png":
                    reader.setFormat(b"png")
                elif ext == "gif":
                    reader.setFormat(b"gif")
                elif ext == "bmp":
                    reader.setFormat(b"bmp")
                elif ext in ["svg", "svgz"]:
                    reader.setFormat(b"svg")

            # Read image
            image = reader.read()
            if image.isNull():
                readData.errorData.hasError = True
                readData.errorData.errorString = reader.errorString()
                readData.errorData.errorNum = reader.error().value
            else:
                readData.image = image
                readData.imageSize = image.size()

        except Exception as e:
            readData.errorData.hasError = True
            readData.errorData.errorString = str(e)

        return readData

    def loadPixmap(self, readData):
        """Load pixmap from ReadData"""
        if readData.image.isNull():
            return

        # Convert to pixmap
        self.loadedPixmap = QPixmap.fromImage(readData.image)

        # Update file details
        self.currentFileDetails.isPixmapLoaded = True
        self.currentFileDetails.baseImageSize = readData.imageSize
        self.currentFileDetails.loadedPixmapSize = self.loadedPixmap.size()
        self.currentFileDetails.errorData.hasError = False

        # Emit signal
        self.updateLoadedPixmapItem.emit()

    def _loadMovie(self, readData):
        """Load animated image as movie"""
        if not readData.absoluteFilePath:
            return

        self.loadedMovie = QMovie(readData.absoluteFilePath)
        if self.loadedMovie.isValid():
            self.currentFileDetails.isMovieLoaded = True
            self.currentFileDetails.baseImageSize = self.loadedMovie.currentPixmap().size()
            self.currentFileDetails.errorData.hasError = False

            # Connect movie signals
            self.loadedMovie.frameChanged.connect(self._onMovieFrameChanged)
        else:
            self.currentFileDetails.errorData.hasError = True
            self.currentFileDetails.errorData.errorString = "Failed to load animated image"

    def _onMovieFrameChanged(self, frameNumber):
        """Handle movie frame changes"""
        if self.loadedMovie.isValid():
            pixmap = self.loadedMovie.currentPixmap()
            self.loadedPixmap = pixmap
            self.updateLoadedPixmapItem.emit()

    def _isAnimatedFormat(self, fileName):
        """Check if file format supports animation"""
        ext = QFileInfo(fileName).suffix().lower()
        return ext in ["gif", "apng", "webp"]

    def closeImage(self):
        """Close current image and reset state"""
        self.loadedPixmap = QPixmap()
        self.loadedMovie.stop()
        self.loadedMovie = QMovie()
        self.currentFileDetails = self.FileDetails()
        self.currentRotation = 0

    def getCompatibleFiles(self, dirPath):
        """Get list of compatible image files in directory"""
        compatibleFiles = []

        if not dirPath:
            return compatibleFiles

        directory = QDir(dirPath)
        directory.setFilter(QDir.Filter.Files | QDir.Filter.NoDotAndDotDot)
        directory.setSorting(QDir.SortFlag.Name)

        # Get all files
        fileInfoList = directory.entryInfoList()

        for fileInfo in fileInfoList:
            if self._isImageFile(fileInfo.fileName()):
                compatibleFile = self.CompatibleFile(
                    fileInfo.absoluteFilePath(), fileInfo.fileName()
                )
                compatibleFile.lastModified = fileInfo.lastModified().toMSecsSinceEpoch()
                compatibleFile.size = fileInfo.size()
                compatibleFiles.append(compatibleFile)

        return compatibleFiles

    def _isImageFile(self, fileName):
        """Check if file is a supported image format"""
        ext = QFileInfo(fileName).suffix().lower()
        return ext in ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "tiff", "tif"]

    def updateFolderInfo(self, dirPath=""):
        """Update folder information with compatible files"""
        if not dirPath and self.currentFileDetails.fileInfo.exists():
            dirPath = self.currentFileDetails.fileInfo.absolutePath()

        if dirPath:
            self.currentFileDetails.folderFileInfoList = self.getCompatibleFiles(dirPath)
            self.currentFileDetails.updateLoadedIndexInFolder()

    def getLoadedPixmap(self):
        return self.loadedPixmap

    def getLoadedMovie(self):
        return self.loadedMovie

    def getCurrentFileDetails(self):
        return self.currentFileDetails

    def getCurrentRotation(self):
        return self.currentRotation

    def rotateImage(self, rotation):
        """Rotate the current image"""
        if self.loadedPixmap.isNull():
            return

        # Create transform
        transform = QTransform()
        transform.rotate(rotation)

        # Apply rotation
        rotatedPixmap = self.loadedPixmap.transformed(
            transform, Qt.TransformationMode.SmoothTransformation
        )
        if not rotatedPixmap.isNull():
            self.loadedPixmap = rotatedPixmap
            self.currentRotation = (self.currentRotation + rotation) % 360
            self.updateLoadedPixmapItem.emit()

    def flipImage(self, horizontal=False, vertical=False):
        """Flip the current image"""
        if self.loadedPixmap.isNull():
            return

        # Create transform
        transform = QTransform()
        if horizontal:
            transform.scale(-1, 1)
        if vertical:
            transform.scale(1, -1)

        # Apply flip
        flippedPixmap = self.loadedPixmap.transformed(transform)
        if not flippedPixmap.isNull():
            self.loadedPixmap = flippedPixmap
            self.updateLoadedPixmapItem.emit()

    def getExifData(self):
        """Get EXIF data from the current image"""
        exifData = {}

        if not self.currentFileDetails.fileInfo.exists():
            return exifData

        try:
            # Try to read EXIF data using QImageReader
            reader = QImageReader(self.currentFileDetails.fileInfo.absoluteFilePath())

            # Get basic image information
            if reader.canRead():
                image = reader.read()
                if not image.isNull():
                    exifData["Width"] = str(image.width())
                    exifData["Height"] = str(image.height())
                    exifData["Depth"] = str(image.depth())
                    exifData["Format"] = (
                        reader.format().data().decode() if reader.format() else "Unknown"
                    )

            # Get file information
            fileInfo = self.currentFileDetails.fileInfo
            exifData["File Name"] = fileInfo.fileName()
            exifData["File Size"] = self._formatFileSize(fileInfo.size())
            exifData["Modified"] = fileInfo.lastModified().toString()

        except Exception as e:
            exifData["Error"] = str(e)

        return exifData

    def _formatFileSize(self, bytes):
        """Format file size in human readable format"""
        for unit in ["B", "KB", "MB", "GB"]:
            if bytes < 1024.0:
                return ".1f"
            bytes /= 1024.0
        return ".1f"
