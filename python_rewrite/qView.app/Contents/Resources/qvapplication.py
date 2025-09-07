from actionmanager import ActionManager
from PyQt6.QtWidgets import QApplication, QMenuBar
from settingsmanager import SettingsManager


class QVApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.lastActiveWindows = []
        self.menuBar = QMenuBar()
        self.nameFilterList = []
        self.fileExtensionList = []
        self.mimeTypeNameList = []

        # Initialize managers
        self.settingsManager = SettingsManager(self)
        self.actionManager = ActionManager(self)

        # Connect settings signal
        self.settingsManager.settingsUpdated.connect(self.actionManager.settingsUpdated)

    @staticmethod
    def openFile(window, file_path, resize=True):
        # TODO: Implement opening file
        pass

    @staticmethod
    def newWindow():
        # TODO: Create and return MainWindow instance
        from mainwindow import MainWindow

        window = MainWindow()
        window.setupMenus(QVApplication.instance())
        window.show()
        return window

    def getMainWindow(self, shouldBeEmpty):
        # TODO: Implement
        pass

    # TODO: Add other methods as needed
