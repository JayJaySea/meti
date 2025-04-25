from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from PySide6.QtCore import Qt, QRect, Property, QRectF, QPointF
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
from gui.widgets.checklist import Checklist
from util import centerLeft, centerRight, topCenter, bottomCenter

class Workspace(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(None)
        self.setObjectName("Workspace")
        self.workspace_width = 5000
        self.workspace_height = 5000
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(0, 0, self.workspace_width, self.workspace_height)
        self.setRenderHints(self.renderHints() | QPainter.Antialiasing)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.is_panning = False
        self.last_mouse_pos = None
        self.zoomed_out = False
        self.parents = None
        self.grid_color = QColor("#cccccc")
        self.line_color = QColor("#cccccc")
        self.grid_size = 50
        self.project = model.getLastAccessedProject()

        self.initChecklists()
        self.adjustChecklistsSize()

    def initChecklists(self):
        self.checklists = {}
        checklists = model.getProjectChecklists(self.project["id"])
        self.parents = self.findParents(checklists)
        for checklist in checklists:
            position = {
                "x": checklist["position_x"],
                "y": checklist["position_y"],
            }

            proxy = TrackingProxy()
            proxy.setFlags(
                QGraphicsItem.ItemIsMovable |
                QGraphicsItem.ItemIsSelectable |
                QGraphicsItem.ItemSendsGeometryChanges
            )
            self.scene.addItem(proxy)

            checklist["widget"] = Checklist(checklist["title"], checklist["checks"], position, checklist["state"], self.grid_size, proxy=proxy, id=checklist["id"])
            proxy.setWidget(checklist["widget"])

            checklist["widget"].state_changed.connect(self.onChecklistStateChanged)
            checklist["widget"].position_changed.connect(self.onChecklistPositionChanged)

            self.checklists[checklist["id"]] = checklist

    def findParents(self, checklists):
        parents = {}
        for checklist in checklists:
            parent = checklist["parent"]
            if parent:
                if parent in parents:
                    parents[parent].append(checklist["id"])
                else:
                    parents[parent] = [ checklist["id"] ]

        return parents

    def adjustChecklistsSize(self):
        for checklist_id in self.checklists:
            checklist = self.checklists[checklist_id]["widget"]
            checklist.adjustSize()

            width = checklist.width()
            new_width = ((width + self.grid_size - 1)//self.grid_size)*self.grid_size

            height = checklist.height()
            new_height = ((height + self.grid_size - 1)//self.grid_size)*self.grid_size
            checklist.setMinimumSize(new_width, new_height)

    def getGridColor(self):
        return self.grid_color

    def setGridColor(self, color):
        if isinstance(color, QColor):
            self.grid_color = color
        else:
            self.grid_color = QColor(color)

    gridColor = Property(QColor, getGridColor, setGridColor)

    def getLineColor(self):
        return self.line_color

    def setLineColor(self, color):
        if isinstance(color, QColor):
            self.line_color = color
        else:
            self.line_color = QColor(color)

    lineColor = Property(QColor, getLineColor, setLineColor)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.zoomed_out:
                self.resetTransform()
                self.zoomed_out = False
            else:
                cursor_pos = event.pos()  # position of the cursor on the view
                scene_pos = self.mapToScene(cursor_pos)  # convert to scene coordinates
                
                # Define the rect (2000x2000) centered around the cursor position
                rect = QRectF(scene_pos.x() - 1250, scene_pos.y() - 1250, 2500, 2500)
                self.fitInView(rect, Qt.KeepAspectRatio)
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
        if not hasattr(self, "grid_initialized"):
            self.grid_initialized = True
            self.grid = GridBackground(grid_size=50, scene_width=self.workspace_width, scene_height=self.workspace_height, grid_color=self.gridColor)
            self.scene.addItem(self.grid)
        if not hasattr(self, "lines_initialized"):
            self.lines_initialized = True
            self.assignParents(self.parents)

    def assignParents(self, parents):
        for parent_id in parents:
            parent = self.checklists[parent_id]["widget"]
            children = parents[parent_id]
            for child_id in children:
                child = self.checklists[child_id]["widget"]

                line = LineItem(parent.proxy, child.proxy, self.lineColor)
                self.scene.addItem(line)

                parent.proxy.addLine(line)
                child.proxy.addLine(line)

    def onChecklistStateChanged(self, state):
        model.updateChecklistState(self.sender().id, state)

    def onChecklistPositionChanged(self, new_x, new_y):
        model.updateChecklistPosition(self.sender().id, new_x, new_y)
        
class GridBackground(QGraphicsItem):
    def __init__(self, grid_size=100, scene_width=3000, scene_height=3000, grid_color="#cccccc"):
        super().__init__()
        self.grid_size = grid_size
        self.scene_width = scene_width
        self.scene_height = scene_height
        self.grid_color = grid_color
        self.setZValue(-1)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.scene_width, self.scene_height)

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(self.grid_color, 1))
        step = self.grid_size
        for x in range(0, int(self.scene_width), step):
            painter.drawLine(x, 0, x, self.scene_width)
        for y in range(0, int(self.scene_height), step):
            painter.drawLine(0, y, self.scene_height, y)

class LineItem(QGraphicsPathItem):
    def __init__(self, source_item, dest_item, color, radius = 15):
        super().__init__()
        self.source_item = source_item
        self.dest_item = dest_item
        self.setZValue(1000)
        self.radius = radius
        self.setPen(QPen(color, 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.updatePath()

    def updatePath(self):
        source_rect = self.source_item.sceneBoundingRect()
        dest_rect = self.dest_item.sceneBoundingRect()

        start = centerRight(source_rect)
        end = centerLeft(dest_rect)

        dx = abs(end.x() - start.x()) * 0.8
        ctrl1 = QPointF(start.x() + dx, start.y())
        ctrl2 = QPointF(end.x() - dx, end.y())

        path = QPainterPath(start)
        path.cubicTo(ctrl1, ctrl2, end)

        self.setPath(path)

class TrackingProxy(QGraphicsProxyWidget):
    def __init__(self):
        super().__init__()
        self.connected_lines = []

    def addLine(self, line):
        self.connected_lines.append(line)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for line in self.connected_lines:
                line.updatePath()
        return super().itemChange(change, value)
