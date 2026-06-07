from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QDoubleSpinBox, QPushButton, QGroupBox,
    QComboBox, QScrollArea, QFrame
)
from PySide6.QtCore import Signal, Qt
from logic.fuzzy_engine import FuzzyMamdani
from logic.data_loader  import load_provinsi, get_data_by_provinsi


class InputPanel(QWidget):
    signal_hitung = Signal(dict)

    def __init__(self):
        super().__init__()
        self.engine = FuzzyMamdani()
        self._build_ui()
        self._load_provinsi()

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Scroll area untuk semua konten ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("📥  Input Data")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        grp_csv = QGroupBox("Data dari CSV BPS 2024")
        grp_csv.setObjectName("groupBox")
        vcsv = QVBoxLayout(grp_csv)
        vcsv.setSpacing(4)

        self.combo_provinsi = QComboBox()
        self.combo_provinsi.addItem("-- Pilih Provinsi --")
        vcsv.addWidget(QLabel("Provinsi:"))
        vcsv.addWidget(self.combo_provinsi)

        btn_load = QPushButton("📂  Isi Otomatis dari CSV")
        btn_load.setObjectName("btnSecondary")
        btn_load.setFixedHeight(32)
        btn_load.clicked.connect(self._isi_dari_csv)
        vcsv.addWidget(btn_load)
        layout.addWidget(grp_csv)

        grp = QGroupBox("Input Manual / Edit")
        grp.setObjectName("groupBox")
        vg = QVBoxLayout(grp)
        vg.setSpacing(4)

        self.spin_luas = self._spin_row(
            vg, "Luas Panen (ha):",
            minimum=200_000, maximum=1_700_000,
            value=476_422, step=1000
        )
        self.spin_hujan = self._spin_row(
            vg, "Curah Hujan (mm):",
            minimum=200, maximum=6000,
            value=4339, step=10
        )
        self.spin_kelembaban = self._spin_row(
            vg, "Kelembaban (%):",
            minimum=40, maximum=100,
            value=87, step=1
        )
        self.spin_suhu = self._spin_row(
            vg, "Suhu Rata-rata (°C):",
            minimum=10, maximum=40,
            value=25, step=0.1, decimals=1
        )
        layout.addWidget(grp)

        info = QLabel(
            "ℹ️  Range valid:\n"
            "• Luas Panen : 200.000 – 1.700.000 ha\n"
            "• Curah Hujan: 200 – 6.000 mm\n"
            "• Kelembaban : 40 – 100 %\n"
            "• Suhu       : 10 – 40 °C"
        )
        info.setObjectName("infoLabel")
        info.setWordWrap(True)
        layout.addWidget(info)

        layout.addStretch()
        scroll.setWidget(container)

        outer.addWidget(scroll, stretch=1)

        btn = QPushButton("⚡  HITUNG PREDIKSI")
        btn.setObjectName("btnHitung")
        btn.setFixedHeight(44)
        btn.clicked.connect(self._hitung)
        outer.addWidget(btn)

    def _spin_row(self, parent_layout, label_text,
                  minimum, maximum, value, step=1, decimals=0):
        lbl = QLabel(label_text)
        spin = QDoubleSpinBox()
        spin.setDecimals(decimals)
        spin.setRange(minimum, maximum)
        spin.setValue(value)
        spin.setSingleStep(step)
        spin.setGroupSeparatorShown(True)
        spin.setFixedHeight(30)
        parent_layout.addWidget(lbl)
        parent_layout.addWidget(spin)
        return spin

    def _load_provinsi(self):
        data = load_provinsi()
        for d in data:
            self.combo_provinsi.addItem(d["provinsi"])

    def _isi_dari_csv(self):
        nama = self.combo_provinsi.currentText()
        if nama == "-- Pilih Provinsi --":
            return
        d = get_data_by_provinsi(nama)
        if d:
            self.spin_luas.setValue(d["luas_panen"])

    def _hitung(self):
        result = self.engine.predict(
            luas_panen   = self.spin_luas.value(),
            curah_hujan  = self.spin_hujan.value(),
            kelembaban   = self.spin_kelembaban.value(),
            suhu         = self.spin_suhu.value(),
        )
        self.signal_hitung.emit(result)