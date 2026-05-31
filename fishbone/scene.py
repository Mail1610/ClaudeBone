"""QGraphicsScene that builds the fishbone diagram with cascading animations."""

from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtGui import (
    QBrush, QColor, QFont, QFontMetrics,
    QLinearGradient, QPainterPath, QPen, QPolygonF, QRadialGradient,
)
from PySide6.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsPathItem, QGraphicsPolygonItem,
    QGraphicsRectItem, QGraphicsScene, QGraphicsTextItem,
)

from .project_card import ProjectCard
from .session_dot import SessionDot
from .theme import Theme
from .utils import GraphicsUtils


class FishboneScene(QGraphicsScene):
    reload_requested = Signal()

    BONE_H   = 220
    CAT_STEP = 340
    SESS_GAP = 38
    MAX_SESS = 8

    def build(self, data: dict) -> None:
        for a in getattr(self, "_anims", []):
            try:
                a.stop()
            except Exception:
                pass
        self.clear()
        self._anims: list = []
        self.cat_positions: dict[str, QPointF] = {}
        cats = list(data.items())
        if not cats:
            return self._empty()

        tw = len(cats) * self.CAT_STEP
        sl, sr, sy = -(tw + 80), 110, 0

        self._draw_background(sl, sr, tw)
        t = self._draw_spine(sl, sr, sy)
        t = self._draw_user_node(sr, sy, t)
        self._draw_categories(cats, sl, sy, t)

    # ── background ────────────────────────────────────────────────────────────
    def _draw_background(self, sl: float, sr: float, tw: float) -> None:
        bg = QLinearGradient(0, -450, 0, 450)
        bg.setColorAt(0, Theme.BG_DARK); bg.setColorAt(1, Theme.BG_MID)
        bgr = QGraphicsRectItem(sl - 220, -450, tw + 700, 900)
        bgr.setBrush(QBrush(bg)); bgr.setPen(QPen(Qt.PenStyle.NoPen))
        bgr.setZValue(-100); self.addItem(bgr)

        dot_c = QColor(200, 140, 80, 14)
        for gx in range(int(sl - 200), int(sr + 450), 42):
            for gy in range(-430, 435, 42):
                d = QGraphicsEllipseItem(gx - 1, gy - 1, 2, 2)
                d.setPen(Qt.PenStyle.NoPen); d.setBrush(QBrush(dot_c))
                d.setZValue(-99); self.addItem(d)

    # ── spine ─────────────────────────────────────────────────────────────────
    def _draw_spine(self, sl: float, sr: float, sy: float) -> int:
        t = 0
        for width, alpha in [(14, 10), (5, 55), (2, 220)]:
            pen = QPen(QColor(232, 200, 160, alpha), width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            self._anims.append(GraphicsUtils.fade_in(self.addLine(sl, sy, sr, sy, pen), 600, t))
        t += 100

        arr = QPolygonF([QPointF(sr, sy - 14), QPointF(sr + 28, sy), QPointF(sr, sy + 14)])
        ap = QGraphicsPolygonItem(arr)
        ap.setBrush(QBrush(Theme.SPINE)); ap.setPen(QPen(Qt.PenStyle.NoPen))
        self.addItem(ap); self._anims.append(GraphicsUtils.fade_in(ap, 400, t))
        return t + 50

    # ── user node ─────────────────────────────────────────────────────────────
    def _draw_user_node(self, sr: float, sy: float, t: int) -> int:
        for it in self._make_user(sr + 62, sy):
            self._anims.append(GraphicsUtils.fade_in(it, 450, t))
        return t + 150

    # ── categories ────────────────────────────────────────────────────────────
    def _draw_categories(self, cats: list, sl: float, sy: float, t: int) -> None:
        for i, (cat_name, projects) in enumerate(cats):
            color  = Theme.CAT_COLORS[i % len(Theme.CAT_COLORS)]
            side   = -1 if i % 2 == 0 else 1
            xa     = sl + (i + 1) * self.CAT_STEP
            xb, yb = xa + 55, side * self.BONE_H
            self.cat_positions[cat_name] = QPointF(xb, yb)

            t = self._draw_bone(xa, xb, yb, sy, color, t)
            t = self._draw_cat_pill(cat_name, color, xb, yb, side, t)
            t = self._draw_projects(projects, color, side, xb, yb, t)

    def _draw_bone(
        self, xa: float, xb: float, yb: float, sy: float, color: QColor, t: int
    ) -> int:
        for w2, a in [(10, 12), (3.5, 75), (1.8, 210)]:
            c = QColor(color); c.setAlpha(a)
            bp = QPen(c, w2); bp.setCapStyle(Qt.PenCapStyle.RoundCap)
            self._anims.append(GraphicsUtils.fade_in(self.addLine(xa, sy, xb, yb, bp), 380, t))

        att = QGraphicsEllipseItem(xa - 5, sy - 5, 10, 10)
        att.setBrush(QBrush(color)); att.setPen(QPen(Qt.PenStyle.NoPen))
        self.addItem(att); self._anims.append(GraphicsUtils.fade_in(att, 250, t))
        return t

    def _draw_cat_pill(
        self, name: str, color: QColor, xb: float, yb: float, side: int, t: int
    ) -> int:
        for it in self._make_cat_pill(name, color, xb, yb, side):
            self._anims.append(GraphicsUtils.fade_in(it, 320, t))
        return t + 180

    def _draw_projects(
        self, projects: list, color: QColor, side: int,
        xb: float, yb: float, t: int,
    ) -> int:
        for j, proj in enumerate(projects):
            px = xb + (j - len(projects) / 2 + 0.5) * (self.CAT_STEP * 0.88)
            py = yb + side * 70

            sub_c = QColor(color); sub_c.setAlpha(55)
            self._anims.append(
                GraphicsUtils.fade_in(
                    self.addLine(xb, yb, px, py, QPen(sub_c, 1, Qt.PenStyle.DashLine)),
                    250, t,
                )
            )

            card = ProjectCard(proj, color)
            card.setPos(px, py); self.addItem(card)
            self._anims.append(GraphicsUtils.fade_in(card, 300, t))
            t += 70
            t = self._draw_sessions(proj, color, side, px, py, t)
        return t

    def _draw_sessions(
        self, proj: dict, color: QColor, side: int,
        px: float, py: float, t: int,
    ) -> int:
        shown   = proj.get("sessions", [])[:self.MAX_SESS]
        n_extra = len(proj.get("sessions", [])) - len(shown)

        for k, sess in enumerate(shown):
            sx  = px + (k - len(shown) / 2 + 0.5) * self.SESS_GAP
            sy2 = py + side * 58
            lc  = QColor(color); lc.setAlpha(30)
            self._anims.append(
                GraphicsUtils.fade_in(
                    self.addLine(px, py + side * 18, sx, sy2, QPen(lc, 1)), 200, t
                )
            )
            dot = SessionDot(sess, color, on_delete=lambda: self.reload_requested.emit())
            dot.setPos(sx, sy2); self.addItem(dot)
            self._anims.append(GraphicsUtils.fade_in(dot, 240, t + k * 35))

        if n_extra:
            ex = QGraphicsTextItem(f"+{n_extra}")
            ex.setFont(QFont("Segoe UI", 8))
            ex.setDefaultTextColor(color.lighter(130))
            ex.setPos(
                px + (len(shown) / 2 + 0.5) * self.SESS_GAP - 10,
                py + side * 50,
            )
            self.addItem(ex); self._anims.append(GraphicsUtils.fade_in(ex, 200, t))

        return t + 60

    # ── node builders ─────────────────────────────────────────────────────────
    def _make_user(self, cx: float, cy: float) -> list:
        w, h = 118, 74
        path = QPainterPath()
        path.addEllipse(QRectF(cx - w / 2, cy - h / 2, w, h))
        pi = QGraphicsPathItem(path)
        grad = QRadialGradient(cx, cy - 12, 52)
        grad.setColorAt(0, Theme.CORAL); grad.setColorAt(1, Theme.USER_G1)
        pi.setBrush(QBrush(grad))
        bp = QPen(Theme.ORANGE.lighter(130)); bp.setWidthF(1.5); pi.setPen(bp)
        pi.setGraphicsEffect(GraphicsUtils.glow(Theme.ORANGE, 35))
        self.addItem(pi)

        lbl = QGraphicsTextItem("你 (Ian)")
        lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl.setDefaultTextColor(Theme.USER_TEXT)
        lbl.setPos(cx - lbl.boundingRect().width() / 2, cy - 11)
        self.addItem(lbl)
        return [pi, lbl]

    def _make_cat_pill(
        self, name: str, color: QColor, cx: float, cy: float, side: int
    ) -> list:
        font = QFont("Segoe UI", 10, QFont.Weight.Bold)
        fm = QFontMetrics(font)
        w = fm.horizontalAdvance(name) + 30; h = 32
        oy = side * 12
        path = QPainterPath()
        path.addRoundedRect(QRectF(cx - w / 2, cy + oy - h / 2, w, h), 16, 16)
        pill = QGraphicsPathItem(path)
        pg = QLinearGradient(cx - w / 2, 0, cx + w / 2, 0)
        c1 = QColor(color); c1.setAlpha(230)
        c2 = QColor(color); c2.setAlpha(150)
        pg.setColorAt(0, c1); pg.setColorAt(1, c2)
        pill.setBrush(QBrush(pg)); pill.setPen(QPen(Qt.PenStyle.NoPen))
        pill.setGraphicsEffect(GraphicsUtils.glow(color, 22))
        self.addItem(pill)
        lbl = QGraphicsTextItem(name)
        lbl.setFont(font); lbl.setDefaultTextColor(QColor("#FFFFFF"))
        lbl.setPos(
            cx - lbl.boundingRect().width() / 2,
            cy + oy - lbl.boundingRect().height() / 2,
        )
        self.addItem(lbl)
        return [pill, lbl]

    def _empty(self) -> None:
        t = QGraphicsTextItem("找不到任何 Claude session 資料")
        t.setFont(QFont("Segoe UI", 16))
        t.setDefaultTextColor(Theme.TEXT_MUT)
        self.addItem(t)
