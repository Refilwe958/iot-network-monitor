import streamlit as st
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="IoT Network Monitor",
    page_icon="🌐",
    layout="wide",
)


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

PERFORMANCE_FILE = Path("data/network_performance.csv")
SCAN_FILE = Path("data/network_scan.csv")
EVENT_FILE = Path("logs/network_events.log")


# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("IoT Network Monitor")
st.caption("Real-time monitoring of IoT device network performance")
st.divider()
st.markdown(
    """
    This dashboard provides an overview of Downtown Student Living network performance.
    
    Designed by Olga Masupe.
    """
)

# --------------------------------------------------
# LOAD PERFORMANCE DATA
# --------------------------------------------------

if PERFORMANCE_FILE.exists():

    performance_data = pd.read_csv(PERFORMANCE_FILE)

else:

    performance_data = pd.DataFrame()


# --------------------------------------------------
# LOAD SCAN DATA
# --------------------------------------------------

if SCAN_FILE.exists():

    scan_data = pd.read_csv(SCAN_FILE)

else:

    scan_data = pd.DataFrame()


# --------------------------------------------------
# LOAD EVENT LOG
# --------------------------------------------------

events = []

if EVENT_FILE.exists():

    with EVENT_FILE.open("r", encoding="utf-8") as file:
        events = file.readlines()


# --------------------------------------------------
# CALCULATE DASHBOARD METRICS
# --------------------------------------------------

if not performance_data.empty:

    total_records = len(performance_data)

    online_devices = performance_data[
        performance_data["status"] == "ONLINE"
    ]

    device_count = online_devices["ip_address"].nunique()

    average_latency = online_devices["latency_ms"].mean()

    maximum_latency = online_devices["latency_ms"].max()

    minimum_latency = online_devices["latency_ms"].min()

    latest_timestamp = performance_data["timestamp"].iloc[-1]

else:

    total_records = 0
    device_count = 0
    average_latency = 0
    maximum_latency = 0
    minimum_latency = 0
    latest_timestamp = "No data"


# --------------------------------------------------
# TOP METRICS
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Devices Detected",
        device_count
    )

with col2:
    st.metric(
        "Average Latency",
        f"{average_latency:.2f} ms"
    )

with col3:
    st.metric(
        "Maximum Latency",
        f"{maximum_latency:.2f} ms"
    )

with col4:
    st.metric(
        "Minimum Latency",
        f"{minimum_latency:.2f} ms"
    )


st.divider()


# --------------------------------------------------
# NETWORK LATENCY GRAPH
# --------------------------------------------------

st.subheader("📈 Network Latency")

if not performance_data.empty:

    chart_data = performance_data.copy()

    chart_data["timestamp"] = pd.to_datetime(
        chart_data["timestamp"]
    )

    chart_data = chart_data.dropna(
        subset=["latency_ms"]
    )

    st.line_chart(
        chart_data,
        x="timestamp",
        y="latency_ms",
    )

else:

    st.info("No network performance data available yet.")


# --------------------------------------------------
# DEVICE STATUS
# --------------------------------------------------

st.subheader("💻 Connected Devices")

if not performance_data.empty:

    latest_timestamp = performance_data["timestamp"].iloc[-1]

    latest_data = performance_data[
        performance_data["timestamp"] == latest_timestamp
    ]

    display_data = latest_data[
        ["ip_address", "latency_ms", "status"]
    ]

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info("No device information available.")


# --------------------------------------------------
# RECENT EVENTS
# --------------------------------------------------

st.subheader("📋 Recent Network Events")

if events:

    recent_events = events[-10:]

    for event in reversed(recent_events):

        st.text(event.strip())

else:

    st.info("No network events recorded yet.")


# --------------------------------------------------
# RAW PERFORMANCE DATA
# --------------------------------------------------

with st.expander("View Performance Data"):

    if not performance_data.empty:

        st.dataframe(
            performance_data,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No performance data available.")