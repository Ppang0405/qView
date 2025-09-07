import platform

from PyQt6.QtCore import QFileInfo, QObject, QSettings, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QFileIconProvider, QMenu, QMenuBar


class ActionManager(QObject):
    recentsMenuUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.actionLibrary = {}
        self.actionCloneLibrary = {}
        self.menuCloneLibrary = {}
        self.recentsList = []
        self.recentsListMaxLength = 10
        self.openWithMaxLength = 10
        self.isSaveRecentsEnabled = True

        # Initialize settings
        self.settingsUpdated()

        # Initialize action library
        self.initializeActionLibrary()

        # Timer for saving recents
        self.recentsSaveTimer = QTimer(self)
        self.recentsSaveTimer.setSingleShot(True)
        self.recentsSaveTimer.setInterval(500)
        self.recentsSaveTimer.timeout.connect(self.saveRecentsList)

        # Load recents
        self.loadRecentsList()

    def settingsUpdated(self):
        # TODO: Connect to settings manager
        self.isSaveRecentsEnabled = True  # Default value

    def addCloneOfAction(self, parent, key):
        if action := self.getAction(key):
            newAction = QAction(parent)
            newAction.setIcon(action.icon())
            newAction.setData(action.data())
            newAction.setText(action.text())
            newAction.setEnabled(action.isEnabled())
            newAction.setShortcuts(action.shortcuts())
            newAction.setVisible(action.isVisible())

            if key not in self.actionCloneLibrary:
                self.actionCloneLibrary[key] = []
            self.actionCloneLibrary[key].append(newAction)

            parent.addAction(newAction)
            return newAction
        return None

    def getAction(self, key):
        return self.actionLibrary.get(key)

    def getAllInstancesOfAction(self, key):
        actions = self.getAllClonesOfAction(key)
        if mainAction := self.getAction(key):
            actions.append(mainAction)
        return actions

    def getAllClonesOfAction(self, key):
        return self.actionCloneLibrary.get(key, [])

    def buildMenuBar(self, parent):
        menuBar = QMenuBar(parent)

        # File menu
        fileMenu = QMenu("&File", menuBar)
        if platform.system() == "Darwin":  # macOS
            self.addCloneOfAction(fileMenu, "newwindow")
        self.addCloneOfAction(fileMenu, "open")
        self.addCloneOfAction(fileMenu, "openurl")
        fileMenu.addMenu(self.buildRecentsMenu(True, fileMenu))
        self.addCloneOfAction(fileMenu, "reloadfile")
        fileMenu.addSeparator()
        if platform.system() == "Darwin":
            fileMenu.addSeparator()
            self.addCloneOfAction(fileMenu, "closewindow")
            self.addCloneOfAction(fileMenu, "closeallwindows")
        fileMenu.addSeparator()
        fileMenu.addMenu(self.buildOpenWithMenu(fileMenu))
        self.addCloneOfAction(fileMenu, "opencontainingfolder")
        self.addCloneOfAction(fileMenu, "showfileinfo")
        fileMenu.addSeparator()
        self.addCloneOfAction(fileMenu, "quit")
        menuBar.addMenu(fileMenu)

        # Edit menu
        editMenu = QMenu("&Edit", menuBar)
        self.addCloneOfAction(editMenu, "undo")
        editMenu.addSeparator()
        self.addCloneOfAction(editMenu, "copy")
        self.addCloneOfAction(editMenu, "paste")
        self.addCloneOfAction(editMenu, "rename")
        editMenu.addSeparator()
        self.addCloneOfAction(editMenu, "delete")
        self.addCloneOfAction(editMenu, "deletepermanent")
        menuBar.addMenu(editMenu)

        # View menu
        menuBar.addMenu(self.buildViewMenu(False, menuBar))

        # Go menu
        goMenu = QMenu("&Go", menuBar)
        self.addCloneOfAction(goMenu, "firstfile")
        self.addCloneOfAction(goMenu, "previousfile")
        self.addCloneOfAction(goMenu, "nextfile")
        self.addCloneOfAction(goMenu, "lastfile")
        menuBar.addMenu(goMenu)

        # Tools menu
        menuBar.addMenu(self.buildToolsMenu(False, menuBar))

        # Help menu
        menuBar.addMenu(self.buildHelpMenu(False, menuBar))

        return menuBar

    def buildViewMenu(self, addIcon, parent):
        viewMenu = QMenu("&View", parent)
        viewMenu.menuAction().setData("view")
        if addIcon:
            viewMenu.setIcon(QIcon.fromTheme("zoom-fit-best"))

        self.addCloneOfAction(viewMenu, "zoomin")
        self.addCloneOfAction(viewMenu, "zoomout")
        self.addCloneOfAction(viewMenu, "resetzoom")
        self.addCloneOfAction(viewMenu, "originalsize")
        viewMenu.addSeparator()
        self.addCloneOfAction(viewMenu, "rotateright")
        self.addCloneOfAction(viewMenu, "rotateleft")
        viewMenu.addSeparator()
        self.addCloneOfAction(viewMenu, "mirror")
        self.addCloneOfAction(viewMenu, "flip")
        viewMenu.addSeparator()
        self.addCloneOfAction(viewMenu, "fullscreen")

        if "view" not in self.menuCloneLibrary:
            self.menuCloneLibrary["view"] = []
        self.menuCloneLibrary["view"].append(viewMenu)

        return viewMenu

    def buildToolsMenu(self, addIcon, parent):
        toolsMenu = QMenu("&Tools", parent)
        toolsMenu.menuAction().setData("tools")
        if addIcon:
            toolsMenu.setIcon(QIcon.fromTheme("configure"))

        self.addCloneOfAction(toolsMenu, "saveframeas")
        self.addCloneOfAction(toolsMenu, "pause")
        self.addCloneOfAction(toolsMenu, "nextframe")
        toolsMenu.addSeparator()
        self.addCloneOfAction(toolsMenu, "decreasespeed")
        self.addCloneOfAction(toolsMenu, "resetspeed")
        self.addCloneOfAction(toolsMenu, "increasespeed")
        toolsMenu.addSeparator()
        self.addCloneOfAction(toolsMenu, "slideshow")
        self.addCloneOfAction(toolsMenu, "options")

        if "tools" not in self.menuCloneLibrary:
            self.menuCloneLibrary["tools"] = []
        self.menuCloneLibrary["tools"].append(toolsMenu)

        return toolsMenu

    def buildHelpMenu(self, addIcon, parent):
        helpMenu = QMenu("&Help", parent)
        helpMenu.menuAction().setData("help")
        if addIcon:
            helpMenu.setIcon(QIcon.fromTheme("help-about"))

        self.addCloneOfAction(helpMenu, "about")
        self.addCloneOfAction(helpMenu, "welcome")

        if "help" not in self.menuCloneLibrary:
            self.menuCloneLibrary["help"] = []
        self.menuCloneLibrary["help"].append(helpMenu)

        return helpMenu

    def buildRecentsMenu(self, includeClearAction, parent):
        recentsMenu = QMenu("Open &Recent", parent)
        recentsMenu.menuAction().setData("recents")
        recentsMenu.setIcon(QIcon.fromTheme("document-open-recent"))

        # Create placeholder actions
        for i in range(self.recentsListMaxLength):
            action = QAction("Empty", recentsMenu)
            action.setVisible(False)
            action.setIconVisibleInMenu(True)
            action.setData(f"recent{i}")

            recentsMenu.addAction(action)
            if f"recent{i}" not in self.actionCloneLibrary:
                self.actionCloneLibrary[f"recent{i}"] = []
            self.actionCloneLibrary[f"recent{i}"].append(action)

        if includeClearAction:
            recentsMenu.addSeparator()
            self.addCloneOfAction(recentsMenu, "clearrecents")

        if "recents" not in self.menuCloneLibrary:
            self.menuCloneLibrary["recents"] = []
        self.menuCloneLibrary["recents"].append(recentsMenu)

        self.updateRecentsMenu()
        return recentsMenu

    def buildOpenWithMenu(self, parent):
        openWithMenu = QMenu("Open With", parent)
        openWithMenu.menuAction().setData("openwith")
        openWithMenu.setIcon(QIcon.fromTheme("system-run"))
        openWithMenu.setDisabled(True)

        # Create placeholder actions
        for i in range(self.openWithMaxLength):
            action = QAction("Empty", openWithMenu)
            action.setVisible(False)
            action.setIconVisibleInMenu(True)
            action.setData([f"openwith{i}", ""])

            openWithMenu.addAction(action)
            if f"openwith{i}" not in self.actionCloneLibrary:
                self.actionCloneLibrary[f"openwith{i}"] = []
            self.actionCloneLibrary[f"openwith{i}"].append(action)

        openWithMenu.addSeparator()
        self.addCloneOfAction(openWithMenu, "openwithother")

        if "openwith" not in self.menuCloneLibrary:
            self.menuCloneLibrary["openwith"] = []
        self.menuCloneLibrary["openwith"].append(openWithMenu)

        return openWithMenu

    def loadRecentsList(self):
        if self.recentsSaveTimer.isActive():
            return

        settings = QSettings()
        settings.beginGroup("recents")
        # TODO: Load recents from settings
        self.auditRecentsList()

    def saveRecentsList(self):
        self.auditRecentsList()
        settings = QSettings()
        settings.beginGroup("recents")
        # TODO: Save recents to settings

    def addFileToRecentsList(self, fileInfo):
        self.recentsList.insert(
            0, {"fileName": fileInfo.fileName(), "filePath": fileInfo.filePath()}
        )
        self.auditRecentsList()
        self.recentsSaveTimer.start()

    def auditRecentsList(self):
        if not self.isSaveRecentsEnabled:
            self.recentsList.clear()

        # Remove non-existent files and duplicates
        i = 0
        while i < len(self.recentsList):
            recent = self.recentsList[i]
            filePath = recent["filePath"]

            if not QFileInfo.exists(filePath):
                self.recentsList.pop(i)
                continue

            # Check for duplicates
            duplicateFound = False
            for j in range(len(self.recentsList)):
                if i != j and self.recentsList[j]["filePath"] == filePath:
                    self.recentsList.pop(j)
                    if j < i:
                        i -= 1
                    duplicateFound = True
                    break

            if not duplicateFound:
                i += 1

        # Trim to max length
        while len(self.recentsList) > self.recentsListMaxLength:
            self.recentsList.pop()

        self.updateRecentsMenu()

    def clearRecentsList(self):
        self.recentsList.clear()
        self.saveRecentsList()

    def updateRecentsMenu(self):
        for i in range(self.recentsListMaxLength):
            if f"recent{i}" in self.actionCloneLibrary:
                for action in self.actionCloneLibrary[f"recent{i}"]:
                    if i < len(self.recentsList):
                        recent = self.recentsList[i]
                        action.setVisible(True)
                        action.setText(recent["fileName"])

                        # Set icon based on platform
                        if platform.system() in ["Linux", "FreeBSD", "NetBSD", "OpenBSD"]:
                            # Use theme icons for Linux
                            action.setIcon(QIcon.fromTheme("text-x-generic"))
                        else:
                            # Use file icon provider for macOS/Windows
                            fileInfo = QFileInfo(recent["filePath"])
                            provider = QFileIconProvider()
                            icon = provider.icon(fileInfo)
                            action.setIcon(icon)

                        action.setIconVisibleInMenu(True)
                    else:
                        action.setVisible(False)

        self.recentsMenuUpdated.emit()

    def initializeActionLibrary(self):
        # File actions
        quitAction = QAction(QIcon.fromTheme("application-exit"), "&Quit")
        if platform.system() == "Windows":
            quitAction.setText("Exit")
        self.actionLibrary["quit"] = quitAction

        newWindowAction = QAction(QIcon.fromTheme("window-new"), "New Window")
        self.actionLibrary["newwindow"] = newWindowAction

        openAction = QAction(QIcon.fromTheme("document-open"), "&Open...")
        self.actionLibrary["open"] = openAction

        openUrlAction = QAction(QIcon.fromTheme("document-open-remote"), "Open &URL...")
        self.actionLibrary["openurl"] = openUrlAction

        reloadFileAction = QAction(QIcon.fromTheme("view-refresh"), "Re&load File")
        reloadFileAction.setData(["disable"])
        self.actionLibrary["reloadfile"] = reloadFileAction

        closeWindowAction = QAction(QIcon.fromTheme("window-close"), "Close Window")
        self.actionLibrary["closewindow"] = closeWindowAction

        closeAllWindowsAction = QAction(QIcon.fromTheme("window-close"), "Close All")
        self.actionLibrary["closeallwindows"] = closeAllWindowsAction

        openContainingFolderAction = QAction(
            QIcon.fromTheme("document-open"), "Open Containing &Folder"
        )
        if platform.system() == "Windows":
            openContainingFolderAction.setText("Show in E&xplorer")
        elif platform.system() == "Darwin":
            openContainingFolderAction.setText("Show in &Finder")
        openContainingFolderAction.setData(["disable"])
        self.actionLibrary["opencontainingfolder"] = openContainingFolderAction

        showFileInfoAction = QAction(QIcon.fromTheme("document-properties"), "Show File &Info")
        showFileInfoAction.setData(["disable"])
        self.actionLibrary["showfileinfo"] = showFileInfoAction

        deleteAction = QAction(QIcon.fromTheme("edit-delete"), "&Move to Trash")
        if platform.system() == "Windows":
            deleteAction.setText("&Delete")
        deleteAction.setData(["disable"])
        self.actionLibrary["delete"] = deleteAction

        deletePermanentAction = QAction(QIcon.fromTheme("edit-delete"), "Delete Permanently")
        deletePermanentAction.setData(["disable"])
        self.actionLibrary["deletepermanent"] = deletePermanentAction

        undoAction = QAction(QIcon.fromTheme("edit-undo"), "&Restore from Trash")
        if platform.system() == "Windows":
            undoAction.setText("&Undo Delete")
        undoAction.setData(["undodisable"])
        self.actionLibrary["undo"] = undoAction

        # Edit actions
        copyAction = QAction(QIcon.fromTheme("edit-copy"), "&Copy")
        copyAction.setData(["disable"])
        self.actionLibrary["copy"] = copyAction

        pasteAction = QAction(QIcon.fromTheme("edit-paste"), "&Paste")
        self.actionLibrary["paste"] = pasteAction

        renameAction = QAction(QIcon.fromTheme("edit-rename"), "R&ename...")
        renameAction.setData(["disable"])
        self.actionLibrary["rename"] = renameAction

        # View actions
        zoomInAction = QAction(QIcon.fromTheme("zoom-in"), "Zoom &In")
        zoomInAction.setData(["disable"])
        self.actionLibrary["zoomin"] = zoomInAction

        zoomOutAction = QAction(QIcon.fromTheme("zoom-out"), "Zoom &Out")
        zoomOutAction.setData(["disable"])
        self.actionLibrary["zoomout"] = zoomOutAction

        resetZoomAction = QAction(QIcon.fromTheme("zoom-fit-best"), "Reset &Zoom")
        resetZoomAction.setData(["disable"])
        self.actionLibrary["resetzoom"] = resetZoomAction

        originalSizeAction = QAction(QIcon.fromTheme("zoom-original"), "Ori&ginal Size")
        originalSizeAction.setData(["disable"])
        self.actionLibrary["originalsize"] = originalSizeAction

        rotateRightAction = QAction(QIcon.fromTheme("object-rotate-right"), "Rotate &Right")
        rotateRightAction.setData(["disable"])
        self.actionLibrary["rotateright"] = rotateRightAction

        rotateLeftAction = QAction(QIcon.fromTheme("object-rotate-left"), "Rotate &Left")
        rotateLeftAction.setData(["disable"])
        self.actionLibrary["rotateleft"] = rotateLeftAction

        mirrorAction = QAction(QIcon.fromTheme("object-flip-horizontal"), "&Mirror")
        mirrorAction.setData(["disable"])
        self.actionLibrary["mirror"] = mirrorAction

        flipAction = QAction(QIcon.fromTheme("object-flip-vertical"), "&Flip")
        flipAction.setData(["disable"])
        self.actionLibrary["flip"] = flipAction

        fullScreenAction = QAction(QIcon.fromTheme("view-fullscreen"), "Enter F&ull Screen")
        self.actionLibrary["fullscreen"] = fullScreenAction

        # Navigation actions
        firstFileAction = QAction(QIcon.fromTheme("go-first"), "&First File")
        firstFileAction.setData(["folderdisable"])
        self.actionLibrary["firstfile"] = firstFileAction

        previousFileAction = QAction(QIcon.fromTheme("go-previous"), "Previous Fi&le")
        previousFileAction.setData(["folderdisable"])
        self.actionLibrary["previousfile"] = previousFileAction

        nextFileAction = QAction(QIcon.fromTheme("go-next"), "&Next File")
        nextFileAction.setData(["folderdisable"])
        self.actionLibrary["nextfile"] = nextFileAction

        lastFileAction = QAction(QIcon.fromTheme("go-last"), "Las&t File")
        lastFileAction.setData(["folderdisable"])
        self.actionLibrary["lastfile"] = lastFileAction

        # Animation actions
        saveFrameAsAction = QAction(QIcon.fromTheme("document-save-as"), "Save Frame &As...")
        saveFrameAsAction.setData(["gifdisable"])
        self.actionLibrary["saveframeas"] = saveFrameAsAction

        pauseAction = QAction(QIcon.fromTheme("media-playback-pause"), "Pa&use")
        pauseAction.setData(["gifdisable"])
        self.actionLibrary["pause"] = pauseAction

        nextFrameAction = QAction(QIcon.fromTheme("media-skip-forward"), "&Next Frame")
        nextFrameAction.setData(["gifdisable"])
        self.actionLibrary["nextframe"] = nextFrameAction

        decreaseSpeedAction = QAction(QIcon.fromTheme("media-seek-backward"), "&Decrease Speed")
        decreaseSpeedAction.setData(["gifdisable"])
        self.actionLibrary["decreasespeed"] = decreaseSpeedAction

        resetSpeedAction = QAction(QIcon.fromTheme("media-playback-start"), "&Reset Speed")
        resetSpeedAction.setData(["gifdisable"])
        self.actionLibrary["resetspeed"] = resetSpeedAction

        increaseSpeedAction = QAction(QIcon.fromTheme("media-skip-forward"), "&Increase Speed")
        increaseSpeedAction.setData(["gifdisable"])
        self.actionLibrary["increasespeed"] = increaseSpeedAction

        slideshowAction = QAction(QIcon.fromTheme("media-playback-start"), "Start S&lideshow")
        slideshowAction.setData(["disable"])
        self.actionLibrary["slideshow"] = slideshowAction

        # Application actions
        optionsAction = QAction(QIcon.fromTheme("configure"), "&Settings")
        if platform.system() == "Darwin":
            optionsAction.setText("Setting&s...")
        self.actionLibrary["options"] = optionsAction

        aboutAction = QAction(QIcon.fromTheme("help-about"), "&About")
        if platform.system() == "Darwin":
            aboutAction.setText("&About qView")
        self.actionLibrary["about"] = aboutAction

        welcomeAction = QAction(QIcon.fromTheme("help-faq"), "&Welcome")
        self.actionLibrary["welcome"] = welcomeAction

        clearRecentsAction = QAction(QIcon.fromTheme("edit-delete"), "Clear &Menu")
        self.actionLibrary["clearrecents"] = clearRecentsAction

        openWithOtherAction = QAction(QIcon.fromTheme("system-run"), "Other Application...")
        if platform.system() == "Windows":
            openWithOtherAction.setText("Choose another app")
        elif platform.system() == "Darwin":
            openWithOtherAction.setText("Other...")
        self.actionLibrary["openwithother"] = openWithOtherAction

        # Set data values and disable actions
        for key, action in self.actionLibrary.items():
            data = action.data()
            if isinstance(data, list):
                data.insert(0, key)
            else:
                data = [key, data] if data else [key]
            action.setData(data)

            if data and len(data) > 1 and "disable" in str(data[-1]):
                action.setEnabled(False)
