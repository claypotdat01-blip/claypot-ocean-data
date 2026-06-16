import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Ocean Health & Fisheries Dashboard",
    layout="wide"
)
if "page" not in st.session_state:
    st.session_state.page = "home"

if "role" not in st.session_state:
    st.session_state.role = None
# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    df = pd.read_csv("rangkuman_historis_20tahun.csv")
    df["time"] = pd.to_datetime(df["time"])
    return df

df = load_data()
if st.session_state.page == "home":

    st.title("🌊 Platform Informasi & Prediksi Klimatologi Oseanografi")

    c1,c2 = st.columns(2)

    with c1:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/3063/3063822.png",
            width=150
        )

        if st.button(
            "🐟 Masuk Sebagai Nelayan",
            use_container_width=True
        ):
            st.session_state.role="nelayan"
            st.session_state.page="dashboard"
            st.rerun()

    with c2:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/3135/3135810.png",
            width=150
        )

        if st.button(
            "🎓 Masuk Sebagai Akademisi",
            use_container_width=True
        ):
            st.session_state.role="akademisi"
            st.session_state.page="dashboard"
            st.rerun()

    st.stop()
# =========================
# NORMALIZATION
# =========================
def normalize(series):
    return (series - series.min()) / (series.max() - series.min())
mode = st.sidebar.selectbox(
    "Mode Data",
    [
        "Historis",
        "Real Time",
        "Prediksi"
    ]
)

indeks = st.sidebar.selectbox(
    "Indeks",
    [
        "Ocean Health Index",
        "Fisheries Index"
    ]
)
if st.session_state.page == "home":

    st.title("🌊 Platform Informasi & Prediksi Klimatologi Oseanografi")

    c1,c2 = st.columns(2)

    with c1:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/3063/3063822.png",
            width=150
        )

        if st.button(
            "🐟 Masuk Sebagai Nelayan",
            use_container_width=True
        ):
            st.session_state.role="nelayan"
            st.session_state.page="dashboard"
            st.rerun()

    with c2:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/3135/3135810.png",
            width=150
        )

        if st.button(
            "🎓 Masuk Sebagai Akademisi",
            use_container_width=True
        ):
            st.session_state.role="akademisi"
            st.session_state.page="dashboard"
            st.rerun()

    st.stop()
# =========================
# DERIVED VARIABLES
# =========================
df["current_speed"] = np.sqrt(df["uo"]**2 + df["vo"]**2)

# Ocean Health Index
df["SOHI"] = (
    0.25 * normalize(df["do"]) +
    0.20 * normalize(df["ph"]) +
    0.20 * normalize(df["chla"]) +
    0.15 * normalize(df["salinitas"]) +
    0.10 * (1 - normalize(abs(df["ssta"]))) +
    0.10 * (1 - normalize(df["gelombang"]))
) * 100

# Fisheries Suitability Index
df["FSI"] = (
    0.35 * normalize(df["chla"]) +
    0.25 * normalize(df["do"]) +
    0.20 * normalize(df["current_speed"]) +
    0.10 * (1 - normalize(abs(df["ssta"]))) +
    0.10 * (1 - normalize(df["gelombang"]))
) * 100

# =========================
# SIDEBAR
# =========================
st.sidebar.title("⚙️ Konfigurasi")

parameter = st.sidebar.selectbox(
    "Pilih Parameter",
    [
        "SOHI",
        "FSI",
        "sst",
        "ssta",
        "ph",
        "do",
        "salinitas",
        "chla",
        "current_speed",
        "gelombang",
        "angin_u",
        "angin_v"
    ]
)
mode = st.sidebar.selectbox(
    "Mode Data",
    [
        "Historis",
        "Real Time",
        "Prediksi"
    ]
)

indeks = st.sidebar.selectbox(
    "Indeks",
    [
        "Ocean Health Index",
        "Fisheries Index"
    ]
)
# =========================
# HEADER
# =========================
st.title("🌊 Ocean Health & Fisheries Monitoring Dashboard")
st.markdown("Analisis data oseanografi 2001–2020")

# =========================
# METRICS
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.metric("Mean", f"{df[parameter].mean():.2f}")
col2.metric("Min", f"{df[parameter].min():.2f}")
col3.metric("Max", f"{df[parameter].max():.2f}")
col4.metric("Std", f"{df[parameter].std():.2f}")

# =========================
# TABS
# =========================
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📈 Time Series",
        "📊 Statistics",
        "🔥 Correlation",
        "🌊 Ocean Health"
    ]
)
df["year"] = df["time"].dt.year
df["month"] = df["time"].dt.month
tahun = st.sidebar.selectbox(
    "Pilih Tahun",
    sorted(df["year"].unique())
)
# =========================
# TAB 1
# =========================
with tab1:
    fig = px.line(
        df,
        x="time",
        y=parameter,
        title=f"Time Series {parameter}"
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================
# TAB 2
# =========================
with tab2:
    st.dataframe(df.describe())

# =========================
# TAB 3
# =========================
with tab3:
    numeric_df = df.select_dtypes(include=np.number)

    corr = numeric_df.corr()

    fig = px.imshow(
        corr,
        text_auto=".2f",
        title="Correlation Matrix"
    )

    st.plotly_chart(fig, use_container_width=True)
musim = {
    "Musim Barat":[12,1,2],
    "Peralihan I":[3,4,5],
    "Musim Timur":[6,7,8],
    "Peralihan II":[9,10,11]
}
df_filter = df[df["year"] == tahun]
# =========================
if breakdown == "Bulanan":

    bulan = st.sidebar.selectbox(
        "Bulan",
        [
            "Jan","Feb","Mar","Apr",
            "Mei","Jun","Jul","Agu",
            "Sep","Okt","Nov","Des"
        ]
    )

    idx = [
        "Jan","Feb","Mar","Apr",
        "Mei","Jun","Jul","Agu",
        "Sep","Okt","Nov","Des"
    ].index(bulan)+1

    df_filter = df_filter[
        df_filter["month"] == idx
    ]
    if breakdown == "Musiman":

    musim_pilih = st.sidebar.selectbox(
        "Musim",
        list(musim.keys())
    )

    df_filter = df_filter[
        df_filter["month"].isin(
            musim[musim_pilih]
        )
    ]
    lat
lon

fig = px.scatter_mapbox(
    df_filter,
    lat="lat",
    lon="lon",
    color="SOHI",
    color_continuous_scale="RdYlGn",
    zoom=4,
    mapbox_style="open-street-map"
)
fig = px.scatter_mapbox(
    df_filter,
    lat="lat",
    lon="lon",
    color="FSI",
    color_continuous_scale="Turbo",
    zoom=4,
    mapbox_style="open-street-map"
)
if st.session_state.role == "nelayan":
    st.metric(
    "Fisheries Index",
    f"{df_filter['FSI'].mean():.1f}"
)

st.metric(
    "Ocean Health",
    f"{df_filter['SOHI'].mean():.1f}"
)
if df_filter["FSI"].mean() > 80:

    st.success(
        "🐟 Sangat Potensial untuk penangkapan ikan"
    )

elif df_filter["FSI"].mean() > 60:

    st.info(
        "🐟 Potensial untuk penangkapan ikan"
    )

else:

    st.warning(
        "⚠ Potensi tangkap rendah"
    )
    tab1,tab2,tab3,tab4 = st.tabs(
    [
        "🗺️ Spasial",
        "📈 Time Series",
        "📊 Statistik",
        "🔥 Korelasi"
    ]
)
    st.dataframe(
    df_filter.describe()
)

corr = df.select_dtypes(
    include=np.number
).corr()

fig = px.imshow(
    corr,
    text_auto=".2f"
)

corr = df.select_dtypes(
    include=np.number
).corr()

fig = px.imshow(
    corr,
    text_auto=".2f"
)

if mode == "Real Time":

    st.info(
        "📡 Belum terhubung ke NOAA/CMEMS."
    )
    if mode == "Real Time":

    st.info(
        "📡 Belum terhubung ke NOAA/CMEMS."
    )
    trend = (
    df.groupby("year")
    ["SOHI"]
    .mean()
    .reset_index()
)
    from sklearn.linear_model import LinearRegression
    
# TAB 4
# =========================
with tab4:

    col_a, col_b = st.columns(2)

    with col_a:
        fig_sohi = px.line(
            df,
            x="time",
            y="SOHI",
            title="Ocean Health Index"
        )
        st.plotly_chart(fig_sohi, use_container_width=True)

    with col_b:
        fig_fsi = px.line(
            df,
            x="time",
            y="FSI",
            title="Fisheries Suitability Index"
        )
        st.plotly_chart(fig_fsi, use_container_width=True)

    st.subheader("Kategori Kondisi Laut")

    latest_sohi = df["SOHI"].iloc[-1]
    latest_fsi = df["FSI"].iloc[-1]

    if latest_sohi > 80:
        st.success("Ocean Health: Sangat Baik")
    elif latest_sohi > 60:
        st.info("Ocean Health: Baik")
    elif latest_sohi > 40:
        st.warning("Ocean Health: Sedang")
    else:
        st.error("Ocean Health: Buruk")

    if latest_fsi > 80:
        st.success("Fisheries Potential: Sangat Potensial")
    elif latest_fsi > 60:
        st.info("Fisheries Potential: Potensial")
    elif latest_fsi > 40:
        st.warning("Fisheries Potential: Cukup Potensial")
    else:
        st.error("Fisheries Potential: Rendah")
