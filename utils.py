import pandas as pd
import simplekml
import geopandas as gpd
from shapely.geometry import Point
import zipfile
import io
import os
import shutil
import tempfile
from typing import Tuple, Optional
import datetime
import json

def detect_coordinate_columns(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    """
    Auto-detect latitude and longitude columns from a dataframe.
    
    Args:
        df: The input dataframe.
        
    Returns:
        A tuple of (lat_column_name, lon_column_name).
    """
    lat_keywords = ['lat', 'latitude', 'y']
    lon_keywords = ['lon', 'long', 'longitude', 'x']
    
    lat_col = None
    lon_col = None
    
    cols = [c.lower() for c in df.columns]
    
    for i, col in enumerate(cols):
        if any(kw == col for kw in lat_keywords):
            lat_col = df.columns[i]
        if any(kw == col for kw in lon_keywords):
            lon_col = df.columns[i]
            
    return lat_col, lon_col

def validate_coordinates(df: pd.DataFrame, lat_col: str, lon_col: str) -> pd.DataFrame:
    """
    Validate coordinate ranges and types.
    
    Args:
        df: Dataframe containing coordinates.
        lat_col: Latitude column name.
        lon_col: Longitude column name.
        
    Returns:
        DataFrame with an additional 'valid_coord' boolean column.
    """
    def is_valid(row):
        try:
            lat = float(row[lat_col])
            lon = float(row[lon_col])
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except (ValueError, TypeError):
            return False
            
    df['valid_coord'] = df.apply(is_valid, axis=1)
    return df

def generate_kml(df: pd.DataFrame, lat_col: str, lon_col: str, name_col: Optional[str] = None) -> str:
    """
    Generate KML string with custom styling from a dataframe.
    """
    kml = simplekml.Kml()
    
    # Define styles
    style_accept = simplekml.Style()
    style_accept.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/grn-circle.png'
    style_accept.iconstyle.scale = 1.2
    
    style_reject = simplekml.Style()
    style_reject.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/red-circle.png'
    style_reject.iconstyle.scale = 1.2

    style_pending = simplekml.Style()
    style_pending.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png'

    for _, row in df.iterrows():
        name = str(row[name_col]) if name_col and name_col in df.columns else f"Point {row.name}"
        pnt = kml.newpoint(name=name, coords=[(row[lon_col], row[lat_col])])
        
        # Add description
        details = "<br>".join([f"<b>{col}:</b> {val}" for col, val in row.items() if col not in [lat_col, lon_col]])
        pnt.description = f"Verified on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br><br>{details}"
        
        # Apply style based on Status
        status = str(row.get('Status', 'Pending')).lower()
        if status == 'accept':
            pnt.style = style_accept
        elif status == 'reject':
            pnt.style = style_reject
        else:
            pnt.style = style_pending
            
    return kml.kml()

def generate_geojson(df: pd.DataFrame, lat_col: str, lon_col: str) -> str:
    """Generate GeoJSON string from dataframe."""
    geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf.to_json()

def generate_shapefile_zip(df: pd.DataFrame, lat_col: str, lon_col: str) -> bytes:
    """Generate a Shapefile inside a ZIP archive in-memory."""
    geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    
    # Shapefiles have column name limit (10 chars), GeoPandas handles this but we clean up non-serializable objects
    for col in gdf.columns:
        if gdf[col].dtype == 'object':
            gdf[col] = gdf[col].astype(str)
            
    with tempfile.TemporaryDirectory() as tmp_dir:
        shapefile_basename = "verified_data"
        tmp_path = os.path.join(tmp_dir, f"{shapefile_basename}.shp")
        gdf.to_file(tmp_path, engine='pyogrio')
        
        # Create ZIP
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(tmp_dir):
                for file in files:
                    zf.write(os.path.join(root, file), file)
        
        return zip_buffer.getvalue()

def get_download_filename(original_name: str, extension: str) -> str:
    """Generate a timestamped filename for exports."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = original_name.rsplit('.', 1)[0] if '.' in original_name else original_name
    return f"{base_name}_verified_{timestamp}.{extension}"
