import sys
from PySide6.QtWidgets import QApplication
from ImageMixerApp import ImageMixerApp

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageMixerApp()
    sys.exit(app.exec())
