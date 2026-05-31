"""Right-side overview / navigation panel."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel,
    QScrollArea, QVBoxLayout, QWidget,
)

from .theme import Theme


class _CategoryRow(QWidget):
    clicked = Signal(str)

    def __init__(self, cat_name: str, color: QColor, n_proj: int, n_sess: int) -> None:
        super().__init__()
        self._name = cat_name
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(54)
        self.setStyleSheet("background:transparent; border-radius:6px;")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(8)

        dot = QLabel("●")
        dot.setFixedWidth(16)
        dot.setStyleSheet(f"color:{color.name()}; font-size:14px;")

        right = QWidget()
        right.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        right.setStyleSheet("background:transparent;")
        rl = QVBoxLayout(right)
        rl.setContentsMargins(0, 5, 0, 5)
        rl.setSpacing(3)

        name_lbl = QLabel(cat_name)
        name_lbl.setStyleSheet("color:#D4BFA0; font-size:12px; font-weight:bold;")

        stats_lbl = QLabel(f"{n_proj} 專案  ·  {n_sess} sessions")
        stats_lbl.setStyleSheet("color:#6A5A48; font-size:10px; font-family:Consolas;")

        rl.addWidget(name_lbl)
        rl.addWidget(stats_lbl)

        layout.addWidget(dot)
        layout.addWidget(right, stretch=1)

    def enterEvent(self, e) -> None:
        self.setStyleSheet("background:#251A0E; border-radius:6px;")
        super().enterEvent(e)

    def leaveEvent(self, e) -> None:
        self.setStyleSheet("background:transparent; border-radius:6px;")
        super().leaveEvent(e)

    def mousePressEvent(self, event) -> None:
        self.clicked.emit(self._name)
        super().mousePressEvent(event)


class SidebarPanel(QWidget):
    navigate = Signal(str)
    WIDTH = 210

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedWidth(self.WIDTH)
        self.setStyleSheet("background:#161008; border-left:1px solid #2A1E10;")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        header = QLabel("  概覽")
        header.setFixedHeight(36)
        header.setStyleSheet(
            "color:#C8996A; font-size:12px; font-weight:bold;"
            " background:#1A1008; border-bottom:1px solid #2A1E10; padding-left:12px;"
        )
        outer.addWidget(header)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("""
            QScrollArea { border:none; background:#161008; }
            QScrollBar:vertical { background:#1A1008; width:4px; border-radius:2px; }
            QScrollBar::handle:vertical { background:#3A2818; border-radius:2px; min-height:20px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0px; }
        """)
        self._content = QWidget()
        self._content.setStyleSheet("background:transparent;")
        self._vbox = QVBoxLayout(self._content)
        self._vbox.setContentsMargins(6, 8, 6, 8)
        self._vbox.setSpacing(2)
        self._vbox.addStretch()
        self._scroll.setWidget(self._content)
        outer.addWidget(self._scroll, stretch=1)

        self._footer = QLabel("—")
        self._footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._footer.setStyleSheet(
            "color:#4A3828; font-size:10px; font-family:Consolas;"
            " padding:8px 4px; border-top:1px solid #2A1E10; background:#161008;"
        )
        outer.addWidget(self._footer)

        self._rows: list[_CategoryRow] = []

    def update_data(self, data: dict) -> None:
        while self._vbox.count():
            item = self._vbox.takeAt(0)
            if w := item.widget():
                w.deleteLater()
        self._rows.clear()

        total_p = total_s = 0
        for i, (cat_name, projects) in enumerate(data.items()):
            color  = Theme.CAT_COLORS[i % len(Theme.CAT_COLORS)]
            n_proj = len(projects)
            n_sess = sum(len(p.get("sessions", [])) for p in projects)
            total_p += n_proj
            total_s += n_sess

            if self._rows:
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.HLine)
                sep.setFixedHeight(1)
                sep.setStyleSheet("background:#2A1E10; border:none;")
                self._vbox.addWidget(sep)

            row = _CategoryRow(cat_name, color, n_proj, n_sess)
            row.clicked.connect(self.navigate)
            self._vbox.addWidget(row)
            self._rows.append(row)

        self._vbox.addStretch()
        self._footer.setText(f"{len(data)} 類別  ·  {total_p} 專案\n{total_s} sessions")
