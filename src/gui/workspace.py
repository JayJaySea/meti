from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QRect, Property 
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
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
from gui.widgets.checklist import Checklist

class Workspace(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(None)
        self.setObjectName("Workspace")
        self.grid_color = QColor("#cccccc")  # default
        self.grid_size = 50
        self.project = model.getLastAccessedProject()

        self.initChecklists()
        self.adjustChecklistsSize()

    def getGridColor(self):
        return self.grid_color

    def setGridColor(self, color):
        if isinstance(color, QColor):
            self.grid_color = color
        else:
            self.grid_color = QColor(color)

    gridColor = Property(QColor, getGridColor, setGridColor)

    def initChecklists(self):
        self.checklists = {}
        checklists = model.getProjectChecklists(self.project["id"])
        for checklist in checklists:
            position = {
                "x": checklist["position_x"],
                "y": checklist["position_y"],
            }

            checklist_widget = Checklist(checklist["title"], checklist["checks"], position, checklist["state"], self.grid_size, parent=self)
            checklist_widget.state_changed.connect(self.onChecklistStateChanged)
            self.checklists[checklist_widget] = checklist

    def onChecklistStateChanged(self, state):
        model.updateChecklistState(self.checklists[self.sender()]["id"], state)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.grid_color)
        pen.setWidth(1)
        painter.setPen(pen)

        rect = self.rect()
        left = rect.left()
        top = rect.top()
        right = rect.right()
        bottom = rect.bottom()

        x = left
        while x <= right:
            painter.drawLine(x, top, x, bottom)
            x += self.grid_size

        y = top
        while y <= bottom:
            painter.drawLine(left, y, right, y)
            y += self.grid_size

    def adjustChecklistsSize(self):
        for checklist in self.checklists:
            checklist.adjustSize()

            width = checklist.width()
            new_width = ((width + self.grid_size - 1)//self.grid_size)*self.grid_size

            height = checklist.height()
            new_height = ((height + self.grid_size - 1)//self.grid_size)*self.grid_size
            checklist.setMinimumSize(new_width, new_height)
