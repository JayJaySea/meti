from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtCore import Qt, QRect, Property, QRectF
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsItem,
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
from gui.widgets.checklist import Checklist

class Workspace(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(None)
        self.setObjectName("Workspace")
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, 3000, 3000)
        self.setRenderHints(self.renderHints() | QPainter.Antialiasing)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.is_panning = False
        self.last_mouse_pos = None
        self.zoomed_out = False
        self.grid_color = QColor("#cccccc")
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

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.zoomed_out:
                self.resetTransform()
                self.zoomed_out = False
            else:
                self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)
                self.zoomed_out = True
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            item = self.scene.itemAt(scene_pos, self.transform())
        
            if item is None or isinstance(item, GridBackground):
                self.is_panning = True
                self.last_mouse_pos = event.pos()
                self.viewport().setCursor(Qt.ClosedHandCursor)
            else:
                self.is_panning = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_panning:
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            self.translate(delta.x() * -1, delta.y() * -1)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_panning = False
            self.viewport().setCursor(Qt.ArrowCursor)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        event.accept()

    def showEvent(self, event):
        super().showEvent(event)
        if not hasattr(self, "_grid_initialized"):
            self._grid_initialized = True
            self.grid = GridBackground(grid_size=50, scene_size=3000, grid_color=self.gridColor)
            self.scene.addItem(self.grid)

    def initChecklists(self):
        self.checklists = {}
        checklists = model.getProjectChecklists(self.project["id"])
        for checklist in checklists:
            position = {
                "x": checklist["position_x"],
                "y": checklist["position_y"],
            }

            proxy = QGraphicsProxyWidget()
            proxy.setFlags(
                QGraphicsItem.ItemIsMovable |
                QGraphicsItem.ItemIsSelectable |
                QGraphicsItem.ItemSendsGeometryChanges
            )
            checklist_widget = Checklist(checklist["title"], checklist["checks"], position, checklist["state"], self.grid_size, proxy=proxy)
            checklist_widget.show()
            proxy.setWidget(checklist_widget)
            self.scene.addItem(proxy)

            checklist_widget.state_changed.connect(self.onChecklistStateChanged)
            self.checklists[checklist_widget] = checklist

    def onChecklistStateChanged(self, state):
        model.updateChecklistState(self.checklists[self.sender()]["id"], state)
        
    def adjustChecklistsSize(self):
        for checklist in self.checklists:
            checklist.adjustSize()

            width = checklist.width()
            new_width = ((width + self.grid_size - 1)//self.grid_size)*self.grid_size

            height = checklist.height()
            new_height = ((height + self.grid_size - 1)//self.grid_size)*self.grid_size
            checklist.setMinimumSize(new_width, new_height)

class GridBackground(QGraphicsItem):
    def __init__(self, grid_size=100, scene_size=3000, grid_color="#cccccc"):
        super().__init__()
        self.grid_size = grid_size
        self.scene_size = scene_size
        self.grid_color = grid_color
        self.setZValue(-1)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.scene_size, self.scene_size)

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(self.grid_color, 1))
        step = self.grid_size
        for x in range(0, int(self.scene_size), step):
            painter.drawLine(x, 0, x, self.scene_size)
        for y in range(0, int(self.scene_size), step):
            painter.drawLine(0, y, self.scene_size, y)
