# IRIS: Investment Research & Insight System

Screener saham IDX untuk persiapan sebelum bursa buka esok hari. IRIS membaca file **Ringkasan Saham** harian dari IDX, lalu menyaring saham berdasarkan pola candle, volume, tren, dan kondisi penutupan. Semua perhitungan berjalan di browser Anda, tidak ada data yang dikirim ke server lain.

## Isi folder

```
iris/
├── IRIS.html              # aplikasi (tampilan + semua logika screener)
├── serve.py               # server lokal kecil untuk membaca folder data
├── Ringkasan_Saham/       # taruh file harian IDX di sini (dibuat otomatis)
└── images/                # opsional, untuk favicon (white.png)
```

## Kebutuhan

- Python 3 (tanpa library tambahan)
- Browser modern (Chrome, Edge, Firefox, Safari)
- Koneksi internet saat membuka halaman, karena library SheetJS (pembaca .xlsx) dan font IBM Plex Sans dimuat dari CDN

## Cara menjalankan

1. Download file Ringkasan Saham harian dari situs IDX, lalu taruh di folder `Ringkasan_Saham/`.
2. Jalankan server:
   ```bash
   python serve.py
   ```
3. Browser terbuka otomatis di `http://localhost:8000`. Jika tidak, buka alamat itu secara manual.
4. Hentikan server dengan `Ctrl+C`.

Setiap kali halaman dibuka, IRIS mengecek folder dan hanya membaca file yang belum pernah dimuat. Hasil bacaan disimpan di IndexedDB browser, jadi pembukaan berikutnya lebih cepat. Server hanya bisa diakses dari komputer Anda sendiri (`127.0.0.1`).

## Format data

- **Tipe file:** `.xlsx`, `.xls`, atau `.csv` (pemisah koma, titik koma, atau tab).
- **Nama file:** harus mengandung 8 digit tanggal, misalnya `Ringkasan_Saham-20261116.xlsx`. Tanggal diambil dari sini.
- **Kolom wajib:** Kode, Close (Penutupan), Volume.
- **Kolom opsional:** Nama, Open (Pembukaan), High (Tertinggi), Low (Terendah), Nilai (nilai transaksi dalam rupiah), Sebelumnya (penutupan sebelumnya), Bid.
- Nama kolom bahasa Indonesia maupun Inggris dikenali.
- Disarankan minimal **60 hari** data agar MA50 bisa dihitung. ARB 3 Hari butuh minimal 3 file harian berurutan.

Catatan: kolom Open kosong pada sebagian saham di file IDX, sehingga saham tersebut tidak bisa dinilai di tab Hammer.

## Tab screener

| Tab | Yang dicari |
|---|---|
| **Marubozu** | Saham naik lebih dari batas kenaikan (default 7%) dengan shadow atas kecil (maks. 5 tick dari High) dan Close > VWAP. |
| **Hammer** | Jarum bawah minimal 50% dari range High–Low dan Close > VWAP. |
| **Volume Spike** | Volume hari terakhir ≥ N× pembanding, dan harga naik dibanding kemarin. |
| **ARB 3 Hari** | Tiga hari perdagangan terakhir semuanya ditutup di ARB (Close = Low dan turun sesuai batas BEI). |
| **Analisa Penutupan** | Saham yang memenuhi minimal satu dari empat kriteria: dekat High, Close > VWAP, Close di Bid, jauh dari Low. |
| **Spike Periode** | Dalam N hari terakhir pernah ada hari naik dengan volume spike. |
| **Uptrend MA** | Close > MA cepat dan MA cepat > MA lambat (default MA20/MA50). |
| **Uptrend + Vol Spike** | Gabungan Uptrend MA dan spike volume saat harga naik. |
| **Koreksi/Distribusi** | Turun ≥ X% dari puncak 20 hari (koreksi), atau turun hari ini dengan volume besar (distribusi). |

### Aturan tab Marubozu dan Hammer

- Filter hanya memakai 2 kriteria. Marubozu: shadow atas dan Close > VWAP. Hammer: jarum bawah dan Close > VWAP.
- **Close di Bid bukan syarat filter.** Saham yang tidak close di Bid tetap tampil dengan tanda ✗ Tidak. Kolom Skor tetap menghitung Bid (x/3), sehingga saham yang close di Bid berada di urutan atas.
- Parameter "min. kriteria" bernilai 1 atau 2 (default 2).

## Parameter

Semua parameter ada di panel bawah tabel dan langsung memperbarui hasil.

| Parameter | Default | Keterangan |
|---|---|---|
| Pengali volume | 2× | Ambang spike volume |
| Pembanding volume | 1 hari | Volume dibandingkan dengan rata-rata N hari sebelumnya |
| Periode spike | 5 hari | Jendela untuk tab Spike Periode dan Uptrend + Vol Spike |
| MA cepat / lambat | 20 / 50 | Untuk tab Uptrend |
| Koreksi dari puncak | 8% | Ambang koreksi |
| Min. nilai/hari | 0 jt | Filter likuiditas, dalam juta rupiah |
| Dekat High: maks. selisih | 1 poin % | Selisih High terhadap Close |
| Jauh dari Low: min. selisih | 3 poin % | Selisih Close terhadap Low |
| Batas ARB manual | kosong | Kosong berarti otomatis sesuai aturan BEI |
| Tanpa Shadow Atas: maks. tick | 5 | Jarak Close ke High dalam tick |
| Tanpa Shadow Atas: min. kenaikan | 7% | Syarat naik di tab Marubozu |
| Jarum Bawah: min. % dari range | 50% | Syarat di tab Hammer |
| Min. kriteria dua tab candle | 2 | Jumlah kriteria minimal yang harus lolos |

## Istilah penting

- **Rasio Vol:** volume hari terakhir dibagi rata-rata volume N hari sebelumnya.
- **VWAP:** Nilai ÷ Volume. Jika Nilai kosong, memakai (High + Low + Close) ÷ 3.
- **Strong Close:** posisi Close di rentang High–Low ≥ 80% dan Close tidak lebih dari 3% di atas VWAP.
- **Tick:** fraksi harga BEI (1, 2, 5, 10, atau 25 rupiah tergantung rentang harga).
- **Close di Bid:** Close sama dengan Bid terbaik di file IDX.
- **ARB otomatis:** 15% sampai 18 Okt 2026, 7% mulai 19 Okt 2026, lalu 35/25/20% sesuai rentang harga mulai 1 Jan 2027. Harga sampai Rp10 memakai batas Rp1.

## Pemecahan masalah

| Masalah | Solusi |
|---|---|
| "Folder tidak terhubung" | Jalankan `python serve.py`, lalu buka `http://localhost:8000` (bukan membuka `IRIS.html` langsung). |
| "Folder kosong atau tidak ada file yang bisa dibaca" | Pastikan file ada di `Ringkasan_Saham/` dengan ekstensi `.xlsx`, `.xls`, atau `.csv`. |
| Tanggal tidak terbaca | Tambahkan 8 digit tanggal (YYYYMMDD) pada nama file. |
| Tab MA kosong | Data kurang dari 50 hari. Tambah file harian atau turunkan MA lambat. |
| "Data Bid tidak ditemukan" | File tidak punya kolom Bid. Gunakan file Ringkasan Saham asli dari IDX. |
| Library atau font tidak muncul | Cek koneksi internet, karena SheetJS dan font dimuat dari CDN. |
| Ingin mengubah port | Ubah `PORT` di `serve.py`. |
| Data lama bermasalah | Hapus data situs `localhost:8000` di browser (IndexedDB `iris`), lalu muat ulang. |

## Catatan

IRIS adalah alat bantu penyaringan, bukan rekomendasi investasi. Hasil screener perlu dikonfirmasi dengan analisa dan manajemen risiko Anda sendiri.
