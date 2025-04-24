from PySide6 import QtGui
from PySide6.QtCore import QSize, Qt, QPoint
from PySide6.QtGui import QPixmap, QColor
from PySide6.QtWidgets import QPushButton, QStyleOption, QStyle
import os
from data import DATA_DIR


class IconButton(QPushButton):
    def __init__(self, name, icon_name, callback):
        super().__init__()
        self.setObjectName(name)
        self.callback = callback
        self.icon_default = QPixmap(os.path.join(DATA_DIR, "icons", icon_name+".png"))
        self.icon_hover = QPixmap(os.path.join(DATA_DIR, "icons", icon_name+"-hover.png"))
        self.icon_active = QPixmap(os.path.join(DATA_DIR, "icons", icon_name+"-active.png"))
        self.hovering = False
        self.active = False

        self.setMouseTracking(True)

        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setFixedSize(40, 40)
        self.setIcon(self.icon_default)
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
    def __init__(self, callback):
        super().__init__("AddButton", "add", callback)

class BackButton(IconButton):
    def __init__(self, callback):
        super().__init__("BackButton", "back", callback)

class AcceptButton(IconButton):
    def __init__(self, callback):
        super().__init__("AcceptButton", "accept", callback)

class DeleteButton(IconButton):
    def __init__(self, callback):
        super().__init__("DeleteButton", "delete", callback)
