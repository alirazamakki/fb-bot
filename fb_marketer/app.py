from __future__ import annotations

import sys

from PySide6 import QtWidgets

from fb_marketer.config import load_config
from fb_marketer.db import get_engine
from fb_marketer.db.init_db import init_db
from fb_marketer.logging_config import configure_logging
from fb_marketer.ui.main_window import MainWindow


def main() -> int:
    cfg = load_config()
    configure_logging(cfg.log_level)
    engine = get_engine()
    init_db(engine)

    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

