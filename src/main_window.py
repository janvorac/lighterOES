import sys
from ui_mainwindow import Ui_Widget
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QWidget
)
from PySide6.QtCore import QFile
from PySide6.QtUiTools import loadUiType, QUiLoader

import read_data


class SpecWindow(QMainWindow):

    # def __init__(self):
    #     super().__init__()
    #
    #     # # self.menu_actions()
    #     self.setupUi(self)
    #     self.setWindowTitle('LighterOES')
    #     self.loadButton.clicked.connect(lambda: self.open_file_dialog())
    #     self.spectraButton.clicked.connect(lambda: self.save_spectra())
    #     self.paramsButton.clicked.connect(lambda: self.save_params())
    #     self.fitButton.clicked.connect(lambda: self.fit())
    #
    # def open_file_dialog(self): # needs to be adjusted in the future
    #     dialog = QFileDialog()
    #     filename = dialog.getOpenFileName()
    #     if filename:
    #         self.title = f"LighterOES - {filename[0]}"
    #         self.data = read_data.read_data(filename[0])
    #         print(self.data)
    #     else:
    #         self.title = "LighterOES"
    #     self.setWindowTitle(self.title)
    #
    # def save_spectra(self):
    #     print("Clicked Save params button!!!")
    #
    # def save_params(self):
    #     print("Clicked Save spectra button!!!")
    #
    # def fit(self):
    #     print("Clicked Fitting button!!!")

    # def menu_actions(self): #this is initial funtion from honza, i will probably use it as saving function
    #     self.menuBar = self.menuBar()
    #     self.fileMenu = self.menuBar.addMenu("File")
    #     self.actionOpen = self.fileMenu.addAction("Open")
    #     self.actionOpen.triggered.connect(self.open_file_dialog)
    #     self.actionQuit = self.fileMenu.addAction("Exit")
    #     self.actionQuit.triggered.connect(sys.exit)

    def __init__(self):
        super().__init__()

        self.ui = Ui_Widget()
        self.ui.setupUi(self)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SpecWindow()
    win.show()
    app.exec()

