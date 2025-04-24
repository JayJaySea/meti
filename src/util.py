from PySide6.QtCore import QPoint, QSize

def snapWidgetEdges(widget_pos: QPoint, size: QSize, grid: int) -> QPoint:
    x, y = widget_pos.x(), widget_pos.y()
    w, h = size.width(), size.height()

    edges = {
        "left": x,
        "right": x + w,
        "top": y,
        "bottom": y + h
    }

    snapped_edges = {}
    for name, pos in edges.items():
        snapped = round(pos / grid) * grid
        snapped_edges[name] = snapped

    min_delta = float("inf")
    snap_axis = None
    snap_value = 0

    for name in edges:
        delta = abs(edges[name] - snapped_edges[name])
        if delta < min_delta:
            min_delta = delta
            snap_axis = name
            snap_value = snapped_edges[name]

    if snap_axis == "left":
        x = snap_value
    elif snap_axis == "right":
        x = snap_value - w
    elif snap_axis == "top":
        y = snap_value
    elif snap_axis == "bottom":
        y = snap_value - h

    return QPoint(x, y)

def snapWidgetByCorner(pos: QPoint, size: QSize, grid: int) -> QPoint:
    x, y = pos.x(), pos.y()
    w, h = size.width(), size.height()

    corners = {
        "top_left": (x, y),
        "top_right": (x + w, y),
        "bottom_left": (x, y + h),
        "bottom_right": (x + w, y + h),
    }

    best_corner = None
    min_distance = float("inf")
    snap_position = QPoint()

    for name, (cx, cy) in corners.items():
        snapped_cx = round(cx / grid) * grid
        snapped_cy = round(cy / grid) * grid

        delta_x = snapped_cx - cx
        delta_y = snapped_cy - cy

        dist = abs(delta_x) + abs(delta_y)

        if dist < min_distance:
            min_distance = dist
            best_corner = name
            if name == "top_left":
                snap_position = QPoint(snapped_cx, snapped_cy)
            elif name == "top_right":
                snap_position = QPoint(snapped_cx - w, snapped_cy)
            elif name == "bottom_left":
                snap_position = QPoint(snapped_cx, snapped_cy - h)
            elif name == "bottom_right":
                snap_position = QPoint(snapped_cx - w, snapped_cy - h)

    return snap_position
