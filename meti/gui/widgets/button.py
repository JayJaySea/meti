from PySide6 import QtGui
from PySide6.QtCore import QSize, Qt, QPoint, Signal, QEvent
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QPushButton, QStyleOption, QStyle
import os
from meti.data import DATA_DIR


class IconButton(QPushButton):
    pressed = Signal(str)

    def __init__(self, name, icon_name, callback, size="large", parent=None, id=None):
        super().__init__(parent)
        self.setObjectName(name)
        self.callback = callback
        self.icon_default = QPixmap(os.path.join(DATA_DIR, "icons", icon_name+".png"))
        self.icon_hover = QPixmap(os.path.join(DATA_DIR, "icons", icon_name+"-hover.png"))
        self.icon_active = QPixmap(os.path.join(DATA_DIR, "icons", icon_name+"-active.png"))
        self.hovering = False
        self.active = False
        self.id = id

        self.setMouseTracking(True)

        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setIcon(self.icon_default)
        self.setSize(size)

    def setSize(self, size):
        if size == "small":
            self.setFixedSize(20, 20)
            self.setIconSize(QSize(6, 6))
        elif size == "medium":
            self.setFixedSize(30, 30)
            self.setIconSize(QSize(16, 16))
        else:
            self.setFixedSize(40, 40)
            self.setIconSize(QSize(26, 26))

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        self.hoverStyle()

    def mouseMoveEvent(self, event):
        mouse_pos = event.globalPosition().toPoint()
        button_rect = self.rect().translated(self.mapToGlobal(QPoint(0, 0)))

        if button_rect.contains(mouse_pos):
            if not self.hovering:
                self.hovering = True
        else:
            if self.hovering:
                self.hovering = False

        if not self.hovering:
            self.defaultStyle()
        elif self.active:
            self.activeStyle()

    def leaveEvent(self, event):
        self.unsetCursor()
        self.defaultStyle()

    def mousePressEvent(self, event):
        self.active = True
        self.activeStyle()

    def mouseReleaseEvent(self, event):
        self.active = False
        self.defaultStyle()
        if self.hovering:
            self.callback()
            if self.id:
                self.pressed.emit(self.id)

    def defaultStyle(self):
        self.setProperty("hover", False)
        self.setProperty("active", False)
        self.setIcon(self.icon_default)
        self.refreshStyle()

    def hoverStyle(self):
        self.setProperty("hover", True)
        self.refreshStyle()
        self.setIcon(self.icon_hover)

    def activeStyle(self):
        self.setProperty("active", True)
        self.setIcon(self.icon_active)
        self.refreshStyle()

    def refreshStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

class AddButton(IconButton):
    def __init__(self, callback, size="large", parent=None, id=None):
        super().__init__("AddButton", "add", callback, size=size, parent=parent, id=id)

class BackButton(IconButton):
    def __init__(self, callback, size="large", parent=None, id=None):
        super().__init__("BackButton", "back", callback, size=size, parent=parent, id=id)

class AcceptButton(IconButton):
    def __init__(self, callback, size="large", parent=None, id=None):
        super().__init__("AcceptButton", "accept", callback, size=size, parent=parent, id=id)

class DeleteButton(IconButton):
    def __init__(self, callback, size="large", parent=None, id=None):
        super().__init__("DeleteButton", "delete", callback, size=size, parent=parent, id=id)

class CloseButton(IconButton):
    def __init__(self, callback, size="large", parent=None, id=None):
        super().__init__("CloseButton", "close", callback, size=size, parent=parent, id=id)

class MenuButton(IconButton):
    def __init__(self, callback, size="large", parent=None, id=None):
        super().__init__("MenuButton", "menu", callback, size=size, parent=parent, id=id)

class OpenButton(IconButton):
    def __init__(self, callback, size="large", parent=None, id=None):
        super().__init__("OpenButton", "open", callback, size=size, parent=parent, id=id)

class UpDownButton(IconButton):
    pressed = Signal()
    moving = Signal(QEvent)
    released = Signal()

    def __init__(self, callback=None, size="large", parent=None, id=None):
        super().__init__("UpDownButton", "updown", callback=lambda: (), size=size, parent=parent, id=id)

    def enterEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        self.hoverStyle()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.setCursor(Qt.ClosedHandCursor)
        self.pressed.emit()

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.released.emit()

    def mouseMoveEvent(self, event):
        self.moving.emit(event)

class EditButton(IconButton):
    def __init__(self, callback, size="large", parent=None, id=None):
        super().__init__("EditButton", "edit", callback, size=size, parent=parent, id=id)

class PushButton(IconButton):
    def __init__(self, callback, size="large", parent=None, id=None):
        super().__init__("PushButton", "push", callback, size=size, parent=parent, id=id)

class PullButton(IconButton):
    def __init__(self, callback, size="large", parent=None, id=None):
        super().__init__("PullButton", "pull", callback, size=size, parent=parent, id=id)

class DuplicateButton(IconButton):
    def __init__(self, callback, size="large", parent=None, id=None):
        super().__init__("DuplicateButton", "duplicate", callback, size=size, parent=parent, id=id)
