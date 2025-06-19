from PySide6.QtCore import QPoint, QSize, QPointF, QEvent, Qt, QObject

def centerLeft(rect):
    return QPointF(rect.left(), rect.top() + rect.height() / 2)

def centerRight(rect):
    return QPointF(rect.right(), rect.top() + rect.height() / 2)

def topCenter(rect):
    return QPointF(rect.left() + rect.width() / 2, rect.top())

def bottomCenter(rect):
    return QPointF(rect.left() + rect.width() / 2, rect.bottom())

class ArrowKeyNavigator(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Up:
                obj.focusPreviousChild()
                return True
            elif event.key() == Qt.Key_Down:
                obj.focusNextChild()
                return True
        return super().eventFilter(obj, event)
