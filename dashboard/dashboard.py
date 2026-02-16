import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Konfigurasi Halaman
st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

COLORS = {
    "primary": "#6366F1",
    "secondary": "#10B981",
    "accent": "#F59E0B",
    "danger": "#EF4444",
    "bg_dark": "#0E1117",
    "card_bg": "#1E1E1E",
    "text": "#FAFAFA"
}

# Styling
st.markdown(f"""
<style>
/* Force absolute dark mode */
:root {{
    --streamlit-color-background: {COLORS['bg_dark']} !important;
    --streamlit-color-text: {COLORS['text']} !important;
}}

.stApp {{
    background-color: {COLORS['bg_dark']} !important;
    color: {COLORS['text']} !important;
}}

/* Perbaikan: Header/Top Bar sesuai tema gelap */
header {{
    background-color: {COLORS['bg_dark']} !important;
    color: {COLORS['text']} !important;
    border-bottom: 1px solid #30363D !important;
}}

/* Perbaikan: Sidebar menggunakan variabel warna yang konsisten */
[data-testid="stSidebar"] {{
    background-color: {COLORS['bg_dark']} !important;
    border-right: 1px solid #30363D !important;
}}

/* Perbaikan: Header sidebar */
[data-testid="stSidebarHeader"] {{
    background-color: {COLORS['bg_dark']} !important;
}}

/* Perbaikan: Footer */
footer {{
    visibility: hidden;
}}

[data-testid="stMetric"] {{
    background-color: #2A2E3A !important;
    border: 1px solid #30363D !important;
    padding: 16px !important;
    border-radius: 10px !important;
    text-align: center !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3) !important;
}}

[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
    color: #FFFFFF !important;
    font-size: 24px !important;
    font-weight: bold !important;
}}

[data-testid="stMetric"] label {{
    color: #9CA3AF !important;
    font-size: 14px !important;
}}

.stTabs [role="tab"] {{
    background-color: #2A2E3A !important; 
    color: #C0C0C0 !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 10px 20px !important;
    font-weight: 500 !important;
    border: 1px solid transparent !important;
}}

.stTabs [role="tab"]:hover {{
    color: #FFFFFF !important;
    background-color: #353B4A !important;
}}

.stTabs [role="tab"].st-active {{
    background-color: #1E293B !important;
    color: #FFFFFF !important;
    font-weight: 600 !important;
    border-bottom: 2px solid {COLORS['primary']} !important;
}}

.insight-box {{
    background-color: #2A2E3A !important;
    border-left: 4px solid {COLORS['primary']} !important;
    padding: 12px 16px !important;
    border-radius: 0 4px 4px 0 !important;
    font-size: 18px !important;
    color: #D1D1D1 !important;
    height: 100% !important;
}}

.block-container {{
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}}

html, body, .stApp > div:first-child {{
    background-color: {COLORS['bg_dark']} !important;
    overflow-x: hidden !important;
}}

* {{
    margin: 0;
    padding: 0; 
    box-sizing: border-box;
}}
</style>
""", unsafe_allow_html=True)

# Konfigurasi matplotlib
plt.rcParams.update({
    'font.size': 9,
    'axes.titlesize': 11,
    'axes.labelsize': 9,
    'xtick.labelsize': 8,
    'ytick.labelsize': 8,
    'legend.fontsize': 8,
    'figure.titlesize': 11,
    'axes.titleweight': 'bold',
    'axes.labelweight': 'bold',
    'figure.dpi': 96,
    'figure.facecolor': COLORS['bg_dark'],
    'axes.facecolor': COLORS['bg_dark'],
})

def apply_notebook_style(ax, xlabel, ylabel):
    """Fungsi untuk menerapkan styling konsisten pada grafik"""
    ax.set_facecolor(COLORS['bg_dark'])
    ax.set_xlabel(xlabel, color=COLORS['text'], fontsize=9, fontweight='bold')
    ax.set_ylabel(ylabel, color=COLORS['text'], fontsize=9, fontweight='bold')
    ax.tick_params(colors=COLORS['text'], labelsize=8)
    
    # Styling sumbu
    for spine in ax.spines.values():
        spine.set_color('#333333')
    
    # Styling judul
    if ax.get_title():
        ax.set_title(ax.get_title(), color=COLORS['text'], fontsize=11, fontweight='bold')
    
    # Styling legenda
    if ax.get_legend():
        legend = ax.get_legend()
        for text in legend.get_texts():
            text.set_color(COLORS['text'])
            text.set_fontsize(8)
        if legend.get_title():
            legend.get_title().set_color(COLORS['text'])
            legend.get_title().set_fontsize(8)
            legend.get_title().set_weight('bold')
    
    plt.tight_layout()

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    try:
        day_df = pd.read_csv("data/day.csv")
        hour_df = pd.read_csv("data/hour.csv")
    except FileNotFoundError:
        st.error("File `data/day.csv` atau `data/hour.csv` tidak ditemukan. Pastikan folder `data/` berada di direktori yang sama dengan `dashboard.py`.")
        st.stop()
    
    # Konversi kolom tanggal
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    
    # Mapping musim dan cuaca
    season_map = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    weathersit_map = {1: 'Clear', 2: 'Mist', 3: 'Light Rain/Snow', 4: 'Heavy Rain/Snow'}
    
    # Tambahkan kolom label
    day_df['season_label'] = day_df['season'].map(season_map)
    day_df['weathersit_label'] = day_df['weathersit'].map(weathersit_map)
    
    return day_df, hour_df

# Load data
day_df, hour_df = load_data()

# Sidebar
st.sidebar.header("⚙️ Filter Dashboard")
min_date, max_date = day_df['dteday'].min().date(), day_df['dteday'].max().date()
date_range = st.sidebar.date_input("Rentang Waktu", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# Filter data berdasarkan tanggal
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_day = day_df[(day_df['dteday'].dt.date >= start_date) & (day_df['dteday'].dt.date <= end_date)]
    filtered_hour = hour_df[(hour_df['dteday'].dt.date >= start_date) & (hour_df['dteday'].dt.date <= end_date)]
else:
    filtered_day, filtered_hour = day_df, hour_df

# Header
st.title("Bike Sharing Analytics Dashboard")
st.caption("Analisis Pola Penggunaan Sepeda | Dicoding ID: bilanawati_99")

# Hero Metrics
c1, c2, c3 = st.columns(3)
c1.metric("Total Hari", f"{len(filtered_day):,}")
c2.metric("Total Sewa", f"{filtered_day['cnt'].sum():,}")
c3.metric("Rata-rata/Hari", f"{filtered_day['cnt'].mean():,.0f}")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Rata-rata Sewa per Musim", 
    "Hari Kerja vs Non-Kerja",
    "Pola Penggunaan per Jam", 
    "Pengaruh Cuaca",
    "Respons Cuaca: Casual vs Registered", 
    "Clustering Segmentasi"
])

# Tab 1: Rata-rata Sewa per Musim
with tab1:
    st.subheader("Rata-rata Sewa per Musim: Casual vs Registered (2011–2012)")
    col_chart, col_text = st.columns([6, 4])
    with col_chart:
        season_data = filtered_day.groupby('season_label')[['casual', 'registered']].mean().reindex(['Spring', 'Summer', 'Fall', 'Winter']).reset_index()
        fig, ax = plt.subplots(figsize=(6.0, 3.5), facecolor=COLORS['bg_dark'], dpi=96)
        melted = season_data.melt(id_vars='season_label', var_name='User Type', value_name='Avg')
        sns.barplot(data=melted, x='season_label', y='Avg', hue='User Type', palette=['#66c2a5', '#fc8d62'], ax=ax)
        apply_notebook_style(ax, "Musim", "Rata-rata Sewa")
        st.pyplot(fig)
    with col_text:
        st.markdown("""
        <div class="insight-box">
        <b>Insight:</b><br>
        Musim Fall mencatat volume tertinggi. Pengguna Registered mendominasi secara konsisten di setiap musim.
        </div>
        """, unsafe_allow_html=True)

# Tab 2: Hari Kerja vs Non-Kerja
with tab2:
    st.subheader("Rata-rata Sewa: Hari Kerja vs Non-Kerja (2011–2012)")
    col_chart, col_text = st.columns([6, 4])
    with col_chart:
        work_data = filtered_day.groupby('workingday')['cnt'].mean().reset_index()
        work_data['Label'] = work_data['workingday'].map({0: 'Libur', 1: 'Hari Kerja'})
        fig, ax = plt.subplots(figsize=(6.0, 3.5), facecolor=COLORS['bg_dark'], dpi=96)
        sns.barplot(data=work_data, x='Label', y='cnt', hue='Label', palette='viridis', legend=False, ax=ax)
        apply_notebook_style(ax, "", "Total Sewa")
        st.pyplot(fig)
    with col_text:
        st.markdown("""
        <div class="insight-box">
        <b>Insight:</b><br>
        Hari kerja menunjukkan volume sewa yang stabil, mengindikasikan penggunaan sepeda untuk mobilitas rutin.
        </div>
        """, unsafe_allow_html=True)

# Tab 3: Pola Penggunaan per Jam
with tab3:
    st.subheader("Pola Penggunaan per Jam: Perbedaan Casual vs Registered (2011-2012)")
    col_chart, col_text = st.columns([6, 4])
    with col_chart:
        hr_data = filtered_hour.groupby('hr')[['casual', 'registered']].mean().reset_index()
        fig, ax = plt.subplots(figsize=(6.0, 3.5), facecolor=COLORS['bg_dark'], dpi=96)
        ax.plot(hr_data['hr'], hr_data['registered'], label='Registered', color='#fc8d62', marker='o', markersize=3)
        ax.plot(hr_data['hr'], hr_data['casual'], label='Casual', color='#66c2a5', marker='s', markersize=3)
        ax.legend(fontsize=8)
        apply_notebook_style(ax, "Jam", "Rata-rata Sewa")
        st.pyplot(fig)
    with col_text:
        st.markdown("""
        <div class="insight-box">
        <b>Insight:</b><br>
        Dua puncak utama terjadi pada jam sibuk (08:00 & 17:00) yang didorong oleh pengguna Registered.
        </div>
        """, unsafe_allow_html=True)

# Tab 4: Pengaruh Cuaca
with tab4:
    st.subheader("Pengaruh Kondisi Cuaca terhadap Total Sewa (2011-2012)")
    col_chart, col_text = st.columns([6, 4])
    with col_chart:
        w_data = filtered_day.groupby('weathersit_label')['cnt'].mean().reindex(['Clear', 'Mist', 'Light Rain/Snow']).reset_index()
        fig, ax = plt.subplots(figsize=(6.0, 3.5), facecolor=COLORS['bg_dark'], dpi=96)
        sns.barplot(data=w_data, x='weathersit_label', y='cnt', hue='weathersit_label', palette='rocket', legend=False, ax=ax)
        apply_notebook_style(ax, "Cuaca", "Total Sewa")
        st.pyplot(fig)
    with col_text:
        st.markdown("""
        <div class="insight-box">
        <b>Insight:</b><br>
        Cuaca Cerah (Clear) adalah pendorong utama aktivitas penyewaan. Penurunan signifikan terjadi saat hujan.
        </div>
        """, unsafe_allow_html=True)

# Tab 5: Respons Cuaca
with tab5:
    st.subheader("Perbedaan Respons Cuaca: Casual vs Registered (2011-2012)")
    col_chart, col_text = st.columns([6, 4])
    with col_chart:
        wr_data = filtered_day.groupby('weathersit_label')[['casual', 'registered']].mean().reindex(['Clear', 'Mist', 'Light Rain/Snow']).reset_index()
        fig, ax = plt.subplots(figsize=(6.0, 3.5), facecolor=COLORS['bg_dark'], dpi=96)
        melted_wr = wr_data.melt(id_vars='weathersit_label', var_name='User Type', value_name='Avg')
        sns.lineplot(data=melted_wr, x='weathersit_label', y='Avg', hue='User Type', marker='o', markersize=3, palette=['#66c2a5', '#fc8d62'], ax=ax)
        ax.legend(fontsize=8)
        apply_notebook_style(ax, "Cuaca", "Rata-rata Sewa")
        st.pyplot(fig)
    with col_text:
        st.markdown("""
        <div class="insight-box">
        <b>Insight:</b><br>
        Pengguna Casual lebih sensitif terhadap cuaca buruk dibandingkan pengguna Registered.
        </div>
        """, unsafe_allow_html=True)

# Tab 6: Clustering Segmentasi
with tab6:
    st.subheader("Clustering Segmentasi Hari (2011-2012)")
    col_chart, col_text = st.columns([6, 4])
    with col_chart:
        filtered_day['casual_ratio'] = (filtered_day['casual'] / filtered_day['cnt']) * 100
        filtered_day['cluster'] = pd.cut(filtered_day['casual_ratio'], bins=[0, 15, 30, 100], labels=['Komuter', 'Transisi', 'Rekreasi'])
        counts = filtered_day['cluster'].value_counts().sort_index().reset_index()
        counts.columns = ['Segmen', 'Jumlah Hari']
        fig, ax = plt.subplots(figsize=(6.0, 3.5), facecolor=COLORS['bg_dark'], dpi=96)
        sns.barplot(data=counts, x='Segmen', y='Jumlah Hari', hue='Segmen', palette='magma', legend=False, ax=ax)
        apply_notebook_style(ax, "Segmen Hari", "Jumlah Hari")
        st.pyplot(fig)
    with col_text:
        st.markdown("""
        <div class="insight-box">
        <b>Insight:</b><br>
        Mayoritas hari masuk dalam segmen "Komuter", menunjukkan fungsi utama sepeda sebagai alat transportasi harian.
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.caption("2026 | 🧑‍💻 Bilanawati Maulia Masruroh")
