"""Main application window."""

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import (
    QTransform, QBrush, QColor, QIcon, QKeySequence, QPainter,
    QPen, QPixmap, QPolygonF, QShortcut,
)
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QVBoxLayout, QWidget,
)

from .loader import LoaderThread
from .scene import FishboneScene
from .sidebar import SidebarPanel
from .theme import Styles
from .view import FishboneView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Claude Session 魚骨圖")
        self.setWindowIcon(self._make_icon())
        self._apply_responsive_size()
        self.setStyleSheet("background:#12100E;")

        self._scene   = FishboneScene()
        self._view    = FishboneView(self._scene)
        self._status  = QLabel("載入中…")
        self._sidebar = SidebarPanel()

        self.setCentralWidget(self._build_central())
        self._register_shortcuts()
        self._sidebar.navigate.connect(self._on_navigate)
        self._reload()

    # ── responsive sizing ─────────────────────────────────────────────────────
    def _apply_responsive_size(self) -> None:
        screen = QApplication.primaryScreen().availableGeometry()
        w = max(1100, int(screen.width()  * 0.88))
        h = max(680,  int(screen.height() * 0.88))
        self.resize(w, h)
        self.move(
            screen.left() + (screen.width()  - w) // 2,
            screen.top()  + (screen.height() - h) // 2,
        )

    # ── layout ────────────────────────────────────────────────────────────────
    def _build_central(self) -> QWidget:
        central = QWidget()
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._build_toolbar())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._view, stretch=1)
        body.addWidget(self._sidebar)
        outer.addLayout(body, stretch=1)
        return central

    def _build_toolbar(self) -> QWidget:
        tb = QWidget()
        tb.setStyleSheet("background:#1A1008; border-bottom:1px solid #3A2818;")
        layout = QHBoxLayout(tb)
        layout.setContentsMargins(14, 7, 14, 7)
        layout.setSpacing(8)

        title = QLabel("◈  Claude Session 魚骨圖")
        title.setStyleSheet(
            "color:#D97757; font-size:14px; font-weight:bold; letter-spacing:1.2px;"
        )

        reload_btn = QPushButton("⟳  重新載入")
        reload_btn.setStyleSheet(Styles.TOOLBAR_BTN)
        reload_btn.clicked.connect(self._reload)

        fit_btn = QPushButton("⊞  全圖")
        fit_btn.setStyleSheet(Styles.TOOLBAR_BTN)
        fit_btn.clicked.connect(self._fit)

        self._sidebar_btn = QPushButton("▶  概覽")
        self._sidebar_btn.setStyleSheet(Styles.TOOLBAR_BTN)
        self._sidebar_btn.setCheckable(True)
        self._sidebar_btn.setChecked(True)
        self._sidebar_btn.toggled.connect(self._toggle_sidebar)

        hint = QLabel("✋ 拖曳移動  ·  滾輪縮放  ·  右鍵專案可重命名／刪除  ·  移到 ● 查看對話")
        hint.setStyleSheet("color:#7A5A3A; font-size:11px;")
        self._status.setStyleSheet(
            "color:#7A5A3A; font-size:11px; font-family:Consolas;"
        )

        layout.addWidget(title)
        layout.addSpacing(6)
        layout.addWidget(reload_btn)
        layout.addWidget(fit_btn)
        layout.addWidget(self._sidebar_btn)
        layout.addSpacing(4)
        layout.addWidget(hint)
        layout.addStretch()
        layout.addWidget(self._status)
        return tb

    def _register_shortcuts(self) -> None:
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(self._reload)
        QShortcut(QKeySequence("F"), self).activated.connect(self._fit)
        QShortcut(QKeySequence("Ctrl+Equal"), self).activated.connect(
            lambda: self._view.zoom_by(1.15)
        )
        QShortcut(QKeySequence("Ctrl+Minus"), self).activated.connect(
            lambda: self._view.zoom_by(1 / 1.15)
        )
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(
            self._sidebar_btn.toggle
        )

    # ── actions ───────────────────────────────────────────────────────────────
    def _reload(self) -> None:
        self._status.setText("載入中…")
        self._loader = LoaderThread()
        self._loader.done.connect(self._on_loaded)
        self._loader.start()

    def _on_loaded(self, data: dict) -> None:
        self._scene.build(data)
        self._sidebar.update_data(data)
        total_s = sum(len(p["sessions"]) for v in data.values() for p in v)
        total_p = sum(len(v) for v in data.values())
        self._status.setText(
            f"{len(data)} 類別  ·  {total_p} 專案  ·  {total_s} sessions"
        )
        self._fit()

    def _fit(self) -> None:
        self._view.setTransform(QTransform())
        self._view.fitInView(
            self._scene.sceneRect().adjusted(-70, -70, 70, 70),
            Qt.AspectRatioMode.KeepAspectRatio,
        )
        self._view._zoom = self._view.transform().m11()

    def _toggle_sidebar(self, checked: bool) -> None:
        self._sidebar.setVisible(checked)
        self._sidebar_btn.setText("▶  概覽" if checked else "◀  概覽")

    def _on_navigate(self, cat_name: str) -> None:
        pos = getattr(self._scene, "cat_positions", {}).get(cat_name)
        if pos is None:
            return
        self._view.centerOn(pos)

    # ── icon ──────────────────────────────────────────────────────────────────
    @staticmethod
    def _make_icon() -> QIcon:
        px = QPixmap(48, 48)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QBrush(QColor("#D97757")))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(2, 2, 44, 44)
        p.setPen(QPen(QColor("#FAF0E6"), 2.5))
        p.drawLine(9, 24, 39, 24)
        p.setBrush(QBrush(QColor("#FAF0E6")))
        p.setPen(Qt.PenStyle.NoPen)
        pts = QPolygonF([QPointF(37, 19), QPointF(44, 24), QPointF(37, 29)])
        p.drawPolygon(pts)
        p.setPen(QPen(QColor("#FAF0E6"), 2))
        for x in [16, 23, 30]:
            p.drawLine(x, 24, x - 4, 17)
            p.drawLine(x, 24, x - 4, 31)
        p.end()
        return QIcon(px)
