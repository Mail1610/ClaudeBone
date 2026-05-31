"""Graphics helpers – glow effect and fade-in animation."""

from PySide6.QtCore import QEasingCurve, QTimer, QVariantAnimation
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect


class GraphicsUtils:
    @staticmethod
    def glow(color: QColor, radius: int = 18) -> QGraphicsDropShadowEffect:
        fx = QGraphicsDropShadowEffect()
        fx.setBlurRadius(radius)
        fx.setColor(color)
        fx.setOffset(0, 0)
        return fx

    @staticmethod
    def fade_in(
        item,
        duration: int = 350,
        delay: int = 0,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    ) -> QVariantAnimation:
        """Fade in any QGraphicsItem without replacing its existing graphicsEffect."""
        item.setOpacity(0.0)
        anim = QVariantAnimation()
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(easing)
        anim.valueChanged.connect(lambda v: item.setOpacity(float(v)))
        if delay:
            QTimer.singleShot(delay, anim.start)
        else:
            anim.start()
        return anim
