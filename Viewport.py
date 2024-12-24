import numpy as np
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtWidgets import QGridLayout, QLabel, QComboBox, QFileDialog, QPushButton, QFrame

from Image import Image
from RegionSelect import RegionSelect
from logger_config import setup_logger

logger = setup_logger(__name__)


class ViewPort(QFrame):
    image_size = QSize(220, 220)
    max_brightness = 50
    min_brightness = -50
    brightness_step = -1
    max_contrast = 5
    min_contrast = 0.1
    contrast_step = 0.1

    def __init__(self, is_input=True, index=0, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Shape.Panel)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
        self.image = None
        self.brightness = 0
        self.contrast = 1

        # Tracking drag state
        self.dragging = False
        self.last_pos = None

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.layout.setColumnStretch(6, 1)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 0)

        self.image_label = QLabel()
        self.image_label.setMaximumSize(ViewPort.image_size)
        self.image_label.setMinimumSize(ViewPort.image_size)
        if is_input:
            self.image_label.setMouseTracking(True)
            self.image_label.mousePressEvent = self.start_drag
            self.image_label.mouseReleaseEvent = self.end_drag
            self.image_label.mouseMoveEvent = self.drag_motion
        self.layout.addWidget(self.image_label, 0, 0, 1, 6)

        self.ft_label = QLabel()
        self.ft_label.setMaximumSize(ViewPort.image_size)
        self.ft_label.setMinimumSize(ViewPort.image_size)
        self.layout.addWidget(self.ft_label, 0, 6, 1, 6)

        if is_input:
            self.reset_edits_btn = QPushButton()
            self.reset_edits_btn.setIcon(QIcon("UI/reset.png"))
            self.reset_edits_btn.setIconSize(QSize(20, 20))
            self.reset_edits_btn.clicked.connect(self.reset_edits)
            self.layout.addWidget(self.reset_edits_btn, 1, 0, 1, 1)

            self.image_title = QLabel(f"Image {index + 1}")
            self.layout.addWidget(self.image_title, 1, 1, 1, 5)

        self.component_combo = QComboBox()
        self.component_combo.addItems(["Magnitude", "Phase", "Real", "Imaginary"])
        self.component_combo.currentIndexChanged.connect(self.update_ft_label)
        if is_input:
            combo_box_col_span = 5
        else:
            combo_box_col_span = 6
        self.layout.addWidget(self.component_combo, 1, 6, 1, combo_box_col_span)

        if is_input:
            self.region_select_btn = QPushButton()
            self.region_select_btn.setIcon(QIcon("UI/rectangle.png"))
            self.region_select_btn.setIconSize(QSize(20, 20))
            self.layout.addWidget(self.region_select_btn, 1, 11)

            self.region_selector = RegionSelect(self.ft_label)

            self.image_label.mouseDoubleClickEvent = lambda even: self.load_image()

    def start_drag(self, event):
        if self.image is not None and event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_pos = event.pos()

    def end_drag(self, event):
        if self.dragging and self.image is not None:
            self.dragging = False
            self.update_labels()

    def drag_motion(self, event):
        if self.dragging and self.image is not None:
            if self.last_pos is None:
                self.last_pos = event.pos()
                return

            dx = event.pos().x() - self.last_pos.x()
            dy = event.pos().y() - self.last_pos.y()

            sensitivity = 0.1

            # contrast => horizontal
            new_contrast = self.contrast + dx * self.contrast_step * sensitivity
            new_contrast = max(self.min_contrast, min(new_contrast, self.max_contrast))

            # brightness => vertical
            new_brightness = self.brightness + dy * self.brightness_step * sensitivity
            new_brightness = max(self.min_brightness, min(new_brightness, self.max_brightness))

            self.contrast = new_contrast
            self.brightness = new_brightness

            self.image.changeBrightnessContrast(self.brightness, self.contrast)

            self.update_labels()
            self.last_pos = event.pos()

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
        q_img = QImage(self.image.get_image_data().data, width, height, bytes_per_line, QImage.Format_Grayscale8)
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
        self.image.resize((self.image_label.size().width(), self.image_label.size().height()))
        self.brightness = 0
        self.contrast = 1
        self.image.changeBrightnessContrast(self.brightness, self.contrast)
        self.update_labels()

    def reset_edits(self):
        self.brightness = 0
        self.contrast = 1
        self.image.changeBrightnessContrast(self.brightness, self.contrast)
        self.update_labels()
        logger.info("Image edits reset")
