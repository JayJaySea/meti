from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from PySide6.QtCore import Qt, QRect, Property, QRectF, QPointF, QTimer
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

import math
from db import model
from gui.widgets.checklist import Checklist, CreateChecklistButton, CreateChecklistDestination, ChecklistEditor
from gui.widgets.dialog import DialogTemplate
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

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.MinimalViewportUpdate)
        self.setOptimizationFlags(QGraphicsView.DontAdjustForAntialiasing | 
                                  QGraphicsView.DontSavePainterState)
        self.setRenderHint(QPainter.Antialiasing, True)  # Enable only when needed
        
        # For high-DPI displays
        self.setRenderHint(QPainter.SmoothPixmapTransform, False)
        
        # Scroll settings for better performance
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Viewport settings
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setCacheMode(QGraphicsView.CacheBackground)

        self.project = project
        self.is_panning = False
        self.last_mouse_pos = None
        self.zoomed_out = self.project["zoomed_out"]
        self.parents = None
        self.grid_color = QColor("#cccccc")
        self.line_color = QColor("#cccccc")
        self.grid_size = 50
        self.creator_checklist_id = None

        proxy = QGraphicsProxyWidget()
        self.scene.addItem(proxy)
        self.create_checklist_destination = CreateChecklistDestination(proxy=proxy)
        proxy.setWidget(self.create_checklist_destination)
        self.create_checklist_destination.hide()

        self.checklist_editor = ChecklistEditor()
        self.checklist_editor.checklist_ready.connect(self.checklistReady)
        self.checklist_editor_dialog = DialogTemplate(self.checklist_editor, self.parent().window())
        self.creating_checklist = False
        self.creator_line = None

        self.initRoot()
        self.initChecklists()
        self.assignRootChecklists()
        self.adjustChecklistsSize()

    def initRoot(self):
        self.root = {}
        self.root["widget"] = QLabel(self.project["name"], alignment=Qt.AlignmentFlag.AlignCenter)
        self.root["widget"].setObjectName("ProjectName")
        self.root["widget"].adjustSize()

        width = self.root["widget"].width()
        new_width = ((width + self.grid_size - 1)//self.grid_size)*self.grid_size
        self.root["widget"].resize(new_width, self.grid_size)
        self.root["widget"].move(self.grid_size, self.workspace_height//100*self.grid_size)

        proxy = QGraphicsProxyWidget()
        proxy.setWidget(self.root["widget"])
        self.scene.addItem(proxy)

        proxy = QGraphicsProxyWidget()
        proxy.setZValue(100)
        self.root["creator"] = CreateChecklistButton(proxy=proxy, id=self.project["id"])
        self.root["creator"].pressed.connect(self.checklistCreatorPressed)
        self.root["creator"].released.connect(self.checklistCreatorReleased)
        self.root["creator"].adjustSize()
        self.root["creator"].move(
            self.root["widget"].x() + self.root["widget"].width() - self.root["creator"].width()/2,
            self.root["widget"].y() + self.root["widget"].height()/2 - self.root["creator"].height()/2,
        )
        proxy.setWidget(self.root["creator"])
        self.scene.addItem(proxy)

    def initChecklists(self):
        self.checklists = {}
        checklists = model.getProjectChecklists(self.project["id"])
        self.parents = self.findParents(checklists)
        for checklist in checklists:
            checklist["widget"] = self.createChecklistWidget(checklist)
            checklist["creator"] = self.createChecklistCreator(checklist["id"])

            self.checklists[checklist["id"]] = checklist

    def assignRootChecklists(self):
        for checklist_id in self.checklists:
            checklist = self.checklists[checklist_id]
            if checklist["parent_id"]:
                continue

            line = LineItem(self.root["creator"].proxy, checklist["widget"].proxy, self.lineColor)
            self.scene.addItem(line)
            checklist["widget"].addLine(line)

    def createChecklistWidget(self, checklist):
        position = {
            "x": checklist["position_x"],
            "y": checklist["position_y"],
        }

        proxy = QGraphicsProxyWidget()
        self.scene.addItem(proxy)

        widget = Checklist(checklist["title"], checklist["checks"], position, self.grid_size, proxy=proxy, id=checklist["id"])
        proxy.setWidget(widget)

        widget.position_changed.connect(self.onChecklistPositionChanged)
        widget.checklist_moved.connect(self.onChecklistMoved)
        widget.delete_checklist.connect(self.deleteChecklist)
        widget.edit_checklist.connect(self.showChecklistEditDialog)

        return widget

    def showChecklistEditDialog(self, id):
        checklist = self.checklists[id]
        self.checklist_editor.setId(id)
        self.checklist_editor.setChecklistName(checklist["title"])
        self.checklist_editor.setChecks(checklist["checks"])
        self.checklist_editor_dialog.show()

    def createChecklistCreator(self, id):
        proxy = QGraphicsProxyWidget()
        proxy.setZValue(100)
        self.scene.addItem(proxy)
        creator = CreateChecklistButton(proxy=proxy, id=id)
        creator.pressed.connect(self.checklistCreatorPressed)
        creator.released.connect(self.checklistCreatorReleased)
        proxy.setWidget(creator)

        return creator

    def findParents(self, checklists):
        parents = {}
        for checklist in checklists:
            parent = checklist["parent_id"]
            if parent:
                if parent in parents:
                    parents[parent].append(checklist["id"])
                else:
                    parents[parent] = [ checklist["id"] ]

        return parents

    def adjustChecklistsSize(self):
        for checklist_id in self.checklists:
            checklist = self.checklists[checklist_id]
            self.adjustChecklistSize(checklist)

    def adjustChecklistSize(self, checklist):
        checklist["widget"].adjustSize()

        width = checklist["widget"].width()
        new_width = ((width + self.grid_size - 1)//self.grid_size)*self.grid_size

        height = checklist["widget"].height()
        new_height = ((height + self.grid_size - 1)//self.grid_size)*self.grid_size
        checklist["widget"].resize(new_width, new_height)

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

            scene_pos = self.mapToScene(event.pos())  
            if self.zoomed_out:
                self.resetTransform()
                self.centerOn(scene_pos.x(), scene_pos.y())
                self.zoomed_out = False
                model.updateProjectZoomedOut(self.project["id"], False)
            else:
                rect = QRectF(scene_pos.x() - 1250, scene_pos.y() - 1250, 2500, 2500)
                self.fitInView(rect, Qt.KeepAspectRatio)
                self.zoomed_out = True
                model.updateProjectZoomedOut(self.project["id"], True)
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            scene_pos = self.mapToScene(event.pos())
            item = self.scene.itemAt(scene_pos, self.transform())
        
            if item is None or isinstance(item, GridBackground):
                self.is_panning = True
                self.setRenderHint(QPainter.Antialiasing, False)
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
            
            event.accept()
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
            self.setRenderHint(QPainter.Antialiasing, True)
            self.viewport().setCursor(Qt.ArrowCursor)

            view = self.mapToScene(self.viewport().rect()).boundingRect()
            model.updateProjectView(self.project["id"], view.x() + view.width()/2, view.y() + view.height()/2)

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
        if not hasattr(self, "transformations_restored"):
            self.transformations_restored = True
            if self.project["view_x"] is None or self.project["view_y"] is None:
                self.centerOn(0, self.workspace_height/2 - self.root["widget"].height()/2)
            else:
                if not self.zoomed_out:
                    self.centerOn(self.project["view_x"], self.project["view_y"])
                else:
                    rect = QRectF(self.project["view_x"] - 1250, self.project["view_y"] - 1250, 2500, 2500)
                    self.fitInView(rect, Qt.KeepAspectRatio)

    def assignParents(self, parents):
        for parent_id in parents:
            parent = self.checklists[parent_id]["widget"]
            children = parents[parent_id]
            for child_id in children:
                child = self.checklists[child_id]["widget"]
                self.createParentChildLine(parent, child)

    def createParentChildLine(self, parent, child):
        line = LineItem(parent.proxy, child.proxy, self.lineColor)
        self.scene.addItem(line)

        parent.addLine(line)
        child.addLine(line)

    def updateCreatorsPosition(self):
        for checklist in self.checklists.values():
            self.updateCreatorPosition(checklist)

    def updateCreatorPosition(self, checklist):
        new_x = checklist["widget"].x() + checklist["widget"].width() - checklist["creator"].width()/2
        new_y = checklist["widget"].y() + checklist["widget"].height()/2 - checklist["creator"].height()/2
        checklist["creator"].move(new_x, new_y)

    def onChecklistMoved(self):
        self.updateCreatorsPosition()

    def onChecklistPositionChanged(self, new_x, new_y):
        model.updateChecklistPosition(self.sender().id, new_x, new_y)
        self.updateCreatorsPosition()

    def checklistCreatorPressed(self, event):
        if event.button() == Qt.LeftButton:
            self.checklist_editor.setId(None)
            self.creator_checklist_id = self.sender().id
            self.creating_checklist = True
            self.creator_line = LineItem(self.sender().proxy, self.create_checklist_destination.proxy, self.lineColor)
            self.creator_line.hide()
            self.scene.addItem(self.creator_line)

    def checklistCreatorReleased(self, event):
        if event.button() == Qt.LeftButton:
            self.creating_checklist = False
            self.scene.removeItem(self.creator_line)
            self.creator_line = None
            self.create_checklist_destination.hide()
            self.checklist_editor_dialog.show()
        
    def resizeEvent(self, event):
        self.checklist_editor_dialog.resizeEvent(event)

    def checklistReady(self, title, checks, id):
        if id: 
            self.updateChecklist(title, checks, id)
        else:
            self.createChecklist(title, checks)

    def updateChecklist(self, title, checks, id):
        self.checklist_editor_dialog.hide()
        self.checklist_editor.setChecklistName(None)
        self.checklist_editor.setChecks(None)
        checklist = self.checklists[id]
        checklist["title"] = title

        check_ids = {check.get("id") for check in checks}
        deleted = [check for check in checklist["checks"] if check.get("id") not in check_ids]
        for check in deleted:
            model.deleteCheck(check["id"])

        for check in checks:
            if check.get("id"):
                model.updateCheck(check["id"], check["content"], check["state"], check["position"])
            else:
                id = model.createCheck(checklist["id"], check["content"], 0, check["position"])
                check["id"] = id

        checklist["checks"] = checks

        checklist["widget"].setTitle(title)
        checklist["widget"].setChecks(checks)

        QTimer.singleShot(0, lambda: self.resizeChecklistAndUpdate(checklist))

    def resizeChecklistAndUpdate(self, checklist):
        self.adjustChecklistSize(checklist)
        checklist["widget"].updateLines()
        self.updateCreatorPosition(checklist)

    def createChecklist(self, title, checks):
        self.checklist_editor_dialog.hide()
        self.checklist_editor.setChecklistName(None)
        self.checklist_editor.setChecks(None)

        checklist = {
            "template_id": None,
            "project_id": self.project["id"],
            "parent_id": self.creator_checklist_id if self.creator_checklist_id != self.project["id"] else None,
            "title": title,
            "position_x": 0,
            "position_y": 0
        }
        checklist["id"] = model.createChecklist(checklist)

        for check in checks:
            check["id"] = model.createCheck(checklist["id"], check["content"], check["state"], check["position"])
            check["checklist_id"] = checklist["id"]

        checklist["checks"] = checks
        checklist["widget"] = self.createChecklistWidget(checklist)
        checklist["creator"] = self.createChecklistCreator(checklist["id"])


        self.checklists[checklist["id"]] = checklist
        self.adjustChecklistsSize()

        new_x, new_y = self.calculateSnapPosition(checklist["widget"], self.create_checklist_destination.x(), self.create_checklist_destination.y())
        model.updateChecklistPosition(checklist["id"], new_x, new_y)

        checklist["widget"].move(new_x, new_y)
        self.updateCreatorsPosition()

        if self.creator_checklist_id != self.project["id"]:
            parent = checklist["parent_id"]
            if parent in self.parents:
                self.parents[parent].append(checklist["id"])
            else:
                self.parents[parent] = [ checklist["id"] ]

            self.createParentChildLine(self.checklists[checklist["parent_id"]]["widget"], checklist["widget"])
        else:
            line = LineItem(self.root["creator"].proxy, checklist["widget"].proxy, self.lineColor)
            self.scene.addItem(line)
            checklist["widget"].addLine(line)

    def calculateSnapPosition(self, widget, x, y):
        cell_x = x // self.grid_size * self.grid_size
        cell_y = y // self.grid_size * self.grid_size

        corners = [
            (cell_x, cell_y),
            (cell_x + self.grid_size, cell_y),
            (cell_x, cell_y + self.grid_size),
            (cell_x + self.grid_size, cell_y + self.grid_size),
        ]

        new_x, new_y = min(corners, key=lambda c: math.hypot(x - c[0], y - c[1]))
        new_y -= round(widget.height()/100)*50
        
        return new_x, new_y

    def deleteChecklist(self, id):
        if id in self.parents:
            return

        checklist = self.checklists[self.sender().id]

        proxy = checklist["widget"].proxy
        line = checklist["widget"].connected_lines[0]
        checklist["widget"].removeLine(line)

        if checklist["parent_id"]:
            parent = self.checklists.get(checklist["parent_id"])
            parent["widget"].removeLine(line)
            self.parents[parent["id"]].remove(checklist["id"])
            if not self.parents[parent["id"]]:
                self.parents.pop(parent["id"], None)

        self.scene.removeItem(line)
        line.setParentItem(None)

        self.scene.removeItem(proxy)
        checklist["widget"].deleteLater()
        proxy.deleteLater()

        proxy = checklist["creator"].proxy
        checklist["creator"].deleteLater()
        proxy.deleteLater()
        self.checklists.pop(checklist["id"], None)
        model.deleteChecklist(checklist["id"])


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
