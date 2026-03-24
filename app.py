import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import utils
import io

# Page Config
st.set_page_config(
    page_title="GIS Coordinate Verification",
    page_icon="🌍",
    layout="wide"
)

# Custom CSS for modern look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #2E86C1;
        color: white;
    }
    .stDataFrame {
        border-radius: 10px;
    }
    .status-pending { color: #f39c12; font-weight: bold; }
    .status-accept { color: #27ae60; font-weight: bold; }
    .status-reject { color: #e74c3c; font-weight: bold; }
    </style>
    """, unsafe_allow_name=True)

def main():
    st.title("🌍 GIS Coordinate Verification Prototype")
    st.markdown("---")
    
    # Sidebar: File Upload
    with st.sidebar:
        st.header("Upload Files")
        uploaded_files = st.file_uploader(
            "Upload CSV or Excel files",
            type=["csv", "xlsx"],
            accept_multiple_files=True
        )
        
        st.info("Files are processed in-memory for security.")
        
        if uploaded_files:
            if st.button("Clear All Data"):
                st.session_state.data = None
                st.rerun()

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
                 # Handle new uploads if needed, for simplicity we replace if empty or re-init
                 combined_df['Status'] = 'Pending'
                 st.session_state.data = combined_df

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
                
                # Interactive Data Editor
                # We prioritize showing Lat, Lon, Status, and name if available
                display_cols = ['Status', lat_col, lon_col] if lat_col and lon_col else ['Status']
                other_cols = [c for c in st.session_state.data.columns if c not in display_cols]
                
                edited_df = st.data_editor(
                    st.session_state.data[display_cols + other_cols],
                    column_config={
                        "Status": st.column_config.SelectboxColumn(
                            "Verification Status",
                            options=["Pending", "Accept", "Reject"],
                            required=True,
                        ),
                    },
                    hide_index=True,
                    num_rows="dynamic",
                    key="data_editor"
                )
                
                if not edited_df.equals(st.session_state.data):
                    st.session_state.data = edited_df

                # Export Section
                st.subheader("📤 Export Results")
                if st.session_state.data is not None:
                    accepted_df = st.session_state.data[st.session_state.data['Status'] == 'Accept']
                    
                    st.write(f"Points Accepted: {len(accepted_df)}")
                    
                    ecol1, ecol2 = st.columns(2)
                    
                    with ecol1:
                        # CSV Export
                        csv = accepted_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Accepted CSV",
                            data=csv,
                            file_name=utils.get_download_filename("data", "csv"),
                            mime="text/csv"
                        )
                    
                    with ecol2:
                        # KML Export
                        if lat_col and lon_col:
                            try:
                                kml_str = utils.generate_kml(accepted_df, lat_col, lon_col)
                                st.download_button(
                                    label="Download Accepted KML",
                                    data=kml_str,
                                    file_name=utils.get_download_filename("data", "kml"),
                                    mime="application/vnd.google-earth.kml+xml"
                                )
                            except Exception as e:
                                st.error(f"KML Error: {e}")
                        else:
                            st.warning("Cannot export KML: Latitude/Longitude columns not identified.")

    else:
        # Welcome Screen
        st.info("👋 Welcome! Please upload your coordinate files in the sidebar to get started.")
        st.image("https://images.unsplash.com/photo-1524661135-423995f22d0b?auto=format&fit=crop&q=80&w=1000", caption="Satellite View - Ready for Verification")

if __name__ == "__main__":
    main()
