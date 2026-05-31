"""Zoomable, pannable QGraphicsView for the fishbone diagram."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QTransform
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView


class FishboneView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__(scene)
        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform,
        )
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setStyleSheet("background:#12100E; border:none;")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._zoom = 1.0

    def zoom_by(self, factor: float) -> None:
        self._zoom = max(0.15, min(self._zoom * factor, 6.0))
        t = QTransform(); t.scale(self._zoom, self._zoom); self.setTransform(t)

    def wheelEvent(self, event) -> None:
        self.zoom_by(1.15 if event.angleDelta().y() > 0 else 1 / 1.15)
