import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import utils
import io
import os

# Page Config
st.set_page_config(
    page_title="GIS Coordinate Verification",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS for modern premium look
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    /* Specific font override for main elements but NOT icons to avoid text like 'keyboard_double_Arrow_Right' */
    html, body, div[data-testid="stAppViewContainer"], .stMarkdown, .stButton, .stMetric, .stSelectbox, .stTextInput, .stAlert, .stHeader { 
        font-family: 'Inter', sans-serif; 
    }
    .main { background-color: #f0f2f6; }
    div[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background: linear-gradient(135deg, #2E86C1 0%, #1B4F72 100%); color: white; font-weight: 600; border: none; transition: all 0.3s ease; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }
    .stDataFrame { border-radius: 12px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); background: white; }
    .stHeader { background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(10px); padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem; border: 1px solid rgba(255, 255, 255, 0.3); }
    /* Compact buttons for exports */
    .compact-btn div[data-testid="stColumn"] button {
        font-size: 0.75rem !important;
        height: 2.8rem !important;
        min-height: 2.8rem !important;
        padding: 0 5px !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🌍 GIS Coordinate Verification Prototype")
    st.markdown("---")
    
    # Sidebar: Branding & File Upload
    with st.sidebar:
        # Logo Section - Check for valid file
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path) and os.path.getsize(logo_path) > 0:
            # Centered, smaller logo
            left_co, cent_co, last_co = st.columns([1, 2, 1])
            with cent_co:
                st.image(logo_path, width=120)
            
            st.markdown("""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <h3 style='margin-top:0;'>
                        <span style='color: #27ae60;'>Graphmen</span> 
                        <span style='color: #2E86C1;'>Geospatial</span>
                    </h3>
                </div>
            """, unsafe_allow_html=True)
            st.markdown("---")  # Clear separation between brand and upload
        else:
            st.title("🌱 Graphmen Geospatial")
            st.markdown("---")
            
        st.header("Upload Files")
        uploaded_files = st.file_uploader(
            "Upload CSV or Excel files",
            type=["csv", "xlsx"],
            accept_multiple_files=True
        )
        
        st.info("Files are processed in-memory for security.")
        
        if uploaded_files:
            if st.button("🗑️ Clear All Data", type="secondary"):
                st.session_state.data = None
                st.rerun()
        
        st.markdown("---")

    # Initialize session state for data
    if 'data' not in st.session_state:
        st.session_state.data = None

    if uploaded_files:
        all_dfs = []
        for file in uploaded_files:
            try:
                if file.name.endswith(".csv"):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                df['Source File'] = file.name
                all_dfs.append(df)
            except Exception as e:
                st.error(f"Error reading {file.name}: {e}")
        
        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            
            # Detect Lat/Long
            lat_col, lon_col = utils.detect_coordinate_columns(combined_df)
            
            if st.session_state.data is None:
                combined_df['Status'] = 'Pending'
                st.session_state.data = combined_df
            elif len(st.session_state.data) != len(combined_df):
                 combined_df['Status'] = 'Pending'
                 st.session_state.data = combined_df

            # Compact Metrics Row
            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.info(f"📍 Total: **{len(st.session_state.data)}**")
            with mcol2:
                st.success(f"✅ Accepted: **{len(st.session_state.data[st.session_state.data['Status'] == 'Accept'])}**")
            with mcol3:
                st.error(f"❌ Rejected: **{len(st.session_state.data[st.session_state.data['Status'] == 'Reject'])}**")

            st.markdown("<br>", unsafe_allow_html=True)

            # UI Breakdown
            col1, col2 = st.columns([1, 1])
            
            with col1:
                 st.subheader("📍 Interactive Map")
                 
                 # Map Center: Default to Zimbabwe or first coordinate
                 center = [-19.0154, 29.1549]
                 if lat_col and lon_col and not st.session_state.data.empty:
                     valid_points = st.session_state.data.dropna(subset=[lat_col, lon_col])
                     if not valid_points.empty:
                         center = [valid_points.iloc[0][lat_col], valid_points.iloc[0][lon_col]]
                 
                 m = folium.Map(
                     location=center,
                     zoom_start=6,
                     tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                     attr='Esri World Imagery'
                 )
                 
                 # Add points to map
                 if lat_col and lon_col:
                     for idx, row in st.session_state.data.iterrows():
                         try:
                             lat = float(row[lat_col])
                             lon = float(row[lon_col])
                             
                             color = 'orange'
                             if row['Status'] == 'Accept': color = 'green'
                             if row['Status'] == 'Reject': color = 'red'
                             
                             folium.CircleMarker(
                                 [lat, lon],
                                 radius=5,
                                 color=color,
                                 fill=True,
                                 tooltip=f"Lat: {lat}, Lon: {lon} | Status: {row['Status']}"
                             ).add_to(m)
                         except:
                             continue
                 
                 st_folium(m, width="100%", height=500, key="gis_map")

            with col2:
                st.subheader("📋 Verification Workflow")
                
                # Export Section (Now at Top for Convenience)
                accepted_df = st.session_state.data[st.session_state.data['Status'] == 'Accept']
                if not accepted_df.empty:
                    st.success(f"🎉 **{len(accepted_df)}** points verified!")
                    
                    st.markdown('<div class="compact-btn">', unsafe_allow_html=True)
                    exp_col1, exp_col2, exp_col3, exp_col4 = st.columns(4)
                    
                    with exp_col1:
                        csv = accepted_df.to_csv(index=False).encode('utf-8')
                        st.download_button("📥 CSV", data=csv, file_name=utils.get_download_filename("data", "csv"), mime="text/csv", use_container_width=True)
                    
                    with exp_col2:
                        kml_str = utils.generate_kml(accepted_df, lat_col, lon_col)
                        st.download_button("🌍 KML", data=kml_str, file_name=utils.get_download_filename("data", "kml"), mime="application/vnd.google-earth.kml+xml", use_container_width=True)
                    
                    with exp_col3:
                        geojson_str = utils.generate_geojson(accepted_df, lat_col, lon_col)
                        st.download_button("🟢 GeoJSON", data=geojson_str, file_name=utils.get_download_filename("data", "geojson"), mime="application/geo+json", use_container_width=True)
                        
                    with exp_col4:
                        try:
                            shp_zip = utils.generate_shapefile_zip(accepted_df, lat_col, lon_col)
                            st.download_button("📦 SHP", data=shp_zip, file_name=utils.get_download_filename("data", "zip"), mime="application/zip", use_container_width=True)
                        except:
                            st.button("📦 SHP Error", disabled=True, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("---")
                else:
                    st.info("💡 **Select 'Accept' in the table below** to enable these buttons.")
                
                # Bulk Actions Bar
                bcol1, bcol2 = st.columns(2)
                with bcol1:
                    if st.button("✅ Accept All Currently Shown", use_container_width=True):
                        st.session_state.data['Status'] = 'Accept'
                        st.rerun()
                with bcol2:
                    if st.button("❌ Reject All Currently Shown", use_container_width=True):
                        st.session_state.data['Status'] = 'Reject'
                        st.rerun()

                st.markdown("---")

                # Interactive Data Editor
                # Status at the END (far right)
                other_cols = [c for c in st.session_state.data.columns if c != 'Status']
                
                st.markdown("""
                💡 **Pro Tip:** **Click the text 'Pending' in the last column** of any row to select **Accept**.
                """)
                st.markdown("⬇️ **Select 'Accept' in the Status column (far right) below:**")
                
                # Container with border to make editor stand out
                with st.container(border=True):
                    edited_df = st.data_editor(
                        st.session_state.data[other_cols + ['Status']],
                        column_config={
                            "Status": st.column_config.SelectboxColumn(
                                "🔘 Status (Click me)",
                                help="Click the 'Pending' text below to change me!",
                                options=["Pending", "Accept", "Reject"],
                                required=True,
                                width="large"
                            ),
                        },
                        hide_index=True,
                        num_rows="dynamic",
                        height=500,
                        key="data_editor",
                        use_container_width=True
                    )
                
                if not edited_df.equals(st.session_state.data):
                    st.session_state.data = edited_df

                # End of Workflow Section
                
        # Footer
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.8rem; background: rgba(255,255,255,0.5); border-radius: 10px; backdrop-filter: blur(5px);'>
                🌍 <b>GIS Verification Tool</b> | Built By Manuel Ndebele(Graphmen Geospatial) | manuza3993@gmail.com/ graphmen.geo@gmail.com--+263773807928
            </div>
        """, unsafe_allow_html=True)

    else:
        # Welcome Screen
        st.info("👋 Welcome! Please upload your coordinate files in the sidebar to get started.")
        st.image("https://images.unsplash.com/photo-1524661135-423995f22d0b?auto=format&fit=crop&q=80&w=1000", caption="Satellite View - Ready for Verification")

if __name__ == "__main__":
    main()
