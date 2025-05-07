from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QRegion
from PySide6.QtCore import Qt, QRect, Property, QRectF, QPointF, QSize, QEvent, Signal
from PySide6.QtWidgets import (
    QTabWidget,
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
from gui.widgets.button import BackButton, AcceptButton, CloseButton, MenuButton, AddButton, OpenButton, EditButton
from gui.widgets.dialog import DialogTemplate
from gui.widgets.checklist import CheckBox, ChecklistEditor

class Project(QFrame):
    project_created = Signal()
    open_project = Signal(dict)
    open_project_template = Signal(dict)

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.setLayout(None)
        self.setObjectName("Project")
        self.project = project
        self.projects = model.getProjects()
        self.project_templates = model.getProjectTemplates()
        self.checklist_templates = model.getChecklistTemplates()
        self.workspace = Workspace(project, parent=self)
        self.create_project_dialog = DialogTemplate(self.initCreateProjectDialog(), self.window())
        self.main_menu_dialog = DialogTemplate(self.initMainMenu(), self.window())

        self.initTopMenu()

    def initTopMenu(self):
        self.menu_button = MenuButton(lambda: self.main_menu_dialog.show(), parent=self)
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

    def initMainMenu(self):
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.addTab(self.initManageProjectsMenu(), "PROJECTS")
        tabs.addTab(self.initManageTemplatesMenu(), "TEMPLATES")

        self.checklist_editor = ChecklistEditor()
        self.checklist_editor.checklist_ready.connect(self.checklistReady)
        self.checklist_editor.back.connect(lambda: self.main_menu.setCurrentIndex(0))

        self.main_menu = QStackedWidget()
        self.main_menu.setFixedHeight(500)
        self.main_menu.addWidget(tabs)
        self.main_menu.addWidget(self.checklist_editor)

        return self.main_menu

    def initManageProjectsMenu(self):
        layout = QVBoxLayout()
        for project in self.projects:
            hlayout = QHBoxLayout()
            button = OpenButton(lambda: (), id=project["id"])
            button.pressed.connect(self.openProject)
            hlayout.addWidget(button)
            label = QLabel(project["name"])
            label.setObjectName("ProjectNameAlt")
            label.setFixedHeight(40)
            hlayout.addWidget(label, stretch=1)
            layout.addLayout(hlayout)

        layout.addStretch()
        container = QFrame()
        container.setLayout(layout)

        menu = QScrollArea()
        menu.setWidget(container)
        menu.setObjectName("BorderlessContainer")
        menu.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 0, 10, 5)
        layout.addWidget(menu)

        menu_container = QFrame()
        menu_container.setObjectName("TabDialog")
        menu_container.setLayout(layout)

        return menu_container

    def initManageTemplatesMenu(self):
        templates = QTabWidget()
        templates.tabBar().setObjectName("SubTabBar")
        templates.addTab(self.initManageProjectTemplatesMenu(), "PROJECT")
        templates.addTab(self.initManageChecklistTemplatesMenu(), "CHECKLIST")

        return templates

    def initManageProjectTemplatesMenu(self):
        layout = QVBoxLayout()
        for project in self.project_templates:
            hlayout = QHBoxLayout()
            button = OpenButton(lambda: (), id=project["id"])
            button.pressed.connect(self.openProjectTemplate)
            hlayout.addWidget(button)
            label = QLabel(project["name"])
            label.setObjectName("ProjectNameAlt")
            label.setFixedHeight(40)
            hlayout.addWidget(label, stretch=1)
            layout.addLayout(hlayout)

        layout.addStretch()
        container = QFrame()
        container.setLayout(layout)

        manage_p_templates = QScrollArea()
        manage_p_templates.setWidget(container)
        manage_p_templates.setObjectName("BorderlessContainer")
        manage_p_templates.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 0, 10, 5)
        layout.addWidget(manage_p_templates)

        container = QFrame()
        container.setObjectName("TabDialog")
        container.setLayout(layout)

        return container

    def initManageChecklistTemplatesMenu(self):
        layout = QVBoxLayout()
        for template in self.checklist_templates:
            hlayout = QHBoxLayout()
            button = EditButton(lambda: (), id=template["id"])
            button.pressed.connect(self.editChecklistTemplate)
            hlayout.addWidget(button)
            label = QLabel(template["title"])
            label.setObjectName("ProjectName")
            label.setFixedHeight(40)
            hlayout.addWidget(label, stretch=1)
            layout.addLayout(hlayout)

        layout.addStretch()
        container = QFrame()
        container.setLayout(layout)

        manage_c_templates = QScrollArea()
        manage_c_templates.setWidget(container)
        manage_c_templates.setObjectName("BorderlessContainer")
        manage_c_templates.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 0, 10, 5)
        layout.addWidget(manage_c_templates)

        container = QFrame()
        container.setObjectName("TabDialog")
        container.setLayout(layout)

        return container

    def openProject(self, project_id):
        for project in self.projects:
            if project["id"] == project_id:
                self.open_project.emit(project)
                self.main_menu_dialog.hide()

    def openProjectTemplate(self, template_id):
        for template in self.project_templates:
            if template["id"] == template_id:
                self.open_project_template.emit(template)
                self.main_menu_dialog.hide()

    def editChecklistTemplate(self, template_id):
        template = next((template for template in self.checklist_templates if template["id"] == template_id), None)

        if not template:
            return

        self.checklist_editor.setChecklistName(template["title"])
        self.checklist_editor.setChecks(template["checks"])
        self.checklist_editor.setId(template["id"])

        self.main_menu.setCurrentIndex(1)

    def checklistReady(self, title, checks, id):
        self.main_menu.setCurrentIndex(0)
        self.checklist_editor.setChecklistName(None)
        self.checklist_editor.setChecks(None)

        template = next((template for template in self.checklist_templates if template["id"] == id), None)
        template["title"] = title

        check_ids = {check.get("id") for check in checks}
        deleted = [check for check in template["checks"] if check.get("id") not in check_ids]
        for check in deleted:
            model.deleteTemplateCheck(check["id"])

        for check in checks:
            if check.get("id"):
                model.updateTemplateCheck(check["id"], check["content"], check["position"])
            else:
                id = model.createTemplateCheck(template["id"], check["content"], check["position"])
                check["id"] = id

        template["checks"] = checks

    def resizeEvent(self, event):
        self.updateRects()
        self.main_menu_dialog.resizeEvent(event)
        self.create_project_dialog.resizeEvent(event)

    def showEvent(self, event):
        self.updateRects()

    def updateRects(self):
        self.workspace.resize(self.size())
        self.menu_button.move(10, 10)
        self.add_button.move(self.menu_button.width() + 20, 10)
        self.project_name.move(self.size().width()/2 - self.project_name.width()/2, 10)
        self.close_button.move(self.size().width() - self.close_button.width() - 10, 10)
