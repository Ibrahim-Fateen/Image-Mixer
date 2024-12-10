from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QWidget, QPushButton, QProgressBar, QLabel, QComboBox, QSlider

from Image import Image
from Viewport import ViewPort
from RegionSelect import RegionSelectManager
from Mixer import Mixer, MixingThread


class ImageMixerApp(QMainWindow):
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

        self.mixBtn = self.ui.findChild(QPushButton, "mixBtn")
        self.mixingProgressBar = self.ui.findChild(QProgressBar, "mixingProgressBar")
        self.leftSlidersLabel = self.ui.findChild(QLabel, "leftSlidersLabel")
        self.rightSlidersLabel = self.ui.findChild(QLabel, "rightSlidersLabel")
        self.mixingModeCombo = self.ui.findChild(QComboBox, "compsSelectionComboBox")

        self.mixBtn.clicked.connect(self.mix_images)
        self.mixingModeCombo.currentIndexChanged.connect(self.update_sliders_labels)
        self.mixing_thread = None

    def update_sliders_labels(self):
        selected_index = self.mixingModeCombo.currentIndex()
        if selected_index == 0:
            self.leftSlidersLabel.setText("Magnitude")
            self.rightSlidersLabel.setText("Phase")
        else:
            self.leftSlidersLabel.setText("Real")
            self.rightSlidersLabel.setText("Imaginary")

    def mix_images(self):
        self.mixingProgressBar.setValue(0)

        region = None
        if self.region_select_manager.is_selecting:
            region_rect = self.inputViewPorts[0].region_selector.region_rect
            x, y, w, h = region_rect.getRect()
            inside_is_selected = self.region_select_manager.inside_selected
            region = (inside_is_selected, x, y, w, h)

        mixer = Mixer([viewport.image for viewport in self.inputViewPorts], region)
        weights = self.__get_weights()
        mode = self.mixingModeCombo.currentIndex()

        self.mixing_thread = MixingThread(mixer, weights, mode)

        def handle_result(output_image):
            output_index = self.ui.findChild(QComboBox, "outputSelectionComboBox").currentIndex()
            self.outputViewPorts[output_index].set_image(output_image)
            self.mixingProgressBar.setValue(100)

        def handle_error(error):
            print(error)

        def update_progress_bar():
            self.mixingProgressBar.setValue(self.mixingProgressBar.value() + 25)

        mixer.first_component_mixed.connect(update_progress_bar)
        mixer.second_component_mixed.connect(update_progress_bar)
        mixer.total_ft_found.connect(update_progress_bar)
        mixer.ifft_computed.connect(update_progress_bar)

        self.mixing_thread.result_ready.connect(handle_result)
        self.mixing_thread.error_occurred.connect(handle_error)

        self.mixing_thread.start()

    def __get_weights(self):
        weights = []
        for i in range(4):
            left_weight = self.ui.findChild(QSlider, f"image{i+1}LeftSlider").value() / 100
            right_weight = self.ui.findChild(QSlider, f"image{i+1}RightSlider").value() / 100
            weights.append([left_weight, right_weight])
        return weights
