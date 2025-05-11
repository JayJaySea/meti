from PySide6.QtCore import QPoint, QSize, QPointF 

def centerLeft(rect):
    return QPointF(rect.left(), rect.top() + rect.height() / 2)

def centerRight(rect):
    return QPointF(rect.right(), rect.top() + rect.height() / 2)

def topCenter(rect):
    return QPointF(rect.left() + rect.width() / 2, rect.top())

def bottomCenter(rect):
    return QPointF(rect.left() + rect.width() / 2, rect.bottom())
