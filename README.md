# Dashboard Analisis Keterpencilan Geografis Desa — Kutai Kartanegara

Versi Streamlit dari notebook `Dashboard_Analisis_Desa_Kukar.ipynb`.
Dipakai untuk Pra-Riset Program Internet Desa Gratis (Tim 2 — Diskominfo),
Beasiswa Tematik Pemkab Kutai Kartanegara x Telkom University Bandung.

## Cara menjalankan

1. Pastikan file `Data_Desa_Kutai_Kartanegara.xlsx` ada di folder yang sama dengan `app.py`.
2. Install dependency:

   ```bash
   pip install -r requirements.txt
   ```

3. Jalankan aplikasi:

   ```bash
   streamlit run app.py
   ```

4. Browser otomatis terbuka di `http://localhost:8501`.

## Fitur

- **Filter Kecamatan** & pengaturan clustering (K-Means / DBSCAN) di sidebar.
- **Tab Peta** — sebaran desa & indikasi prioritas geografis secara interaktif.
- **Tab EDA** — jumlah desa per kecamatan, korelasi fitur, distribusi fitur.
- **Tab Clustering** — elbow method, silhouette score, daftar desa prioritas verifikasi.
- **Tab Data & Unduh** — tabel lengkap + unduh CSV/Excel hasil clustering.
- **Tab SVM — Data Asli** — unggah data status konektivitas resmi dari Diskominfo
  (kolom minimal: `Kecamatan`, `Desa`, `status_konektivitas`) untuk melatih model
  SVM dan memprediksi status desa yang belum diverifikasi langsung.

## Catatan Penting

Label prioritas ("Sangat Terpencil", dst.) di tab Peta/Clustering adalah **indikasi
awal berbasis jarak geografis (proxy)**, bukan status konektivitas resmi. Wajib
diverifikasi lewat audiensi dengan Diskominfo/DPMD/Bappeda sebelum dipakai sebagai
kesimpulan, sesuai prinsip pra-riset (faktual, objektif, memisahkan fakta & dugaan).

## Deploy online (opsional)

Bisa langsung di-deploy gratis lewat [Streamlit Community Cloud](https://streamlit.io/cloud):
push folder ini (termasuk file Excel-nya) ke repo GitHub, lalu hubungkan lewat
dashboard Streamlit Cloud — pilih `app.py` sebagai entry point.
