import numpy as np
from PySide6.QtCore import QRect, Qt, QPoint
from PySide6.QtGui import QPainter, QPen, QImage, QBrush, QPixmap
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox, QFileDialog, QPushButton
from Image import Image


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
            self.region_btn = QPushButton("Select Region")
            self.region_btn.clicked.connect(self.add_select_region)
            self.layout.addWidget(self.region_btn, 1, 11)

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

    def add_select_region(self):
        if not hasattr(self, 'region_selector'):
            self.region_selector = RegionSelect(self.ft_label)
            self.layout.addWidget(self.region_selector, 0, 6)

        self.region_selector.initialize_region(self.ft_label)
        self.region_selector.show()


class RegionSelect(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.region_rect = None
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Resize handles
        self.handles = {
            'top_left': QRect(),
            'top_right': QRect(),
            'bottom_left': QRect(),
            'bottom_right': QRect()
        }

        self.current_handle = None

        self.is_inside_selected = True
        self.setMouseTracking(True)

    def initialize_region(self, parent_widget):
        """
        Initialize region in the center of the parent widget
        """
        parent_width = parent_widget.width()
        parent_height = parent_widget.height()

        region_width = parent_width // 3
        region_height = parent_height // 3

        x = (parent_width - region_width) // 2
        y = (parent_height - region_height) // 2

        self.region_rect = QRect(x, y, region_width, region_height)
        self.update_handles()

    def update_handles(self):
        """
        Update resize handle positions
        """
        handle_size = 10
        half_handle = handle_size // 2

        # Top left handle
        self.handles['top_left'] = QRect(
            self.region_rect.topLeft().x() - half_handle,
            self.region_rect.topLeft().y() - half_handle,
            handle_size, handle_size
        )

        # Top right handle
        self.handles['top_right'] = QRect(
            self.region_rect.topRight().x() - half_handle,
            self.region_rect.topRight().y() - half_handle,
            handle_size, handle_size
        )

        # Bottom left handle
        self.handles['bottom_left'] = QRect(
            self.region_rect.bottomLeft().x() - half_handle,
            self.region_rect.bottomLeft().y() - half_handle,
            handle_size, handle_size
        )

        # Bottom right handle
        self.handles['bottom_right'] = QRect(
            self.region_rect.bottomRight().x() - half_handle,
            self.region_rect.bottomRight().y() - half_handle,
            handle_size, handle_size
        )

    def maintain_centered_square(self, event):
        """
        Maintain square aspect ratio while keeping center fixed
        """
        # Get the center point of the current region
        center = self.region_rect.center()

        # Calculate the distance from the center to the event point
        dx = abs(event.pos().x() - center.x())
        dy = abs(event.pos().y() - center.y())

        # Use the maximum of dx and dy to maintain square shape
        size = max(dx, dy) * 2

        # Calculate new rectangle keeping center fixed
        self.region_rect = QRect(
            center.x() - size // 2,
            center.y() - size // 2,
            size,
            size
        )

    def mousePressEvent(self, event):
        # Check if a resize handle is clicked
        for handle_name, handle_rect in self.handles.items():
            if handle_rect.contains(event.pos()):
                self.current_handle = handle_name
                return

        # If inside region, toggle selection
        if self.region_rect.contains(event.pos()):
            self.is_inside_selected = not self.is_inside_selected
            self.update()

    def mouseMoveEvent(self, event):
        if not self.current_handle:
            return

        self.maintain_centered_square(event)

        self.update_handles()
        self.update()

    def mouseReleaseEvent(self, event):
        self.current_handle = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw region rectangle
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        painter.drawRect(self.region_rect)

        painter.setBrush(QBrush(Qt.red))
        for handle_rect in self.handles.values():
            painter.drawRect(handle_rect)

        # Shade region
        painter.setOpacity(0.3)
        if self.is_inside_selected:
            # Shade outside region
            painter.setBrush(QBrush(Qt.black))
            painter.drawRect(0, 0, self.width(), self.height())
            painter.drawRect(self.region_rect)
        else:
            # Shade inside region
            painter.setBrush(QBrush(Qt.black))
            painter.drawRect(self.region_rect)
