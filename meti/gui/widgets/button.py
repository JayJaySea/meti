from PySide6 import QtGui
from PySide6.QtCore import QSize, Qt, QPoint, Signal, QEvent
from PySide6.QtGui import QPixmap, QColor, QCursor
from PySide6.QtWidgets import QPushButton, QStyleOption, QStyle, QHBoxLayout
import os
from meti.data import DATA_DIR

class IconButton(QPushButton):
    clicked = Signal(str)

    def __init__(self, icon_name, color, size="large", parent=None, id=None):
        super().__init__(parent)
        self.setObjectName("IconButton")
        self.icon_default = QPixmap(os.path.join(DATA_DIR, "icons", icon_name+".png"))
        self.icon_hover = QPixmap(os.path.join(DATA_DIR, "icons", icon_name+"-hover.png"))
        self.icon_active = QPixmap(os.path.join(DATA_DIR, "icons", icon_name+"-active.png"))
        self.hovering = False
        self.active = False
        self.id = id
        self.color = color

        self.setMouseTracking(True)
        self.setProperty("color", color)

        self.indicator = QPushButton(self)
        self.indicator.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.indicator.setObjectName("ButtonIndicator")
        self.indicator.setProperty(size, True)
        self.indicator.setIcon(self.icon_default)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.indicator)

        self.setLayout(layout)

        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setSize(size)

    def setSize(self, size):
        if size == "small":
            self.setFixedSize(20, 20)
            self.setIconSize(QSize(6, 6))
        elif size == "medium":
            self.setFixedSize(30, 30)
            self.indicator.setFixedSize(22, 22)
            self.indicator.setIconSize(QSize(20, 20))
        else:
            self.setFixedSize(40, 40)
            self.indicator.setFixedSize(32, 32)
            self.indicator.setIconSize(QSize(26, 26))

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        self.hoverStyle()

    def mouseMoveEvent(self, event):
        self.updateHover()

    def updateHover(self):
        mouse_pos = QCursor.pos()
        button_rect = self.rect().translated(self.mapToGlobal(QPoint(0, 0)))

        if button_rect.contains(mouse_pos):
            if not self.hovering:
                self.hovering = True
                self.setCursor(Qt.PointingHandCursor)
        else:
            if self.hovering:
                self.hovering = False
                self.setCursor(Qt.ArrowCursor)

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
            self.clicked.emit(self.id)

    def defaultStyle(self):
        self.indicator.setProperty("hover", False)
        self.indicator.setProperty("color", False)
        self.indicator.setIcon(self.icon_default)
        self.refreshStyle()

    def hoverStyle(self):
        self.indicator.setProperty("hover", True)
        self.indicator.setIcon(self.icon_hover)
        self.refreshStyle()

    def activeStyle(self):
        self.indicator.setProperty("color", self.color)
        self.indicator.setIcon(self.icon_active)
        self.refreshStyle()

    def refreshStyle(self):
        self.indicator.style().unpolish(self.indicator)
        self.indicator.style().polish(self.indicator)
        self.indicator.update()
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

class AddButton(IconButton):
    def __init__(self, size="large", parent=None, id=None):
        super().__init__("add", "green", size=size, parent=parent, id=id)

class BackButton(IconButton):
    def __init__(self, size="large", parent=None, id=None):
        super().__init__("back", "red", size=size, parent=parent, id=id)

class AcceptButton(IconButton):
    def __init__(self, size="large", parent=None, id=None):
        super().__init__("accept", "blue", size=size, parent=parent, id=id)

class DeleteButton(IconButton):
    def __init__(self, size="large", parent=None, id=None):
        super().__init__("delete", "red", size=size, parent=parent, id=id)
        # self.setFocusPolicy(Qt.ClickFocus)
        # self.indicator.setFocusPolicy(Qt.ClickFocus)

class CloseButton(IconButton):
    def __init__(self, size="large", parent=None, id=None):
        super().__init__("close", "red", size=size, parent=parent, id=id)

class MenuButton(IconButton):
    def __init__(self, size="large", parent=None, id=None):
        super().__init__("menu", "blue", size=size, parent=parent, id=id)

class OpenButton(IconButton):
    def __init__(self, size="large", parent=None, id=None):
        super().__init__("open", "blue", size=size, parent=parent, id=id)

class UpDownButton(IconButton):
    pressed = Signal()
    moving = Signal(QEvent)
    released = Signal()

    def __init__(self, size="large", parent=None, id=None):
        super().__init__("updown", "yellow", size=size, parent=parent, id=id)
        self.setFocusPolicy(Qt.ClickFocus)
        self.indicator.setFocusPolicy(Qt.ClickFocus)

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
    def __init__(self, size="large", parent=None, id=None):
        super().__init__("edit", "yellow", size=size, parent=parent, id=id)

class PushButton(IconButton):
    def __init__(self, size="large", parent=None, id=None):
        super().__init__("push", "purple", size=size, parent=parent, id=id)

class PullButton(IconButton):
    def __init__(self, size="large", parent=None, id=None):
        super().__init__("pull", "yellow", size=size, parent=parent, id=id)

class DuplicateButton(IconButton):
    def __init__(self, size="large", parent=None, id=None):
        super().__init__("duplicate", "purple", size=size, parent=parent, id=id)
