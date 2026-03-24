# GIS Coordinate Verification Prototype 🌍

A high-performance, web-based tool designed for verifying geographic coordinates from spreadsheets. This prototype was built to demonstrate proficiency in GIS development, data handling, and rapid web application deployment.

## 🚀 Live Demo
*[Insert Link to Streamlit Cloud Deployment here]*

## ✨ Features
- **Smart Data Ingestion**: Drag-and-drop support for CSV and Excel files.
- **Auto-Detection**: Case-insensitive logic for identifying Latitude and Longitude columns.
- **Satellite Map Interface**: Uses high-resolution **Esri World Imagery** for precise location verification.
- **Interactive Workflow**: Editable grid to Accept/Reject points with real-time map marker updates.
- **Bulk Export**:
    - **CSV**: Detailed spreadsheet of all "Accepted" entries.
    - **KML**: Ready-to-use placemarks for **Google Earth Pro/Desktop**.

## 🛠️ Tech Stack
- **Frontend/Backend**: [Streamlit](https://streamlit.io/)
- **Mapping**: [Folium](https://python-visualization.github.io/folium/) & [Streamlit-Folium](https://github.com/randyzwitch/streamlit-folium)
- **Data Science**: [Pandas](https://pandas.pydata.org/)
- **Excel Support**: `openpyxl`
- **GIS Formats**: `simplekml`

## 📦 Local Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/gis-verification-prototype.git
   cd gis-verification-prototype
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

## ☁️ Deployment Guide

### Option 1: Streamlit Cloud (Recommended)
1. Push this code to a public GitHub repository.
2. Sign in to [Streamlit Cloud](https://share.streamlit.io/).
3. Click "New App", select your repo, and set the main file to `app.py`.
4. Your app will be live in seconds!

### Option 2: Vercel
1. The repository includes a `vercel.json` and is pre-configured for Vercel's Python runtime.
2. Connect your GitHub repository to [Vercel](https://vercel.com/).
3. Vercel will automatically detect the Streamlit framework and deploy.

## 📂 Project Structure
- `app.py`: Main interactive UI and map logic.
- `utils.py`: Backend utilities for KML generation and data parsing.
- `requirements.txt`: Python package dependencies.
- `.streamlit/config.toml`: Custom theme and layout settings.
- `vercel.json`: Deployment configuration.

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
