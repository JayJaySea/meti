from PySide6.QtWidgets import QApplication
from PySide6 import QtGui
from PySide6.QtCore import Qt, QPoint, Signal, Slot, QRect
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QLineEdit,
    QLabel,
    QPushButton,
    QSizePolicy,
    QGridLayout,
    QStyleOption,
    QStyle,
    QWidget,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QLayout,
)

from gui.widgets.button import DeleteButton
from util import snapWidgetByCorner

class Checklist(QFrame):
    state_changed = Signal(str)

    def __init__(self, title, items, position, state, grid_size, proxy=None, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.grabbed = False
        self.grabbed_pos = None
        self.title = title
        self.position = position
        self.state = state
        self.grid_size = grid_size
        self.parent_checklist = None
        self.proxy = proxy

        self.move(position["x"], position["y"])
        self.setObjectName("Checklist")

        self.initHead()
        self.initBody(items)
        self.initLayout()

    def initHead(self):
        layout = QHBoxLayout()
        title = QLabel(self.title)
        title.setObjectName("ChecklistTitle")
        layout.addWidget(title, stretch=1)
        placeholder = QWidget()
        placeholder.setFixedSize(50, 50)
        layout.addWidget(placeholder)
        layout.addWidget(DeleteButton(self.delete))

        self.head = QWidget()
        self.head.setObjectName("ChecklistHead")
        self.head.setLayout(layout)

    def initBody(self, items):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 5)
        layout.setSpacing(0)
        self.items = {}
        for item in items:
            checkbox = CheckBox(item["content"], True if self.state[item["position"]] == "1" else False)
            checkbox.state_changed.connect(self.onCheckboxStateChanged)
            self.items[checkbox] = item

            layout.addWidget(checkbox)

        self.body = QWidget()
        self.body.setObjectName("ChecklistBody")
        self.body.setLayout(layout)

    def initLayout(self):
        layout = QVBoxLayout() 

        layout.setContentsMargins(0, 0, 0, 0)
        #layout.setSpacing(0)
        layout.addWidget(self.head)
        layout.addWidget(self.body, stretch=1)

        self.setLayout(layout)

    def setParentChecklist(self, checklist):
        self.parent_checklist = checklist

    def delete(self):
        pass

    def enterEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)

    def mousePressEvent(self, event):
        self.grabbed = True
        self.grabbed_pos = event.pos()
        self.proxy.setCursor(Qt.SizeAllCursor)

    def mouseReleaseEvent(self, event):
        self.proxy.setCursor(Qt.OpenHandCursor)
        self.grabbed = False
        new_pos = self.pos() + (event.pos() - self.grabbed_pos)
        new_pos.setX(round(new_pos.x() / self.grid_size) * self.grid_size)
        new_pos.setY(round(new_pos.y() / self.grid_size) * self.grid_size)

        scene_rect = self.proxy.scene().sceneRect()
        widget_rect = self.rect()

        new_x = max(scene_rect.left(), min(new_pos.x(), scene_rect.right() - widget_rect.width()))
        new_y = max(scene_rect.top(), min(new_pos.y(), scene_rect.bottom() - widget_rect.height()))
        self.move(new_x, new_y)

    def mouseMoveEvent(self, event):
        if not self.grabbed:
            return

        new_pos = self.pos() + (event.pos() - self.grabbed_pos)
        scene_rect = self.proxy.scene().sceneRect()
        widget_rect = self.rect()

        new_x = max(scene_rect.left(), min(new_pos.x(), scene_rect.right() - widget_rect.width()))
        new_y = max(scene_rect.top(), min(new_pos.y(), scene_rect.bottom() - widget_rect.height()))
        self.move(new_x, new_y)

    def onCheckboxStateChanged(self, state):
        item = self.items.get(self.sender())
        if not item:
            return

        self.state = self.updateState(self.state, item["position"], "1" if state == True else "0")
        self.state_changed.emit(self.state)

    def updateState(self, state_str, index, new_value):
        state_list = list(state_str)
        state_list[index] = new_value
        return "".join(state_list)


class CheckBox(QFrame):
    state_changed = Signal(bool)

    def __init__(self, label, active, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.label = label
        self.setObjectName("CheckBoxWidget")

        self.active = active
        self.hovering = False

        self.initLayout()
        if self.active:
            self.activeStyle()

    def initLayout(self):
        self.checkbox = QFrame(self)
        self.checkbox.setLayout(None)
        self.checkbox.setObjectName("CheckBox")
        self.checkbox.setFixedSize(20, 20)

        self.indicator = QFrame(self.checkbox)
        self.indicator.setObjectName("CheckBoxIndicator")
        self.indicator.setFixedSize(12, 12)
        self.indicator.move(4, 4)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(5)

        layout.addWidget(self.checkbox)
        label = QLabel(self.label)
        label.setObjectName("CheckBoxLabel")
        layout.addWidget(label, stretch=1)
        self.setLayout(layout)

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

        if not self.active:
            self.hoverStyle()
        event.accept()

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        if not self.active:
            self.defaultStyle()
        event.accept()

    def mousePressEvent(self, event):
        self.active = not self.active
        if self.active:
            self.state_changed.emit(True)
            self.activeStyle()
        else:
            self.state_changed.emit(False)
            self.hoverStyle()
        event.accept()

    def mouseReleaseEvent(self, event):
        event.accept()

    def mouseMoveEvent(self, event):
        mouse_pos = event.globalPosition().toPoint()
        widget_rect = self.rect().translated(self.mapToGlobal(QPoint(0, 0)))

        if widget_rect.contains(mouse_pos):
            if not self.hovering:
                self.hovering = True
        else:
            if self.hovering:
                self.hovering = False

        if not self.active:
            if not self.hovering:
                self.defaultStyle()
            elif self.active:
                self.activeStyle()

        event.accept()

    def defaultStyle(self):
        self.indicator.setProperty("hover", False)
        self.indicator.setProperty("active", False)
        self.refreshStyle()

    def hoverStyle(self):
        self.indicator.setProperty("active", False)
        self.indicator.setProperty("hover", True)
        self.refreshStyle()

    def activeStyle(self):
        self.indicator.setProperty("hover", False)
        self.indicator.setProperty("active", True)
        self.refreshStyle()

    def refreshStyle(self):
        self.indicator.style().unpolish(self.indicator)
        self.indicator.style().polish(self.indicator)
        self.indicator.update()
