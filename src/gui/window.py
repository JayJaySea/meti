from PySide6.QtCore import  QSize, Qt, QTime, Slot
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QStackedWidget,
)

from gui.login import Login
from gui.workspace import Workspace

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
        
    @Slot()
    def onDatabaseDecrypted(self):
        self.stack.addWidget(Workspace(self))
        self.stack.setCurrentIndex(1)
