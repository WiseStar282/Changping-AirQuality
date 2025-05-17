import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Dashboard Eksplorasi Data Kualitas Udara Changping")
st.write("Data ini berisi informasi tentang kualitas udara di Changping, Beijing, China. Data ini mencakup berbagai polutan dan kondisi cuaca.")

df = pd.read_csv("dataset/Air Quality Data_Changping.csv") 

# Sidebar
st.sidebar.header("Filter")
faktor = st.sidebar.selectbox("Pilih Faktor", ['Polutan', 'Cuaca'])
# Filter data
if faktor == 'Polutan':
    cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
else:
    cols = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']

# Tabel ringkasan statistik
st.subheader(f"Ringkasan Faktor {faktor}")
st.dataframe(df[cols].describe().T.round(2))

############################
# Visualisasi distribusi nilai
# Buat dua kolom layout
col1, col2 = st.columns(2)
# Cek kolom yang tersedia di data
available_cols = [col for col in cols if col in df.columns]
st.subheader(f"Distribusi Nilai {faktor} (Histogram)")
# Buat histogram dalam grid
n = len(available_cols)
rows = (n + 2) // 3  
fig, axs = plt.subplots(nrows=rows, ncols=3, figsize=(15, 5 * rows))
axs = axs.flatten()
for i, col in enumerate(available_cols):
    axs[i].hist(df[col].dropna(), bins=30, color='skyblue', edgecolor='black')
    axs[i].set_title(col)
    axs[i].set_xlabel('Nilai')
    axs[i].set_ylabel('Frekuensi')
# Kosongkan subplot yang tidak terpakai
for j in range(i+1, len(axs)):
    axs[j].axis('off')
plt.tight_layout()
st.pyplot(fig)

##########################
# Visualisasi heatmap korelasi antar variabel
st.subheader(f"Korelasi Antar Variabel")
# Kolom berdasarkan faktor
cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3','TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
# Hitung korelasi
corr_matrix = df[cols].corr()
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
plt.title(f'Heatmap Korelasi', fontsize=14)
st.pyplot(fig)

#########################     
## Visualisasi line plot tiap faktor
def visual_line(df, faktor, skala='mingguan'):
    # Pilih kolom berdasarkan faktor
    if faktor == 'Polutan':
        cols = ['PM2.5', 'PM10', 'SO2', 'NO2', 'O3']
        vertikal = 'Konsentrasi (μg/m³)'
    else:
        cols = ['TEMP', 'DEWP', 'RAIN', 'WSPM']
        vertikal = 'Nilai'
    data = [col for col in cols if col in df.columns]
    # Buat kolom datetime dan set sebagai index
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df = df.set_index('datetime')
    # Resampling data
    if skala == 'mingguan':
        dff = df[data].resample('W').mean()
        skala_title = 'Mingguan'
    elif skala == 'bulanan':
        dff = df[data].resample('M').mean()
        skala_title = 'Bulanan'
    elif skala == 'tahunan':
        dff = df[data].resample('Y').mean()
        skala_title = 'Tahunan'
    # Plot
    fig, ax = plt.subplots(figsize=(15, 6))
    for col in data:
        ax.plot(dff.index, dff[col], label=col)
    ax.set_xlabel('Waktu')
    ax.set_ylabel(vertikal) #'Konsentrasi (μg/m³ atau ppm)')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    
## Tabs untuk skala waktu
tab1, tab2, tab3 = st.tabs(["Mingguan", "Bulanan", "Tahunan"])
with tab1:
    st.subheader(f"Tren Mingguan Faktor {faktor} di Changping")
    visual_line(df, faktor=faktor, skala='mingguan')
with tab2:
    st.subheader(f"Tren Bulanan Faktor {faktor} di Changping")
    visual_line(df, faktor=faktor, skala='bulanan')
with tab3:
    st.subheader(f"Tren Tahunan Faktor {faktor} di Changping")
    visual_line(df, faktor=faktor, skala='tahunan')
    
############################
# Hari berbahaya berdasarkan kualitas udara
def hari_berbahaya(df, tahun, kolom='PM2.5', threshold=100):
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day']])
    df_year = df[df['year'] == tahun].copy()
    df_year['date'] = df_year['datetime'].dt.date
    # Hitung rata-rata harian
    daily_avg = df_year.groupby('date')[kolom].mean()
    danger_days = daily_avg[daily_avg > threshold]
    # Tampilkan info
    st.subheader(f"Tahun {tahun} - Hari Berbahaya berdasarkan {kolom}")
    st.write(f"Jumlah hari berbahaya: **{len(danger_days)} hari** (>{threshold})")
    # Tampilkan tabel
    st.dataframe(danger_days,width=800, height=200)
    
    # Visualisasi
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(daily_avg.index, daily_avg.values, label=f'{kolom} Harian')
    ax.axhline(threshold, color='red', linestyle='--', label=f'Ambang Batas ({threshold})')
    ax.set_title(f'Tren {kolom} Harian - Tahun {tahun}')
    ax.set_xlabel('Tanggal')
    ax.set_ylabel(f'{kolom} (µg/m³ atau satuan lain)')
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    
st.subheader(f"Visualisasi Hari Berbahaya Berdasarkan Kualitas Udara & Cuaca (2013–2017)")

# Pilih kolom dan ambang batas
kolom_pilihan = st.sidebar.selectbox("Pilih Kolom", cols)
ambang_batas = st.sidebar.slider("Ambang Batas", min_value=10, max_value=500, step=5, value=100)
# Tabs untuk tiap tahun
tabs = st.tabs([f"{tahun}" for tahun in range(2013, 2018)])
for i, tahun in enumerate(range(2013, 2018)):
    with tabs[i]:
        hari_berbahaya(df.copy(), tahun, kolom=kolom_pilihan, threshold=ambang_batas)
        
#############
# Visualisasi distribusi arah angin saat nilai faktor tinggi
# Judul dan Sidebar
st.subheader("Distribusi Arah Angin saat Nilai Faktor Tinggi")

# Filter data berdasarkan ambang batas
df_filtered = df[df[kolom_pilihan] > ambang_batas]
wind_counts = df_filtered['wd'].value_counts()

# Tampilkan hasil
st.write(f"Arah Angin Saat {kolom_pilihan} > {ambang_batas}")

# Visualisasi
fig, ax = plt.subplots(figsize=(8, 5))
wind_counts.plot(kind='bar', ax=ax)
ax.set_title(f'Distribusi Arah Angin saat {kolom_pilihan} Tinggi')
ax.set_xlabel('Arah Angin')
ax.set_ylabel('Jumlah Kejadian')
ax.grid(axis='y')
plt.xticks(rotation=45)
st.pyplot(fig)
####################