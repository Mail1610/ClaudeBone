"""Claude Session 魚骨圖 – entry point."""

import sys
import traceback

from PySide6.QtWidgets import QApplication, QMessageBox

from fishbone.window import MainWindow


def _excepthook(exc_type, exc_value, exc_tb) -> None:
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    box = QMessageBox()
    box.setWindowTitle("ClaudeBone — 發生錯誤")
    box.setIcon(QMessageBox.Icon.Critical)
    box.setText(str(exc_value))
    box.setDetailedText(msg)
    box.exec()


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    sys.excepthook = _excepthook
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
