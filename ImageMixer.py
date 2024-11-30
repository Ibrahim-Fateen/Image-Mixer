from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QFrame


class ImageMixer(QMainWindow):
    def __init__(self):
        super().__init__()

        loader = QUiLoader()
        file = QFile("UI/main_window.ui")
        file.open(QFile.ReadOnly)
        self.ui = loader.load(file, self)
        file.close()

        self.setCentralWidget(self.ui)
        self.ui.showMaximized()
        self.ui.setWindowTitle("Image Mixer")
