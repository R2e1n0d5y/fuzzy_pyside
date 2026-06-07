import csv
import os
import sys

if getattr(sys, 'frozen', False):
    _base = sys._MEIPASS
else:
    _base = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(_base, "2024.csv")

def load_provinsi():
    data = []
    if not os.path.exists(CSV_PATH):
        return data

    with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        rows = list(reader)

    for row in rows[4:]:
        if len(row) < 4:
            continue
        nama = row[0].strip()
        if not nama or nama.upper() == "INDONESIA":
            continue
        try:
            luas_panen    = float(row[1].replace(",", "."))
            produktivitas = float(row[2].replace(",", "."))
            produksi      = float(row[3].replace(",", "."))
            data.append({
                "provinsi"      : nama,
                "luas_panen"    : luas_panen,
                "produktivitas" : produktivitas,
                "produksi"      : produksi,
            })
        except (ValueError, IndexError):
            continue

    return data

def get_provinsi_names():
    return [d["provinsi"] for d in load_provinsi()]

def get_data_by_provinsi(nama):
    for d in load_provinsi():
        if d["provinsi"].upper() == nama.upper():
            return d
    return None