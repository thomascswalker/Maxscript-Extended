# Standard imports
import sys, os, PySide2

from PySide2.QtWidgets import QWidget, QDialog, QMainWindow, QVBoxLayout, QMenu
from PySide2.QtCore import Qt, QFile, QSortFilterProxyModel, QSettings
from PySide2.QtUiTools import QUiLoader
from pymxs import runtime as rt

# Need to do this to establish the current directory
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(ROOT_DIR)

# Asset Tracker imports
import constants
reload(constants)
from core import model
reload(model)
from helpers import helpers
reload(helpers)

# Reimport all classes
from constants import *
from core.model import *
from helpers.helpers import *

class AssetTrackerDialog(QMainWindow):
    def __init__(self, parent=QWidget.find(rt.windows.getMAXHWND())):
        QMainWindow.__init__(self, parent)
        
        # Load UI from .ui file
        loader = QUiLoader()
        ui_file_path = os.path.join(ROOT_DIR, 'ui\\mainwindow.ui')
        ui_file = QFile(ui_file_path)
        ui_file.open(QFile.ReadOnly)
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setCentralWidget(self.ui)
        
        # Set events
        self.ui.treeView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.treeView.customContextMenuRequested.connect(self.openMenu)

        # Load settings
        self.settings = QSettings("MaxExtended", "BetterAssetTracker")
        self.readSettings()

    def writeSettings(self):
        self.settings.beginGroup("mainWindow")
        self.settings.setValue("pos", self.MainWindow.pos())
        self.settings.setValue("maximized", self.MainWindow.isMaximized())
        if not self.MainWindow.isMaximized():
            self.settings.setValue("size", self.MainWindow.size())

        self.settings.endGroup()

    def readSettings(self):
        self.settings.beginGroup("mainWindow")
        # No need for toPoint, etc. : PySide converts types
        try:
            self.MainWindow.move(self.settings.value("pos"))
            if self.settings.value("maximized") in 'true':
                self.MainWindow.showMaximized()
            else:
                self.MainWindow.resize(self.settings.value("size"))
        except:
            pass
        self.settings.endGroup()
        
    # https://wiki.python.org/moin/PyQt/Creating%20a%20context%20menu%20for%20a%20tree%20view
    def openMenu(self, position):
        menu = getMenu(self.ui.treeView)
        if (menu):
            menu.exec_(self.ui.treeView.viewport().mapToGlobal(position))

    def closeEvent(self, args):
        print(args)
        self.writeSettings()

def main():
    # Try to close any existing dialogs so there aren't
    # duplicates open.
    global pyAssetTrackerDialog
    try:
        pyAssetTrackerDialog.ui.close()
    except:
        pass

    # Instantiate the main dialog
    pyAssetTrackerDialog = AssetTrackerDialog()
    ui = pyAssetTrackerDialog.ui

    # Create the source model, but map it to a proxy model to enable
    # sorting, filtering, etc.
    sourceModel = model.Model()
    proxyModel = QSortFilterProxyModel()
    proxyModel.setSourceModel(sourceModel)

    # Assign the proxy model to the tree view
    ui.treeView.setModel(proxyModel)

    # Show the UI
    ui.show()
    ui.setWindowTitle("Better Asset Tracker")

if __name__ == '__main__':
    main()
