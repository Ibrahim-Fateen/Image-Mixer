from PySide6.QtCore import QRect, Qt
from PySide6.QtGui import QPainter, QPen
from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QComboBox
from Image import Image


class ViewPort(QWidget):
    def __init__(self, is_input=True, parent=None):
        super().__init__(parent)
        self.image = None
        self.brightness = 0
        self.contrast = 1

        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.image_label = QLabel()
        self.layout.addWidget(self.image_label, 0, 0)

        self.ft_label = QLabel()
        self.layout.addWidget(self.ft_label, 0, 1)

        self.component_combo = QComboBox()
        self.component_combo.addItems(["Real", "Imaginary", "Magnitude", "Phase"])
        self.layout.addWidget(self.component_combo, 1, 1)

        if is_input:
            self.image_label.mouseDoubleClickEvent = lambda e: self.load_image()
            # add drag event to change brightness and contrast

    def load_image(self):
        pass

class SelectRegion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.region_rect = QRect(0, 0, 0, 0)
        self.is_selecting = False
        self.is_inside_selected = True
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.region_rect.contains(event.pos()):
                self.is_inside_selected = not self.is_inside_selected
                self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.region_rect.setBottomRight(event.pos())
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        painter.drawRect(self.region_rect)

        painter.setOpacity(0.3)
        if self.is_inside_selected:
            painter.setBrush(Qt.black)
            painter.drawRect(0, 0, self.width(), self.height())
            painter.drawRect(self.region_rect)
        else:
            painter.setBrush(Qt.black)
            painter.drawRect(self.region_rect)