from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QScrollArea, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class ProcessPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        title = QLabel("🔎  Alur Proses Fuzzy Mamdani")
        title.setObjectName("panelTitle")
        root.addWidget(title)

        penjelasan = QLabel(
            "<b>Tahapan Metode Fuzzy Mamdani:</b><br><br>"
            "<b>1. Fuzzifikasi</b> — Mengubah nilai input crisp menjadi derajat "
            "keanggotaan pada himpunan fuzzy (Rendah / Sedang / Tinggi) "
            "menggunakan fungsi keanggotaan trapesium dan segitiga.<br><br>"
            "<b>2. Inferensi (Rule Evaluation)</b> — Mengevaluasi 15 aturan fuzzy "
            "IF-THEN menggunakan operator AND (min). Setiap aturan menghasilkan "
            "nilai alpha-predikat.<br><br>"
            "<b>3. Agregasi</b> — Menggabungkan hasil semua aturan per himpunan output "
            "menggunakan operator MAX.<br><br>"
            "<b>4. Defuzzifikasi (Centroid)</b> — Mengubah himpunan fuzzy output "
            "menjadi nilai crisp menggunakan metode centroid:<br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;Z* = ∫ z·μ(z) dz / ∫ μ(z) dz<br><br>"
            "<b>Sumber:</b> Septyono dkk., SANTIKA 2023 — UPN Veteran Jawa Timur"
        )
        penjelasan.setObjectName("penjelasanLabel")
        penjelasan.setWordWrap(True)
        penjelasan.setTextFormat(Qt.RichText)
        root.addWidget(penjelasan)

        lbl_tabel = QLabel("<b>📋 Tabel Evaluasi 15 Aturan Fuzzy:</b>")
        lbl_tabel.setTextFormat(Qt.RichText)
        root.addWidget(lbl_tabel)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Rule", "Luas Panen", "Curah Hujan",
            "Kelembaban", "Suhu", "Output", "α (min)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setObjectName("ruleTable")
        root.addWidget(self.table)

    def tampilkan(self, r: dict):
        rules = r["detail_rules"]
        self.table.setRowCount(len(rules))

        color_map = {
            "Rendah": QColor("#f38ba8"),
            "Sedang": QColor("#fab387"),
            "Tinggi": QColor("#a6e3a1"),
        }

        for i, rl in enumerate(rules):
            alpha = rl["alpha"]
            items = [
                rl["rule"],
                rl["lp"],
                rl["ch"],
                rl["kel"],
                rl["suhu"],
                rl["output"],
                f"{alpha:.4f}",
            ]
            for j, val in enumerate(items):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                # Warnai baris berdasarkan output
                if j in (1, 2, 3, 4):
                    item.setForeground(color_map.get(val, QColor("#cdd6f4")))
                if j == 5:
                    item.setForeground(color_map.get(val, QColor("#cdd6f4")))
                # Highlight aturan yang aktif (alpha > 0)
                if alpha > 0:
                    item.setBackground(QColor("#313244"))
                self.table.setItem(i, j, item)