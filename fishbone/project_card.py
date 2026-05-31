"""Project card node with hover highlight and right-click context menu."""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import (
    QBrush, QColor, QFont, QFontMetrics,
    QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient,
)
from PySide6.QtWidgets import (
    QGraphicsObject, QInputDialog, QMenu, QMessageBox,
)

from .theme import Styles, Theme


class ProjectCard(QGraphicsObject):
    PAD    = 14
    PAD_V  = 9
    CORNER = 9
    ACCENT = 4

    def __init__(self, proj: dict, color: QColor) -> None:
        super().__init__()
        self._proj = proj
        self._color = color
        self._hover = False
        self._calc()
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def _calc(self) -> None:
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        fm = QFontMetrics(font)
        self._w = max(
            fm.horizontalAdvance(self._proj["project"]) + self.PAD * 2 + self.ACCENT,
            130,
        )
        self._h = fm.height() + self.PAD_V * 2

    def boundingRect(self) -> QRectF:
        return QRectF(-self._w / 2 - 6, -self._h / 2 - 6, self._w + 12, self._h + 12)

    def paint(self, p: QPainter, *_) -> None:
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h, r = self._w, self._h, self.CORNER

        if self._hover:
            bloom = QRadialGradient(0, h * 0.5, w * 0.75)
            bc = QColor(self._color); bc.setAlpha(45)
            bloom.setColorAt(0, bc)
            bc2 = QColor(self._color); bc2.setAlpha(0)
            bloom.setColorAt(1, bc2)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(bloom))
            p.drawEllipse(QRectF(-w * 0.75, h * 0.0, w * 1.5, h * 1.2))

        path = QPainterPath()
        path.addRoundedRect(QRectF(-w / 2, -h / 2, w, h), r, r)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(Theme.CARD_BG))
        p.drawPath(path)

        bp = QPen(self._color if self._hover else Theme.CARD_BRD)
        bp.setWidthF(1.5 if self._hover else 1.0)
        p.setPen(bp); p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawPath(path)

        ag = QLinearGradient(0, -h / 2, 0, h / 2)
        ag.setColorAt(0, self._color); ag.setColorAt(1, self._color.darker(130))
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(ag))
        acc = QPainterPath()
        acc.addRoundedRect(QRectF(-w / 2, -h / 2, self.ACCENT, h), 2, 2)
        p.drawPath(acc)

        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        p.setFont(font)
        p.setPen(QPen(Theme.TEXT_PRI if self._hover else QColor("#D4BFA0")))
        tx = -w / 2 + self.ACCENT + self.PAD
        p.drawText(
            QRectF(tx, -h / 2, w - self.ACCENT - self.PAD * 2, h),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self._proj["project"],
        )

    def hoverEnterEvent(self, e) -> None:
        self._hover = True; self.update(); super().hoverEnterEvent(e)

    def hoverLeaveEvent(self, e) -> None:
        self._hover = False; self.setScale(1.0); self.update(); super().hoverLeaveEvent(e)

    def mousePressEvent(self, e) -> None:
        self.setScale(0.96); super().mousePressEvent(e)

    def mouseReleaseEvent(self, e) -> None:
        self.setScale(1.0); super().mouseReleaseEvent(e)

    def contextMenuEvent(self, event) -> None:
        menu = QMenu()
        menu.setStyleSheet(Styles.CONTEXT_MENU)
        ra = menu.addAction("✏️   重命名專案")
        da = menu.addAction("🗑️   刪除此專案")
        ch = menu.exec(event.screenPos())
        if ch == ra:
            nm, ok = QInputDialog.getText(
                None, "重命名", "新名稱：", text=self._proj["project"]
            )
            if ok and nm.strip():
                self._proj["project"] = nm.strip(); self._calc(); self.update()
        elif ch == da:
            if (
                QMessageBox.question(
                    None, "確認", f"刪除「{self._proj['project']}」？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                == QMessageBox.StandardButton.Yes
            ):
                if sc := self.scene():
                    sc.removeItem(self)
