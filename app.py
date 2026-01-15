import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import sys
import os

# Ensure src is in pythonpath
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src import config
from src import sheets
from src import etl

st.set_page_config(page_title="Table Cleaning ETL", page_icon="📊", layout="wide")

# --- Custom CSS for Styling Buttons ---
st.markdown("""
<style>
/* 
   Robust Targeting using Invisible Markers 
   Structure: div(contains marker) + div(contains button)
*/



/* 
   Hack to hide the markdown marker containers so they don't take up space/cause layout shifts.
   We target the 'stElementContainer' div that contains our unique marker span.
   
   Using 'display: none' breaks the sibling selector in some cases or fails to target the wrapper.
   Solution: Force the container to be absolutely positioned and tiny.
*/
div[data-testid="stElementContainer"]:has(span#run-marker),
div[data-testid="stElementContainer"]:has(span#delete-marker),
div[data-testid="stElementContainer"]:has(span#nav-active-marker) {
    position: absolute !important;
    width: 0px !important;
    height: 0px !important;
    min-height: 0px !important;
    opacity: 0 !important;
    margin: 0px !important;
    padding: 0px !important;
    pointer-events: none !important;
}

/* 
   Sibling Selectors:
   Since the marker container is now absolutely positioned (out of flow), it is still in the DOM.
   The sibling selector '+' finds the next element in the DOM tree.
*/

/* Green Run Button */
div:has(span#run-marker) + div button {
    background-color: #28a745 !important;
    color: white !important;
    border-color: #28a745 !important;
}
div:has(span#run-marker) + div button:hover {
    background-color: #218838 !important;
    border-color: #1e7e34 !important;
}

/* Red Delete Button */
div:has(span#delete-marker) + div button {
    background-color: #dc3545 !important;
    color: white !important;
    border-color: #dc3545 !important;
}
div:has(span#delete-marker) + div button:hover {
    background-color: #c82333 !important;
    border-color: #bd2130 !important;
}

/* Sidebar Nav Selected State */
div:has(span#nav-active-marker) + div button {
    background-color: #0d6efd !important;
    color: white !important;
    border-color: #0d6efd !important;
}
</style>
""", unsafe_allow_html=True)

# Application Title
st.title("📊 Table Cleaning ETL")

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")

# Init page state
if "page" not in st.session_state:
    st.session_state["page"] = "run_pipeline"

def nav_to(page):
    st.session_state["page"] = page

# Run Pipeline Nav Button
if st.session_state["page"] == "run_pipeline":
    st.sidebar.markdown('<span id="nav-active-marker"></span>', unsafe_allow_html=True)
if st.sidebar.button("🚀 Run Pipeline", use_container_width=True):
    nav_to("run_pipeline")
    st.rerun()

# Manage Pipeline Nav Button
if st.session_state["page"] == "manage_sheets":
    st.sidebar.markdown('<span id="nav-active-marker"></span>', unsafe_allow_html=True)
if st.sidebar.button("🗑️ Manage Target Sheet", use_container_width=True):
    nav_to("manage_sheets")
    st.rerun()

# --- Page: Run Pipeline ---
if st.session_state["page"] == "run_pipeline":
    st.subheader("🚀 Run Pipeline")
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 📅 Date Range")
        with st.container(border=True):
            # Defaults: Use config if valid, else default to Last 7 Days relative to today
            today = date.today()
            
            # Parsing from config
            conf_start = config.START_DATE.date() if config.START_DATE else None
            conf_end = config.END_DATE.date() if config.END_DATE else None
            
            if conf_start and conf_end:
                 default_start = conf_start
                 default_end = conf_end
            elif conf_end:
                 default_end = conf_end
                 default_start = conf_end - timedelta(days=7)
            elif conf_start:
                 default_start = conf_start
                 default_end = conf_start + timedelta(days=7)
            else:
                default_end = today
                default_start = today - timedelta(days=7)
            
            start_date = st.date_input("Start Date", value=default_start, format="DD/MM/YYYY")
            end_date = st.date_input("End Date", value=default_end, format="DD/MM/YYYY")
    
    with col2:
        st.markdown("### 🚀 Actions")
        with st.container(border=True):
            # Inject Marker for Green Button
            st.markdown('<span id="run-marker"></span>', unsafe_allow_html=True)
            run_btn = st.button("Run ETL Pipeline", type="primary", use_container_width=True)

    if run_btn:
        # Use 'with' to ensure explicit state management
        with st.status("Connecting to Google Sheets...", expanded=True) as status:
            try:
                # 1. Connect
                client = sheets.connect()
                if not client:
                    status.update(label="❌ Connection Failed", state="error")
                    st.error("Failed to connect to Google Sheets. Check logs/credentials.")
                    st.stop()
                    
                # 2. Run ETL
                st.write("Fetching and processing data...")
                # Convert date objects to datetime for the pipeline
                s_dt = datetime.combine(start_date, datetime.min.time())
                e_dt = datetime.combine(end_date, datetime.min.time())
                
                df = etl.run_etl_pipeline(client, start_date=s_dt, end_date=e_dt)
                
                if df.empty:
                    status.update(label="⚠️ No Data Found", state="complete", expanded=False)
                    st.warning("No data found for the selected range.")
                else:
                    st.write(f"Processed {len(df)} rows!")
                    
                    # 3. Write
                    st.write("Writing to Target Sheet...")
                    tab_name = sheets.write_latest_week(client, df, target_sheet_id=config.TARGET_SHEET_ID)
                    
                    status.update(label=f"✅ Done! Written to {tab_name}", state="complete", expanded=False)
                    
                    st.balloons()
                    st.success(f"✅ Successfully written to **{tab_name}**")
    
                    # Preview
                    st.subheader("Preview Data")
                    st.dataframe(df.head(50), use_container_width=True)
                    
            except Exception as e:
                status.update(label="❌ Error Occurred", state="error")
                st.error(f"An error occurred: {e}")
                st.exception(e)

# --- Page: Manage Target Sheet ---
elif st.session_state["page"] == "manage_sheets":
    
    st.subheader("🗑️ Manage Target Sheet")
    st.markdown("Use this tool to clean up old run tabs from your Google Sheet.")
    
    from src.utils import parse_tab_datetime
    
    # Init vars
    if "all_tabs" not in st.session_state:
        st.session_state["all_tabs"] = []
    if "selected_tabs" not in st.session_state:
        st.session_state["selected_tabs"] = []
    if "auto_fetched" not in st.session_state:
        st.session_state["auto_fetched"] = False
        
    def fetch_tabs():
        try:
            client = sheets.connect()
            if client:
                st.session_state["all_tabs"] = sheets.get_all_tabs(client, target_sheet_id=config.TARGET_SHEET_ID)
                st.session_state["auto_fetched"] = True
        except Exception as e:
            st.error(f"Failed to fetch tabs: {e}")

    # Auto-fetch once on entry to this page
    if not st.session_state["auto_fetched"]:
         with st.spinner("Auto-fetching tabs..."):
            fetch_tabs()

    if st.button("🔄 Refresh List"):
        fetch_tabs()

    all_tabs = st.session_state["all_tabs"]
    
    if all_tabs:
        st.markdown(f"**Found {len(all_tabs)} tabs**")
        
        st.divider()
        st.subheader("Filter & Select")
        
        f_col1, f_col2 = st.columns([1, 2])
        with f_col1:
            filter_mode = st.radio("Filter Mode", ["Custom Select", "Older Than (Before)", "Date Range", "Older Than 60 Days"], horizontal=False)
            
        with f_col2:
            to_add = []
            if filter_mode == "Custom Select":
                st.info("Manually select tabs from the dropdown below. You can also 'Select All'.")
                if st.button("➕ Select All"):
                    st.session_state["selected_tabs"] = all_tabs
                    st.rerun()

            elif filter_mode == "Older Than (Before)":
                date_thresh = st.date_input("Select tabs created BEFORE:", value=None)
                if st.button("➕ Add Matching Tabs"):
                    if date_thresh:
                        count = 0
                        for t in all_tabs:
                            dt = parse_tab_datetime(t)
                            if dt and dt.date() < date_thresh:
                                to_add.append(t)
                                count += 1
                        if count > 0:
                            st.toast(f"Added {count} tabs!")
            
            elif filter_mode == "Date Range":
                d_start = st.date_input("Start Date", value=None)
                d_end = st.date_input("End Date", value=None)
                if st.button("➕ Add Tabs in Range"):
                    if d_start and d_end:
                        count = 0
                        for t in all_tabs:
                            dt = parse_tab_datetime(t)
                            if dt and d_start <= dt.date() <= d_end:
                                to_add.append(t)
                                count += 1
                        if count > 0:
                            st.toast(f"Added {count} tabs!")

            elif filter_mode == "Older Than 60 Days":
                sixty_days_ago = date.today() - timedelta(days=60)
                st.write(f"This will select all tabs created strictly before **{sixty_days_ago}**.")
                if st.button("➕ Select Matchings"):
                    count = 0
                    for t in all_tabs:
                        dt = parse_tab_datetime(t)
                        if dt and dt.date() < sixty_days_ago:
                            to_add.append(t)
                            count += 1
                    if count > 0:
                        st.toast(f"Added {count} tabs!")
                    else:
                        st.toast("No tabs older than 60 days found.", icon="ℹ️")

            if to_add:
                current = set(st.session_state["selected_tabs"])
                current.update(to_add)
                st.session_state["selected_tabs"] = list(current)
                st.rerun()

        # Selection Actions Layout
        st.write("### Tabs to Delete:")
        
        selected = st.multiselect(
            "Tabs to Delete:", 
            options=all_tabs,
            key="selected_tabs",
            label_visibility="collapsed"
        )
        
        if selected:
            st.warning(f"You are about to delete {len(selected)} tabs.")
            
            # Callback defined explicitly
            def on_confirm_delete(tid):
                to_delete = st.session_state.get("selected_tabs", [])
                if not to_delete:
                    return
                try:
                    conn = sheets.connect()
                    if conn:
                        deleted, failed = sheets.delete_tabs(conn, to_delete, target_sheet_id=tid)
                        if deleted:
                            st.toast(f"✅ Deleted {len(deleted)} tabs!", icon="🗑️")
                        if failed:
                            st.toast(f"⚠️ Failed to delete: {failed}", icon="❌")
                        
                        st.session_state["all_tabs"] = sheets.get_all_tabs(conn, target_sheet_id=tid)
                        st.session_state["selected_tabs"] = []
                except Exception as ex:
                    st.toast(f"Error: {ex}", icon="🔥")

            # Inject Marker for Red Button
            st.markdown('<span id="delete-marker"></span>', unsafe_allow_html=True)
            st.button("🗑️ Confirm Delete", on_click=on_confirm_delete, args=(config.TARGET_SHEET_ID,), type="primary")
