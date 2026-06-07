from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QFrame, QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt
import sys

try:
    import matplotlib
    matplotlib.use("Qt5Agg")
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class ResultPanel(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(10)

        title = QLabel("📊  Hasil Prediksi")
        title.setObjectName("panelTitle")
        root.addWidget(title)

        self.lbl_hasil = QLabel("—")
        self.lbl_hasil.setObjectName("hasilUtama")
        self.lbl_hasil.setAlignment(Qt.AlignCenter)
        self.lbl_hasil.setMinimumHeight(90)
        self.lbl_hasil.setWordWrap(True)
        root.addWidget(self.lbl_hasil)

        self.lbl_klas = QLabel("—")
        self.lbl_klas.setObjectName("klasifikasi")
        self.lbl_klas.setAlignment(Qt.AlignCenter)
        root.addWidget(self.lbl_klas)

        self.lbl_mf = QLabel("—")
        self.lbl_mf.setObjectName("mfLabel")
        self.lbl_mf.setWordWrap(True)
        self.lbl_mf.setTextFormat(Qt.RichText)
        root.addWidget(self.lbl_mf)

        self.lbl_alpha = QLabel("—")
        self.lbl_alpha.setObjectName("alphaLabel")
        self.lbl_alpha.setWordWrap(True)
        self.lbl_alpha.setTextFormat(Qt.RichText)
        root.addWidget(self.lbl_alpha)

        if HAS_MPL:
            self.fig = Figure(figsize=(5, 2.5), facecolor="#1e1e2e")
            self.canvas = FigureCanvas(self.fig)
            self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            root.addWidget(self.canvas)
        else:
            root.addWidget(QLabel("⚠️  Install matplotlib untuk melihat grafik"))

        root.addStretch()

    def tampilkan(self, r: dict):
        # Hasil numerik
        hasil_juta = r["hasil"] / 1_000_000
        self.lbl_hasil.setText(
            f"<b>Prediksi Produksi Padi</b><br>"
            f"<span style='font-size:22pt; color:#a6e3a1;'>"
            f"{r['hasil']:,.0f} ton</span><br>"
            f"<small>≈ {hasil_juta:.2f} juta ton</small>"
        )
        self.lbl_hasil.setTextFormat(Qt.RichText)

        color = r["color"]
        label = r["label"]
        self.lbl_klas.setText(
            f"<b>Klasifikasi Output:</b>  "
            f"<span style='color:{color}; font-size:14pt;'>{label}</span>"
        )
        self.lbl_klas.setTextFormat(Qt.RichText)

        def fmt_mf(name, mf):
            parts = "  |  ".join(
                f"<b>{k}</b>: {v:.3f}" for k, v in mf.items()
            )
            return f"<b>{name}</b>: {parts}"

        mf_html = "<br>".join([
            fmt_mf("Luas Panen",    r["mf_lp"]),
            fmt_mf("Curah Hujan",   r["mf_ch"]),
            fmt_mf("Kelembaban",    r["mf_kel"]),
            fmt_mf("Suhu",          r["mf_su"]),
        ])
        self.lbl_mf.setText(
            f"<b>🔢 Derajat Keanggotaan Input:</b><br>{mf_html}"
        )

        a = r["alpha"]
        self.lbl_alpha.setText(
            f"<b>⚖️  Agregasi (MAX per himpunan output):</b><br>"
            f"<span style='color:#f38ba8;'>Rendah: {a['Rendah']:.3f}</span>  "
            f"<span style='color:#fab387;'>Sedang: {a['Sedang']:.3f}</span>  "
            f"<span style='color:#a6e3a1;'>Tinggi: {a['Tinggi']:.3f}</span>"
        )

        if HAS_MPL:
            self._plot_defuzz(r)

    def _plot_defuzz(self, r):
        self.fig.clear()
        ax = self.fig.add_subplot(111, facecolor="#181825")
        z = r["z_arr"] / 1_000_000  # ke juta ton
        u = r["u_arr"]
        ax.fill_between(z, u, alpha=0.35, color="#89b4fa")
        ax.plot(z, u, color="#89b4fa", linewidth=1.5, label="Output Fuzzy")
        ax.axvline(r["hasil"] / 1_000_000, color="#a6e3a1",
                   linewidth=2, linestyle="--", label=f"Z* = {r['hasil']/1e6:.2f} Jt ton")
        ax.set_facecolor("#181825")
        ax.tick_params(colors="#cdd6f4", labelsize=8)
        ax.spines[:].set_color("#45475a")
        ax.set_xlabel("Produksi (juta ton)", color="#cdd6f4", fontsize=8)
        ax.set_ylabel("Derajat Keanggotaan", color="#cdd6f4", fontsize=8)
        ax.set_title("Grafik Defuzzifikasi (Centroid)", color="#cdd6f4", fontsize=9)
        ax.legend(facecolor="#313244", edgecolor="#45475a",
                  labelcolor="#cdd6f4", fontsize=8)
        self.fig.tight_layout()
        self.canvas.draw()