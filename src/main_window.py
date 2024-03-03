import sys
from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QFileDialog,
    QMainWindow,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice

import read_data 


# class SpecWindow(QMainWindow):

    # def __init__(self,parent=None):
    #     pass
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.title = "SpecApp"
    #     self.layout = QVBoxLayout()
    #     self.setWindowTitle(self.title)
    #     self.menu_actions()
    #     self.show()
    #
    #     self.measured_data = None
    #
    # def menu_actions(self):
    #     self.menuBar = self.menuBar()
    #     self.fileMenu = self.menuBar.addMenu("File")
    #     self.actionOpen = self.fileMenu.addAction("Open")
    #     self.actionOpen.triggered.connect(self.open_file_dialog)
    #     self.actionQuit = self.fileMenu.addAction("Exit")
    #     self.actionQuit.triggered.connect(sys.exit)
    #
    # def open_file_dialog(self):
    #     dialog = QFileDialog()
    #     filename = dialog.getOpenFileName()
    #     if filename:
    #         self.title = f"SpecApp - {filename[0]}"
    #         self.data = read_data.read_data(filename[0])
    #         print(self.data)
    #     else:
    #         self.title = "SpecApp"
    #     self.setWindowTitle(self.title)
        
loader = QUiLoader()
app = QApplication(sys.argv)
window = loader.load("UI_structure.ui", None)
window.show()
app.exec()

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#
#     ui_file_name = "UI_structure.ui"
#     ui_file = QFile(ui_file_name)
#     if not ui_file.open(QIODevice.ReadOnly):
#         print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
#         sys.exit(-1)
#
#     loader = QUiLoader()
#     window = loader.load(ui_file)
#     ui_file.close()
#     if not window:
#         print(loader.errorString())
#         sys.exit(-1)
#     window.show()
#
#     sys.exit(app.exec())
