import numpy as np
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox, QFileDialog, QPushButton

from Image import Image
from RegionSelect import RegionSelect


class ViewPort(QWidget):
    image_size = (220, 220)

    def __init__(self, is_input=True, parent=None):
        super().__init__(parent)
        self.image = None
        self.brightness = 0
        self.contrast = 1

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.image_label = QLabel()
        self.image_label.setMaximumSize(*ViewPort.image_size)
        self.layout.addWidget(self.image_label, 0, 0, 1, 6)

        self.ft_label = QLabel()
        self.ft_label.setMaximumSize(*ViewPort.image_size)
        self.layout.addWidget(self.ft_label, 0, 6, 1, 6)

        self.component_combo = QComboBox()
        self.component_combo.addItems(["Magnitude", "Phase", "Real", "Imaginary"])
        self.component_combo.currentIndexChanged.connect(self.update_ft_label)
        if is_input:
            col_span = 5
        else:
            col_span = 6
        self.layout.addWidget(self.component_combo, 1, 6, 1, col_span)

        if is_input:
            self.region_select_btn = QPushButton()
            self.region_select_btn.setIcon(QIcon("UI/rectangle.png"))
            self.region_select_btn.setIconSize(QSize(20, 20))
            self.layout.addWidget(self.region_select_btn, 1, 11)

            self.region_selector = RegionSelect(self.ft_label)

            self.image_label.mouseDoubleClickEvent = lambda even: self.load_image()
            # add drag event to change brightness and contrast

    def load_image(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Images (*.png *.jpg *jpeg)")
        if file_dialog.exec():
            file_path = file_dialog.selectedFiles()[0]
            self.set_image(Image.from_file(file_path))

    def update_ft_label(self):
        height, width = self.image.size
        bytes_per_line = width
        relevant_ft = self.image.get_ft_image(self.component_combo.currentText())
        contiguous_arr = np.ascontiguousarray(relevant_ft.data)  # Fixed C-contiguous error
        q_ft = QImage(contiguous_arr, width, height, bytes_per_line, QImage.Format_Grayscale8)
        self.ft_label.setPixmap(QPixmap.fromImage(q_ft).scaled(
            self.ft_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))

    def update_img_label(self):
        height, width = self.image.size
        bytes_per_line = width
        q_img = QImage(self.image.image_data.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        self.image_label.setPixmap(QPixmap.fromImage(q_img).scaled(
            self.image_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        ))

    def update_labels(self):
        self.update_img_label()
        self.update_ft_label()

    def set_image(self, image):
        self.image = image
        self.image.resize(ViewPort.image_size)
        self.update_labels()
