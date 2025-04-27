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
from gui.widgets.checklist import Checklist, CreateChecklistButton, CreateChecklistDestination
from util import centerLeft, centerRight, topCenter, bottomCenter

class Workspace(QGraphicsView):
    def __init__(self, project, parent=None):
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

        self.project = project
        self.is_panning = False
        self.last_mouse_pos = None
        self.zoomed_out = False
        self.parents = None
        self.grid_color = QColor("#cccccc")
        self.line_color = QColor("#cccccc")
        self.grid_size = 50

        proxy = QGraphicsProxyWidget()
        self.scene.addItem(proxy)
        self.create_checklist_destination = CreateChecklistDestination(proxy=proxy)
        proxy.setWidget(self.create_checklist_destination)
        self.create_checklist_destination.hide()
        self.creating_checklist = False
        self.creator_line = None

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

            proxy = QGraphicsProxyWidget()
            self.scene.addItem(proxy)

            checklist["widget"] = Checklist(checklist["title"], checklist["checks"], position, checklist["state"], self.grid_size, proxy=proxy, id=checklist["id"])
            proxy.setWidget(checklist["widget"])

            checklist["widget"].state_changed.connect(self.onChecklistStateChanged)
            checklist["widget"].position_changed.connect(self.onChecklistPositionChanged)
            checklist["widget"].checklist_moved.connect(self.onChecklistMoved)

            proxy = QGraphicsProxyWidget()
            proxy.setZValue(100)
            self.scene.addItem(proxy)
            checklist["creator"] = CreateChecklistButton(proxy=proxy)
            checklist["creator"].pressed.connect(self.checklistCreatorPressed)
            checklist["creator"].released.connect(self.checklistCreatorReleased)
            proxy.setWidget(checklist["creator"])

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
            scene_pos = self.mapToScene(event.pos())
            item = self.scene.itemAt(scene_pos, self.transform())
            if not isinstance(item, GridBackground):
                return

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
        if self.creating_checklist:
            if not self.creator_line.isVisible():
                self.creator_line.show()
                self.create_checklist_destination.show()

            scene_pos = self.mapToScene(event.pos())
            new_x = scene_pos.x() - self.create_checklist_destination.width()/2
            new_y = scene_pos.y() - self.create_checklist_destination.height()/2
            self.create_checklist_destination.move(new_x, new_y)
            self.creator_line.updatePath()

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
        if not hasattr(self, "creators_initialized"):
            self.creators_initialized = True
            self.updateCreatorsPosition()

    def assignParents(self, parents):
        for parent_id in parents:
            parent = self.checklists[parent_id]["widget"]
            children = parents[parent_id]
            for child_id in children:
                child = self.checklists[child_id]["widget"]

                line = LineItem(parent.proxy, child.proxy, self.lineColor)
                self.scene.addItem(line)

                parent.addLine(line)
                child.addLine(line)

    def updateCreatorsPosition(self):
        for checklist in self.checklists.values():
            new_x = checklist["widget"].x() + checklist["widget"].width() - checklist["creator"].width()/2
            new_y = checklist["widget"].y() + checklist["widget"].height()/2 - checklist["creator"].height()/2
            checklist["creator"].move(new_x, new_y)

    def onChecklistStateChanged(self, state):
        model.updateChecklistState(self.sender().id, state)

    def onChecklistMoved(self):
        self.updateCreatorsPosition()

    def onChecklistPositionChanged(self, new_x, new_y):
        model.updateChecklistPosition(self.sender().id, new_x, new_y)
        self.updateCreatorsPosition()

    def checklistCreatorPressed(self, event):
        self.creating_checklist = True
        self.creator_line = LineItem(self.sender().proxy, self.create_checklist_destination.proxy, self.lineColor)
        self.creator_line.hide()
        self.scene.addItem(self.creator_line)

    def checklistCreatorReleased(self, event):
        self.creating_checklist = False
        self.scene.removeItem(self.creator_line)
        self.creator_line = None
        self.create_checklist_destination.hide()
        
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
    def __init__(self, source_item, dest_item, color, radius=15):
        super().__init__()
        self.source_item = source_item
        self.dest_item = dest_item
        self.setZValue(10)
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
