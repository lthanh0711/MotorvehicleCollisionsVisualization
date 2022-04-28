import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = "./Motor_Vehicle_Collisions_Crashes.csv"

# LOAD DATA
st.title("Motor Vehicle Collisions in New York City")
st.markdown("This application is used to analyze motor vehicle collisions in NYC 🗽💥🚗")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows, parse_dates=[["CRASH_DATE", "CRASH_TIME"]])
    # Remove NAN data
    data.dropna(subset=["LATITUDE", "LONGITUDE"], inplace=True)
    # Lowercase column
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis="columns", inplace=True)
    # Rename some column with easy to understand name
    data.rename(columns={"crash_date_crash_time" : "date/time"}, inplace=True)
    return data

original_data = load_data(100000)

# SHOW MAP
st.header("Where are the most people injured in NYC ?")
# Max 19 people in the dataset
injured_people = st.slider("Number of persons injured in vehicle collisions", 0, int(original_data["injured_persons"].max()))
st.map(original_data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

st.header("How many collisions occur during a given time of a day ?")
hour = st.slider("Hour to look at", 0, 23)
data = original_data[original_data["date/time"].dt.hour == hour]

# VISUALIZE ON 3D MAP
st.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))
midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))

# Show map using pydeck
st.write(pdk.Deck(
    map_style="mapbox://style/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[["date/time", "latitude", "longitude"]],
            get_position=["longitude", "latitude"],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000]
        )
    ]
))

# CREATE CHART
st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data["date/time"].dt.hour >= hour) & (data["date/time"].dt.hour < hour + 1)
]
hist = np.histogram(filtered["date/time"].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})
fig = px.bar(chart_data, x="minute", y="crashes", hover_data=["minute", "crashes"], height=400)
st.write(fig)

# FILTER DATA
st.header("Top 5 dangerous streets by affected type")
select = st.selectbox("Affected type of people", ["Pedestrians", "Cyclists", "Motorists"])
# Choose top 5 streets
if (select == "Pedestrians"):
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=["injured_pedestrians"], ascending=False).dropna(how="any")[:5])
elif (select == "Cyclists"):
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=["injured_cyclists"], ascending=False).dropna(how="any")[:5])
elif (select == "Motorists"):
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=["injured_motorists"], ascending=False).dropna(how="any")[:5])
    
# SHOW RAW DATA
if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)

    