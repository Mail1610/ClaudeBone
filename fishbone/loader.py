"""Background data-loading thread."""

from PySide6.QtCore import QThread, Signal

from session_parser import load_all_projects


class LoaderThread(QThread):
    done = Signal(dict)

    def run(self) -> None:
        self.done.emit(load_all_projects())
