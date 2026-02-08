# Bike Sharing Analysis Dashboard

Dashboard interaktif untuk menganalisis pola penggunaan sepeda berdasarkan karakteristik pengguna dan kondisi eksternal.

## 📊 Pertanyaan Bisnis yang Dijawab

1. **Bagaimana perbedaan pola penggunaan sepeda antara pengguna casual (non-terdaftar) dan registered (terdaftar) berdasarkan waktu (musim, hari dalam minggu)?**  
   - Pengguna **casual** dominan pada musim panas (22.2%) dan akhir pekan (31.7%) → pola rekreasi.
   - Pengguna **registered** dominan pada hari kerja (86.8%) → pola komuter harian.

2. **Bagaimana pengaruh kondisi cuaca terhadap total sewa sepeda?**  
   - Kondisi **cerah** menghasilkan rata-rata sewa tertinggi: **4,877/hari**.
   - Hujan/salju ringan menurunkan sewa hingga **63%** dibanding cuaca cerah.

## 🚀 Cara Menjalankan Dashboard

### Prasyarat
- Python 3.8+
- Dataset `day.csv` dan `hour.csv` di folder `data/`

### Instalasi & Jalankan
```bash
# 1. Buat virtual environment (opsional tapi direkomendasikan)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Jalankan dashboard
streamlit run dashboard/dashboard.py