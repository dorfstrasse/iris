"""
unduh_idx.py - unduh Ringkasan Saham IDX untuk hari ini (kecuali akhir pekan).

    pip install selenium
    python unduh_idx.py
"""
import re
import time
from datetime import date
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service


URL = "https://www.idx.co.id/id/data-pasar/ringkasan-perdagangan/ringkasan-saham/"
FOLDER = Path(__file__).resolve().parent

# Format tanggal yang mungkin tampil di kolom. Tambahkan kalau belum ada.
FORMATS = [
    (r"^\d{4}-\d{2}-\d{2}$", "%Y-%m-%d"),
    (r"^\d{2}-\d{2}-\d{4}$", "%d-%m-%Y"),
    (r"^\d{2}/\d{2}/\d{4}$", "%d/%m/%Y"),
    (r"^\d{8}$", "%Y%m%d"),
]


def isi_tanggal(driver, wait, tgl):
    kolom = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "input.mx-input[name='date']")))
    sekarang = kolom.get_attribute("value") or ""
    fmt = next((f for pola, f in FORMATS if re.match(pola, sekarang)), None)
    if not fmt:
        raise RuntimeError(f"Format tanggal tidak dikenali, isi kolom: {sekarang!r}")
    teks = tgl.strftime(fmt)
    kolom.click()
    kolom.send_keys(Keys.END)
    kolom.send_keys(Keys.BACKSPACE * 20)
    kolom.send_keys(teks)
    kolom.send_keys(Keys.ENTER)
    time.sleep(1)
    if kolom.get_attribute("value") != teks:
        raise RuntimeError(
            f"Tanggal tidak terpilih: diminta {teks}, kolom berisi {kolom.get_attribute('value')!r}")


def tunggu_file_baru(sebelum, batas_detik=90):
    for _ in range(batas_detik):
        sekarang = set(FOLDER.iterdir())
        baru = [f for f in sekarang - sebelum if not f.name.endswith((".crdownload", ".tmp"))]
        if baru and not any(f.name.endswith(".crdownload") for f in sekarang):
            return baru[0]
        time.sleep(1)
    raise TimeoutError("Unduhan tidak selesai dalam waktu yang ditentukan")


def main():
    hari_ini = date.today()
    if hari_ini.weekday() >= 5:  # 5 = Sabtu, 6 = Minggu
        print(f"{hari_ini} adalah akhir pekan, tidak ada perdagangan. Dilewati.")
        return

    opts = webdriver.ChromeOptions()
    opts.add_experimental_option("prefs", {
        "download.default_directory": str(FOLDER),
        "download.prompt_for_download": False,
    })
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 30)
    try:
        driver.get(URL)
        isi_tanggal(driver, wait, hari_ini)
        time.sleep(3)  # tunggu tabel dimuat ulang
        # Kalau perlu klik tombol seperti "Cari" dulu, tambahkan di sini.
        sebelum = set(FOLDER.iterdir())
        wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Unduh')]"))).click()
        file = tunggu_file_baru(sebelum)

        # IRIS membaca tanggal dari nama file, jadi pastikan tanggalnya ada.
        tag = hari_ini.strftime("%Y%m%d")
        if tag not in file.name:
            file = file.rename(file.with_name(f"Ringkasan_Saham-{tag}{file.suffix}"))
        print("Tersimpan:", file.name)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()