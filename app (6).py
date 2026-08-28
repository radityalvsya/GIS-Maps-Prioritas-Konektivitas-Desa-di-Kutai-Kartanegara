import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import BallTree

st.set_page_config(page_title="Dashboard Desa Kukar", layout="wide")

# Custom CSS (Dark Mode + Red Accent)
st.markdown("""
    <style>
    .stApp { background-color: #000000; color: #ffffff; }
    [data-testid='stSidebar'] { background-color: #000000; border-right: 1px solid #ff0000; }
    .sidebar-header { color: #ff0000; font-weight: 800; font-size: 1.3rem; text-transform: uppercase; }
    [data-testid='stMetric'] { background-color: #111111; border: 1px solid #ff0000; padding: 20px; border-radius: 5px; }
    /* Mengubah warna nilai metrik menjadi putih sesuai permintaan user */
    [data-testid='stMetricValue'] > div { color: #ffffff !important; }
    .stTabs [aria-selected='true'] { color: #ff0000 !important; border-bottom: 3px solid #ff0000 !important; }
    </style>
    """, unsafe_allow_html=True)

DATA_PATH = "Data_Desa_Kutai_Kartanegara.xlsx"
RANDOM_STATE = 42
FEATURE_COLS = ["jarak_ke_pusat_kab_km", "jarak_ke_centroid_kec_km", "jarak_tetangga_terdekat_km", "kepadatan_desa_10km"]

WARNA_HEX = {
    "Sangat Terpencil (Prioritas Tinggi utk Verifikasi)": "#FF0000",
    "Terpencil (Prioritas Sedang)": "#FFA500",
    "Cukup Terjangkau": "#0000FF",
    "Dekat Pusat Kota/Infrastruktur": "#008000",
}

def haversine(lat1, lon1, lat2, lon2):
    r = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    return r * 2 * np.arcsin(np.sqrt(a))

@st.cache_data
def load_data():
    df = pd.read_excel(DATA_PATH)
    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns={"Desa / Kelurahan": "Desa"})
    pusat_kab_coords = (-0.4147, 116.9807)
    df["jarak_ke_pusat_kab_km"] = haversine(df["Latitude"], df["Longitude"], pusat_kab_coords[0], pusat_kab_coords[1])
    centroid_kec = df.groupby("Kecamatan")[["Latitude", "Longitude"]].mean().rename(columns={"Latitude": "lat_c", "Longitude": "lon_c"})
    df = df.merge(centroid_kec, on="Kecamatan", how="left")
    df["jarak_ke_centroid_kec_km"] = haversine(df["Latitude"], df["Longitude"], df["lat_c"], df["lon_c"])
    coords_rad = np.radians(df[["Latitude", "Longitude"]].values)
    tree = BallTree(coords_rad, metric="haversine")
    dist, _ = tree.query(coords_rad, k=2)
    df["jarak_tetangga_terdekat_km"] = dist[:, 1] * 6371.0
    df["kepadatan_desa_10km"] = tree.query_radius(coords_rad, r=10/6371.0, count_only=True) - 1
    return df

try:
    df_app = load_data()
    with st.sidebar:
        st.markdown('<p class="sidebar-header">Control Panel</p>', unsafe_allow_html=True)
        all_kec = sorted(df_app['Kecamatan'].unique())
        selected_kec = st.multiselect("Pilih Kecamatan", options=all_kec, default=all_kec)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_app[FEATURE_COLS])
    km = KMeans(n_clusters=4, random_state=RANDOM_STATE, n_init=10)
    df_app['cluster'] = km.fit_predict(X_scaled)
    avg_dist = df_app.groupby('cluster')['jarak_ke_pusat_kab_km'].mean().sort_values(ascending=False)
    order = avg_dist.index.tolist()
    mapping = {order[0]: 'Sangat Terpencil (Prioritas Tinggi utk Verifikasi)', order[1]: 'Terpencil (Prioritas Sedang)', order[2]: 'Cukup Terjangkau', order[3]: 'Dekat Pusat Kota/Infrastruktur'}
    df_app['label_prioritas'] = df_app['cluster'].map(mapping)
    df_display = df_app[df_app['Kecamatan'].isin(selected_kec)]

    st.title("RISER GEOSPASIAL KUTAI KARTANEGARA")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("TOTAL DESA", len(df_display))
    m2.metric("KECAMATAN", df_display['Kecamatan'].nunique())
    m3.metric("RERATA JARAK", f"{df_display['jarak_ke_pusat_kab_km'].mean():.1f} KM")
    m4.metric("PRIORITAS TINGGI", len(df_display[df_display['label_prioritas'].str.contains('Sangat')]))

    tabs = st.tabs(["Peta Geospasial", "Analisis Data", "Karakteristik Wilayah", "Inventori Desa"])

    with tabs[0]:
        m = folium.Map(location=[-0.4147, 116.9807], zoom_start=9, tiles='CartoDB dark_matter')
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in df_display.iterrows():
            color = WARNA_HEX.get(row['label_prioritas'], 'gray')
            folium.CircleMarker(location=[row['Latitude'], row['Longitude']], radius=8, color=color, fill=True, fill_color=color, popup=f"{row['Desa']} ({row['label_prioritas']})").add_to(marker_cluster)
        st_folium(m, width=1200, height=600, use_container_width=True)

    with tabs[1]:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Jumlah Desa per Kecamatan**")
            fig_bar = px.bar(df_display['Kecamatan'].value_counts().reset_index(), y='Kecamatan', x='count', orientation='h', template="plotly_dark", color_discrete_sequence=['#FF3131'])
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_b:
            st.markdown("**Distribusi Fitur Keterpencilan**")
            feat_select = st.selectbox("Pilih Fitur untuk Distribusi", FEATURE_COLS)
            fig_dist = px.histogram(df_display, x=feat_select, color="label_prioritas", color_discrete_map=WARNA_HEX, template="plotly_dark", barmode="overlay")
            st.plotly_chart(fig_dist, use_container_width=True)
        st.markdown("---")
        st.markdown("**Matriks Korelasi Fitur**")
        fig_corr = px.imshow(df_display[FEATURE_COLS].corr(), text_auto=True, color_continuous_scale='RdBu_r', template="plotly_dark")
        st.plotly_chart(fig_corr, use_container_width=True)

    with tabs[2]:
        st.markdown("### Profil Statistik Klaster")
        profile = df_app.groupby('label_prioritas')[FEATURE_COLS].mean().round(2)
        st.dataframe(profile, use_container_width=True)
        fig_box = px.box(df_display, x="label_prioritas", y="jarak_ke_pusat_kab_km", color="label_prioritas", color_discrete_map=WARNA_HEX, template="plotly_dark", title="Sebaran Jarak ke Pusat Kabupaten per Klaster")
        st.plotly_chart(fig_box, use_container_width=True)

    with tabs[3]:
        st.dataframe(df_display[['Kecamatan', 'Desa', 'label_prioritas']].sort_values('Kecamatan'), use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
