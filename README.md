# Beijing Air Quality — Proyek Analisis Data

Analisis PM2.5 pada 12 stasiun Beijing, 1 Maret 2013–28 Februari 2017.
Notebook mengikuti urutan templat proyek dan memuat hasil eksekusi, dokumentasi,
insight setiap tahap, dua pertanyaan SMART, tiga visualisasi, kesimpulan, dan rekomendasi.

## Menjalankan dashboard

Gunakan Python **3.13** (versi yang dipakai dalam pengujian). Buka terminal di folder ini:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run dashboard/dashboard.py
```

Untuk macOS/Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run dashboard/dashboard.py
```

Buka alamat lokal yang ditampilkan terminal (biasanya http://localhost:8501).
Dashboard dapat langsung dijalankan karena `dashboard/main_data.csv` sudah disertakan.
Filter tersedia untuk stasiun, periode, dan minimum kelengkapan jam harian.

## Menjalankan ulang notebook

Buka `notebook.ipynb` menggunakan VS Code Jupyter atau Jupyter yang sudah tersedia,
pilih interpreter dari `.venv`, lalu **Restart & Run All** dari folder proyek ini.
Alternatif tanpa memasang antarmuka Jupyter:

```powershell
.venv\Scripts\python -m ipykernel install --user --name airquality --display-name "Air Quality"
.venv\Scripts\python -c "import nbformat; from nbclient import NotebookClient; p='notebook.ipynb'; n=nbformat.read(p,as_version=4); NotebookClient(n,kernel_name='airquality',timeout=180).execute(); nbformat.write(n,p)"
```

Eksekusi notebook membaca seluruh CSV asli, membangun ulang data harian dashboard,
dan menyimpan tiga grafik di `figures/`. Lengkapi nama, email, dan ID Dicoding di sel pertama
sebelum mengirim submission. Identitas tidak diisi secara asumsi.

## Pertanyaan dan metode

1. Stasiun mana memiliki rata-rata PM2.5 harian tertinggi pada periode penelitian,
   untuk memprioritaskan audit pemantauan?
2. Bulan kalender mana memiliki rata-rata tertinggi/terendah dan berapa selisihnya,
   untuk menjadwalkan pemantauan tambahan?

- Hari valid: sedikitnya **18 dari 24** pengamatan PM2.5. Ini aturan analitis proyek.
- Nilai kosong tidak diisi nol atau diinterpolasi. Outlier IQR ditandai dan dipertahankan.
- Rata-rata stasiun memakai hari valid dengan bobot setara.
- Pola bulan kalender: rata-rata stasiun-bulan-tahun → rata-rata antarstasiun →
  rata-rata antar-tahun. Setiap stasiun dan setiap tahun mendapat bobot sama pada tahapnya.
- Jan–Feb mewakili 2014–2017, Mar–Des mewakili 2013–2016. Grafik bukan tren satu tahun.
- Sensitivitas notebook membandingkan minimum 18 versus 24 jam serta tanggal yang
  valid bersamaan pada seluruh stasiun.
- Analisis lanjutan menggunakan **binning/manual clustering** `pd.cut`: [0,25],
  (25,50], (50,100], (100,150], (150,∞) µg/m³. Tanpa machine learning.
- Interval merupakan kelompok konsentrasi deskriptif, **bukan AQI atau standar kesehatan**.
  Persentase memakai jumlah hari valid masing-masing stasiun sebagai denominator.
- Semua batang dimulai dari nol, unit dinyatakan, waktu diurutkan, dan data hilang
  tidak ditampilkan sebagai nol. Rentang pada grafik bulanan adalah min–maks antar-tahun,
  bukan confidence interval. Grafik dan tabel menggunakan sumber/agregasi yang sama.

Missingness mungkin tidak acak dan stasiun tidak mewakili paparan penduduk.
Temuan bersifat historis/deskriptif; tidak membuktikan penyebab atau kondisi masa kini.

## Struktur

```text
submission/
├── data/                  # 12 CSV asli
├── dashboard/
│   ├── dashboard.py
│   └── main_data.csv       # agregat stasiun-hari beserta cakupan
├── figures/               # grafik dari notebook
├── .streamlit/config.toml
├── notebook.ipynb         # sudah dieksekusi
├── requirements.txt
├── README.md
└── url.txt                # status deployment; ganti dengan URL setelah terverifikasi
```

`main_data.csv`: `pm25_observed_mean` adalah rata-rata jam yang tersedia;
`valid_hours` jumlah nilai PM2.5; `observed_hours` jumlah baris jam sumber;
`outlier_hours` jumlah nilai >247,5 µg/m³; `coverage_pct` adalah valid_hours/24×100;
`eligible` menerapkan minimum 18 jam; `pm25_mean` kosong jika tidak eligible;
`concentration_group` berasal dari binning `pm25_mean`.
Slider dashboard menghitung ulang kelayakan memakai `valid_hours` dan rata-rata observasi.

## Deploy ke Streamlit Community Cloud

**Status: belum dideploy.** Halaman Cloud memerlukan login pengguna; belum ada URL aplikasi
publik yang terverifikasi. Isi `url.txt` saat aplikasi benar-benar berhasil dibuka.

1. Unggah isi folder `submission` ke repositori GitHub Anda. Hindari mengunggah `.venv`,
   cache, kredensial, dan ZIP. Sertakan `requirements.txt` serta `dashboard/main_data.csv`.
2. Masuk ke [Streamlit Community Cloud](https://share.streamlit.io/).
3. Pilih **Create app**, repositori dan branch yang sesuai, lalu main file
   **`dashboard/dashboard.py`**. Pilih Python **3.13** pada pengaturan deployment.
4. Deploy, buka aplikasi, lalu periksa filter stasiun/tanggal dan tab kelompok konsentrasi.
5. Ganti isi `url.txt` dengan URL publik `https://....streamlit.app` yang sudah terverifikasi.
6. Buat ulang ZIP agar URL dan identitas terbaru ikut terkirim.

Jika folder `submission` dipertahankan di dalam repo, gunakan entrypoint
`submission/dashboard/dashboard.py`; paling sederhana jadikan isi folder ini sebagai root repo.
Panduan resmi: [Deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app).

## Sumber dan atribusi

Chen, S. (2017). *Beijing Multi-Site Air Quality* [Dataset]. UCI Machine Learning Repository.
DOI: [10.24432/C5RK5G](https://doi.org/10.24432/C5RK5G). Lisensi **CC BY 4.0**.
Pengamatan udara berasal dari Beijing Municipal Environmental Monitoring Center;
metadata lengkap tersedia pada [halaman dataset UCI](https://archive.ics.uci.edu/dataset/501/beijing+multi+site+air+quality+data).
Data mentah disalin dari berkas yang disediakan pengguna; agregasi harian dan kelompok konsentrasi
merupakan hasil transformasi proyek ini.
