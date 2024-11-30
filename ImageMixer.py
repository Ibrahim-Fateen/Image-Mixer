from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QWidget
from Image import Image
from Viewport import ViewPort


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

        self.images = [
            Image.from_file("Images/landscape.png"),
            Image.from_file("Images/Husky.jpg"),
            Image.from_file("Images/Retriever.jpg"),
            Image.from_file("Images/roses.jpg")
        ]

        inputViewportWidgets = [self.ui.findChild(QWidget, f"inputViewPort{i+1}") for i in range(4)]
        self.inputViewPorts = [ViewPort(is_input=True, parent=widget) for widget in inputViewportWidgets]
        for i, viewport_widget in enumerate(inputViewportWidgets):
            viewport_widget.layout().addWidget(self.inputViewPorts[i])

        outputViewportWidgets = [self.ui.findChild(QWidget, f"outputViewPort{i+1}") for i in range(2)]
        self.outputViewPorts = [ViewPort(is_input=False, parent=widget) for widget in outputViewportWidgets]
        for i, viewport_widget in enumerate(outputViewportWidgets):
            viewport_widget.layout().addWidget(self.outputViewPorts[i])

        for img, viewport in zip(self.images, self.inputViewPorts):
            viewport.set_image(img)
