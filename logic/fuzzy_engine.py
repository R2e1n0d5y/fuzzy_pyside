class FuzzyMamdani:
    def _trapezoid(self, x, a, b, c, d):
        """Fungsi keanggotaan trapesium generik"""
        if x <= a or x >= d:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a) if (b - a) != 0 else 1.0
        elif b < x <= c:
            return 1.0
        elif c < x < d:
            return (d - x) / (d - c) if (d - c) != 0 else 1.0
        return 0.0

    def _triangle(self, x, a, b, c):
        """Fungsi keanggotaan segitiga generik"""
        if x <= a or x >= c:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a) if (b - a) != 0 else 1.0
        elif b < x < c:
            return (c - x) / (c - b) if (c - b) != 0 else 1.0
        return 0.0

    def mf_luas_panen(self, x):
        rendah  = self._trapezoid(x, 200000, 200000, 350000, 550000)
        sedang  = self._triangle (x, 200000, 500000, 800000)
        tinggi  = self._trapezoid(x, 550000, 700000, 900000, 900000)
        return {"Rendah": rendah, "Sedang": sedang, "Tinggi": tinggi}

    def mf_curah_hujan(self, x):
        rendah  = self._trapezoid(x, 200,  200,  1000, 2500)
        sedang  = self._triangle (x, 200,  2200, 4000)
        tinggi  = self._trapezoid(x, 2500, 4000, 6000, 6000)
        return {"Rendah": rendah, "Sedang": sedang, "Tinggi": tinggi}

    def mf_kelembaban(self, x):
        rendah  = self._trapezoid(x, 40, 40, 55, 70)
        sedang  = self._triangle (x, 40, 62, 85)
        tinggi  = self._trapezoid(x, 70, 85, 100, 100)
        return {"Rendah": rendah, "Sedang": sedang, "Tinggi": tinggi}

    def mf_suhu(self, x):
        rendah  = self._trapezoid(x, 10, 10, 15, 20)
        sedang  = self._triangle (x, 10, 22, 30)
        tinggi  = self._trapezoid(x, 20, 30, 40, 40)
        return {"Rendah": rendah, "Sedang": sedang, "Tinggi": tinggi}

    RULES = [
        # (Luas Panen, Curah Hujan, Kelembaban, Suhu, Output)
        ("Rendah", "Sedang",  "Sedang", "Sedang", "Rendah"),   # R1
        ("Rendah", "Sedang",  "Tinggi", "Rendah", "Rendah"),   # R2
        ("Rendah", "Rendah",  "Tinggi", "Rendah", "Rendah"),   # R3
        ("Rendah", "Rendah",  "Sedang", "Sedang", "Rendah"),   # R4
        ("Rendah", "Tinggi",  "Tinggi", "Rendah", "Rendah"),   # R5
        ("Tinggi", "Tinggi",  "Sedang", "Tinggi", "Sedang"),   # R6
        ("Sedang", "Rendah",  "Sedang", "Sedang", "Sedang"),   # R7
        ("Sedang", "Sedang",  "Sedang", "Sedang", "Sedang"),   # R8
        ("Sedang", "Tinggi",  "Tinggi", "Sedang", "Sedang"),   # R9
        ("Sedang", "Sedang",  "Tinggi", "Sedang", "Sedang"),   # R10
        ("Tinggi", "Sedang",  "Sedang", "Sedang", "Tinggi"),   # R11
        ("Tinggi", "Rendah",  "Sedang", "Sedang", "Tinggi"),   # R12
        ("Tinggi", "Rendah",  "Sedang", "Rendah", "Tinggi"),   # R13
        ("Tinggi", "Rendah",  "Sedang", "Sedang", "Tinggi"),   # R14
        ("Sedang", "Rendah",  "Sedang", "Rendah", "Tinggi"),   # R15
    ]

    def inferensi(self, mf_lp, mf_ch, mf_kel, mf_suhu):
        """
        Hitung alpha-predikat tiap rule dengan operator AND (min).
        Kemudian agregasi dengan MAX per himpunan output.
        """
        alpha = {"Rendah": 0.0, "Sedang": 0.0, "Tinggi": 0.0}
        detail_rules = []

        for i, (lp, ch, kel, su, out) in enumerate(self.RULES):
            vals = [
                mf_lp[lp],
                mf_ch[ch],
                mf_kel[kel],
                mf_suhu[su]
            ]
            a = min(vals)
            detail_rules.append({
                "rule"  : f"R{i+1}",
                "lp"    : lp,
                "ch"    : ch,
                "kel"   : kel,
                "suhu"  : su,
                "output": out,
                "vals"  : vals,
                "alpha" : a
            })
            if a > alpha[out]:
                alpha[out] = a

        return alpha, detail_rules

    def defuzzifikasi(self, alpha):
        """
        Centroid defuzzification.
        Himpunan Output:
          Rendah : [1.000.000, 3.000.000]
          Sedang : [1.000.000, 4.000.000]  → titik tengah 2.500.000
          Tinggi : [3.000.000, 5.000.000]
        """
        import numpy as np

        z = np.linspace(1_000_000, 5_000_000, 1000)
        u = np.zeros_like(z)

        for i, zi in enumerate(z):
            # MF output Rendah: trapesium [1M, 1M, 2M, 3M]
            mu_r = self._trapezoid(zi, 1_000_000, 1_000_000, 2_000_000, 3_000_000)
            # MF output Sedang: segitiga [1M, 2.5M, 4M]
            mu_s = self._triangle(zi,  1_000_000, 2_500_000, 4_000_000)
            # MF output Tinggi: trapesium [3M, 4M, 5M, 5M]
            mu_t = self._trapezoid(zi, 3_000_000, 4_000_000, 5_000_000, 5_000_000)

            # Clipping dengan alpha
            u[i] = max(
                min(alpha["Rendah"], mu_r),
                min(alpha["Sedang"], mu_s),
                min(alpha["Tinggi"], mu_t)
            )

        denom = np.sum(u)
        if denom == 0:
            return 0.0, z, u
        z_star = np.sum(z * u) / denom
        return z_star, z, u

    def klasifikasi(self, nilai):
        if nilai < 2_000_000:
            return "🔴 Rendah", "#e74c3c"
        elif nilai < 3_500_000:
            return "🟡 Sedang", "#f39c12"
        else:
            return "🟢 Tinggi", "#27ae60"

    def predict(self, luas_panen, curah_hujan, kelembaban, suhu):
        mf_lp  = self.mf_luas_panen(luas_panen)
        mf_ch  = self.mf_curah_hujan(curah_hujan)
        mf_kel = self.mf_kelembaban(kelembaban)
        mf_su  = self.mf_suhu(suhu)

        alpha, detail_rules = self.inferensi(mf_lp, mf_ch, mf_kel, mf_su)
        z_star, z_arr, u_arr = self.defuzzifikasi(alpha)
        label, color = self.klasifikasi(z_star)

        return {
            "luas_panen"    : luas_panen,
            "curah_hujan"   : curah_hujan,
            "kelembaban"    : kelembaban,
            "suhu"          : suhu,
            "mf_lp"         : mf_lp,
            "mf_ch"         : mf_ch,
            "mf_kel"        : mf_kel,
            "mf_su"         : mf_su,
            "alpha"         : alpha,
            "detail_rules"  : detail_rules,
            "hasil"         : z_star,
            "label"         : label,
            "color"         : color,
            "z_arr"         : z_arr,
            "u_arr"         : u_arr,
        }