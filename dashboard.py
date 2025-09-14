import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, JsCode
from datetime import datetime, timedelta
import plotly.express as px
from PIL import Image 




# Page title
#st.title("Pressure Sensor Monitoring Dashboard")

st.set_page_config(page_title="Pressure Anomaly Dashboard", layout="wide")

logo = Image.open("assets/plmpundit_logo.jpeg")  
st.logo(logo, size="large")

# Hide top padding / empty space
st.markdown(
    """
    <style>
        /* Remove top padding/margin */
     .block-container {
        padding-top: 1rem; /* Adjust this value as needed, 0rem for minimal top space */
     }
     div[data-testid="stSidebarContent"] {
            padding-top: 0rem; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🚨 Predictive Maintenance Dashboard")


# Upload CSV
#uploaded_file = st.file_uploader("Upload pressure data (CSV)", type=["csv"])

#if uploaded_file:

# load Data
df = pd.read_csv("dataset/fox_creek_25-csv.csv", usecols=["t_stamp", "Well Pads/Fox Creek 25SE/12-63 25-2-1/Heater Treater/Gas Meter/Today Flow"])
df = df.rename(columns={
    "t_stamp": "timestamp",
    "Well Pads/Fox Creek 25SE/12-63 25-2-1/Heater Treater/Gas Meter/Today Flow" : "pressure"
})
   # Normalize column names to lowercase (strip spaces too)

# convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])

# --- Initialize session state ---
if 'df' not in st.session_state:
    # load Data
    df = pd.read_csv("dataset/fox_creek_25-csv.csv", usecols=["t_stamp", "Well Pads/Fox Creek 25SE/12-63 25-2-1/Heater Treater/Gas Meter/Today Flow"])
    df = df.rename(columns={
        "t_stamp": "timestamp",
        "Well Pads/Fox Creek 25SE/12-63 25-2-1/Heater Treater/Gas Meter/Today Flow" : "pressure"
    })
    # Normalize column names to lowercase (strip spaces too)

    # convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # --- Standardize column names ---
    df.rename(columns={'timestamp': 'Time', 'pressure': 'Pressure'}, inplace=True)
    
    # Add required columns
    df['row_id'] = df.index
    df['Error/Warning'] = ""
    df['Severity Status'] = ""
    df['Error Confirmation'] = "Error"
    df['Root Cause Remarks'] = ""
    df['SNOW Ticket'] = ""
    
    
    st.session_state.df = df.copy()
else:
    df = st.session_state.df.copy()
    # Ensure all required columns exist
    for col in ['row_id', 'Severity Status', 'Error Confirmation', 'Root Cause Remarks']:
        if col not in df.columns:
            if col == 'row_id':
                df['row_id'] = df.index
            elif col == 'Severity Status':
                df['Severity Status'] = ""
            elif col == 'Error Confirmation':
                df['Error Confirmation'] = "Error"
            else:
                df['Root Cause Remarks'] = ""

# --- Detect anomalies ---
if 'df_alert' not in st.session_state:
    df['Severity Status'] = ""
    df.loc[df['Pressure'] > 500, 'Severity Status'] = "High Pressure ⚠️"
    df.loc[df['Pressure'] < 50, 'Severity Status'] = "Low Pressure ⚠️"
    df['diff'] = df['Pressure'].diff().abs()
    df.loc[df['diff'] > 100, 'Severity Status'] = df.loc[df['diff'] > 100, 'Severity Status'].replace("", "Sudden Change ⚠️")

    # Error: Pressure is 0
    df.loc[df['Pressure'] == 0, 'Error/Warning'] = "Error"

    # Warning: Pressure deviates more than ±20% from mean
    mean_pressure = df['Pressure'].mean()
    upper_limit = mean_pressure * 1.2
    lower_limit = mean_pressure * 0.8

    df.loc[(df['Pressure'] != 0) & ((df['Pressure'] > upper_limit) | (df['Pressure'] < lower_limit)), 'Error/Warning'] = "Warning"

    st.session_state.df_alert = df.copy()
else:
    df = st.session_state.df_alert.copy()

# --- Timeframe selection ---


#logo = Image.open("assets/plmpundit_logo.jpeg")  
#st.sidebar.image(logo, width=60)
st.sidebar.subheader("Select Timeframe")

timeframe_option = st.sidebar.selectbox(
    "Timeframe for anomalies:",
    options=["1 Day", "1 Month", "6 Months", "1 Year"]
)
delta_dict = {"1 Day": 1, "1 Month": 30, "6 Months": 182, "1 Year": 365}
delta = timedelta(days=delta_dict[timeframe_option])
start_time = pd.Timestamp(datetime.now() - delta)

# --- Tabs ---
tab1, tab2 = st.tabs(["Error/Warning Logs", "Live Feed"])

with tab1:
    # --- Filter anomalies ---
    df_filtered = df[(df['Severity Status'] != "") & (df['Time'] >= start_time)].copy()

    if df_filtered.empty:
        st.warning(f"No anomalies found in the last {timeframe_option.lower()}!")
    else:
        # --- AgGrid Configuration ---
        gb = GridOptionsBuilder.from_dataframe(df_filtered)
        gb.configure_columns(["row_id", "diff"], hide=True)
        gb.configure_column(
            "Error/Warning",
            cellStyle=JsCode("""
            function(params) {
                if (params.value == 'Error') {
                    return {'color': 'white', 'backgroundColor': 'red'};
                } else if (params.value == 'Warning') {
                    return {'color': 'black', 'backgroundColor': 'yellow'};
                } else {
                    return {};
                }
            }
            """)
        )
        gb.configure_column(
            "Error Confirmation",
            editable=True,
            cellEditor="agSelectCellEditor",
            cellEditorParams={"values": ["Select","Error", "Ignore"]}
        )
        # Rootcause Remarks editable
        gb.configure_column(
            "Root Cause Remarks",
            editable=True,
            cellStyle=JsCode("""
            function(params) {
                return {'backgroundColor': '#e0fdff'};  // Light blue
            }
            """)
        )
        # Conditional formatting for Severity Status
        cell_style_jscode = JsCode("""
        function(params) {
            if (params.data['Severity Status'].includes('High Pressure')) {
                return {'color': 'white', 'backgroundColor': 'red'};
            } else if (params.data['Severity Status'].includes('Low Pressure')) {
                return {'color': 'black', 'backgroundColor': 'orange'};
            } else if (params.data['Severity Status'].includes('Sudden Change')) {
                return {'color': 'black', 'backgroundColor': 'yellow'};
            } else {
                return {};
            }
        };
        """)
        gb.configure_column("Severity Status", cellStyle=cell_style_jscode)
        gb.configure_column("SNOW Ticket", editable=False)
        gb.configure_grid_options(pagination=True, paginationPageSize=50)
        grid_options = gb.build()

        grid_response = AgGrid(
            df_filtered,
            gridOptions=grid_options,
            height=500,
            width='100%',
            update_mode='MODEL_CHANGED',
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True
        )

        # Update session_state with edited values
        updated_df = pd.DataFrame(grid_response['data'])
        updated_df.loc[updated_df['Error Confirmation'] == "Error", 'SNOW Ticket'] = "Created"
        st.session_state.df.update(updated_df)

        # Download button
        def convert_df_to_csv(df):
            return df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="Download Cleaned Data",
            data=convert_df_to_csv(st.session_state.df),
            file_name='cleaned_pressure_data.csv',
            mime='text/csv'
        )

with tab2:
    st.subheader("Live Feed Analysis")
    # Filter out ignored rows for plotting
    df_plot = st.session_state.df[st.session_state.df['Error Confirmation'] != "Ignore"].copy()
    
    if df_plot.empty:
        st.warning("No data available for time series plot!")
    else:
        # Convert to Python datetime for slider
        df_plot['Time'] = pd.to_datetime(df_plot['Time'])
        min_time = df_plot['Time'].min().to_pydatetime()
        max_time = df_plot['Time'].max().to_pydatetime()
        
        fig = px.line(df_plot, x='Time', y='Pressure', title='Accumulator')
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