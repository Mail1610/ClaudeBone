"""Animated dot representing a single Claude session."""

import subprocess
import sys
from typing import Callable

from PySide6.QtCore import (
    QAbstractAnimation, QEasingCurve, QPointF, QRectF,
    Property, Qt, QPropertyAnimation,
)
from PySide6.QtGui import (
    QBrush, QColor, QFont, QPainter, QPen, QRadialGradient,
)
from PySide6.QtWidgets import QGraphicsObject, QMenu, QMessageBox

from .theme import Styles, Theme
from .tooltip import TooltipCard


class SessionDot(QGraphicsObject):
    RADIUS  = 9
    LABEL_W = 88

    def __init__(
        self,
        session: dict,
        color: QColor,
        on_delete: Callable | None = None,
    ) -> None:
        super().__init__()
        self._session  = session
        self._color    = color
        self._scale_v  = 1.0
        self._tip: TooltipCard | None = None
        self._on_delete = on_delete
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def boundingRect(self) -> QRectF:
        r = self.RADIUS * 2.2
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

        p.setFont(QFont("Segoe UI", 7))
        p.setPen(QPen(Theme.TEXT_MUT))
        p.drawText(
            QRectF(r + 5, -8, self.LABEL_W, 16),
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

    def mouseDoubleClickEvent(self, event) -> None:
        self._open_conversation()
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event) -> None:
        menu = QMenu()
        menu.setStyleSheet(Styles.CONTEXT_MENU)
        open_a = menu.addAction("▶   開啟對話")
        menu.addSeparator()
        del_a  = menu.addAction("🗑   永久刪除此紀錄")
        ch = menu.exec(event.screenPos())
        if ch == open_a:
            self._open_conversation()
        elif ch == del_a:
            self._delete_session()

    # ── actions ───────────────────────────────────────────────────────────
    def _open_conversation(self) -> None:
        session_id = self._session["id"]
        cwd = self._read_cwd_from_jsonl()
        try:
            if sys.platform == "win32":
                subprocess.Popen(
                    ["cmd", "/k", f"claude --resume {session_id}"],
                    creationflags=subprocess.CREATE_NEW_CONSOLE,
                    cwd=cwd,
                )
            else:
                subprocess.Popen(["claude", "--resume", session_id], cwd=cwd)
        except FileNotFoundError:
            QMessageBox.warning(
                None, "找不到 claude",
                "找不到 claude 指令。\n\n請確認 Claude Code CLI 已安裝並加入 PATH。",
            )
        except Exception as e:
            QMessageBox.warning(None, "錯誤", str(e))

    def _read_cwd_from_jsonl(self) -> str | None:
        import json
        path = self._session.get("path")
        if not path:
            return None
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                for i, line in enumerate(fh):
                    if i > 10:
                        break
                    try:
                        obj = json.loads(line)
                        if cwd := obj.get("cwd"):
                            return cwd
                    except Exception:
                        continue
        except Exception:
            pass
        return None

    def _delete_session(self) -> None:
        path = self._session.get("path")
        reply = QMessageBox.question(
            None,
            "確認永久刪除",
            f"確定要永久刪除這筆 session 紀錄？\n\n"
            f"日期：{self._session['date']}\n"
            f"檔案：{path}\n\n"
            "此操作無法復原。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            if path and path.exists():
                path.unlink()
        except Exception as e:
            QMessageBox.warning(None, "刪除失敗", str(e))
            return
        if self._on_delete:
            self._on_delete()

    # ── tooltip ───────────────────────────────────────────────────────────
    def _show_tip(self, pos: QPointF) -> None:
        self._remove_tip()
        text = f"📅  {self._session['date']}\n\n{self._session['summary']}"
        self._tip = TooltipCard(text, self._color)
        if sc := self.scene():
            sc.addItem(self._tip)
            self._tip.setPos(pos + QPointF(18, -24))

    def _remove_tip(self) -> None:
        if self._tip:
            try:
                sc = self._tip.scene()
                if sc:
                    sc.removeItem(self._tip)
            except RuntimeError:
                pass
        self._tip = None
