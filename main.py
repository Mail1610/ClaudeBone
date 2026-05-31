"""Claude Session 魚骨圖 – entry point."""

import sys

from PySide6.QtWidgets import QApplication

from fishbone.window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
