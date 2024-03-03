import sys
import os
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow
)
from PySide6.QtUiTools import loadUiType

import read_data 


current_dir = os.path.dirname(os.path.abspath(__file__))
Form, Base = loadUiType(os.path.join(current_dir, "UI_structure.ui"))

class SpecWindow(Base, Form):

    def __init__(self):
        super().__init__()

        # # self.menu_actions()
        self.setupUi(self)
        self.setWindowTitle('LighterOES')
        self.loadButton.clicked.connect(lambda: self.open_file_dialog())
        self.spectraButton.clicked.connect(lambda: self.save_spectra())
        self.paramsButton.clicked.connect(lambda: self.save_params())
        self.fitButton.clicked.connect(lambda: self.fit())

    def open_file_dialog(self): # needs to be adjusted in the future
        dialog = QFileDialog()
        filename = dialog.getOpenFileName()
        if filename:
            self.title = f"SpecApp - {filename[0]}"
            self.data = read_data.read_data(filename[0])
            print(self.data)
        else:
            self.title = "SpecApp"
        self.setWindowTitle(self.title)

    def save_spectra(self):
        print("Clicked Save params button!!!")

    def save_params(self):
        print("Clicked Save spectra button!!!")

    def fit(self):
        print("Clicked Fitting button!!!")

    # def menu_actions(self): #this is initial funtion from honza, i will probably use it as saving function
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
    sys.exit(app.exec())

