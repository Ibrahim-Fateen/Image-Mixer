from PySide6.QtCore import QRect, Qt, QPoint, Signal, QObject
from PySide6.QtGui import QPainter, QColor
from PySide6.QtWidgets import QWidget


class RegionSelect(QWidget):
    region_changed = Signal(QRect)
    inside_selected_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowModality(Qt.ApplicationModal)
        self.setMouseTracking(True)
        self.setFixedSize(parent.size())

        # Calculate min and max sizes
        parent_width = parent.size().width()
        self.min_size = parent_width // 5
        self.max_size = parent_width * 4 // 5

        # Initialize region with a default size
        init_region_size = parent_width // 3
        self.region_rect = QRect(parent.size().width() // 2 - init_region_size // 2,
                                 parent.size().height() // 2 - init_region_size // 2,
                                 init_region_size, init_region_size)
        self.inside_selected = True
        self.selected_handle = None
        self.last_mouse_pos = None

        self.handles = {
            "top_left": QRect(0, 0, 10, 10),
        }
        self.update_handles()

    def update_handles(self):
        self.handles["top_left"].moveTopLeft(self.region_rect.topLeft() + QPoint(-5, -5))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.handles["top_left"].contains(event.pos()):
                self.selected_handle = "top_left"
                self.last_mouse_pos = event.pos()
            elif self.region_rect.contains(event.pos()):
                self.inside_selected = not self.inside_selected
                self.inside_selected_changed.emit()
                self.selected_handle = None
                self.update()

    def mouseReleaseEvent(self, event):
        self.selected_handle = None
        self.last_mouse_pos = None
        self.region_changed.emit(self.region_rect)

    def mouseMoveEvent(self, event):
        if self.selected_handle and self.last_mouse_pos:
            # Calculate the difference in mouse movement
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()

            # Determine the change amount
            change = delta.x() if abs(delta.x()) > abs(delta.y()) else delta.y()

            # Create a copy of the current region rect to modify
            new_rect = QRect(self.region_rect)

            # Adjust all corners symmetrically
            new_rect.setTopLeft(new_rect.topLeft() + QPoint(change, change))
            new_rect.setTopRight(new_rect.topRight() + QPoint(-change, change))
            new_rect.setBottomLeft(new_rect.bottomLeft() + QPoint(change, -change))
            new_rect.setBottomRight(new_rect.bottomRight() + QPoint(-change, -change))

            # Enforce size and position constraints
            width = abs(new_rect.width())
            if width < self.min_size or width > self.max_size:
                return

            # Ensure the region stays within the parent widget
            if not self.parent().rect().contains(new_rect):
                return

            # Update the region rect if constraints are met
            self.region_rect = new_rect
            self.update_handles()
            self.update()
            self.region_changed.emit(self.region_rect)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Set up shade color (semi-transparent black)
        shade_color = QColor(0, 0, 0, 128)  # Last parameter is alpha (0-255)

        # Determine shading logic based on inside_selected
        if not self.inside_selected:
            # Outside selected: shade inside
            painter.fillRect(self.region_rect, shade_color)
        else:
            # Inside selected: shade outside
            # Top shade
            painter.fillRect(0, 0, self.width(), self.region_rect.top(), shade_color)
            # Bottom shade
            painter.fillRect(0, self.region_rect.bottom() + 1, self.width(),
                             self.height() - self.region_rect.bottom() - 1, shade_color)
            # Left shade
            painter.fillRect(0, self.region_rect.top(), self.region_rect.left(),
                             self.region_rect.height(), shade_color)
            # Right shade
            painter.fillRect(self.region_rect.right() + 1, self.region_rect.top(),
                             self.width() - self.region_rect.right() - 1,
                             self.region_rect.height(), shade_color)

        # Draw the region outline
        painter.setPen(Qt.red)
        painter.setBrush(Qt.NoBrush)
        painter.drawRect(self.region_rect)

        # Draw handles
        painter.setPen(Qt.blue)
        for handle in self.handles.values():
            painter.drawRect(handle)

        painter.end()


class RegionSelectManager(QObject):
    def __init__(self):
        super().__init__()
        self.listeners = []
        self.is_selecting = False
        self.inside_selected = True

    def add_listener(self, listener: RegionSelect):
        self.listeners.append(listener)
        listener.region_changed.connect(self.update_listeners)
        listener.inside_selected_changed.connect(self.toggle_inside_selected)

    def update_listeners(self, region):
        sender = self.sender()
        for listener in self.listeners:
            if listener == sender:
                continue
            listener.region_rect = region
            listener.update_handles()
            listener.update()

    def toggle_inside_selected(self):
        self.inside_selected = not self.inside_selected
        for listener in self.listeners:
            listener.inside_selected = self.inside_selected
            listener.update()

    def toggle_select_region(self):
        self.is_selecting = not self.is_selecting
        for listener in self.listeners:
            if self.is_selecting:
                listener.show()
            else:
                listener.hide()
