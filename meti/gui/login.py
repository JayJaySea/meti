from PySide6.QtWidgets import QApplication
from PySide6 import QtGui
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
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
from meti.gui.widgets.button import IconButton, BackButton, AcceptButton
from meti.db import model
from time import sleep

class Login(QWidget):
    database_decrypted = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.initDialog()
        self.initLayout()

    def initDialog(self):
        title = QLabel("METI")
        title.setAlignment(Qt.AlignCenter)
        title.setObjectName("LoginTitle")
        subtitle = QLabel("BY JJS")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("LoginSubTitle")

        password_label = QLabel("PASSWORD")
        password_label.setObjectName("LoginPasswordLabel")

        if not model.databaseExists():
            password_label = QLabel("SET DATABASE PASSWORD")

        password_label.setAlignment(Qt.AlignCenter)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_error = QLabel("INCORRECT PASSWORD")
        self.login_error.setAlignment(Qt.AlignCenter)
        self.login_error.setObjectName("LoginError")
        sp_retain = self.login_error.sizePolicy();
        sp_retain.setRetainSizeWhenHidden(True);
        self.login_error.setSizePolicy(sp_retain);
        self.login_error.hide()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch()
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_error)
        layout.addStretch()

        buttons = QHBoxLayout()
        back_button = BackButton()
        back_button.clicked.connect(lambda: QApplication.instance().quit())
        buttons.addWidget(back_button)
        buttons.addStretch()
        accept_button = AcceptButton()
        accept_button.clicked.connect(lambda: self.verifyLogin())
        buttons.addWidget(accept_button)
        layout.addLayout(buttons)

        self.dialog = QWidget()
        self.dialog.setLayout(layout)
        self.dialog.setObjectName("LoginDialog")
        self.dialog.setFixedSize(400, 300)

    def initLayout(self):
        layout = QVBoxLayout()
        layout.addWidget(self.dialog, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def verifyLogin(self):
        password = self.password_input.text()
        if not model.databaseExists():
            model.createDatabase(password)
            
        if model.decryptDatabase(password):
            self.database_decrypted.emit()
        else:
            self.password_input.setText("")
            self.login_error.show()

    def refreshStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return:
            self.verifyLogin()
