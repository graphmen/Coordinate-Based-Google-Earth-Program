import pandas as pd
import simplekml
from typing import Tuple, Optional
import datetime

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
    Generate KML string from a dataframe.
    
    Args:
        df: Dataframe with accepted coordinates.
        lat_col: Latitude column.
        lon_col: Longitude column.
        name_col: Column to use for placemark names.
        
    Returns:
        KML string.
    """
    kml = simplekml.Kml()
    
    for _, row in df.iterrows():
        name = str(row[name_col]) if name_col and name_col in df.columns else f"Point {row.name}"
        pnt = kml.newpoint(name=name, coords=[(row[lon_col], row[lat_col])])
        
        # Add timestamp and source if available in description
        desc = f"Verified on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        pnt.description = desc
        
    return kml.kml()

def get_download_filename(original_name: str, extension: str) -> str:
    """Generate a timestamped filename for exports."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = original_name.rsplit('.', 1)[0] if '.' in original_name else original_name
    return f"{base_name}_verified_{timestamp}.{extension}"
