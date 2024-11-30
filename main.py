import sys
from PySide6.QtWidgets import QApplication
from ImageMixer import ImageMixer

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageMixer()
    sys.exit(app.exec())
