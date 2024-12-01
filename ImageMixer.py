from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QWidget

from Image import Image
from Viewport import ViewPort
from RegionSelect import RegionSelectManager


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


        self.region_select_manager = RegionSelectManager()

        inputViewportWidgets = [self.ui.findChild(QWidget, f"inputViewPort{i+1}") for i in range(4)]
        self.inputViewPorts = [
            ViewPort(is_input=True, parent=widget)
            for widget in inputViewportWidgets
        ]
        for viewport in self.inputViewPorts:
            self.region_select_manager.add_listener(viewport.region_selector)
            viewport.region_selector.hide()
            viewport.region_select_btn.clicked.connect(self.region_select_manager.toggle_select_region)
            viewport.set_image(Image.placeholder_image())

        for i, viewport_widget in enumerate(inputViewportWidgets):
            viewport_widget.layout().addWidget(self.inputViewPorts[i])

        outputViewportWidgets = [self.ui.findChild(QWidget, f"outputViewPort{i+1}") for i in range(2)]
        self.outputViewPorts = [ViewPort(is_input=False, parent=widget) for widget in outputViewportWidgets]
        output_image_placeholder = Image.placeholder_image()
        for i, viewport_widget in enumerate(outputViewportWidgets):
            viewport_widget.layout().addWidget(self.outputViewPorts[i])
            self.outputViewPorts[i].set_image(output_image_placeholder)
