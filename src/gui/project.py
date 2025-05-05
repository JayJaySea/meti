from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QRegion
from PySide6.QtCore import Qt, QRect, Property, QRectF, QPointF, QSize, QEvent, Signal
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsItem,
    QGraphicsPathItem,
    QGraphicsLineItem,
    QGraphicsScene,
    QGraphicsProxyWidget,
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

from db import model
from gui.workspace import Workspace
from gui.widgets.button import BackButton, AcceptButton, CloseButton, MenuButton, AddButton, OpenButton
from gui.widgets.dialog import DialogTemplate
from gui.widgets.checklist import CheckBox

class Project(QFrame):
    project_created = Signal()
    open_project = Signal(dict)

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.setLayout(None)
        self.setObjectName("Project")
        self.project = project
        self.projects = model.getProjects()
        self.workspace = Workspace(project, parent=self)
        self.create_project_dialog = DialogTemplate(self.initCreateProjectDialog(), self.window())
        self.open_project_dialog = DialogTemplate(self.initOpenProjectDialog(), self.window())

        self.initTopMenu()

    def initTopMenu(self):
        self.menu_button = MenuButton(lambda: self.open_project_dialog.show(), parent=self)
        self.add_button = AddButton(lambda: self.create_project_dialog.show(), parent=self)
        self.project_name = QLabel(self.project["name"], self)
        self.project_name.setObjectName("ProjectName")
        self.project_name.setFixedHeight(40)
        self.close_button = CloseButton(lambda: QApplication.quit(), parent=self)

    def initCreateProjectDialog(self):
        input_label = QLabel("PROJECT NAME")
        input_label.setObjectName("TextInputLabel")
        input_label.setAlignment(Qt.AlignCenter)
        self.project_name_input = QLineEdit()
        self.project_name_input.setObjectName("TextInput")
        self.template_checkbox = CheckBox("IS TEMPLATE", False)
        self.template_checkbox.label.setProperty("alt-font", True)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.addWidget(input_label)
        layout.addWidget(self.project_name_input)

        center_checkbox = QHBoxLayout()
        center_checkbox.addStretch()
        center_checkbox.addWidget(self.template_checkbox)
        center_checkbox.addStretch()
        layout.addLayout(center_checkbox)
        layout.addStretch()

        buttons = QHBoxLayout()
        buttons.addWidget(BackButton(lambda: self.create_project_dialog.hide()))
        buttons.addStretch()
        buttons.addWidget(AcceptButton(lambda: self.createProject()))
        layout.addLayout(buttons)

        creator = QWidget()
        creator.setLayout(layout)
        creator.setObjectName("Dialog")
        creator.setFixedSize(300, 185)

        return creator

    def createProject(self):
        project_name = self.project_name_input.text()
        is_template = True if self.template_checkbox.state else False
        model.createProject(project_name, is_template)
        self.create_project_dialog.hide()
        self.project_created.emit()

    def initOpenProjectDialog(self):
        layout = QVBoxLayout()
        for project in self.projects:
            hlayout = QHBoxLayout()
            button = OpenButton(lambda: (), id=project["id"])
            button.pressed.connect(self.openProject)
            hlayout.addWidget(button)
            label = QLabel(project["name"])
            label.setObjectName("ProjectName")
            hlayout.addWidget(label, stretch=1)
            layout.addLayout(hlayout)

        dialog = QFrame()
        dialog.setLayout(layout)
        dialog.setObjectName("Dialog")
        return dialog

    def openProject(self, project_id):
        for project in self.projects:
            if project["id"] == project_id:
                self.open_project.emit(project)
                self.open_project_dialog.hide()

    def resizeEvent(self, event):
        self.updateRects()
        self.open_project_dialog.resizeEvent(event)
        self.create_project_dialog.resizeEvent(event)

    def showEvent(self, event):
        self.updateRects()

    def updateRects(self):
        self.workspace.resize(self.size())
        self.menu_button.move(10, 10)
        self.add_button.move(self.menu_button.width() + 20, 10)
        self.project_name.move(self.size().width()/2 - self.project_name.width()/2, 10)
        self.close_button.move(self.size().width() - self.close_button.width() - 10, 10)
