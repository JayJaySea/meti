from PySide6.QtCore import  QSize, Qt, QTime, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QStackedWidget,
)

from meti.gui.login import Login
from meti.gui.project import Project
from meti.db import model

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Meti")
        self.initCentralWidget()

    def initCentralWidget(self):
        self.stack = QStackedWidget()

        login = Login(self)
        login.database_decrypted.connect(self.onDatabaseDecrypted)

        self.stack.addWidget(login)
        self.setCentralWidget(self.stack)
        
    def onDatabaseDecrypted(self):
        project = model.getLastAccessedProject()
        self.displayProject(project)

    def onProjectCreated(self):
        old_project = self.stack.widget(1)
        self.stack.removeWidget(old_project)
        old_project.deleteLater()

        project = model.getLastAccessedProject()
        self.displayProject(project)

    def onOpenProject(self, project):
        old_project = self.stack.widget(1)
        self.stack.removeWidget(old_project)
        old_project.deleteLater()

        self.displayProject(project)

    def displayProject(self, project):
        model.updateLastAccessedProject(project["id"])
        project_widget = Project(project, parent=self)
        project_widget.project_created.connect(self.onProjectCreated)
        project_widget.open_project.connect(self.onOpenProject)
        self.stack.addWidget(project_widget)
        self.stack.setCurrentIndex(1)
