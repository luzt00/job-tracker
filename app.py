import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import plotly.express as px
from datetime import datetime, timedelta

# 🔹 Function to fetch earthquake data
def fetch_earthquake_data(start_time, end_time, min_magnitude, max_magnitude):
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
    params = {
        "format": "geojson",
        "starttime": start_time,
        "endtime": end_time,
        "minmagnitude": min_magnitude,
        "maxmagnitude": max_magnitude,
        "limit": 10000  # Adjust based on API limits
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    earthquakes = []
    for feature in data["features"]:
        properties = feature["properties"]
        geometry = feature["geometry"]
        
        earthquakes.append({
            "Time": datetime.utcfromtimestamp(properties["time"] / 1000),
            "Magnitude": properties["mag"],
            "Place": properties["place"],
            "Longitude": geometry["coordinates"][0],
            "Latitude": geometry["coordinates"][1],
            "Tsunami": properties.get("tsunami", 0)
        })
    
    return pd.DataFrame(earthquakes)

# 🔹 Streamlit App Layout
st.title("Earthquake Data & Analysis")
st.sidebar.header("Filters")

# Sidebar filters
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=30))
end_date = st.sidebar.date_input("End Date", datetime.now())
min_magnitude = st.sidebar.slider("Min Magnitude", 0.0, 10.0, 2.5)
max_magnitude = st.sidebar.slider("Max Magnitude", 0.0, 10.0, 8.0)
ts_only = st.sidebar.checkbox("Show Only Tsunami Events")

# Fetch data
df = fetch_earthquake_data(start_date, end_date, min_magnitude, max_magnitude)
if ts_only:
    df = df[df["Tsunami"] == 1]

st.subheader("Earthquake Data")
st.dataframe(df)

# 🔹 Interactive Map
st.subheader("Earthquake Locations")
map_center = [df["Latitude"].mean(), df["Longitude"].mean()] if not df.empty else [0, 0]
map_ = folium.Map(location=map_center, zoom_start=2)

for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=row["Magnitude"] * 1.5,
        color="red" if row["Tsunami"] else "blue",
        fill=True,
        fill_opacity=0.7,
        popup=f"Magnitude: {row['Magnitude']}\nLocation: {row['Place']}"
    ).add_to(map_)

st_folium(map_, width=700, height=450)

# 🔹 Visualizations
st.subheader("📈 Earthquake Trends")
if not df.empty:
    fig = px.histogram(df, x="Magnitude", nbins=20, title="Magnitude Distribution")
    st.plotly_chart(fig)
    
    fig_time = px.line(df.sort_values("Time"), x="Time", y="Magnitude", title="Magnitude Over Time")
    st.plotly_chart(fig_time)
else:
    st.warning("No data available for the selected filters.")
