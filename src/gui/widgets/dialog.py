from PySide6.QtWidgets import (
    QApplication, QMainWindow, QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QGraphicsOpacityEffect, QFrame
)
from PySide6.QtCore import Qt
import sys

class DialogTemplate(QFrame):
    def __init__(self, dialog, window):
        super().__init__(window)

        print(window.rect())
        self.setGeometry(window.rect())
        self.setFixedSize(window.width(), window.height())
        self.setStyleSheet("DialogTemplate{background-color: rgba(0,0,0,100)}")
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.dialog = dialog
        self.dialog.setParent(self)
        self.dialog.move(
            (self.width() - self.dialog.width()) // 2,
            (self.height() - self.dialog.height()) // 2
        )
        self.dialog.show()

    def destroy(self):
        self.dialog.setParent(None)
        self.dialog.deleteLater()
        self.setParent(None)
        self.deleteLater()
