import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from network_monitor.availability import load_availability_history

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    def st_autorefresh(*args, **kwargs):
        """Fallback no-op when streamlit-autorefresh is unavailable."""
        return None


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="IoT Network Monitor",
    page_icon="🌐",
    layout="wide",
)

st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1 {
        margin-bottom: 0.2rem;
    }

    [data-testid="stMetric"] {
        border: 1px solid rgba(128, 128, 128, 0.25);
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Automatically refresh dashboard every 60 seconds
st_autorefresh(
    interval=60000,
    key="network_monitor_refresh"
)

st.sidebar.title("Network Monitor")

st.sidebar.markdown("### Monitoring")
st.sidebar.write("Real-time LAN monitoring")

st.sidebar.markdown("### Refresh Rate")
st.sidebar.write("Every 60 seconds")

st.sidebar.markdown("### Data Sources")
st.sidebar.write("• Network scan")
st.sidebar.write("• Performance data")
st.sidebar.write("• Network events")

st.sidebar.markdown("---")
st.sidebar.caption("IoT Network Monitor")
st.sidebar.caption("Refilwe Olga Masupe")

# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

PERFORMANCE_FILE = Path("data/network_performance.csv")
SCAN_FILE = Path("data/network_scan.csv")
EVENT_FILE = Path("logs/network_events.log")
ESP32_FILE = Path("data/esp32_telemetry.csv")


# --------------------------------------------------
# PAGE TITLE
# --------------------------------------------------

st.title("IoT Network Monitor")
st.caption("Real-time Local Network Monitoring Dashboard")
st.divider()
st.markdown(
    """
    This dashboard provides an overview of Downtown Student Living network performance.
    
    Real-time LAN monitoring and network performance dashboard
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
# LOAD ESP32 TELEMETRY
# --------------------------------------------------

if ESP32_FILE.exists():
    esp32_data = pd.read_csv(ESP32_FILE)

    if not esp32_data.empty and "timestamp" in esp32_data.columns:
        esp32_data["timestamp"] = pd.to_datetime(
            esp32_data["timestamp"], errors="coerce"
        )
        esp32_data = esp32_data.dropna(subset=["timestamp"])
        esp32_data = esp32_data.sort_values("timestamp")
else:
    esp32_data = pd.DataFrame()


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
# MONITOR STATUS
# --------------------------------------------------

monitor_status = "OFFLINE"

if not performance_data.empty:

    latest_timestamp = pd.to_datetime(
        performance_data["timestamp"].iloc[-1]
    )

    current_time = datetime.now()

    seconds_since_update = (
        current_time - latest_timestamp
    ).total_seconds()

    if seconds_since_update <= 60:
        monitor_status = "ACTIVE"

# --------------------------------------------------
# NETWORK HEALTH
# --------------------------------------------------

st.subheader("Network Health")

if not performance_data.empty:

    online_records = performance_data[
        performance_data["status"] == "ONLINE"
    ]

    total_records = len(performance_data)
    online_records_count = len(online_records)

    if total_records > 0:
        packet_loss = (
            (total_records - online_records_count)
            / total_records
        ) * 100
    else:
        packet_loss = 0

    if average_latency < 20:
        performance_status = "EXCELLENT"
    elif average_latency < 50:
        performance_status = "GOOD"
    elif average_latency < 100:
        performance_status = "FAIR"
    else:
        performance_status = "POOR"

    health_col1, health_col2 = st.columns(2)

    with health_col1:
        st.metric(
            "Packet Loss",
            f"{packet_loss:.2f}%"
        )

    with health_col2:
        st.metric(
            "Performance",
            performance_status
        )

else:

    st.info("No network health data available.")

if not performance_data.empty:

    latest_scan = performance_data["timestamp"].iloc[-1]

    st.caption(
        f"Last network scan: {latest_scan}"
    )    

st.divider()

# --------------------------------------------------
# TOP METRICS
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)
with col1:
    if monitor_status == "ACTIVE":
        st.success("ACTIVE")
    else:
        st.error("OFFLINE")

    st.caption("Monitor Status")

with col2:
    st.metric(
        "Devices Detected",
        device_count
    )

with col3:
    st.metric(
        "Average Latency",
        f"{average_latency:.2f} ms"
    )
with col4:
    st.metric(
        "Total Records",
        total_records
    )

st.subheader("Network Health")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Packet Loss",
        f"{packet_loss}%"
    )

with col2:
    st.metric(
        "Performance",
        performance_status
    )

with col3:
    st.metric(
        "Last Scan",
        latest_scan
    )
st.divider()

# --------------------------------------------------
# NETWORK LATENCY GRAPH
# --------------------------------------------------

st.subheader("Network Latency Over Time")

if not performance_data.empty:

    chart_data = performance_data.copy()

    chart_data["timestamp"] = pd.to_datetime(
        chart_data["timestamp"]
    )

    chart_data = chart_data.dropna(
        subset=["latency_ms"]
    )

    chart_data = chart_data[
        ["timestamp", "ip_address", "latency_ms"]
    ]

    chart_data = chart_data.pivot_table(
        index="timestamp",
        columns="ip_address",
        values="latency_ms",
        aggfunc="mean",
    )

    st.line_chart(
        chart_data,
        y_label="Latency (ms)",
        x_label="Time",
    )

else:

    st.info("No network performance data available yet.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Device Latency")
    if not performance_data.empty:

        devices = sorted(
            performance_data["ip_address"].dropna().unique()
        )

        selected_device = st.selectbox(
            "Select device to inspect",
            ["All devices"] + devices,
        )

    if selected_device != "All devices":

        device_data = performance_data[
            performance_data["ip_address"] == selected_device
        ].copy()

        device_data["timestamp"] = pd.to_datetime(
            device_data["timestamp"]
        )

        device_data = device_data.dropna(
            subset=["latency_ms"]
        )

        st.line_chart(
            device_data,
            x="timestamp",
            y="latency_ms",
            y_label="Latency (ms)",
            x_label="Time",
        )    

with col2:
    st.subheader("Connected Devices")
    if not performance_data.empty:

        latest_timestamp = performance_data["timestamp"].iloc[-1]

        latest_data = performance_data[
            performance_data["timestamp"] == latest_timestamp
        ].copy()

        latest_data["latency_ms"] = latest_data["latency_ms"].round(2)

        latest_data = latest_data[
            ["ip_address", "latency_ms", "status"]
        ]

        latest_data = latest_data.rename(
            columns={
                "ip_address": "IP Address",
                "latency_ms": "Latency (ms)",
                "status": "Status",
            }
        )

        st.dataframe(
            latest_data,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No device information available.")    


# --------------------------------------------------
# NETWORK ALERTS
# --------------------------------------------------

st.subheader("Network Alerts")

if events:

    recent_events = [event.strip() for event in events[-20:]]

    alert_events = []

    for event in recent_events:

        if (
            "WARNING" in event
            or "OFFLINE" in event
            or "NEW DEVICE" in event
        ):
            alert_events.append(event)

    if alert_events:

        for alert in reversed(alert_events[-10:]):

            if "OFFLINE" in alert:
                st.error(f"{alert}")

            elif "WARNING" in alert:
                st.warning(f"{alert}")

            elif "NEW DEVICE" in alert:
                st.info(f"{alert}")

    else:

        st.success("No network alerts detected.")

else:

    st.success("No network alerts detected.")

# --------------------------------------------------
# RECENT NETWORK EVENTS
# --------------------------------------------------

st.subheader("Recent Network Events")

if events:

    recent_events = events[-15:]

    event_data = []

    for event in recent_events:

        event = event.strip()

        if not event:
            continue

        if "] " in event:

            timestamp, message = event.split("] ", 1)

            timestamp = timestamp.replace("[", "")

        else:

            timestamp = ""
            message = event

        event_data.append({
            "Timestamp": timestamp,
            "Event": message,
        })

    event_df = pd.DataFrame(event_data)

    st.dataframe(
        event_df,
        use_container_width=True,
        hide_index=True,
    )

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

st.divider()

st.caption(
    "IoT Network Monitor • Python • Streamlit • Network Performance Monitoring"
)        


# --------------------------------------------------
# ESP32 IOT TELEMETRY
# --------------------------------------------------

st.divider()
st.header("ESP32 IoT Device Telemetry")
st.caption("Live telemetry received through MQTT")

if not esp32_data.empty:
    latest_esp32 = esp32_data.iloc[-1]

    device_status = str(latest_esp32.get("status", "Unknown"))
    device_ip = str(latest_esp32.get("ip", "Unknown"))

    try:
        latest_rssi = float(latest_esp32["rssi"])
    except (ValueError, TypeError, KeyError):
        latest_rssi = None

    try:
        uptime_seconds = float(latest_esp32["uptime_seconds"])
    except (ValueError, TypeError, KeyError):
        uptime_seconds = None

    # Check when telemetry was last received
    last_message_time = latest_esp32["timestamp"]
    seconds_since_message = (
        datetime.now().astimezone()
        - last_message_time.to_pydatetime()
    ).total_seconds()

    device_online = (
        device_status.lower() == "online"
        and 0 <= seconds_since_message <= 30
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "ESP32 Status",
            "ONLINE" if device_online else "STALE / OFFLINE"
        )

    with col2:
        st.metric("ESP32 IP Address", device_ip)

    with col3:
        st.metric(
            "Wi-Fi Signal (RSSI)",
            f"{latest_rssi:.0f} dBm"
            if latest_rssi is not None else "N/A"
        )

    with col4:
        if uptime_seconds is not None:
            st.metric(
                "Device Uptime",
                f"{uptime_seconds / 3600:.2f} hours"
            )
        else:
            st.metric("Device Uptime", "N/A")

    st.caption(
        f"Last message: {last_message_time} | "
        f"Total telemetry records: {len(esp32_data)}"
    )

    # RSSI history
    st.subheader("ESP32 Wi-Fi Signal Strength Over Time")

    if latest_rssi is not None:
        signal_data = esp32_data.copy()
        signal_data["rssi"] = pd.to_numeric(
            signal_data["rssi"], errors="coerce"
        )
        signal_data = signal_data.dropna(subset=["rssi"])

        if not signal_data.empty:
            signal_chart = signal_data.set_index("timestamp")[["rssi"]]
            st.line_chart(
                signal_chart,
                y_label="Signal strength (dBm)",
                x_label="Time"
            )

    with st.expander("View ESP32 Telemetry Records"):
        st.dataframe(
            esp32_data.tail(100).sort_values(
                "timestamp", ascending=False
            ),
            use_container_width=True,
            hide_index=True
        )

else:
    st.info(
        "No ESP32 telemetry available yet. "
        "Start mqtt_receiver.py and check the MQTT connection."
    )


# --------------------------------------------------
# DEVICE AVAILABILITY HISTORY
# --------------------------------------------------

st.divider()
st.header("Device Availability History")

st.caption(
    "Recorded estimates calculated from device status events. "
    "Durations include only intervals between consecutive events; "
    "time after the last event is not assumed."
)

availability_history = load_availability_history()

if availability_history:
    availability_df = pd.DataFrame(availability_history)

    availability_df["last_event"] = pd.to_datetime(
        availability_df["last_event"]
    ).dt.strftime("%Y-%m-%d %H:%M:%S")

    display_columns = [
        "ip_address",
        "current_status",
        "online_hours",
        "outage_hours",
        "recorded_outages",
        "last_event",
    ]

    st.dataframe(
        availability_df[display_columns].rename(
            columns={
                "ip_address": "IP Address",
                "current_status": "Last Recorded Status",
                "online_hours": "Recorded Online Hours",
                "outage_hours": "Recorded Outage Hours",
                "recorded_outages": "Recorded Outages",
                "last_event": "Last Status Event",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Last recorded status is not a live status check. "
        "Availability history depends on the events captured "
        "while monitoring was running."
    )

else:
    st.info(
        "No device availability events found yet. "
        "Run the network monitor to record device status changes."
    )
