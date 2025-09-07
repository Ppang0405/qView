from PyQt6.QtCore import QObject, pyqtSignal


class SettingsManager(QObject):
    settingsUpdated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settingsLibrary = {}

        # Initialize default settings
        self.initializeSettingsLibrary()
        self.loadSettings()

    def initializeSettingsLibrary(self):
        # Basic settings - can be expanded
        self.settingsLibrary = {
            "saverecents": {"defaultValue": True, "value": True},
            "bgcolor": {"defaultValue": "#000000", "value": "#000000"},
            "scalefactor": {"defaultValue": 1.0, "value": 1.0},
            # Add more settings as needed
        }

    def loadSettings(self):
        # TODO: Load from QSettings
        pass

    def getSetting(self, key, defaults=False):
        if key in self.settingsLibrary:
            if defaults:
                return self.settingsLibrary[key]["defaultValue"]
            return self.settingsLibrary[key]["value"]
        return None

    def getBoolean(self, key, defaults=False):
        value = self.getSetting(key, defaults)
        return bool(value) if value is not None else False

    def getInteger(self, key, defaults=False):
        value = self.getSetting(key, defaults)
        return int(value) if value is not None else 0

    def getDouble(self, key, defaults=False):
        value = self.getSetting(key, defaults)
        return float(value) if value is not None else 0.0

    def getString(self, key, defaults=False):
        value = self.getSetting(key, defaults)
        return str(value) if value is not None else ""

    def isDefault(self, key):
        if key in self.settingsLibrary:
            return self.settingsLibrary[key]["value"] == self.settingsLibrary[key]["defaultValue"]
        return True
