from __future__ import annotations

from PySide6 import QtWidgets, QtGui


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FB Marketer")
        self.resize(1200, 800)

        self._init_ui()

    def _init_ui(self):
        central = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(central)

        sidebar = self._build_sidebar()
        self.stack = QtWidgets.QStackedWidget()
        self.stack.addWidget(self._make_placeholder("Dashboard"))
        self.stack.addWidget(self._make_placeholder("Account Manager"))
        self.stack.addWidget(self._make_placeholder("Group Manager"))
        self.stack.addWidget(self._make_placeholder("Poster Library"))
        self.stack.addWidget(self._make_placeholder("Caption Library"))
        self.stack.addWidget(self._make_placeholder("Link Manager"))
        self.stack.addWidget(self._make_placeholder("Campaign Builder"))
        self.stack.addWidget(self._make_placeholder("Scheduler"))
        self.stack.addWidget(self._make_placeholder("Live Console"))
        self.stack.addWidget(self._make_placeholder("Logs & Reports"))
        self.stack.addWidget(self._make_placeholder("Settings"))

        layout.addWidget(sidebar)
        layout.addWidget(self.stack, 1)
        self.setCentralWidget(central)

    def _build_sidebar(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        items = [
            ("Dashboard", 0),
            ("Account Manager", 1),
            ("Group Manager", 2),
            ("Poster Library", 3),
            ("Caption Library", 4),
            ("Link Manager", 5),
            ("Campaign Builder", 6),
            ("Scheduler", 7),
            ("Live Console", 8),
            ("Logs & Reports", 9),
            ("Settings", 10),
        ]
        for text, idx in items:
            btn = QtWidgets.QPushButton(text)
            btn.clicked.connect(lambda _=False, i=idx: self.stack.setCurrentIndex(i))
            btn.setMinimumHeight(32)
            layout.addWidget(btn)
        layout.addStretch(1)
        return widget

    def _make_placeholder(self, title: str) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        label = QtWidgets.QLabel(title)
        font = label.font()
        font.setPointSize(14)
        font.setBold(True)
        label.setFont(font)
        v.addWidget(label)
        v.addStretch(1)
        return w

