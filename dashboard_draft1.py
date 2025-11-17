# dashboard_draft1.py
import streamlit as st
import pandas as pd
import time
import plotly.express as px
import os

# -------------------------------
# Smart Plug Control (EDIT THIS)
# -------------------------------
def turn_on():
    print("Smart Plug TURNED ON (Replace with TinyTuya code)")

def turn_off():
    print("Smart Plug TURNED OFF (Replace with TinyTuya code)")
# -----------------------------------

st.set_page_config(page_title="⚡ Smart Panel", layout="wide")

# -----------------------------------
# Inject Modern Font (Poppins)
# -----------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
}

h1, h2, h3, h4, h5, h6 {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
}

button, label, .st-bx, .st-bw, .st-cz {
    font-family: 'Poppins', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------

CSV_FILE = "energy_log.csv"

# Initialize session state
if "plug_status" not in st.session_state:
    st.session_state.plug_status = False   # False = OFF, True = ON

# -----------------------------------
# Modern Header
# -----------------------------------
st.markdown("""
<h1 style='text-align:center; font-size:42px;'>⚡ Smart Panel Energy Dashboard</h1>
<p style='text-align:center; font-size:17px; color:gray;'>Real-time monitoring of voltage, current, power & energy usage</p>
""", unsafe_allow_html=True)

st.write("")

# -----------------------------------
# Sidebar Controls
# -----------------------------------
st.sidebar.markdown("### ⚙️ Settings")

refresh_interval = st.sidebar.slider("Auto-refresh interval (seconds)", 2, 30, 5)

st.sidebar.markdown("---")

# -----------------------------------
# Toggle Switch
# -----------------------------------
st.sidebar.markdown("### 🔌 Smart Plug Control")

toggle = st.sidebar.toggle("Power Switch", value=st.session_state.plug_status)

if toggle != st.session_state.plug_status:
    st.session_state.plug_status = toggle
    if toggle:
        turn_on()
    else:
        turn_off()

# Status indicator
if st.session_state.plug_status:
    st.sidebar.success("🟢 Plug Status: **ON**")
else:
    st.sidebar.error("🔴 Plug Status: **OFF**")

st.sidebar.markdown("---")

# -----------------------------------
# Load Data
# -----------------------------------
@st.cache_data(ttl=refresh_interval)
def load_data():
    if not os.path.exists(CSV_FILE):
        st.warning("No data file found yet. Waiting for data...")
        return pd.DataFrame(columns=["Timestamp", "Voltage (V)", "Current (A)", "Power (W)", "Energy (kWh)", "Status"])
    df = pd.read_csv(CSV_FILE)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

placeholder = st.empty()

# -----------------------------------
# Auto-refresh Loop
# -----------------------------------
while True:
    df = load_data()
    with placeholder.container():

        if df.empty:
            st.info("Waiting for new data…")
        else:
            latest = df.iloc[-1]

            # KPI Cards
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("🔌 Voltage", f"{latest['Voltage (V)']:.1f} V")
            col2.metric("🌡 Current", f"{latest['Current (A)']:.3f} A")
            col3.metric("⚡ Power", f"{latest['Power (W)']:.1f} W")
            col4.metric("🔋 Energy", f"{latest['Energy (kWh)']:.3f} kWh")

            st.markdown("---")

            # Power Chart
            fig_power = px.line(
                df, x="Timestamp", y="Power (W)",
                title="⚡ Power Consumption Over Time",
                labels={"Timestamp": "Time", "Power (W)": "Power (W)"}
            )
            st.plotly_chart(fig_power, use_container_width=True)

            colA, colB = st.columns(2)
            with colA:
                fig_voltage = px.line(df, x="Timestamp", y="Voltage (V)", title="🔌 Voltage Trend")
                st.plotly_chart(fig_voltage, use_container_width=True)

            with colB:
                fig_current = px.line(df, x="Timestamp", y="Current (A)", title="🌡 Current Trend")
                st.plotly_chart(fig_current, use_container_width=True)

            st.markdown("---")

            total_energy = df["Energy (kWh)"].max()
            st.subheader(f"🔋 Total Energy Used: **{total_energy:.3f} kWh**")

    time.sleep(refresh_interval)
    st.rerun()
