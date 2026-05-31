"""Claude brand palette and Qt stylesheets."""

from PySide6.QtGui import QColor


class Theme:
    ORANGE    = QColor("#D97757")
    CORAL     = QColor("#E8856C")
    AMBER     = QColor("#F0A868")
    DEEP      = QColor("#B85C3A")
    PEACH     = QColor("#F5C09A")
    ROSE      = QColor("#D46A70")
    GOLD      = QColor("#E8B84B")

    BG_DARK   = QColor("#12100E")
    BG_MID    = QColor("#1D160F")
    SPINE     = QColor("#E8C9A8")
    USER_G1   = QColor("#7C3A1E")
    USER_TEXT = QColor("#FAF0E6")
    TEXT_PRI  = QColor("#F5EAD8")
    TEXT_MUT  = QColor("#7A6A58")
    CARD_BG   = QColor("#1E1610")
    CARD_BRD  = QColor("#3A2A1E")
    TIP_BG    = QColor(20, 14, 8, 245)

    CAT_COLORS = [ORANGE, CORAL, AMBER, DEEP, PEACH, ROSE, GOLD]


class Styles:
    TOOLBAR_BTN = """
QPushButton { background:#2A1C10; color:#C8996A; border:1px solid #4A3020;
              border-radius:7px; padding:5px 16px; font-size:12px; }
QPushButton:hover { background:#3A2818; color:#F5D0A0; border-color:#7A5030; }
QPushButton:pressed { background:#4A3020; padding-top:6px; padding-bottom:4px; }
"""

    CONTEXT_MENU = """
QMenu { background:#1E1610; border:1px solid #4A3020; color:#F5EAD8;
        border-radius:8px; padding:4px; }
QMenu::item { padding:7px 20px; border-radius:5px; }
QMenu::item:selected { background:#3A2818; }
"""
