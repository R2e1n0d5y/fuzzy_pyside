from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QTabWidget, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.input_panel  import InputPanel
from ui.result_panel import ResultPanel
from ui.process_panel import ProcessPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prediksi Produksi Padi dengan Fuzzy Mamdani")
        self.setMinimumSize(1100, 360)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        header = QLabel("🌾  Sistem Prediksi Produksi Padi dengan Fuzzy Mamdani")
        header.setAlignment(Qt.AlignCenter)
        header.setObjectName("header")
        root.addWidget(header)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(4)

        self.input_panel = InputPanel()
        self.input_panel.setMinimumWidth(320)
        self.input_panel.setMaximumWidth(380)
        splitter.addWidget(self.input_panel)

        tabs = QTabWidget()
        tabs.setObjectName("mainTabs")

        self.result_panel  = ResultPanel()
        self.process_panel = ProcessPanel()

        tabs.addTab(self.result_panel,  "📊  Hasil Prediksi")
        tabs.addTab(self.process_panel, "🔎  Alur Proses")

        splitter.addWidget(tabs)
        splitter.setSizes([340, 760])
        root.addWidget(splitter)

        self.input_panel.signal_hitung.connect(self._on_hitung)

    def _on_hitung(self, result: dict):
        self.result_panel.tampilkan(result)
        self.process_panel.tampilkan(result)