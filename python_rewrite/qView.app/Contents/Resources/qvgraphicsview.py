from PyQt6.QtCore import QPoint, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView
from qvimagecore import QVImageCore


class QVGraphicsView(QGraphicsView):
    cancelSlideshow = pyqtSignal()
    fileChanged = pyqtSignal()
    updatedLoadedPixmapItem = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.graphicsScene = QGraphicsScene(self)
        self.setScene(self.graphicsScene)
        self.imageCore = QVImageCore(self)
        self.loadedPixmapItem = QGraphicsPixmapItem()
        self.graphicsScene.addItem(self.loadedPixmapItem)

        # Initialize variables
        self.currentScale = 1.0
        self.isOriginalSize = False
        self.minScale = 0.1
        self.maxScale = 10.0

        # Slideshow variables
        self.slideshowTimer = QTimer(self)
        self.slideshowTimer.timeout.connect(self._nextSlide)
        self.slideshowInterval = 3000  # 3 seconds default
        self.isSlideshowRunning = False

        # Set up view properties
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        # Enable drag and drop
        self.setAcceptDrops(True)

        # Connect signals
        self.imageCore.animatedFrameChanged.connect(self.animatedFrameChanged)
        self.imageCore.updateLoadedPixmapItem.connect(self.updateLoadedPixmapItem)
        self.imageCore.fileChanged.connect(self.fileChanged)

    def loadFile(self, fileName):
        self.imageCore.loadFile(fileName)

    def reloadFile(self):
        # TODO: Implement
        pass

    def zoomIn(self, pos=QPoint(-1, -1)):
        self.zoom(1.2, pos)

    def zoomOut(self, pos=QPoint(-1, -1)):
        self.zoom(1 / 1.2, pos)

    def zoom(self, scaleFactor, pos=QPoint(-1, -1)):
        """Zoom the view by the given scale factor"""
        viewport = self.viewport()
        if not viewport:
            return

        if pos.x() == -1 and pos.y() == -1:
            # Zoom at center if no position specified
            pos = viewport.rect().center()

        # Calculate new scale
        newScale = self.currentScale * scaleFactor
        newScale = max(self.minScale, min(self.maxScale, newScale))

        if abs(newScale - self.currentScale) < 0.001:
            return  # No significant change

        # Apply zoom
        self.scale(newScale / self.currentScale, newScale / self.currentScale)
        self.currentScale = newScale
        self.isOriginalSize = abs(self.currentScale - 1.0) < 0.001

    def resetScale(self):
        """Reset zoom to fit the image in the view"""
        if self.loadedPixmapItem.pixmap().isNull():
            return

        viewport = self.viewport()
        if not viewport:
            return

        # Calculate scale to fit image in view
        viewRect = viewport.rect()
        pixmapRect = self.loadedPixmapItem.boundingRect()

        scaleX = viewRect.width() / pixmapRect.width()
        scaleY = viewRect.height() / pixmapRect.height()
        fitScale = min(scaleX, scaleY)

        # Reset to 1.0 first, then apply fit scale
        self.scale(1.0 / self.currentScale, 1.0 / self.currentScale)
        self.scale(fitScale, fitScale)
        self.currentScale = fitScale
        self.isOriginalSize = abs(self.currentScale - 1.0) < 0.001

    def originalSize(self):
        """Show image at its original size"""
        if self.loadedPixmapItem.pixmap().isNull():
            return

        # Reset to original size
        self.scale(1.0 / self.currentScale, 1.0 / self.currentScale)
        self.currentScale = 1.0
        self.isOriginalSize = True

    def getCurrentFileDetails(self):
        return self.imageCore.getCurrentFileDetails()

    def getLoadedPixmap(self):
        return self.imageCore.getLoadedPixmap()

    def getLoadedMovie(self):
        return self.imageCore.getLoadedMovie()

    def animatedFrameChanged(self, rect):
        # TODO: Handle animated frame change
        pass

    def updateLoadedPixmapItem(self):
        pixmap = self.imageCore.getLoadedPixmap()
        self.loadedPixmapItem.setPixmap(pixmap)
        self.updatedLoadedPixmapItem.emit()

        # Reset view to fit the new image
        if not pixmap.isNull():
            self.resetScale()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming"""
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Zoom with Ctrl+wheel
            zoomFactor = 1.2 if event.angleDelta().y() > 0 else 1.0 / 1.2
            self.zoom(zoomFactor, event.position().toPoint())
            event.accept()
        else:
            # Default scroll behavior
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            # Check if any of the URLs are image files
            for url in event.mimeData().urls():
                filePath = url.toLocalFile()
                if self._isImageFile(filePath):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        """Handle drop events"""
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                filePath = url.toLocalFile()
                if self._isImageFile(filePath):
                    self.loadFile(filePath)
                    # Add to recent files if parent window has action manager
                    if hasattr(self.parent(), "app") and hasattr(
                        self.parent().app, "actionManager"
                    ):
                        from PyQt6.QtCore import QFileInfo

                        fileInfo = QFileInfo(filePath)
                        self.parent().app.actionManager.addFileToRecentsList(fileInfo)
                    event.acceptProposedAction()
                    return
        event.ignore()

    def _isImageFile(self, filePath):
        """Check if file is a supported image format"""
        from PyQt6.QtCore import QFileInfo

        ext = QFileInfo(filePath).suffix().lower()
        return ext in ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "tiff", "tif"]

    def goToFirstFile(self):
        """Go to the first file in the current folder"""
        fileDetails = self.getCurrentFileDetails()
        if fileDetails.folderFileInfoList:
            firstFile = fileDetails.folderFileInfoList[0]
            self.loadFile(firstFile.absoluteFilePath)

    def goToPreviousFile(self):
        """Go to the previous file in the current folder"""
        fileDetails = self.getCurrentFileDetails()
        if fileDetails.folderFileInfoList and fileDetails.loadedIndexInFolder > 0:
            prevFile = fileDetails.folderFileInfoList[fileDetails.loadedIndexInFolder - 1]
            self.loadFile(prevFile.absoluteFilePath)

    def goToNextFile(self):
        """Go to the next file in the current folder"""
        fileDetails = self.getCurrentFileDetails()
        if (
            fileDetails.folderFileInfoList
            and fileDetails.loadedIndexInFolder < len(fileDetails.folderFileInfoList) - 1
        ):
            nextFile = fileDetails.folderFileInfoList[fileDetails.loadedIndexInFolder + 1]
            self.loadFile(nextFile.absoluteFilePath)

    def goToLastFile(self):
        """Go to the last file in the current folder"""
        fileDetails = self.getCurrentFileDetails()
        if fileDetails.folderFileInfoList:
            lastFile = fileDetails.folderFileInfoList[-1]
            self.loadFile(lastFile.absoluteFilePath)

    def startSlideshow(self):
        """Start slideshow"""
        if not self.isSlideshowRunning:
            self.isSlideshowRunning = True
            self.slideshowTimer.start(self.slideshowInterval)

    def stopSlideshow(self):
        """Stop slideshow"""
        if self.isSlideshowRunning:
            self.isSlideshowRunning = False
            self.slideshowTimer.stop()
            self.cancelSlideshow.emit()

    def setSlideshowInterval(self, interval):
        """Set slideshow interval in milliseconds"""
        self.slideshowInterval = interval
        if self.isSlideshowRunning:
            self.slideshowTimer.setInterval(interval)

    def _nextSlide(self):
        """Advance to next slide in slideshow"""
        fileDetails = self.getCurrentFileDetails()
        if fileDetails.folderFileInfoList:
            if fileDetails.loadedIndexInFolder < len(fileDetails.folderFileInfoList) - 1:
                self.goToNextFile()
            else:
                # Loop back to first file
                self.goToFirstFile()
        else:
            # No more files, stop slideshow
            self.stopSlideshow()
