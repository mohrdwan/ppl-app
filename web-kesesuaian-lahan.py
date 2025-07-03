import streamlit as st
import geopandas as gpd
import rasterio
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen
from folium.raster_layers import ImageOverlay
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
from io import BytesIO
from rasterio.mask import mask

# === Konfigurasi halaman ===
st.set_page_config(
    page_title="Analisis Kesesuaian Lahan Kentang - Kecamatan Kertasari",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🥔"
)

# === CSS Custom untuk styling ===
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #2E7D32, #4CAF50);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    color: #FFFFFF;
    text-align: center;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}

.card {
    background-color: #f8f9fa;
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    color: #333333;
}

.metric-card {
    background: linear-gradient(135deg, #bbdefb, #90caf9);
    padding: 15px;
    border-radius: 8px;
    margin: 5px;
    text-align: center;
    color: #1A2526;
}

.layer-stats-container {
    background-color: #e8ecef !important;
    color: #1A2526 !important;
    padding: 5px;
    border-radius: 3px;
    margin: 5px 0;
}

.sidebar-header {
    background-color: #2E7D32;
    color: #FFFFFF;
    padding: 10px;
    border-radius: 5px;
    text-align: center;
    margin-bottom: 15px;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}

@media (prefers-color-scheme: dark) {
    .card {
        background-color: #2c2c2c;
        color: #e0e0e0;
    }
    .metric-card {
        background: linear-gradient(135deg, #4a6fa5, #3b5998);
        color: #e0e0e0;
    }
    .layer-stats-container {
        background-color: #3a3f44 !important;
        color: #e0e0e0 !important;
    }
}
</style>
""", unsafe_allow_html=True)

# === Definisi Layer dan Colormap ===
layer_options = {
    "Kesesuaian Lahan Akhir": "data/potato_suitability_class.tif",
    "Suhu": "data/temperature_suitability_score.tif",
    "Ketinggian": "data/elevation_suitability_score.tif",
    "Kemiringan": "data/slope_suitability_score.tif",
    "pH Tanah": "data/pH_suitability_score.tif",
    "Curah Hujan": "data/rainfall_suitability_score.tif",
    "Tekstur Tanah": "data/soil_texture_suitability_score.tif",
    "Tutupan Lahan": "data/landcover_suitability_score.tif"
}

# === Navigation ===
def main():
    st.sidebar.markdown('<div class="sidebar-header"><h2>🥔 Menu Navigasi</h2></div>', unsafe_allow_html=True)
    
    menu = st.sidebar.selectbox(
        "Pilih Halaman:",
        ["🏠 Beranda", "🗺️ Peta Interaktif", "📊 Analisis Data", "📋 Metodologi", "ℹ️ Tentang"]
    )
    
    if menu == "🏠 Beranda":
        homepage()
    elif menu == "🗺️ Peta Interaktif":
        interactive_map()
    elif menu == "📊 Analisis Data":
        data_analysis()
    elif menu == "📋 Metodologi":
        methodology()
    elif menu == "ℹ️ Tentang":
        about_page()

def homepage():
    st.markdown("""
<div class="main-header">
    <div style="display: flex; align-items: center; justify-content: center; gap: 15px;">
        <h1>🥔 PotatoGIS 🥔</h1>
    </div>
    <h3>Analisis Kesesuaian Lahan Kentang - Kecamatan Kertasari</h3>
    <p>Menggunakan Metode Skoring Multi-kriteria Berbasis GIS dan Python</p>
</div>
""", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
        <h3>🎯 Tujuan Penelitian</h3>
        <p style="text-align: justify;">
        Penelitian ini bertujuan untuk menganalisis kesesuaian lahan untuk budidaya tanaman kentang 
        di Kecamatan Kertasari menggunakan pendekatan multi-kriteria berbasis Sistem Informasi Geografis (GIS). 
        Analisis dilakukan dengan mempertimbangkan 7 parameter lingkungan yang mempengaruhi pertumbuhan kentang.
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
        <h3>📋 Parameter Analisis</h3>
        """, unsafe_allow_html=True)
        
        parameters_data = {
            "No": [1, 2, 3, 4, 5, 6, 7],
            "Parameter": ["Tutupan Lahan", "Curah Hujan", "Suhu", "Ketinggian", "Kemiringan", "pH Tanah", "Tekstur Tanah"],
            "Satuan": ["Kategori", "mm/tahun", "°C", "m dpl", "°", "Skala pH", "Kategori"],
            "Keterangan": [
                "Jenis penggunaan lahan saat ini",
                "Rata-rata curah hujan tahunan",
                "Suhu rata-rata tahunan",
                "Ketinggian tempat dari permukaan laut",
                "Tingkat kemiringan lereng",
                "Tingkat keasaman tanah",
                "Komposisi partikel tanah"
            ]
        }
        
        df_params = pd.DataFrame(parameters_data)
        st.dataframe(df_params, use_container_width=True, hide_index=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
        <h3>📍 Lokasi Penelitian</h3>
        <ul>
            <li><strong>Kecamatan:</strong> Kertasari</li>
            <li><strong>Kabupaten:</strong> Bandung</li>
            <li><strong>Provinsi:</strong> Jawa Barat</li>
            <li><strong>Luas Wilayah:</strong> ± 155.52 km²</li>
            <li><strong>Ketinggian:</strong> 1200-1.800 m dpl</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="card">
        <h3>📈 Ringkasan Hasil</h3>
        <div class="metric-card">
            <h4>Kelas Kesesuaian</h4>
            <p>Distribusi kelas kesesuaian lahan untuk tanaman kentang</p>
        </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Distribusi Kelas Kesesuaian Akhir
    try:
        df_distribution = pd.read_csv("data/potato_suitability_stats.csv")
        
        required_columns = ['Kelas', 'Persentase', 'Piksel', 'Area_km2']
        if not all(col in df_distribution.columns for col in required_columns):
            st.error("File CSV 'data/potato_suitability_stats.csv' tidak memiliki kolom yang diperlukan: Kelas, Persentase, Piksel, Area_km2")
            return
        
        if df_distribution[['Kelas', 'Persentase']].isna().any().any():
            st.error("Data CSV mengandung nilai NaN di kolom Kelas atau Persentase.")
            return
        
        st.markdown("### 📊 Visualisasi Distribusi")
        fig = px.pie(
            df_distribution,
            names='Kelas',
            values='Persentase',
            title='Distribusi Kelas Kesesuaian Lahan',
            color='Kelas',
            color_discrete_map={
                'Sangat Sesuai': '#1a9641',
                'Cukup Sesuai': '#a6d96a',
                'Sesuai Marginal': '#fdae61',
                'Tidak Sesuai': '#d7191c'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📋 Tabel Detail Distribusi")
        df_distribution['Luas (Ha)'] = df_distribution['Area_km2'] * 100
        st.dataframe(df_distribution[['Kelas', 'Piksel', 'Persentase', 'Luas (Ha)']], use_container_width=True, hide_index=True)
        
    except FileNotFoundError:
        st.error("File 'potato_suitability_stats.csv' tidak ditemukan. Pastikan file berada di direktori yang benar.")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

def interactive_map():
    st.markdown("""
    <div class="main-header">
        <h2>🗺️ Peta Interaktif Kesesuaian Lahan Kentang</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("### 🎛️ Kontrol Peta")
    
    selected_layer = st.sidebar.selectbox("🗺️ Pilih Layer:", list(layer_options.keys()))
    raster_path = layer_options[selected_layer]
    opacity = st.sidebar.slider("🔍 Transparansi Layer", 0.1, 1.0, 0.7, 0.1)
    
    st.sidebar.markdown(f"""
    ### 📋 Informasi Layer
    **Layer Aktif:** {selected_layer}
    
    **Deskripsi:**
    {get_layer_description(selected_layer)}
    """)
    
    display_legend(selected_layer)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write(f"Debug: Memuat raster dari {raster_path}")
        map_obj = create_interactive_map(raster_path, selected_layer, opacity)
        st_data = st_folium(map_obj, width=True, height=600)
        
        if st_data and st_data["last_clicked"]:
            lon, lat = st_data["last_clicked"]["lng"], st_data["last_clicked"]["lat"]
            st.success(f"📍 **Koordinat yang diklik:** {lat:.5f}°, {lon:.5f}°")
            
            try:
                with rasterio.open(raster_path) as src:
                    row, col = src.index(lon, lat)
                    value = src.read(1)[row, col]
                    interpretation = interpret_raster_value(selected_layer, value)
                    st.info(f"**Nilai:** {value} - {interpretation}")
            except:
                st.warning("⚠️ Lokasi di luar area studi")
    
    with col2:
        show_layer_statistics(raster_path, selected_layer)

def data_analysis():
    st.markdown("""
    <div class="main-header">
        <h2>📊 Analisis Data dan Statistik</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📈 Distribusi Kelas Kesesuaian Lahan")
    
    try:
        df_distribution = pd.read_csv("data/potato_suitability_stats.csv")
        
        required_columns = ['Kelas', 'Piksel', 'Persentase', 'Area_km2']
        if not all(col in df_distribution.columns for col in required_columns):
            st.error("File CSV 'data/potato_suitability_stats.csv' tidak memiliki kolom yang diperlukan: Kelas, Piksel, Persentase, Area_km2")
            return
        
        df_distribution['Luas (Ha)'] = df_distribution['Area_km2'] * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(
                df_distribution,
                values='Persentase',
                names='Kelas',
                title='Distribusi Kelas Kesesuaian Lahan',
                color='Kelas',
                color_discrete_map={
                    'Sangat Sesuai': '#1a9641',
                    'Cukup Sesuai': '#a6d96a',
                    'Sesuai Marginal': '#fdae61',
                    'Tidak Sesuai': '#d7191c'
                }
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            fig_bar = px.bar(
                df_distribution,
                x='Kelas',
                y='Persentase',
                title='Persentase Kelas Kesesuaian',
                color='Kelas',
                color_discrete_map={
                    'Sangat Sesuai': '#1a9641',
                    'Cukup Sesuai': '#a6d96a',
                    'Sesuai Marginal': '#fdae61',
                    'Tidak Sesuai': '#d7191c'
                }
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        st.markdown("### 📋 Tabel Detail Distribusi")
        st.dataframe(df_distribution[['Kelas', 'Piksel', 'Persentase', 'Luas (Ha)']], use_container_width=True, hide_index=True)
        
    except FileNotFoundError:
        st.error("File 'data/potato_suitability_stats.csv' tidak ditemukan. Pastikan file berada di direktori yang benar.")
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
    
    st.markdown("### 🔍 Analisis Parameter Individual")
    
    param_options = {
        "Suhu": "data/temperature_suitability_stats.csv",
        "Ketinggian": "data/elevation_statistics.csv",
        "Kemiringan": "data/slope_statistics.csv",
        "pH Tanah": "data/pH_suitability_stats.csv",
        "Curah Hujan": "data/rainfall_suitability_stats.csv",
        "Tekstur Tanah": "data/soil_texture_suitability_stats.csv",
        "Tutupan Lahan": "data/landcover_statistics.csv"
    }
    
    selected_param = st.selectbox("Pilih Parameter untuk Analisis:", list(param_options.keys()))
    
    try:
        analyze_parameter(param_options[selected_param], selected_param)
    except Exception as e:
        st.error(f"Error analyzing parameter: {str(e)}")

def methodology():
    st.markdown("""
    <div class="main-header">
        <h2>📋 Metodologi Penelitian</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card">
    <h3>🔄 Alur Kerja Penelitian</h3>
    <ol>
        <li><strong>Pengumpulan Data</strong> - Data spasial dan atribut</li>
        <li><strong>Preprocessing</strong> - Koreksi geometri dan proyeksi</li>
        <li><strong>Skoring Parameter</strong> - Pemberian skor 1-4 untuk setiap parameter</li>
        <li><strong>Pembobotan</strong> - Penentuan bobot kepentingan setiap parameter</li>
        <li><strong>Overlay Analysis</strong> - Penggabungan semua parameter</li>
        <li><strong>Klasifikasi</strong> - Penentuan kelas kesesuaian akhir</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📊 Kriteria Skoring Parameter")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🌡️ Suhu & Iklim", "🏔️ Topografi", "🌱 Tanah", "🏞️ Lahan"])
    
    with tab1:
        st.markdown("""
        #### Suhu Rata-rata Tahunan
        - **Skor 5 (Sangat Sesuai):** 15-20°C
        - **Skor 4 (Sesuai):** 20-25°C
        - **Skor 3 (Cukup Sesuai):** 25-30°C  
        - **Skor 2 (Tidak Sesuai):** 10-15°C
        - **Skor 1 (Sangat Tidak Sesuai):** <10°C atau >30°C
        
        #### Curah Hujan Tahunan
        - **Skor 5 (Sangat Sesuai):** 1000-1500 mm/tahun
        - **Skor 4 (Sesuai):** 900-1000 atau 1500-1700 mm/tahun
        - **Skor 3 (Cukup Sesuai):** 750-900 mm atau 1700-2000 mm/tahun
        - **Skor 2 (Kurang Sesuai):** 600-750 mm atau 2000-2500 mm/tahun
        - **Skor 1 (Tidak Sesuai):** <600 mm atau >2500 mm/tahun
        """)
    
    with tab2:
        st.markdown("""
        #### Ketinggian (m dpl)
        - **Skor 4 (Sangat Baik):** >2000 m dpl
        - **Skor 4 (Baik):** 1000-2000 m dpl
        - **Skor 3 (Sedang):** 500-1000 m dpl
        - **Skor 2 (Kurang Baik):** 100-500 m dpl
        - **Skor 1 (Buruk):** <0 m atau >100 m dpl
        
        #### Kemiringan Lereng
        - **Skor 5 (Sangat Baik):** 0-2° (datar)
        - **Skor 4 (Baik):** 2-8° (landai)
        - **Skor 3 (Sedang):** 8-15° (agak miring)
        - **Skor 2 (Kurang Baik):** 15-25° (miring)
        - **Skor 1 (Buruk):** >25° (sangat miring)
        """)
    
    with tab3:
        st.markdown("""
        #### pH Tanah
        - **Kelas 4 (Sangat Basa):** pH >8.0 
        - **Kelas 4 (Basa):** pH 7.0-8.0 
        - **Kelas 3 (Netral):** pH 5.5-7.0
        - **Kelas 2 (Asam):** pH 4.5-5.5
        - **Kelas 1 (Sangat Asam):** pH <4.5
        
        #### Tekstur Tanah
        - **Skor 5 (Sangat Sesuai):** Lempung, lempung berpasir
        - **Skor 4 (Sesuai):** Lempung berliat, lempung liat berpasir
        - **Skor 3 (Sedang):** Lempung berliat, lempung liat berpasir agak kasar
        - **Skor 2 (Kurang Sesuai):** Liat, pasir berlempung
        - **Skor 1 (Tidak Sesuai):** Pasir, liat berat
        """)
    
    with tab4:
        st.markdown("""
        #### Tutupan Lahan
        - **Skor 4 (Sangat Baik):** Lahan pertanian, tegalan
        - **Skor 3 (Baik):** Padang rumput, semak
        - **Skor 2 (Sedang):** Hutan sekunder
        - **Skor 1 (Buruk):** Pemukiman, badan air, hutan primer
        """)
    
    st.markdown("""
    <div class="card">
    <h3>🧮 Formula Perhitungan</h3>
    <p><strong>Skor Akhir = Σ(Skor Parameter × Bobot Parameter)</strong></p>
    
    <h4>Bobot Parameter:</h4>
    <ul>
        <li>Suhu: 20%</li>
        <li>Curah Hujan: 15%</li>
        <li>Ketinggian: 20%</li>
        <li>pH Tanah: 10%</li>
        <li>Tekstur Tanah: 10%</li>
        <li>Kemiringan: 15%</li>
        <li>Tutupan Lahan: 10%</li>
    </ul>
    
    <h4>Klasifikasi Akhir:</h4>
    <ul>
        <li><strong>S1 (Sangat Sesuai):</strong> Skor ≥ 3.5</li>
        <li><strong>S2 (Cukup Sesuai):</strong> Skor 2.9 - 3.5</li>
        <li><strong>S3 (Sesuai Marginal):</strong> Skor 2.4 - 2.9</li>
        <li><strong>N (Tidak Sesuai):</strong> Skor < 1.8 - 2.4</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

def about_page():
    st.markdown("""
    <div class="main-header">
        <h2>ℹ️ Tentang Aplikasi</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div class="card">
        <h3>👨‍🎓 Peneliti</h3>
        <p><strong>Nama:</strong> Mohamad Ridwan</p>
        <p><strong>Program Studi:</strong> [Teknik Informatika]</p>
        <p><strong>Institusi:</strong> [Universitas Ibn Khaldun]</p>
        <p><strong>Tahun:</strong> 2025</p>
        </div>
        
        <div class="card">
        <h3>🔬 Tentang Penelitian</h3>
        <p style="text-align: justify;">
        Penelitian ini menggunakan pendekatan Sistem Informasi Geografis (GIS) dan Python 
        untuk menganalisis kesesuaian lahan tanaman kentang. Metode yang digunakan adalah 
        multi-criteria scoring yang mempertimbangkan berbagai faktor lingkungan yang 
        mempengaruhi pertumbuhan kentang.
        </p>
        </div>
        
        <div class="card">
        <h3>🛠️ Teknologi yang Digunakan</h3>
        <ul>
            <li><strong>Python:</strong> Bahasa pemrograman utama</li>
            <li><strong>Streamlit:</strong> Framework web application</li>
            <li><strong>GDAL/Rasterio:</strong> Pengolahan data raster</li>
            <li><strong>GeoPandas:</strong> Pengolahan data vektor</li>
            <li><strong>Folium:</strong> Visualisasi peta interaktif</li>
            <li><strong>Matplotlib/Plotly:</strong> Visualisasi data</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
        <h3>📞 Kontak</h3>
        <p>📧 Email: [mohrdwan121@gmail.com]</p>
        <p>📱 WhatsApp: [089611524394]</p>
        <p>🔗 LinkedIn: [Profile LinkedIn]</p>
        </div>
        
        <div class="card">
        <h3>📝 Lisensi</h3>
        <p>Aplikasi ini dibuat untuk keperluan penelitian akademik.</p>
        </div>
        
        <div class="card">
        <h3>🙏 Acknowledgments</h3>
        <ul>
            <li>Dosen Pembimbing</li>
            <li>Instansi Penyedia Data</li>
            <li>Tim Peneliti</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

# === Helper Functions ===

def get_layer_description(layer_name):
    descriptions = {
        "Kesesuaian Lahan Akhir": "Hasil akhir analisis kesesuaian lahan untuk tanaman kentang berdasarkan semua parameter",
        "Suhu": "Distribusi suhu rata-rata tahunan yang mempengaruhi pertumbuhan kentang",
        "Ketinggian": "Ketinggian tempat dari permukaan laut yang optimal untuk budidaya kentang",
        "Kemiringan": "Tingkat kemiringan lereng yang mempengaruhi drainase dan erosi",
        "pH Tanah": "Tingkat keasaman tanah yang mempengaruhi ketersediaan nutrisi",
        "Curah Hujan": "Distribusi curah hujan tahunan untuk kebutuhan air tanaman",
        "Tekstur Tanah": "Komposisi partikel tanah yang mempengaruhi drainase dan aerasi",
        "Tutupan Lahan": "Jenis penggunaan lahan saat ini di area studi"
    }
    return descriptions.get(layer_name, "Deskripsi tidak tersedia")

def display_legend(layer_name):
    if layer_name == "Kesesuaian Lahan Akhir":
        st.sidebar.markdown("""
        ### 🎨 Legenda Kesesuaian Akhir
        <div style="font-size:14px;">
            <div style="margin:5px 0;">
                <span style="background-color:#1a9641; width:15px; height:15px; display:inline-block; margin-right:5px;"></span>
                Sangat Sesuai (S1)
            </div>
            <div style="margin:5px 0;">
                <span style="background-color:#a6d96a; width:15px; height:15px; display:inline-block; margin-right:5px;"></span>
                Cukup Sesuai (S2)
            </div>
            <div style="margin:5px 0;">
                <span style="background-color:#fdae61; width:15px; height:15px; display:inline-block; margin-right:5px;"></span>
                Sesuai Marginal (S3)
            </div>
            <div style="margin:5px 0;">
                <span style="background-color:#d7191c; width:15px; height:15px; display:inline-block; margin-right:5px;"></span>
                Tidak Sesuai (N)
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_interactive_map(raster_path, layer_name, opacity):
    # Initialize map
    m = folium.Map(
        location=[-7.1464, 107.9036],  # Initial center (approximate Kertasari)
        zoom_start=12,
        tiles='OpenStreetMap'  # Only use OpenStreetMap as basemap
    )
    
    # Load shapefile for clipping and zooming
    shp_path = "data/Kec_Kertasari.shp"
    try:
        gdf = gpd.read_file(shp_path)
        if gdf.crs != "EPSG:4326":
            gdf = gdf.to_crs("EPSG:4326")
        
        # Calculate bounds for zooming
        bounds = gdf.total_bounds  # [minx, miny, maxx, maxy]
        m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])  # Fit map to shapefile bounds
        
        # Add GeoJSON layer
        folium.GeoJson(
            gdf,
            name="Batas Kecamatan",
            show=False,
            style_function=lambda x: {
                "color": "black",
                "weight": 2,
                "fill": False
            }
        ).add_to(m)
        
        # Add markers for centroids
        if 'NAMOBJ' not in gdf.columns:
            st.error("File SHP tidak memiliki kolom 'NAMOBJ'. Pastikan kolom ini ada untuk nama kecamatan.")
        else:
            for idx, row in gdf.iterrows():
                centroid = row.geometry.centroid
                name = row['NAMOBJ']
                folium.Marker(
                    [centroid.y, centroid.x],
                    popup=f"<b>{name}</b>",
                    tooltip=name,
                    icon=folium.Icon(color='red', icon='info-sign')
                ).add_to(m)
                
    except FileNotFoundError:
        st.error(f"File SHP '{shp_path}' tidak ditemukan.")
        return m
    except Exception as e:
        st.error(f"Error loading SHP: {str(e)}")
        return m
    
    # Process raster with clipping
    try:
        with rasterio.open(raster_path) as src:
            # Clip raster to shapefile
            gdf_utm = gdf.to_crs(src.crs)  # Reproject shapefile to raster CRS
            shapes = [geom for geom in gdf_utm.geometry]
            out_image, out_transform = mask(src, shapes, crop=True, nodata=src.nodata)
            data = out_image[0]  # First band
            
            # Handle nodata values properly
            if src.nodata is not None:
                data = np.where(data == src.nodata, np.nan, data)
            
            # Ensure data is float to handle NaN properly
            data = data.astype(np.float64)
            
            # Calculate bounds for the clipped raster - use finite values only
            finite_mask = np.isfinite(data)
            rows, cols = np.where(finite_mask)  # Get indices of finite data
            
            if len(rows) == 0 or len(cols) == 0:
                st.error("Raster tidak memiliki data valid setelah clipping.")
                return m
            
            min_row, max_row = rows.min(), rows.max()
            min_col, max_col = cols.min(), cols.max()
            
            # Transform bounds to lat/lon
            top_left = rasterio.transform.xy(out_transform, min_row, min_col)
            bottom_right = rasterio.transform.xy(out_transform, max_row, max_col)
            raster_bounds = [[bottom_right[1], top_left[0]], [top_left[1], bottom_right[0]]]
            
            # Clip data to valid bounds
            data = data[min_row:max_row+1, min_col:max_col+1]
            
            # Prepare colormap and normalize data
            colors = ['#d7191c', '#fdae61', '#a6d96a', '#1a9641']
            vmin, vmax = 1, 4
            
            # Create a clean working copy of data
            data_clean = np.copy(data)
            
            # Identify valid data (not NaN, not infinite)
            valid_mask = np.isfinite(data_clean)
            
            # For invalid pixels, set to a default value that won't interfere with coloring
            data_clean[~valid_mask] = 0
            
            # Clip valid data to the expected range
            data_clean[valid_mask] = np.clip(data_clean[valid_mask], vmin, vmax)
            
            # Create colormap
            cmap = ListedColormap(colors)
            norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5, 4.5], cmap.N)
            
            # Apply colormap to the entire array
            colored_data = plt.cm.ScalarMappable(norm=norm, cmap=cmap).to_rgba(data_clean, bytes=True)
            
            # Set alpha channel: 255 for valid pixels, 0 for invalid pixels
            alpha_channel = np.where(valid_mask, 255, 0).astype(np.uint8)
            colored_data[:, :, 3] = alpha_channel
            
            # Ensure all values are within uint8 range
            colored_data = np.clip(colored_data, 0, 255).astype(np.uint8)
            
            # Create image
            img = Image.fromarray(colored_data, mode='RGBA')
            
            # Save image to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            img_uri = f"data:image/png;base64,{img_str}"
            
            # Add raster overlay
            overlay = folium.raster_layers.ImageOverlay(
                image=img_uri,
                bounds=raster_bounds,
                opacity=opacity,
                name=layer_name,
                interactive=True,
                zindex=1
            )
            overlay.add_to(m)
            
    except Exception as e:
        st.error(f"Error loading raster: {str(e)}")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")
    
    folium.LayerControl().add_to(m)
    Fullscreen().add_to(m)
    
    return m
    
    # Process raster with clipping
    try:
        with rasterio.open(raster_path) as src:
            # Clip raster to shapefile
            gdf_utm = gdf.to_crs(src.crs)  # Reproject shapefile to raster CRS
            shapes = [geom for geom in gdf_utm.geometry]
            out_image, out_transform = mask(src, shapes, crop=True, nodata=np.nan)
            data = out_image[0]  # First band
            
            # Ensure nodata values are handled correctly
            data = np.where(np.isnan(data), np.nan, data)
            
            # Calculate bounds for the clipped raster
            rows, cols = np.where(~np.isnan(data))  # Get indices of valid data
            if len(rows) == 0 or len(cols) == 0:
                st.error("Raster tidak memiliki data valid setelah clipping.")
                return m
            
            min_row, max_row = rows.min(), rows.max()
            min_col, max_col = cols.min(), cols.max()
            
            # Transform bounds to lat/lon
            top_left = rasterio.transform.xy(out_transform, min_row, min_col)
            bottom_right = rasterio.transform.xy(out_transform, max_row, max_col)
            raster_bounds = [[bottom_right[1], top_left[0]], [top_left[1], bottom_right[0]]]  # [[min_lat, min_lon], [max_lat, max_lon]]
            
            # Clip data to valid bounds
            data = data[min_row:max_row+1, min_col:max_col+1]
            
            # Prepare colormap and normalize data
            if layer_name == "Kesesuaian Lahan Akhir":
                colors = ['#d7191c', '#fdae61', '#a6d96a', '#1a9641']
                vmin, vmax = 1, 4
                data = np.clip(data, 1, 4)
            else:
                colors = ['#d7191c', '#fdae61', '#a6d96a', '#1a9641']
                vmin, vmax = 1, 4
                data = np.clip(data, 1, 4)
            
            cmap = ListedColormap(colors)
            norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5, 4.5], cmap.N)
            colored_data = plt.cm.ScalarMappable(norm=norm, cmap=cmap).to_rgba(data, bytes=True)
            
            # Set alpha channel to 0 for NaN values to ensure transparency
            alpha_channel = np.where(np.isnan(data), 0, 255).astype(np.uint8)
            colored_data[:, :, 3] = alpha_channel
            
            # Create image
            img = Image.fromarray(colored_data, mode='RGBA')
            
            # Save image to base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            img_uri = f"data:image/png;base64,{img_str}"
            
            # Add raster overlay
            overlay = folium.raster_layers.ImageOverlay(
                image=img_uri,
                bounds=raster_bounds,
                opacity=opacity,
                name=layer_name,
                interactive=True,
                zindex=1
            )
            overlay.add_to(m)
            
    except Exception as e:
        st.error(f"Error loading raster: {str(e)}")
    
    folium.LayerControl().add_to(m)
    Fullscreen().add_to(m)
    
    return m

def interpret_raster_value(layer_name, value):
    if pd.isna(value) or value == 0:
        return "No Data"
    
    try:
        value = int(round(float(value)))
    except (ValueError, TypeError):
        return "No Data"
    
    if layer_name == "Kesesuaian Lahan Akhir":
        interpretations = {
            1: "Tidak Sesuai (N)",
            2: "Sesuai Marginal (S3)",
            3: "Cukup Sesuai (S2)",
            4: "Sangat Sesuai (S1)"
        }
    else:
        interpretations = {
            1: "Kurang Baik",
            2: "Cukup",
            3: "Baik",
            4: "Sangat Baik"
        }
    
    return interpretations.get(value, f"Nilai {value}")

def show_layer_statistics(raster_path, layer_name):
    try:
        with rasterio.open(raster_path) as src:
            data = src.read(1)
            data = data[data != src.nodata]
            data = data[~np.isnan(data)]
            pixel_size = src.res[0] * src.res[1]  # Luas per piksel dalam meter persegi
            
            if len(data) > 0:
                data = np.clip(data, 1, 4)
                unique, counts = np.unique(data, return_counts=True)
                total = np.sum(counts)
                
                st.markdown("### 📊 Statistik Layer")
                
                if layer_name == "Kesesuaian Lahan Akhir":
                    class_map = {
                        1: "Tidak Sesuai (N)",
                        2: "Sesuai Marginal (S3)",
                        3: "Cukup Sesuai (S2)",
                        4: "Sangat Sesuai (S1)"
                    }
                else:
                    class_map = {
                        1: "Kurang Baik",
                        2: "Cukup",
                        3: "Baik",
                        4: "Sangat Baik"
                    }
                
                for val in sorted(unique):
                    if val in class_map:
                        count = counts[np.where(unique == val)[0][0]]
                        percentage = (count / total) * 100
                        interpretation = class_map[val]
                        area_ha = (count * pixel_size) / 10000  # Konversi m² ke hektar
                        
                        st.markdown(f"""
                        <div class="layer-stats-container">
                            <strong>{interpretation}</strong><br>
                            {percentage:.1f}% ({count:,} piksel)<br>
                            Luas: {area_ha:.1f} Ha
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown(f"**Total Piksel:** {total:,}")
                st.markdown(f"**Luas Total:** {(total * pixel_size) / 10000:.1f} Ha")
            else:
                st.warning("Raster kosong atau tidak memiliki data yang bisa dihitung.")
                
    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")

def analyze_parameter(csv_path, param_name):
    try:
        df_param = pd.read_csv(csv_path)
        
        required_columns = ['Kelas', 'Piksel', 'Persentase', 'Area_km2', 'Skor']
        if not all(col in df_param.columns for col in required_columns):
            st.error(f"File CSV untuk {param_name} tidak memiliki kolom yang diperlukan: Kelas, Piksel, Persentase, Area_km2, Skor")
            return
        
        df_param['Luas (Ha)'] = df_param['Area_km2'] * 100
        
        df_param['Interpretasi'] = df_param['Skor'].apply(lambda x: interpret_raster_value(param_name, x))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Piksel", f"{int(df_param['Piksel'].sum()):,}")
        with col2:
            st.metric("Total Luas (Ha)", f"{df_param['Luas (Ha)'].sum():.1f}")
        with col3:
            st.metric("Jumlah Kelas", f"{len(df_param)}")
        
        st.markdown(f"### 📈 Histogram Distribusi {param_name}")
        fig_hist = px.histogram(
            df_param,
            x='Kelas',
            y='Piksel',
            title=f'Histogram Distribusi {param_name}',
            labels={'x': 'Kelas Skor', 'y': 'Frekuensi'},
            color='Kelas',
            color_discrete_map={
                'Sangat Baik': '#1a9641',
                'Baik': '#a6d96a',
                'Cukup': '#fdae61',
                'Kurang Baik': '#d7191c'
            }
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
        st.markdown(f"### 📊 Box Plot {param_name}")
        fig_box = px.box(
            df_param,
            y='Piksel',
            title=f'Box Plot Distribusi {param_name}',
            labels={'y': 'Jumlah Piksel'},
            color='Kelas',
            color_discrete_map={
                'Sangat Baik': '#1a9641',
                'Baik': '#a6d96a',
                'Cukup': '#fdae61',
                'Kurang Baik': '#d7191c'
            }
        )
        st.plotly_chart(fig_box, use_container_width=True)
        
        st.markdown(f"### 📋 Distribusi Kelas {param_name}")
        st.dataframe(df_param[['Kelas', 'Piksel', 'Persentase', 'Luas (Ha)', 'Interpretasi']], 
                    use_container_width=True, hide_index=True)
        
    except FileNotFoundError:
        st.error(f"File '{csv_path}' tidak ditemukan. Pastikan file berada di direktori yang benar.")
    except Exception as e:
        st.error(f"Error analyzing parameter: {str(e)}")

# === Data Validation Functions ===

def validate_data_files():
    required_files = [
        "data/potato_suitability_class.tif",
        "data/temperature_suitability_score.tif",
        "data/elevation_suitability_score.tif",
        "data/slope_suitability_score.tif",
        "data/pH_suitability_score.tif",
        "data/rainfall_suitability_score.tif",
        "data/soil_texture_suitability_score.tif",
        "data/landcover_suitability_score.tif",
        "data/Kec_Kertasari.shp",
        "data/potato_suitability_stats.csv",
        "data/temperature_suitability_stats.csv",
        "data/elevation_statistics.csv",
        "data/slope_statistics.csv",
        "data/pH_suitability_stats.csv",
        "data/rainfall_suitability_stats.csv",
        "data/soil_texture_suitability_stats.csv",
        "data/landcover_statistics.csv"
    ]
    
    missing_files = []
    for file in required_files:
        try:
            if file.endswith('.tif'):
                with rasterio.open(file) as src:
                    pass
            elif file.endswith('.shp'):
                gpd.read_file(file)
            else:
                pd.read_csv(file)
        except:
            missing_files.append(file)
    
    if missing_files:
        st.sidebar.error("⚠️ File Data Tidak Ditemukan:")
        for file in missing_files:
            st.sidebar.write(f"- {file}")
        st.sidebar.info("Pastikan semua file data raster (.tif), SHP (.shp), dan CSV (.csv) berada dalam direktori yang sesuai.")
        return False
    
    return True

# === Main Application ===

if __name__ == "__main__":
    if validate_data_files():
        main()
    else:
        st.error("❌ Tidak dapat menjalankan aplikasi karena file data tidak lengkap.")
        st.info("""
        **Solusi:**
        1. Pastikan semua file raster (.tif), SHP (.shp), dan CSV (.csv) berada dalam folder yang sesuai
        2. Periksa nama file sesuai dengan yang dibutuhkan
        3. Pastikan file tidak rusak dan dapat dibaca
        """)

# === Footer ===
st.markdown("""
---
<div style="text-align: center; color: #666; margin-top: 50px;">
    <p>© 2025 - Analisis Kesesuaian Lahan Kentang | Mohamad Ridwan - Penelitian Akademik</p>
</div>
""", unsafe_allow_html=True)
