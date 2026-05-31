"""Hover tooltip card shown when the user mouses over a session dot."""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import (
    QBrush, QColor, QFont, QPainter, QPainterPath, QPen, QTextDocument,
)
from PySide6.QtWidgets import QGraphicsPathItem, QStyleOptionGraphicsItem

from .theme import Theme
from .utils import GraphicsUtils


class TooltipCard(QGraphicsPathItem):
    def __init__(self, text: str, accent: QColor) -> None:
        super().__init__()
        self._text = text
        self._accent = accent
        self.setZValue(400)

        font = QFont("Segoe UI", 9)
        doc = QTextDocument()
        doc.setDefaultFont(font)
        doc.setPlainText(text)

        # compute wrapping width from longest line, capped at 400
        max_line_w = max(
            (doc.idealWidth() for _ in [1]),  # triggers layout
            default=100,
        )
        self._w = min(int(max_line_w) + 36, 420)
        doc.setTextWidth(self._w - 36)
        self._h = int(doc.size().height()) + 28

        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self._w, self._h), 10, 10)
        self.setPath(path)
        self.setBrush(QBrush(Theme.TIP_BG))
        pen = QPen(accent)
        pen.setWidthF(1.5)
        self.setPen(pen)
        self.setGraphicsEffect(GraphicsUtils.glow(accent, 22))

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget=None,
    ) -> None:
        # draw the rounded-rect background (handled by QGraphicsPathItem)
        super().paint(painter, option, widget)

        # draw text directly — no child items avoids Qt effect/child rendering bug
        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(QPen(Theme.TEXT_PRI))
        painter.drawText(
            QRectF(18, 12, self._w - 36, self._h - 24),
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop
            | Qt.TextFlag.TextWordWrap,
            self._text,
        )
