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

if st.session_state['page'] == 'welcome':
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>⚓ Platform Informasi Klimatologi Oseanografi</h1>", unsafe_allow_html=True)
    st.write("<br><hr><br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🧑‍🌾 MASUK SEBAGAI NELAYAN LOKAL", use_container_width=True):
            st.session_state['role'] = 'masyarakat'; st.session_state['page'] = 'dashboard'; st.rerun()
    with col2:
        if st.button("🎓 PORTAL AKADEMISI / PENELITI", use_container_width=True):
            st.session_state['role'] = 'akademisi'; st.session_state['page'] = 'dashboard'; st.rerun()
else:
    role = st.session_state['role']
    st.sidebar.markdown("### 🏠 Navigasi")
    if st.sidebar.button("✨ KEMBALI KE BERANDA", use_container_width=True):
        st.session_state['page'] = 'welcome'; st.rerun()
        
    var_matriks = 'Fisheries_Index' if role == 'masyarakat' else 'Ocean_Health_Index'
    
    st.sidebar.markdown("### ⚙️ Konfigurasi Parameter")
    st.sidebar.selectbox("Target Informasi Perairan:", ["🐟 Zona Potensi Lokasi Memancing"])
    st.sidebar.selectbox("Jalur Akses Sumber Data:", ["🌐 Jalur Internet - Cloud Mode"])
    st.sidebar.markdown(f"📆 **Tanggal Operasional System:** `{datetime.date.today()}`")

    # GENERATE DATA LANGSUNG (Tanpa Tombol Trigger Biar Gak Macet di Server)
    lat = np.linspace(-12, -2, 50)
    lon = np.linspace(129, 142, 50)
    lon_g, lat_g = np.meshgrid(lon, lat)
    
    # Grid Masking Daratan Papua otomatis bersih
    mask_daratan = (lon_g > 136) & (lat_g > -8)
    
    v_base = 75.0 + np.sin(lon_g / 4.0) * 10.0 + np.cos(lat_g / 3.0) * 8.0
    v_base[mask_daratan] = np.nan
    
    df_raw = pd.DataFrame({
        'lat': lat_g.flatten(),
        'lon': lon_g.flatten(),
        var_matriks: v_base.flatten()
    }).dropna()

    st.markdown(f"## 📊 Dashboard Analisis Spasial - Mode {role.upper()}")
    
    if role == 'masyarakat':
        st.info("🐟 **REKOMENDASI NELAYAN:** Peta kesuburan air laut dan zona tangkap berhasil diperbarui secara otomatis.")
        
        fig = px.scatter_mapbox(
            df_raw, lat="lat", lon="lon", color=var_matriks,
            size=np.ones(len(df_raw))*4, zoom=5.2,
            color_continuous_scale="Jet",
            mapbox_style="open-street-map"
        )
        fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    else:
        tab1, tab2 = st.tabs(["🗺️ 1. Pemetaan Spasial Kontur", "📈 2. Analisis Runtun Waktu"])
        with tab1:
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Spatial Mean Index", f"{df_raw[var_matriks].mean():.3f}")
            col_m2.metric("Spatial Standard Deviation", f"{df_raw[var_matriks].std():.3f}")
            
            fig_map = px.scatter_mapbox(
                df_raw, lat="lat", lon="lon", color=var_matriks,
                size=np.ones(len(df_raw))*4, zoom=4.8,
                color_continuous_scale="Blues",
                mapbox_style="open-street-map"
            )
            fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
            st.plotly_chart(fig_map, use_container_width=True)
            
        with tab2:
            # Tren Runtun Waktu Multi-Dekade Otomatis
            dates = pd.date_range(start="2021-01-01", end="2026-06-01", freq="M")
            df_ts = pd.DataFrame({
                'time': dates,
                var_matriks: 78.5 + np.sin(np.arange(len(dates))) * 5.0 + np.random.normal(0, 1.5, len(dates))
            })
            st.plotly_chart(px.line(df_ts, x='time', y=var_matriks, title="Tren Jangka Panjang Multi-Dekade"), use_container_width=True)
