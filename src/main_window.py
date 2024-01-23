import sys
from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QFileDialog,
    QMainWindow,
)


class SpecWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title = "SpecApp"
        self.layout = QVBoxLayout()
        self.setWindowTitle(self.title)
        self.menu_actions()
        self.show()

    def menu_actions(self):
        self.menuBar = self.menuBar()
        self.fileMenu = self.menuBar.addMenu("File")
        self.actionOpen = self.fileMenu.addAction("Open")
        self.actionOpen.triggered.connect(self.open_file_dialog)
        self.actionQuit = self.fileMenu.addAction("Exit")
        self.actionQuit.triggered.connect(sys.exit)

    def open_file_dialog(self):
        dialog = QFileDialog()
        filename = dialog.getOpenFileName()
        if filename:
            self.title = f"SpecApp - {filename[0]}"
        else:
            self.title = "SpecApp"
        self.setWindowTitle(self.title)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpecWindow()
    sys.exit(app.exec())
