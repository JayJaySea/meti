from PySide6.QtWidgets import QApplication
from PySide6 import QtGui
from PySide6.QtGui import QRegion, QBitmap, QPainter
from PySide6.QtCore import Qt, QPoint, Signal, Slot, QRect, QEvent
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

from gui.widgets.button import DeleteButton, UpDownButton, AddButton, BackButton, AcceptButton, EditButton

class Checklist(QFrame):
    state_changed = Signal(str)
    checklist_moved = Signal()
    position_changed = Signal(int, int)
    delete_checklist = Signal(str)

    def __init__(self, title, items, position, state, grid_size, proxy=None, parent=None, id=None):
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
        self.connected_lines = []
        self.proxy = proxy
        self.id = id

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
        layout.addWidget(EditButton(lambda: print("TODO!")))
        layout.addWidget(DeleteButton(lambda: self.delete_checklist.emit(self.id)))

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
        layout.addWidget(self.head)
        layout.addWidget(self.body, stretch=1)

        self.setLayout(layout)

    def addLine(self, line):
        self.connected_lines.append(line)

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
        for line in self.connected_lines:
            line.updatePath()

        self.position_changed.emit(new_x, new_y)

    def mouseMoveEvent(self, event):
        if not self.grabbed:
            return

        new_pos = self.pos() + (event.pos() - self.grabbed_pos)
        scene_rect = self.proxy.scene().sceneRect()
        widget_rect = self.rect()

        new_x = max(scene_rect.left(), min(new_pos.x(), scene_rect.right() - widget_rect.width()))
        new_y = max(scene_rect.top(), min(new_pos.y(), scene_rect.bottom() - widget_rect.height()))
        self.move(new_x, new_y)
        self.checklist_moved.emit()
        for line in self.connected_lines:
            line.updatePath()

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

    def removeLine(self, line):
        if line in self.connected_lines:
            self.connected_lines.remove(line)


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
        self.label = QLabel(self.label)
        self.label.setObjectName("CheckBoxLabel")
        layout.addWidget(self.label, stretch=1)
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

class CreateChecklistButton(QFrame):
    pressed = Signal(QEvent)
    released = Signal(QEvent)

    def __init__(self, parent=None, proxy=None, id=None):
        super().__init__(parent)
        self.setObjectName("TransparentContainer")
        self.resize(14, 14)

        self.proxy = proxy
        self.id = id
        self.circle = QFrame(self)
        self.circle.setObjectName("CreateChecklistButton")
        self.circle.resize(14, 14)
        self.inner_circle = QFrame(self.circle)
        self.inner_circle.resize(12, 12)
        self.inner_circle.move(4, 4)
        self.inner_circle.setObjectName("CreateChecklistButtonIndicator")
        self.inner_circle.hide()
    
    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)
        self.circle.setProperty("hover", True)
        self.prev_pos = self.pos()
        self.move(self.x() - 3, self.y() - 3)
        self.resize(20, 20)
        self.circle.resize(20, 20)
        self.refreshStyle()

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        self.circle.setProperty("hover", False)
        self.move(self.prev_pos)
        self.resize(14, 14)
        self.circle.resize(14, 14)
        self.inner_circle.hide()
        self.refreshStyle()

    def mousePressEvent(self, event):
        self.proxy.setCursor(Qt.ArrowCursor)
        self.inner_circle.show()
        self.pressed.emit(event)

    def mouseReleaseEvent(self, event):
        self.inner_circle.hide()
        self.released.emit(event)

    def refreshStyle(self):
        self.circle.style().unpolish(self.circle)
        self.circle.style().polish(self.circle)
        self.circle.update()

class CreateChecklistDestination(QFrame):
    def __init__(self, parent=None, proxy=None):
        super().__init__(parent)
        self.setObjectName("TransparentContainer")
        self.resize(14, 14)
        self.proxy = proxy
        self.circle = QFrame(self)
        self.circle.setObjectName("CreateChecklistDestination")
        self.circle.resize(14, 14)

class ChecklistEditor(QFrame):
    checklist_ready = Signal(str, list, str)

    def __init__(self, title=None, items=None, id=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.items = items
        self.id = id

        self.setObjectName("Dialog")
        self.initLayout()

    def initLayout(self):
        input_label = QLabel("CHECKLIST NAME")
        input_label.setObjectName("TextInputLabel")
        input_label.setAlignment(Qt.AlignCenter)
        self.checklist_name_input = QLineEdit()
        self.checklist_name_input.setObjectName("TextInput")
        items_label = QLabel("ITEMS")
        items_label.setObjectName("TextInputLabel")
        items_label.setAlignment(Qt.AlignCenter)
        self.item_editor = ItemEditor(self.items)
        buttons = QHBoxLayout()
        buttons.addWidget(BackButton(lambda: self.parent().hide()))
        buttons.addStretch()
        buttons.addWidget(AcceptButton(lambda: self.createChecklist()))

        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(input_label)
        layout.addWidget(self.checklist_name_input)
        layout.addWidget(items_label)
        layout.addWidget(self.item_editor)
        layout.addLayout(buttons)

        self.setLayout(layout)
    
    def createChecklist(self):
        title = self.checklist_name_input.text()
        if not title or not self.item_editor.itemsFilled():
            return

        items = self.item_editor.getItems()
        self.checklist_ready.emit(title, items, self.id)



class ItemEditor(QScrollArea):
    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self.items = items if items else []
        self.dragging = False
        self.setFixedSize(500, 300)

        self.setWidgetResizable(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setObjectName("ItemEditor")

        self.initLayout()

    def initLayout(self):
        self.layout = QVBoxLayout()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(0)
        layout.addStretch()
        layout.addWidget(AddButton(lambda: self.addItem()))
        layout.addStretch()

        add_new = QFrame()
        add_new.setLayout(layout)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(add_new)
        self.layout.addStretch()
        for item in self.items:
            self.addItem(item)

        container = QFrame()
        container.setLayout(self.layout)

        self.setWidget(container)

    def addItem(self, item=None):
        if not item:
            item = {}

        item["widget"] = EditableItem(item.get("content"), item.get("id"))
        item["widget"].grabbed.connect(self.itemGrabbed)
        item["widget"].released.connect(self.itemReleased)
        item["widget"].moving.connect(self.itemMoving)
        self.layout.insertWidget(self.layout.count() - 2, item["widget"])
        
        if not item.get("id"):
            self.items.append(item)

    def itemGrabbed(self):
        self.dragging = True

    def itemReleased(self):
        self.dragging = False

    def itemMoving(self, event):
        if not self.dragging:
            return

        dragged = self.sender()
        pos = dragged.mapTo(self.widget(), event.pos())
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if not isinstance(widget, EditableItem):
                continue

            if widget.geometry().contains(pos):
                if dragged is not widget:
                    self.layout.removeWidget(dragged)
                    self.layout.insertWidget(i, dragged)
                    break

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        self.verticalScrollBar().setValue(
            self.verticalScrollBar().value() - delta * 50
        )
        event.accept()

    def itemsFilled(self):
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if not isinstance(widget, EditableItem):
                continue

            if not widget.content:
                return False

        return True

    def getItems(self):
        items = []
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if not isinstance(widget, EditableItem):
                continue

            if not widget.id:
                items.append({
                    "content": widget.content,
                    "position": i
                })
                continue

            for item in self.items:
                if not widget.id == item["id"]:
                    continue

                items.append({
                    "id": widget.id,
                    "template_id": item["template_id"],
                    "content": widget.content,
                    "position": i
                })
                break

        return items

class EditableItem(QFrame):
    grabbed = Signal()
    moving = Signal(QEvent)
    released = Signal()

    def __init__(self, content=None, id=None, parent=None):
        super().__init__(parent)
        self.content = content
        self.id = id

        self.setMaximumHeight(40)
        self.setMaximumHeight(300)
        self.setMouseTracking(True)

        self.initLayout()

    def initLayout(self):
        edit = QLineEdit(self.content)
        edit.setObjectName("TextInput")
        edit.textChanged.connect(self.onTextChanged)

        updown_button = UpDownButton()
        updown_button.pressed.connect(lambda: self.grabbed.emit())
        updown_button.released.connect(lambda: self.released.emit())
        updown_button.moving.connect(lambda event: self.moving.emit(event))

        delete_button = DeleteButton(lambda: self.delete())

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.addWidget(updown_button)
        layout.addWidget(delete_button)
        layout.addWidget(edit, stretch=1)

        self.setLayout(layout)
    
    def onTextChanged(self, text):
        self.content = text

    def delete(self):
        self.parent().layout().removeWidget(self)
        self.setParent(None)
        self.deleteLater()
