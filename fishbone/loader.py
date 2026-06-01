"""Background data-loading thread."""

from PySide6.QtCore import QThread, Signal

from session_parser import load_all_projects


class LoaderThread(QThread):
    done  = Signal(dict)
    error = Signal(str)

    def run(self) -> None:
        try:
            self.done.emit(load_all_projects())
        except Exception as exc:
            self.error.emit(str(exc))
