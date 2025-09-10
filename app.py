import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px



# Configure Streamlit page
st.set_page_config(
    page_title="Predictive Maintenance Dashboard",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem; /* Adjust this value as needed, 0rem for minimal top space */
     }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .alert-critical {
        background-color: #ffebee;
        border-left: 5px solid #f44336;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .alert-warning {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
    }
    .alert-good {
        background-color: #e8f5e8;
        border-left: 5px solid #4caf50;
        padding: 10px;
        margin: 10px 0;
        border-radius: 5px;
        color: black;
    }
    .rc-slider-track {
        background-color: indigo;
    }
    .title-font {
        font-size: 14px !important; /* Adjust as needed */
    }
    .header-font {
        font-size: 14px !important; /* Adjust as needed */
    }
              .rc-slider-track {
            background-color: #337ab7; /* Example blue color */
    }
</style>
""", unsafe_allow_html=True)

# Main Dashboard
title = '⚙️Predictive Maintenance Dashboard'
st.title(title)
#st.markdown("Real-time equipment monitoring with predictive analytics")
st.markdown("🔮 Predictive Analytics")

# Sidebar
st.sidebar.header("Dashboard Controls")
auto_refresh = st.sidebar.checkbox("Auto Refresh", value=False)
if auto_refresh:
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 3)

st.sidebar.button("🔄 Refresh Now")
   # update_sensor_data()

st.sidebar.button("📁 Export Data")

st.sidebar.button("🗑️ Clear Data")
   
st.sidebar.markdown("---")
st.sidebar.success("🟢 All sensors online")
#st.sidebar.info(f"Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")
#st.sidebar.info(f"Data points: {len(st.session_state.sensor_data['timestamp'])}")


# load Data
#df = pd.read_csv("dataset/Casing_pressure-anomaly-csv.csv")
df = pd.read_csv("dataset/2sd-casing-pressure.csv")

df = df.rename(columns={
    "t_stamp": "timestamp",
    "Well Pads/Pronghorn KO/12HNB/Well Head/Well Casing Pressure/Value" : "casing_pressure"
})

# convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

df_non_index = df

#df.to_csv("timestamp-corrected.csv")
df['anomaly_percent'] = ((df['casing_pressure'] - df['casing_pressure'].std()) / df['casing_pressure']) * 100


# Set index for time-series ops
df = df.set_index("timestamp").sort_index()

max_valid_pressure = 300

df_non_index['sensor_malfunction'] = df_non_index['casing_pressure'] > max_valid_pressure

print("\nSensor Error: ", df_non_index['sensor_malfunction'].sum())

#df_non_index.head()
#df_non_index.describe()

df_clean = df_non_index[~df_non_index["sensor_malfunction"]].copy()



fig = px.line(df_clean, x='timestamp', y='casing_pressure', title='Casing Pressure')
fig.update_layout(
    title={'text': "Casing Pressure"}
)
fig.update_layout(
    xaxis_title="Timestamp"
)
fig.update_layout(
    yaxis_title="Casing Pressure"
)
fig.update_xaxes(
    rangeslider_visible=True,
    rangeslider_bordercolor= "#111",
    rangeslider_bgcolor="rgb(230, 234, 241)",
    rangeselector=dict(
        buttons=list([
            dict(count=1, label='5M', step='minute', stepmode='backward'),
            dict(count=1, label='1H', step='hour', stepmode='backward'),
            dict(count=1, label='1D', step='day', stepmode='backward'),
            dict(count=1, label='1M', step='month', stepmode='backward'),
            dict(step='all')
        ])
    )
)

with st.container(border=True):
    st.plotly_chart(fig, use_container_width=True)

# Fox Creek Panel

# load Data
df = pd.read_csv("dataset/fox_creek_25-csv.csv")

df = df.rename(columns={
    "t_stamp": "timestamp",
    "Well Pads/Fox Creek 25SE/12-63 25-2-1/Heater Treater/Gas Meter/Today Flow" : "fc_pressure"
})

# convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.drop('Unnamed: 3', axis=1)

df_non_index = df

df.info()


print("Rows  : ", df.shape[0])
print("Columns  : ", df.shape[1])
print("\nFeatures  :\n", df.columns.to_list())
print("\nMissing Values :\n", df.isnull().any())
print("\n Unique Values :\n", df.nunique())

# Set index for time-series ops
df = df.set_index("timestamp").sort_index()


import plotly.express as px

fig = px.line(df_non_index, x='timestamp', y='fc_pressure', title='Fox Creek Accumulator')
#fig.update_layout(barcornerradius=15, paper_bgcolor="white")
fig.update_layout(
    xaxis_title="Timestamp"
)
fig.update_layout(
    yaxis_title="Accumulator"
)
fig.update_xaxes(
    rangeslider_visible=True,
    rangeslider_bgcolor="rgb(62, 76, 102)",
    rangeselector=dict(
        buttons=list([
            dict(count=1, label='5M', step='minute', stepmode='backward'),
            dict(count=1, label='1H', step='hour', stepmode='backward'),
            dict(count=1, label='1D', step='day', stepmode='backward'),
            dict(count=1, label='1M', step='month', stepmode='backward'),
            dict(step='all')
        ])
    )
)

with st.container(border=True):
    st.plotly_chart(fig, use_container_width=True)
