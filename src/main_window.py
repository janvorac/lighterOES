import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QFileDialog,
    QMainWindow
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import loadUiType

import read_data 


current_dir = os.path.dirname(os.path.abspath(__file__))
Form, Base = loadUiType(os.path.join(current_dir, "UI_structure.ui"))

class SpecWindow(Base, Form):

    def __init__(self):
        super().__init__()
        # self.title = "SpecApp"
        # self.layout = QVBoxLayout()
        # self.setWindowTitle(self.title)
        # # self.menu_actions()

        self.setupUi(self)
        self.loadButton.clicked.connect(lambda: self.open_file_dialog())

    def open_file_dialog(self):
        dialog = QFileDialog()
        filename = dialog.getOpenFileName()
        if filename:
            self.title = f"SpecApp - {filename[0]}"
            self.data = read_data.read_data(filename[0])
            print(self.data)
        else:
            self.title = "SpecApp"
        self.setWindowTitle(self.title)

    # def menu_actions(self):
    #     self.menuBar = self.menuBar()
    #     self.fileMenu = self.menuBar.addMenu("File")
    #     self.actionOpen = self.fileMenu.addAction("Open")
    #     self.actionOpen.triggered.connect(self.open_file_dialog)
    #     self.actionQuit = self.fileMenu.addAction("Exit")
    #     self.actionQuit.triggered.connect(sys.exit)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget=SpecWindow()
    widget.show()
    sys.exit(app.exec_())

