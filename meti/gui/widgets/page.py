from PySide6 import QtGui
from PySide6.QtCore import Qt
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
    QLayout,
)
from gui.widgets.button import IconButton, BackButton, AcceptButton
from gui.widgets.dialog import DialogTemplate

class Page(QWidget):
    def __init__(self, name, title, parent=None):
        super().__init__(parent)
        self.name = name
        self.setObjectName(self.name)

        self.initHead(title)
        self.initBody()
        self.initScrollArea()

        self.initLayout()

    def initHead(self, title):
        self.head = QWidget()
        self.head.setObjectName(self.name + "Head")
        layout = QHBoxLayout(self.head)
        layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel(title)
        title.setObjectName(self.name + "Title")
        layout.addWidget(title)

        buttons = self.initHeadButtons()
        layout.addWidget(buttons)

        self.head.setFixedHeight(100)

    def initHeadButtons(self):
        return Widget()

    def initBody(self):
        self.body = QWidget()
        self.body.setObjectName(self.name + "Body")
        layout = QVBoxLayout(self.body)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(0, 0, 0, 0)

    def initScrollArea(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName(self.name + "Body")
        self.scroll_area.setWidget(self.body)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def initLayout(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.head)
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)
