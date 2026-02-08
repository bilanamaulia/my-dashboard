import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#Konfigurasi Halaman
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

#Load Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("dashboard/main_data.csv")
        df['dteday'] = pd.to_datetime(df['dteday'])
        df['user_cluster'] = pd.Categorical(
            df['user_cluster'],
            categories=['Komuter', 'Transisi', 'Rekreasi'],
            ordered=True
        )
        return df
    except FileNotFoundError:
        st.error("File `dashboard/main_data.csv` tidak ditemukan. Jalankan preprocessing terlebih dahulu.")
        st.stop()

#Inisialisasi Data
df = load_data()

#Sidebar Filter
st.sidebar.header("FilterWhere")
selected_years = st.sidebar.multiselect(
    "Tahun",
    options=sorted(df['year'].unique()),
    default=sorted(df['year'].unique())
)
selected_seasons = st.sidebar.multiselect(
    "Musim",
    options=sorted(df['season_label'].unique()),
    default=sorted(df['season_label'].unique())
)
selected_weather = st.sidebar.multiselect(
    "Kondisi Cuaca",
    options=sorted(df['weathersit_label'].unique()),
    default=sorted(df['weathersit_label'].unique())
)

#Filter data
filtered_df = df[
    (df['year'].isin(selected_years)) &
    (df['season_label'].isin(selected_seasons)) &
    (df['weathersit_label'].isin(selected_weather))
]
if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan filter yang dipilih.")
    st.stop()

#Header
st.title("🚲 Bike Sharing Analysis Dashboard")
st.markdown("""
Dashboard ini menganalisis pola penggunaan sepeda berdasarkan karakteristik pengguna dan kondisi eksternal.
""")

#Metrics Ringkasan
total_rentals = filtered_df['cnt'].sum()
avg_daily = filtered_df['cnt'].mean()
casual_ratio = filtered_df['casual_ratio'].mean()
col1, col2, col3 = st.columns(3)
col1.metric("Total Sewa", f"{total_rentals:,}")
col2.metric("Rata-rata/Hari", f"{avg_daily:.0f}")
col3.metric("Rata-rata Casual %", f"{casual_ratio:.1f}%")

#Visualisasi 1: Perbedaan Pola Pengguna
st.subheader("📊 Perbedaan Pola: Pengguna Casual vs Registered")
st.markdown("""
Pengguna casual dominan pada musim panas dan akhir pekan (pola rekreasi),
sedangkan pengguna registered lebih aktif di hari kerja (pola komuter).
""")

#Agregasi per musim
season_usage = (
    filtered_df.groupby('season_label')[['casual', 'registered']]
    .mean()
    .round(0)
    .reset_index()
    .melt(id_vars='season_label', var_name='Tipe Pengguna', value_name='Rata-rata Sewa')
)
season_usage['Tipe Pengguna'] = season_usage['Tipe Pengguna'].map({
    'casual': 'Casual',
    'registered': 'Registered'
})

fig1, ax1 = plt.subplots(figsize=(10, 6))

#Hitung nilai maksimum untuk menentukan skala
max_value = season_usage['Rata-rata Sewa'].max()
ax1.set_ylim(0, max_value * 1.25)

sns.barplot(
    data=season_usage,
    x='season_label',
    y='Rata-rata Sewa',
    hue='Tipe Pengguna',
    palette=['#66c2a5', '#fc8d62'],
    ax=ax1,
    errorbar=None
)
ax1.set_title('Rata-rata Sewa Harian per Musim oleh Tipe Pengguna', fontsize=14, fontweight='bold')
ax1.set_xlabel('Musim')
ax1.set_ylabel('Rata-rata Jumlah Sewa')
ax1.grid(axis='y', alpha=0.3)
ax1.set_axisbelow(True)

for i, container in enumerate(ax1.containers):
    for j, bar in enumerate(container):
        height = bar.get_height()
        vertical_offset = max_value * 0.06 if height > max_value * 0.8 else max_value * 0.03
        ax1.text(
            bar.get_x() + bar.get_width()/2,
            height + vertical_offset,
            f"{int(height):,}",
            ha='center',
            va='bottom',
            fontsize=9,
            fontweight='bold',
            bbox=dict(
                facecolor='white',
                alpha=0.8,
                edgecolor='none',
                boxstyle='round,pad=0.3'
            )
        )

st.pyplot(fig1)

#Visualisasi 2: Pengaruh Cuaca
st.subheader("🌤️ Pengaruh Kondisi Cuaca terhadap Total Sewa")
st.markdown("""
Kondisi cerah menghasilkan sewa tertinggi.
Hujan/salju ringan menurunkan sewa hingga >60% dibanding cuaca cerah.
""")

#Urutan cuaca
weather_order = ['Clear', 'Mist', 'Light Rain/Snow']
weather_stats = (
    filtered_df[filtered_df['weathersit_label'].isin(weather_order)]
    .groupby('weathersit_label')['cnt']
    .agg(['mean', 'count'])
    .round(0)
    .reindex(weather_order)
    .reset_index()
    .rename(columns={'mean': 'Rata-rata Sewa', 'count': 'Jumlah Hari'})
)

fig2, ax2 = plt.subplots(figsize=(10, 5.5))

#Hitung ruang ekstra untuk label di atas batang tertinggi
max_value = weather_stats['Rata-rata Sewa'].max()
ax2.set_ylim(0, max_value * 1.3)

bars = ax2.bar(
    weather_stats['weathersit_label'],
    weather_stats['Rata-rata Sewa'],
    color=['#1f77b4', '#ff7f0e', '#d62728']
)

#Tambahkan label dengan background putih untuk keterbacaan
for bar, row in zip(bars, weather_stats.itertuples()):
    height = bar.get_height()
    ax2.text(
        bar.get_x() + bar.get_width() / 2,
        height + (max_value * 0.08),
        f"{int(row._2):,}\n({int(row._3)} hari)",
        ha='center',
        va='bottom',
        fontsize=9,
        fontweight='bold',
        bbox=dict(
            facecolor='white',
            alpha=0.85,
            edgecolor='none',
            boxstyle='round,pad=0.4'
        )
    )

ax2.set_title('Rata-rata Sewa Harian Berdasarkan Kondisi Cuaca', fontsize=14, fontweight='bold')
ax2.set_xlabel('Kondisi Cuaca')
ax2.set_ylabel('Rata-rata Jumlah Sewa')
ax2.grid(axis='y', alpha=0.3)
ax2.set_axisbelow(True)

st.pyplot(fig2)

#Insight Utama
st.info("""
🔍 Insight Utama dari Analisis:
• Segmentasi Pengguna:
  - Komuter (368 hari): >85% registered → target promosi loyalitas
  - Rekreasi (162 hari): >35% casual → target promosi akhir pekan & musim panas
• Faktor Cuaca:
  - Suhu ↑ → Sewa ↑ (korelasi kuat: r=0.63)
  - Hujan ringan → Penurunan sewa hingga 63%
• Rekomendasi Bisnis:
  - Tingkatkan konversi casual → registered via promo musiman
  - Siapkan sistem notifikasi cuaca untuk antisipasi penurunan sewa
""")

#Footer
st.markdown("---")
st.caption("Dashboard ini dibuat untuk memenuhi Proyek Analisis Data Dicoding | Data Source: Bike Sharing Dataset")
