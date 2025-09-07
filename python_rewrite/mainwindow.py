import platform

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QMainWindow,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtWidgets import QVBoxLayout as QVBoxLayout2
from qvgraphicsview import QVGraphicsView


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("qView")

        # macOS-specific settings
        if platform.system() == "Darwin":
            self.setUnifiedTitleAndToolBarOnMac(True)
            # Set up proper fullscreen behavior for macOS
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowFullscreenButtonHint)

        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        # Status bar
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Graphics view
        self.graphicsView = QVGraphicsView(self)
        layout.addWidget(self.graphicsView)

        self.resize(800, 600)

        # Defer menu setup until after app is created
        self.app = None

    def setupMenus(self, app):
        self.app = app
        if self.app and hasattr(self.app, "actionManager"):
            # Set up menu bar
            self.setMenuBar(self.app.actionManager.buildMenuBar(self))

            # Connect actions to methods
            self.connectActions()

    def connectActions(self):
        # Connect common actions
        if self.app and hasattr(self.app, "actionManager"):
            action_manager = self.app.actionManager  # type: ignore
            if action := action_manager.getAction("quit"):
                action.triggered.connect(self.app.quit)

            if action := action_manager.getAction("newwindow"):
                action.triggered.connect(self.app.newWindow)

            if action := action_manager.getAction("open"):
                action.triggered.connect(self.openFileDialog)

            if action := action_manager.getAction("fullscreen"):
                action.triggered.connect(self.toggleFullScreen)

            if action := action_manager.getAction("zoomin"):
                action.triggered.connect(self.graphicsView.zoomIn)

            if action := action_manager.getAction("zoomout"):
                action.triggered.connect(self.graphicsView.zoomOut)

            if action := action_manager.getAction("resetzoom"):
                action.triggered.connect(self.graphicsView.resetScale)

            if action := action_manager.getAction("originalsize"):
                action.triggered.connect(self.graphicsView.originalSize)

            if action := action_manager.getAction("rotateright"):
                action.triggered.connect(lambda: self.graphicsView.imageCore.rotateImage(90))

            if action := action_manager.getAction("rotateleft"):
                action.triggered.connect(lambda: self.graphicsView.imageCore.rotateImage(-90))

            if action := action_manager.getAction("mirror"):
                action.triggered.connect(
                    lambda: self.graphicsView.imageCore.flipImage(horizontal=True)
                )

            if action := action_manager.getAction("flip"):
                action.triggered.connect(
                    lambda: self.graphicsView.imageCore.flipImage(vertical=True)
                )

            if action := action_manager.getAction("firstfile"):
                action.triggered.connect(self.graphicsView.goToFirstFile)

            if action := action_manager.getAction("previousfile"):
                action.triggered.connect(self.graphicsView.goToPreviousFile)

            if action := action_manager.getAction("nextfile"):
                action.triggered.connect(self.graphicsView.goToNextFile)

            if action := action_manager.getAction("showfileinfo"):
                action.triggered.connect(self.showFileInfo)

            if action := action_manager.getAction("slideshow"):
                action.triggered.connect(self._toggleSlideshow)

        # Add more action connections as needed

    def openFileDialog(self):
        """Open file dialog to select an image file"""
        # Get supported image formats from image core
        supportedFormats = []
        if hasattr(self.graphicsView, "imageCore") and hasattr(
            self.graphicsView.imageCore, "supportedFormats"
        ):
            for fmt in self.graphicsView.imageCore.supportedFormats:
                supportedFormats.append(f"*.{fmt.data().decode()}")

        # Create filter string
        filterString = "All Images ("
        filterString += " ".join(supportedFormats)
        filterString += ");;"

        # Add individual format filters
        for fmt in supportedFormats:
            ext = fmt.replace("*.", "").upper()
            filterString += f"{ext} Files ({fmt});;"

        filterString += "All Files (*)"

        # Open file dialog
        fileName, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",  # Start in current directory
            filterString,
        )

        if fileName:
            self.openFile(fileName)

            # Add to recent files if action manager exists
            if self.app and hasattr(self.app, "actionManager"):
                from PyQt6.QtCore import QFileInfo

                fileInfo = QFileInfo(fileName)
                self.app.actionManager.addFileToRecentsList(fileInfo)

    def toggleFullScreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def openFile(self, fileName):
        self.graphicsView.loadFile(fileName)
        self.setWindowTitle(f"qView - {fileName}")

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_O and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+O: Open file
            self.openFileDialog()
            event.accept()
        elif (
            event.key() == Qt.Key.Key_Q and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            # Ctrl+Q: Quit
            if self.app:
                self.app.quit()
            event.accept()
        elif event.key() == Qt.Key.Key_F11 or (
            event.key() == Qt.Key.Key_F and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            # F11 or Ctrl+F: Toggle fullscreen
            self.toggleFullScreen()
            event.accept()
        elif event.key() == Qt.Key.Key_Plus or event.key() == Qt.Key.Key_Equal:
            # +: Zoom in
            self.graphicsView.zoomIn()
            event.accept()
        elif event.key() == Qt.Key.Key_Minus:
            # -: Zoom out
            self.graphicsView.zoomOut()
            event.accept()
        elif event.key() == Qt.Key.Key_0:
            # 0: Reset zoom
            self.graphicsView.resetScale()
            event.accept()
        elif event.key() == Qt.Key.Key_1:
            # 1: Original size
            self.graphicsView.originalSize()
            event.accept()
        elif event.key() == Qt.Key.Key_R:
            # R: Rotate right
            self.graphicsView.imageCore.rotateImage(90)
            event.accept()
        elif event.key() == Qt.Key.Key_L:
            # L: Rotate left
            self.graphicsView.imageCore.rotateImage(-90)
            event.accept()
        elif event.key() == Qt.Key.Key_Left:
            # Left arrow: Previous file
            self.graphicsView.goToPreviousFile()
            event.accept()
        elif event.key() == Qt.Key.Key_Right:
            # Right arrow: Next file
            self.graphicsView.goToNextFile()
            event.accept()
        elif event.key() == Qt.Key.Key_Home:
            # Home: First file
            self.graphicsView.goToFirstFile()
            event.accept()
        elif event.key() == Qt.Key.Key_End:
            # End: Last file
            self.graphicsView.goToLastFile()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _toggleSlideshow(self):
        """Toggle slideshow on/off"""
        if self.graphicsView.isSlideshowRunning:
            self.graphicsView.stopSlideshow()
        else:
            self.graphicsView.startSlideshow()

    def showFileInfo(self):
        """Show file information dialog"""
        exifData = self.graphicsView.imageCore.getExifData()

        dialog = QDialog(self)
        dialog.setWindowTitle("File Information")
        dialog.setModal(True)

        layout = QVBoxLayout2(dialog)

        textEdit = QTextEdit(dialog)
        textEdit.setReadOnly(True)

        # Format EXIF data
        infoText = ""
        for key, value in exifData.items():
            infoText += f"{key}: {value}\n"

        textEdit.setPlainText(infoText)
        layout.addWidget(textEdit)

        # Add OK button
        buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok, dialog)
        buttonBox.accepted.connect(dialog.accept)
        layout.addWidget(buttonBox)

        dialog.resize(400, 300)
        dialog.exec()

    # TODO: Add other methods from C++ MainWindow
