"""Animated dot representing a single Claude session."""

from PySide6.QtCore import (
    QAbstractAnimation, QEasingCurve, QPointF, QRectF,
    Property, Qt, QPropertyAnimation,
)
from PySide6.QtGui import (
    QBrush, QColor, QFont, QPainter, QPen, QRadialGradient,
)
from PySide6.QtWidgets import QGraphicsObject

from .theme import Theme
from .tooltip import TooltipCard


class SessionDot(QGraphicsObject):
    RADIUS    = 9
    LABEL_W   = 88  # max width reserved for date text

    def __init__(self, session: dict, color: QColor) -> None:
        super().__init__()
        self._session = session
        self._color = color
        self._scale_v = 1.0
        self._tip: TooltipCard | None = None
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def boundingRect(self) -> QRectF:
        r = self.RADIUS * 2.2
        # extend right to cover the inline date label
        return QRectF(-r, -r, r + self.RADIUS + self.LABEL_W, r * 2)

    def paint(self, p: QPainter, *_) -> None:
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = self.RADIUS

        halo = QRadialGradient(0, 0, r * 2.0)
        gc = QColor(self._color); gc.setAlpha(50)
        halo.setColorAt(0, gc)
        gc2 = QColor(self._color); gc2.setAlpha(0)
        halo.setColorAt(1, gc2)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(halo))
        p.drawEllipse(QRectF(-r * 2, -r * 2, r * 4, r * 4))

        rp = QPen(self._color); rp.setWidthF(1.8)
        p.setPen(rp); p.setBrush(QBrush(Theme.CARD_BG))
        p.drawEllipse(QRectF(-r, -r, r * 2, r * 2))

        inner = QRadialGradient(0, -r * 0.3, r * 0.6)
        inner.setColorAt(0, self._color.lighter(170))
        inner.setColorAt(1, self._color)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(inner))
        ir = r * 0.60
        p.drawEllipse(QRectF(-ir, -ir, ir * 2, ir * 2))

        # date label drawn directly so it always repaints with the dot
        p.setFont(QFont("Segoe UI", 7))
        p.setPen(QPen(Theme.TEXT_MUT))
        lbl_x = r + 5
        p.drawText(
            QRectF(lbl_x, -8, self.LABEL_W, 16),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self._session["date"],
        )

    # ── hover scale property ───────────────────────────────────────────────
    def _get_sv(self) -> float:
        return self._scale_v

    def _set_sv(self, v: float) -> None:
        self._scale_v = v
        self.setScale(v)

    scale_v = Property(float, _get_sv, _set_sv)

    def hoverEnterEvent(self, event) -> None:
        a = QPropertyAnimation(self, b"scale_v", self)
        a.setDuration(160); a.setEndValue(1.35)
        a.setEasingCurve(QEasingCurve.Type.OutBack)
        a.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        self._anim = a
        self._show_tip(event.scenePos())
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        a = QPropertyAnimation(self, b"scale_v", self)
        a.setDuration(130); a.setEndValue(1.0)
        a.setEasingCurve(QEasingCurve.Type.OutCubic)
        a.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
        self._anim = a
        self._remove_tip()
        super().hoverLeaveEvent(event)

    def _show_tip(self, pos: QPointF) -> None:
        self._remove_tip()
        text = f"📅  {self._session['date']}\n\n{self._session['summary']}"
        self._tip = TooltipCard(text, self._color)
        if sc := self.scene():
            sc.addItem(self._tip)
            self._tip.setPos(pos + QPointF(18, -24))

    def _remove_tip(self) -> None:
        if self._tip and self._tip.scene():
            self._tip.scene().removeItem(self._tip)
        self._tip = None
