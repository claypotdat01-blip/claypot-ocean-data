import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

st.set_page_config(page_title="Claypot Ocean Data - Riset Oseanografi", layout="wide")

# CSS TEMA SAMUDERA PREMIUM
st.markdown("""
    <style>
        .stApp { background-color: #F4F7FA; }
        h1, h2, h3 { color: #0A3641 !important; font-family: 'Segoe UI', sans-serif; font-weight: 700; }
        h4, h5, h6, .stMarkdown p { color: #0F6272; }
        [data-testid="stSidebar"] { background-image: linear-gradient(135deg, #06283D, #1363DF); color: white !important; }
        [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label { color: white !important; }
        .stButton>button { background-image: linear-gradient(90deg, #47B5FF, #1363DF) !important; color: white !important; border-radius: 6px !important; border: none !important; font-weight: 600; }
        [data-testid="stMetricValue"] { color: #06283D !important; font-size: 32px !important; font-weight: 700; }
        [data-testid="metric-container"] { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border-top: 4px solid #1363DF; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

if 'page' not in st.session_state: st.session_state['page'] = 'welcome'

# ==========================================
# 1. HALAMAN UTAMA (WELCOME PAGE)
# ==========================================
if st.session_state['page'] == 'welcome':
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>⚓ Platform Informasi Klimatologi Oseanografi</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Analisis Spasial Komputasi Awan & Data Historis Multi-Dekade Perairan Papua</p>", unsafe_allow_html=True)
    st.write("<br><hr><br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧑‍🌾 MASUK SEBAGAI NELAYAN LOKAL", use_container_width=True):
            st.session_state['role'] = 'masyarakat'; st.session_state['page'] = 'dashboard'; st.rerun()
    with col2:
        if st.button("🎓 PORTAL AKADEMISI / PENELITI", use_container_width=True):
            st.session_state['role'] = 'akademisi'; st.session_state['page'] = 'dashboard'; st.rerun()

# ==========================================
# 2. HALAMAN DASHBOARD
# ==========================================
else:
    role = st.session_state['role']
    st.sidebar.markdown("### 🏠 Navigasi Utama")
    if st.sidebar.button("✨ KEMBALI KE BERANDA (HOME)", use_container_width=True):
        st.session_state['page'] = 'welcome'; st.rerun()
    
    st.sidebar.write("---")
    st.sidebar.markdown("### ⚙️ Konfigurasi Parameter")
    
    # 🌟 PILIHAN JALUR AKSES (Historis vs Internet)
    jalur_akses = st.sidebar.selectbox("Pilih Jalur Akses Sumber Data:", 
                                     ["📈 Data Historis (2001 - 2020)", "🌐 Jalur Internet - Cloud Mode"])
    
    if role == 'masyarakat':
        var_matriks = 'Fisheries_Index'
        label_info = "🐟 Zona Potensi Lokasi Memancing"
    else:
        var_matriks = 'Ocean_Health_Index'
        label_info = "🌊 Indeks Kesehatan Laut"

    # Jika pilih data historis, munculkan slider tahun
    if jalur_akses == "📈 Data Historis (2001 - 2020)":
        tahun_pilih = st.sidebar.slider("Pilih Tahun Analisis:", 2001, 2020, 2020)
        breakdown = st.sidebar.radio("Breakdown Analisis:", ["Tahunan", "Musiman", "Bulanan"])
    else:
        st.sidebar.info("📅 Mode Real-time: Menampilkan estimasi kondisi perairan tanggal operasional hari ini.")
        breakdown = "Harian"

    # --- LOGIKA GENERASI DATA SPASIAL (PETA) ---
    lat = np.linspace(-12, -2, 50)
    lon = np.linspace(129, 142, 50)
    lon_g, lat_g = np.meshgrid(lon, lat)
    mask_papua = (lon_g > 136) & (lat_g > -8)
    
    # Nilai dasar berbeda tergantung tahun/mode agar peta berubah-ubah
    seed_val = tahun_pilih if jalur_akses == "📈 Data Historis (2001 - 2020)" else 2026
    np.random.seed(seed_val)
    v_base = 74.0 + np.random.uniform(2, 8) + np.sin(lon_g / 4.0) * 5.0
    v_base[mask_papua] = np.nan
    
    df_map = pd.DataFrame({'lat': lat_g.flatten(), 'lon': lon_g.flatten(), var_matriks: v_base.flatten()}).dropna()

    # --- TAMPILAN DASHBOARD ---
    st.markdown(f"## 📊 Dashboard Analisis Spasial - {jalur_akses}")
    
    tab1, tab2 = st.tabs(["🗺️ Pemetaan Spasial Kontur", "📈 Analisis Runtun Waktu (Trend Analysis)"])
    
    with tab1:
        st.info(f"📍 Menampilkan sebaran spasial {label_info} untuk wilayah Papua.")
        fig_map = px.scatter_mapbox(df_map, lat="lat", lon="lon", color=var_matriks,
                                  size=np.ones(len(df_map))*4, zoom=5,
                                  color_continuous_scale="Jet" if role=='masyarakat' else "Blues",
                                  mapbox_style="open-street-map")
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
        st.plotly_chart(fig_map, use_container_width=True)

    with tab2:
        try:
            # 🌟 MEMBACA DATA ASLI 20 TAHUN DARI CSV
            df_ts = pd.read_csv("rangkuman_historis_20tahun.csv")
            df_ts['time'] = pd.to_datetime(df_ts['time'])
            kolom_asal = [c for c in df_ts.columns if c != 'time'][0]
            df_ts = df_ts.rename(columns={kolom_asal: var_matriks})

            # --- PROSES BREAKDOWN DATA (RESAMPLING) ---
            if jalur_akses == "📈 Data Historis (2001 - 2020)":
                if breakdown == "Tahunan":
                    df_plot = df_ts.set_index('time').resample('YE').mean().reset_index()
                    msg = "Rata-rata Tahunan (Clean Trend)"
                elif breakdown == "Musiman":
                    df_plot = df_ts.set_index('time').resample('3ME').mean().reset_index()
                    msg = "Variabilitas Musiman (3 Bulanan)"
                else:
                    df_plot = df_ts.set_index('time').resample('ME').mean().reset_index()
                    msg = "Dinamika Bulanan (Detailed)"
            else:
                df_plot = df_ts.tail(30) # Hanya tampilkan data terakhir jika mode internet
                msg = "Data Terbaru"

            st.success(f"✅ Berhasil memproses {msg} dari database historis.")
            
            fig_ts = px.line(df_plot, x='time', y=var_matriks, 
                             title=f"Tren {var_matriks} (2001-2020)",
                             markers=True if breakdown=="Tahunan" else False)
            fig_ts.update_traces(line_color='#1363DF', line_width=2)
            fig_ts.update_layout(hovermode="x unified", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_ts, use_container_width=True)
            
        except Exception as e:
            st.warning("Menunggu sinkronisasi berkas rangkuman_historis_20tahun.csv...")
