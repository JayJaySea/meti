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

from meti.gui.widgets.button import DeleteButton, UpDownButton, AddButton, BackButton, AcceptButton, EditButton, PushButton, DuplicateButton
from meti.db import model

class Checklist(QFrame):
    checklist_moved = Signal()
    position_changed = Signal(int, int)
    delete_checklist = Signal(str)
    edit_checklist = Signal(str)
    checkbox_state_changed = Signal(object, object, int)

    def __init__(self, title, items, position, grid_size, proxy=None, parent=None, id=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.grabbed = False
        self.grabbed_pos = None
        self.title = title
        self.position = position
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
        self.title = QLabel(self.title)
        self.title.setObjectName("ChecklistTitle")
        layout.addWidget(self.title, stretch=1)
        placeholder = QWidget()
        placeholder.setFixedSize(50, 50)
        layout.addWidget(placeholder)
        layout.addWidget(EditButton(lambda: self.edit_checklist.emit(self.id)))
        layout.addWidget(DeleteButton(lambda: self.delete_checklist.emit(self.id)))

        self.head = QWidget()
        self.head.setObjectName("ChecklistHead")
        self.head.setLayout(layout)

    def initBody(self, checks):
        self.body_layout = QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 5)
        self.body_layout.setSpacing(0)
        self.checks = {}
        for check in checks:
            checkbox = CheckBox(check["content"], check["state"], id=check["id"])
            checkbox.state_changed.connect(self.checkBoxStateChanged)
            self.checks[checkbox] = check

            self.body_layout.addWidget(checkbox)

        self.body = QWidget()
        self.body.setObjectName("ChecklistBody")
        self.body.setLayout(self.body_layout)

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
        self.updateLines()

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
        self.updateLines()

    def updateState(self, state_str, index, new_value):
        state_list = list(state_str)
        state_list[index] = new_value
        return "".join(state_list)

    def removeLine(self, line):
        if line in self.connected_lines:
            self.connected_lines.remove(line)

    def updateLines(self):
        for line in self.connected_lines:
            line.updatePath()

    def setTitle(self, title):
        self.title.setText(title)

    def setChecks(self, checks):
        while self.body_layout.count():
            widget = self.body_layout.takeAt(0).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        self.checks = {}
        for check in checks:
            checkbox = CheckBox(check["content"], check["state"], id=check["id"])
            checkbox.state_changed.connect(self.checkBoxStateChanged)
            self.checks[checkbox] = check
            self.body_layout.addWidget(checkbox)

        self.body_layout.activate()
        self.repaint()

    def checkBoxStateChanged(self, id, state):
        self.checkbox_state_changed.emit(self.id, id, state)


class CheckBox(QFrame):
    state_changed = Signal(object, int)

    def __init__(self, label, state, id=None, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setObjectName("CheckBoxWidget")

        self.label = label
        self.state = state
        self.hovering = False
        self.id = id

        self.initLayout()
        if self.state == 1:
            self.activeStyle()
        if self.state == 2:
            self.nonApplicableStyle()

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

        if not self.state:
            self.hoverStyle()
        event.accept()

    def leaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        if not self.state:
            self.defaultStyle()
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            if self.id:
                self.state = 2 if self.state != 2 else 0
        elif event.button() == Qt.LeftButton:
            self.state = 1 if self.state != 1 else 0

        if self.state == 2:
            self.nonApplicableStyle()
            self.state_changed.emit(self.id, 2)
        elif self.state:
            self.activeStyle()
            if self.id:
                self.state_changed.emit(self.id, 1)
        else:
            self.hoverStyle()
            if self.id:
                self.state_changed.emit(self.id, 0)

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

        if not self.state:
            if not self.hovering:
                self.defaultStyle()
            elif self.state:
                self.activeStyle()

        event.accept()

    def defaultStyle(self):
        self.indicator.setProperty("hover", False)
        self.indicator.setProperty("active", False)
        self.label.setProperty("strikethrough", False)
        self.refreshStyle()

    def hoverStyle(self):
        self.indicator.setProperty("active", False)
        self.indicator.setProperty("hover", True)
        self.label.setProperty("strikethrough", False)
        self.refreshStyle()

    def activeStyle(self):
        self.indicator.setProperty("hover", False)
        self.indicator.setProperty("active", True)
        self.label.setProperty("strikethrough", False)
        self.refreshStyle()

    def nonApplicableStyle(self):
        self.indicator.setProperty("hover", False)
        self.indicator.setProperty("active", True)
        self.label.setProperty("strikethrough", True)
        self.refreshStyle()

    def refreshStyle(self):
        self.indicator.style().unpolish(self.indicator)
        self.indicator.style().polish(self.indicator)
        self.indicator.update()

        self.label.style().unpolish(self.label)
        self.label.style().polish(self.label)
        self.label.update()

class CreateChecklistButton(QFrame):
    pressed = Signal(QEvent)
    released = Signal(QEvent)

    def __init__(self, parent=None, proxy=None, id=None):
        super().__init__(parent)
        self.setObjectName("TransparentContainer")
        self.resize(14, 14)

        self.proxy = proxy
        self.id = id
        self.grabbed = False
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
        if event.button() == Qt.LeftButton:
            self.proxy.setCursor(Qt.ArrowCursor)
            self.inner_circle.show()
            self.pressed.emit(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.inner_circle.hide()
            self.released.emit(event)
            self.grabbed = False

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

class ChecklistEditor(QStackedWidget):
    checklist_ready = Signal(str, list, str, object)
    back = Signal()

    def __init__(self, title=None, items=None, id=None, is_template=False, parent=None):
        super().__init__(parent)
        self.title = title
        self.checks = items
        self.id = id
        self.is_template = is_template

        self.setObjectName("Dialog")
        self.initLayout()
    
    def setId(self, id):
        if not self.is_template:
            if id:
                self.pull_button.hide()
                self.push_button.show()
            else:
                self.pull_button.show()
                self.push_button.hide()
        self.id = id

    def initLayout(self):
        input_label = QLabel("CHECKLIST NAME")
        input_label.setObjectName("TextInputLabel")
        input_label.setAlignment(Qt.AlignCenter)
        self.checklist_name_input = QLineEdit()
        self.checklist_name_input.setObjectName("TextInput")
        items_label = QLabel("ITEMS")
        items_label.setObjectName("TextInputLabel")
        items_label.setAlignment(Qt.AlignCenter)
        self.item_editor = ItemEditor(self.checks, is_template=self.is_template)
        buttons = QHBoxLayout()
        buttons.addWidget(BackButton(lambda: self.back.emit()))
        buttons.addStretch()
        if not self.is_template:
            self.push_button = PushButton(lambda: self.pushToTemplate())
            self.push_button.hide()
            buttons.addWidget(self.push_button)
            self.pull_button = DuplicateButton(lambda: self.enterTemplatePicker())
            buttons.addWidget(self.pull_button)

        buttons.addWidget(AcceptButton(lambda: self.checklistReady()))

        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(input_label)
        layout.addWidget(self.checklist_name_input)
        layout.addWidget(items_label)
        layout.addWidget(self.item_editor)
        layout.addLayout(buttons)

        self.editor = QFrame()
        self.editor.setLayout(layout)


        self.addWidget(self.editor)
    
    def pushToTemplate(self):
        title = self.checklist_name_input.text()
        if not title or not self.item_editor.itemsFilled():
            return

        checks = self.item_editor.getItems()
        checklist = model.getChecklist(self.id)
        template_id = checklist["template_id"]
        if template_id:
            model.updateTemplateChecklist(template_id, title)
            model.deleteTemplateChecks(template_id)
        else:
            template_id = model.createChecklistTemplate(title)
            model.setTemplateForChecklist(self.id, template_id)

        for check in checks:
            model.createTemplateCheck(template_id, check["content"], check["position"])

    def enterTemplatePicker(self):
        picker = TemplatePicker(model.getChecklistTemplates())
        picker.back.connect(self.leaveTemplatePicker)
        picker.template_picked.connect(self.pullFromTemplate)
        self.addWidget(picker)
        self.setCurrentIndex(1)

    def leaveTemplatePicker(self):
        self.removeWidget(self.widget(1))
        self.setCurrentIndex(0)

    def pullFromTemplate(self, template):
        if not template:
            return

        self.removeWidget(self.widget(1))
        self.setCurrentIndex(0)

        title = template["title"]
        checks = []
        for check in template["checks"]:
            check["state"] = 0
            check.pop("id", None)
            check.pop("template_id", None)
            checks.append(check)

        self.checklist_ready.emit(title, checks, self.id, template["id"])

    def checklistReady(self):
        title = self.checklist_name_input.text()
        if not title or not self.item_editor.itemsFilled():
            return

        items = self.item_editor.getItems()
        self.checklist_ready.emit(title, items, self.id, None)

    def setChecklistName(self, text):
        self.checklist_name_input.setText(text)

    def setChecks(self, checks):
        self.item_editor.setChecks(checks)

    def reset(self):
        if self.widget(1):
            self.removeWidget(self.widget(1))
        self.setCurrentIndex(0)
        self.setChecklistName(None)
        self.setChecks(None)


class ItemEditor(QScrollArea):
    def __init__(self, items=None, is_template=False, parent=None):
        super().__init__(parent)
        self.checks = items if items else []
        self.dragging = False
        self.is_template = is_template
        self.setFixedSize(500, 300)

        self.setWidgetResizable(True)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self.setObjectName("ItemEditor")

        self.initLayout()

    def initLayout(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.addWidget(self.createAddButton())
        self.layout.addStretch()

        for item in self.checks:
            self.addItem(item)

        container = QFrame()
        container.setLayout(self.layout)

        self.setWidget(container)

    def createAddButton(self):
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 5, 0, 5)
        layout.setSpacing(0)
        layout.addStretch()
        layout.addWidget(AddButton(lambda: self.addItem()))
        layout.addStretch()

        add_new = QFrame()
        add_new.setLayout(layout)

        return add_new

    def addItem(self, item=None):
        if not item:
            item = {}

        item["widget"] = EditableItem(item.get("content"), item.get("id"))
        item["widget"].grabbed.connect(self.itemGrabbed)
        item["widget"].released.connect(self.itemReleased)
        item["widget"].moving.connect(self.itemMoving)
        self.layout.insertWidget(self.layout.count() - 2, item["widget"])
        
        if not item.get("id"):
            self.checks.append(item)

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
        checks = []
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if not isinstance(widget, EditableItem):
                continue

            if not widget.id:
                checks.append({
                    "content": widget.content,
                    "state": 0,
                    "position": i
                })
                continue

            for check in self.checks:
                if not widget.id == check["id"]:
                    continue

                c = {
                    "id": widget.id,
                    "content": widget.content,
                    "position": i
                }
                
                if not self.is_template:
                    c["checklist_id"] = check["checklist_id"]
                    c["state"] = check["state"]
                else:
                    c["template_id"] = check["template_id"]

                checks.append(c)
                break

        return checks

    def setChecks(self, checks):
        while self.layout.count():
            widget = self.layout.takeAt(0).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

        self.checks = checks if checks else []
        self.layout.addWidget(self.createAddButton())
        self.layout.addStretch()

        for check in self.checks:
            self.addItem(check)

class EditableItem(QFrame):
    grabbed = Signal()
    moving = Signal(QEvent)
    released = Signal()

    def __init__(self, content=None, id=None, parent=None):
        super().__init__(parent)
        self.content = content
        self.id = id

        self.setMaximumHeight(40)
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

class TemplatePicker(QFrame):
    back = Signal()
    template_picked = Signal(dict)

    def __init__(self, templates, parent=None):
        super().__init__(parent)
        self.picked = None
        self.initLayout(templates)

    def initLayout(self, templates):
        input_label = QLabel("CHOOSE TEMPLATE")
        input_label.setObjectName("TextInputLabel")
        input_label.setAlignment(Qt.AlignCenter)
        self.template_search = QLineEdit()
        self.template_search.setObjectName("TextInput")
        self.template_search.setPlaceholderText("Search...")
        self.template_search.textChanged.connect(self.searchTemplates)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.templates = {}
        for template in templates:
            template_widget = QPushButton(template["title"])
            template_widget.setFixedHeight(40)
            template_widget.toggled.connect(self.updatePicked)
            template_widget.setCheckable(True)
            template_widget.setObjectName("PickerItem")
            self.templates[template_widget] = template
            layout.addWidget(template_widget)

        layout.addStretch()
        container = QFrame()
        container.setLayout(layout)

        items = QScrollArea()
        items.setWidget(container)
        items.setObjectName("BorderlessContainer")
        items.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(input_label)
        layout.addWidget(self.template_search)
        layout.addWidget(items)

        buttons = QHBoxLayout()
        buttons.addWidget(BackButton(lambda: self.back.emit()))
        buttons.addStretch()
        buttons.addWidget(AcceptButton(lambda: self.template_picked.emit(self.picked)))
        layout.addLayout(buttons)

        self.setLayout(layout)

    def updatePicked(self, state):
        if self.picked:
            self.picked["widget"].setChecked(False)

        self.picked = self.templates[self.sender()] if state else None

        if self.picked:
            self.picked["widget"] = self.sender()

    def searchTemplates(self, text):
        if self.picked:
            self.picked["widget"].setChecked(False)

        first = True
        for template_widget in self.templates:
            template = self.templates[template_widget]

            if not text.lower() in template["title"].lower():
                template_widget.hide()
            else:
                if first:
                    template_widget.setChecked(True)
                    first = False
                template_widget.show()

class TemplatePickerLite(QFrame):
    back = Signal()
    template_picked = Signal(dict)

    def __init__(self, templates, parent=None):
        super().__init__(parent)
        self.picked = None
        self.setObjectName("TransparentContainer")
        self.initLayout(templates)

    def initLayout(self, templates):
        input_label = QLabel("AVAILABLE TEMPLATES")
        input_label.setObjectName("TextInputLabel")
        input_label.setAlignment(Qt.AlignCenter)
        self.template_search = QLineEdit()
        self.template_search.setObjectName("TextInput")
        self.template_search.setPlaceholderText("Search...")
        self.template_search.textChanged.connect(self.searchTemplates)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.templates = {}
        for template in templates:
            template_widget = QPushButton(template["title"])
            template_widget.setFixedHeight(40)
            template_widget.toggled.connect(self.updatePicked)
            template_widget.setCheckable(True)
            template_widget.setObjectName("PickerItem")
            self.templates[template_widget] = template
            layout.addWidget(template_widget)

        layout.addStretch()
        container = QFrame()
        container.setLayout(layout)

        items = QScrollArea()
        items.setWidget(container)
        items.setObjectName("BorderlessContainer")
        items.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(input_label)
        layout.addWidget(self.template_search)
        layout.addWidget(items)

        self.setLayout(layout)

    def updatePicked(self, state):
        if self.picked:
            self.picked["widget"].setChecked(False)

        self.picked = self.templates[self.sender()] if state else None

        if self.picked:
            self.picked["widget"] = self.sender()

    def searchTemplates(self, text):
        if self.picked:
            self.picked["widget"].setChecked(False)

        first = True
        for template_widget in self.templates:
            template = self.templates[template_widget]

            if not text.lower() in template["title"].lower():
                template_widget.hide()
            else:
                if first:
                    template_widget.setChecked(True)
                    first = False
                template_widget.show()
