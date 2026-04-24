# Analisis Sentimen Masyarakat Global terhadap Lagu "Hati-Hati di Jalan"

Proyek Big Data ini bertujuan untuk menganalisis sentimen masyarakat global terhadap lagu "Hati-Hati di Jalan" karya Tulus berdasarkan komentar di YouTube menggunakan **Apache Spark** dan algoritma **Logistic Regression**.

## Struktur Folder
- `scrapping/`: Berisi skrip untuk mengambil data komentar dari YouTube.
- `data/`: Folder tempat menyimpan hasil scraping (CSV/JSON).
- `notebooks/` (Upcoming): Berisi file implementasi Spark dan Logistic Regression.

## Persiapan
1. **Dapatkan YouTube API Key**:
   - Buka [Google Cloud Console](https://console.cloud.google.com/).
   - Buat proyek baru.
   - Aktifkan **YouTube Data API v3**.
   - Pergi ke menu **Credentials** dan buat **API Key**.
2. **Install Dependensi**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Konfigurasi Environment**:
   Buat file `.env` di root folder dan tambahkan API Key Anda:
   ```env
   YOUTUBE_API_KEY=YOUR_API_KEY_HERE
   ```

## Cara Menjalankan Scraper
1. Masuk ke folder `scrapping`.
2. Jalankan skrip:
   ```bash
   python youtube_scraper.py
   ```
3. Hasil akan disimpan di folder `data/raw_comments.csv`.

## Metodologi
1. **Scraping**: Mengambil ribuan komentar dari berbagai video terkait "Hati-Hati di Jalan".
2. **Preprocessing**: Membersihkan data menggunakan Spark (stopword removal, stemming, tokenization).
3. **Modeling**: Melatih model Logistic Regression untuk klasifikasi sentimen (Positif, Negatif, Netral).
4. **Evaluation**: Mengukur akurasi model.
