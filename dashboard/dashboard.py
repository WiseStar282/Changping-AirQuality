import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Judul dan deskripsi
st.title("Dashboard Eksplorasi Data Kualitas Udara - Changping, Beijing")
st.write("""
Data ini berisi informasi tentang kualitas udara di Changping, Beijing, China. 
Dataset mencakup berbagai polutan serta parameter cuaca seperti suhu, tekanan udara, dan kelembaban.
""")

# Load dataset
df = pd.read_csv("dataset/filtered_data.csv")

# Sidebar: Filter skala
# Histogram dan Corr Kolom berdasarkan faktor
# faktor = st.sidebar.selectbox("Pilih Faktor", ['Polutan', 'Cuaca'])
# kolom_polutan = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
# kolom_cuaca = ['TEMP', 'PRES', 'DEWP', 'WSPM']

list_kolom = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3','TEMP', 'PRES', 'DEWP','WSPM']

st.sidebar.header("Cek Tren Waktu")
kolom_pilihan1 = st.sidebar.selectbox("Pilih Kolom untuk Visual Tren", list_kolom, index=list_kolom.index("PM2.5"))
skala_pilihan1 = st.sidebar.selectbox("Pilih Skala Waktu untuk Visual Tren", ['tahunan', 'bulanan', 'harian'])

st.sidebar.header("Cek 3 Bulan Tertinggi")
kolom_pilihan2 = st.sidebar.selectbox("Pilih Kolom untuk Bar Chart", list_kolom, index=list_kolom.index("O3"))

st.sidebar.header("Cek Hubungan Antar Faktor")
kolom_opsi = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
x_var = st.sidebar.selectbox("Pilih Variabel X", kolom_opsi, index=kolom_opsi.index("TEMP"))
y_var = st.sidebar.selectbox("Pilih Variabel Y", kolom_opsi, index=kolom_opsi.index("O3"))

###############
## Ringkasan Statistik dan Histogram
# Buat tab
kolom_cuaca = ['TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
kolom_polutan = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
tab_polutan, tab_cuaca = st.tabs(["Polutan", "Cuaca"])

# Tab Polutan
with tab_polutan:
    st.subheader("Ringkasan Statistik - Polutan")
    st.dataframe(df[kolom_polutan].describe())

    st.subheader("Distribusi Nilai - Polutan")
    available_cols = [col for col in kolom_polutan if col in df.columns]
    n = len(available_cols)
    rows = (n + 2) // 3
    fig, axs = plt.subplots(nrows=rows, ncols=3, figsize=(15, 5 * rows))
    axs = axs.flatten()
    for i, col in enumerate(available_cols):
        axs[i].hist(df[col].dropna(), bins=30, color='skyblue', edgecolor='black')
        axs[i].set_title(col)
        axs[i].set_xlabel('Nilai')
        axs[i].set_ylabel('Frekuensi')
    for j in range(i + 1, len(axs)):
        axs[j].axis('off')
    plt.tight_layout()
    st.pyplot(fig)

# Tab Cuaca
with tab_cuaca:
    st.subheader("Ringkasan Statistik - Cuaca")
    st.dataframe(df[kolom_cuaca].describe())

    st.subheader("Distribusi Nilai - Cuaca")
    available_cols = [col for col in kolom_cuaca if col in df.columns]
    n = len(available_cols)
    rows = (n + 2) // 3
    fig, axs = plt.subplots(nrows=rows, ncols=3, figsize=(15, 5 * rows))
    axs = axs.flatten()
    for i, col in enumerate(available_cols):
        axs[i].hist(df[col].dropna(), bins=30, color='lightgreen', edgecolor='black')
        axs[i].set_title(col)
        axs[i].set_xlabel('Nilai')
        axs[i].set_ylabel('Frekuensi')
    for j in range(i + 1, len(axs)):
        axs[j].axis('off')
    plt.tight_layout()
    st.pyplot(fig)

####################
######## Visualisasi Heatmap Korelasi
st.subheader("Korelasi Antar Variabel")
corr_matrix = df[list_kolom].corr()
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, ax=ax)
plt.title('Heatmap Korelasi Antar Variabel', fontsize=14)
st.pyplot(fig)

######## Visualisasi Tren Waktu
st.subheader(f"Visualisasi Tren {kolom_pilihan1.capitalize()}")
def visual_line(df, kolom, skala):
    """
    Menampilkan lineplot dari kolom dan skala yang dipilih.

    Parameter:
    - df: DataFrame yang berisi kolom waktu (year, month, day, hour) dan kolom target
    - kolom: Nama kolom yang dipilih (string), misalnya 'O3', 'PM2.5', 'TEMP', dll
    - skala: Skala waktu yang dipilih ('harian', 'bulanan', 'tahunan')
    """
    df = df.copy()
    df['tanggal'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    df.set_index('tanggal', inplace=True)

    if skala == 'harian':
        data = df.resample('D')[kolom].mean()
        title = f'Tren Harian {kolom}'
        xlabel = 'Hari'
    elif skala == 'bulanan':
        data = df.resample('M')[kolom].mean()
        title = f'Tren Bulanan {kolom}'
        xlabel = 'Bulan'
    elif skala == 'tahunan':
        data = df.resample('Y')[kolom].mean()
        title = f'Tren Tahunan {kolom}'
        xlabel = 'Tahun'
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data.index, data.values, marker='o')
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(f'Rata-rata {kolom}')
    ax.grid(True)
    st.pyplot(fig)

# Visualisasi tren waktu untuk kolom terpilih
visual_line(df, kolom_pilihan1, skala_pilihan1)

############ Visualisasi Bar Chart
# BAR CHART
def visual_bar(df, kolom):
    """
    Menampilkan grafik dan tabel Top 3 bulan dengan rata-rata tertinggi dari kolom yang dipilih.

    Parameter:
    - df: DataFrame yang berisi kolom waktu (year, month, day, hour) dan kolom target
    - kolom: Nama kolom yang dipilih (string), misalnya 'O3', 'PM2.5', 'TEMP', dll
    """
    st.subheader(f"Top 3 Bulan dengan Rata-rata Tertinggi untuk '{kolom}'")

    # Pastikan kolom datetime dan 'month' ada
    if 'tanggal' not in df.columns:
        df['tanggal'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    if 'month' not in df.columns:
        df['month'] = df['tanggal'].dt.month

    # Hitung rata-rata per bulan
    monthly_avg = df.groupby('month')[kolom].mean()
    top3_months = monthly_avg.sort_values(ascending=False).head(3)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(monthly_avg.index, monthly_avg.values, color='skyblue')
    ax.set_title(f'Rata-rata Bulanan {kolom} (2013–2017)')
    ax.set_xlabel('Bulan')
    ax.set_ylabel(f'Rata-rata {kolom}')
    ax.set_xticks(range(1, 13))

    # Sorot 3 bulan tertinggi dengan warna merah
    for i, bar in enumerate(bars):
        if monthly_avg.index[i] in top3_months.index:
            bar.set_color('red')

    st.pyplot(fig)

    # Tampilkan tabel top 3
    st.write(f"### Top 3 Bulan dengan Rata-rata {kolom} Tertinggi:")
    st.dataframe(top3_months.reset_index().rename(columns={'month': 'Bulan', kolom: f'Rata-rata {kolom}'}).round(2))

visual_bar(df, kolom_pilihan2)

############### Visualisasi Scatter Plot
def visual_scatter(df, x_var, y_var):
    """
    Menampilkan scatter plot dan korelasi antara dua variabel yang dipilih.
    Parameter:
    - df: DataFrame
    - x_var: Nama variabel untuk sumbu X (string)
    - y_var: Nama variabel untuk sumbu Y (string)
    """
    st.subheader(f"Hubungan antara {x_var} dan {y_var}")

    # Hitung korelasi
    corr = df[[x_var, y_var]].corr().loc[x_var, y_var]
    corr_rounded = round(corr, 2)
    st.write(f"**Korelasi antara {x_var} dan {y_var}:** {corr_rounded}")

    # Plot scatter
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=df, x=x_var, y=y_var, ax=ax)
    ax.set_title(f'Hubungan antara {x_var} dan {y_var}')
    ax.set_xlabel(x_var)
    ax.set_ylabel(y_var)
    ax.grid(True)
    st.pyplot(fig)
    

# Visualisasi hubungan
visual_scatter(df, x_var, y_var)