# frontend/pages/3_Automation.py
import os
import sys
import requests
import streamlit as st
import time
import re
from src.frontend.auth import check_auth
from src.shared.constant import BACKEND_URL

# Pathing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


if not check_auth():
    st.stop()


# Regex pattern to validate 24-hour HH:MM format (from 00:00 to 23:59)
TIME_PATTERN = re.compile(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$")

st.header("⏰ Proactive Automation Hub")
st.markdown("Set up scheduled tasks, configure inactivity triggers, and automate family safety summary reports.")

def fetch_families():
    try:
        res = requests.get(f"{BACKEND_URL}/api/families")
        return res.json() if res.status_code == 200 else []
    except Exception: return []

def fetch_members():
    try:
        res = requests.get(f"{BACKEND_URL}/api/members")
        return res.json() if res.status_code == 200 else []
    except Exception: return []

def fetch_jobs():
    try:
        res = requests.get(f"{BACKEND_URL}/api/automation")
        return res.json() if res.status_code == 200 else []
    except Exception: return []

families = fetch_families()
members = fetch_members()
jobs = fetch_jobs()

# ADJUSTED: Widened the columns to [1.3, 1.0] to prevent the shrinking/narrow look
col1, col2 = st.columns([1.3, 1.0])

# --- Column 1: Display Active Rules ---
with col1:
    st.subheader("📋 Active Automation Rules")
    
    st.markdown("""
        <style>
        .small-header { font-size:12.5px; font-weight:bold; color:#94a3b8; text-transform:uppercase; }
        .small-text { font-size:12.5px; color:#cbd5e1; }
        </style>
    """, unsafe_allow_html=True)

    m_header = st.columns([3, 2, 2, 1])
    m_header[0].markdown("<div class='small-header'>Rule Name</div>", unsafe_allow_html=True)
    m_header[1].markdown("<div class='small-header'>Trigger Event</div>", unsafe_allow_html=True)
    m_header[2].markdown("<div class='small-header'>Last Triggered</div>", unsafe_allow_html=True)
    m_header[3].markdown("<div class='small-header'>Action</div>", unsafe_allow_html=True)
    st.write("---")

    if jobs:
        for job in jobs:
            m_row = st.columns([3, 2, 2, 1])
            m_row[0].markdown(f"<div class='small-text'>{job['name']}</div>", unsafe_allow_html=True)
            
            if job['job_type'] == "inactivity_check":
                trigger_desc = f"Inactivity > {job['interval_minutes']}m {'(Alert Fam)' if job.get('alert_family') else ''}"
            elif job['job_type'] == "scheduled_prompt":
                trigger_desc = f"Daily at {job['cron_time']}"
            else:
                trigger_desc = f"Digest: {job['cron_day_of_week']} @ {job['cron_time']}"
                
            m_row[1].markdown(f"<div class='small-text'>{trigger_desc}</div>", unsafe_allow_html=True)
            
            last_run = job.get('last_run')
            m_row[2].markdown(f"<div class='small-text'>{last_run[:16] if last_run else 'Never'}</div>", unsafe_allow_html=True)
            
            if m_row[3].button("🗑️ Delete", key=f"del_job_{job['id']}"):
                requests.delete(f"{BACKEND_URL}/api/automation/{job['id']}")
                st.rerun()
    else:
        st.info("No automation rules configured. Configure a new rule using the right-side form.")

# --- Column 2: Add New Rule (Form) ---
with col2:
    st.subheader("➕ Add New Rule")
    if not families or not members:
        st.warning("Ensure at least one Family and Member is configured first.")
    else:
        rule_type = st.selectbox(
            "Select Scenario Type:",
            ["Proactive Check-in", "Family Security Summary"]
        )
        
        target_family = st.selectbox("Assign to Family:", options=families, format_func=lambda x: x["name"])
        
        # --- SCENARIO 1 FORM ---
        if "Proactive" in rule_type:
            seniors_in_family = [m for m in members if m["family_id"] == target_family["id"] and m["member_type"] == "senior"]
            if not seniors_in_family:
                st.error("No Seniors registered to this Family directory.")
            else:
                target_senior = st.selectbox("Select Target Senior:", options=seniors_in_family, format_func=lambda x: f"{x['name']} ({x['chat_id']})")
                
                s1_option = st.radio("Choose Trigger Type:", ["Inactivity Threshold (Minutes)", "Scheduled Time of Day"])
                
                if "Inactivity" in s1_option:
                    minutes = st.number_input("Inactivity Limit (Minutes):", min_value=1, max_value=1440, value=60)
                    alert_fam = st.checkbox("Alert family if senior is inactive")
                    
                    if st.button("Activate Rule", use_container_width=True):
                        payload = {
                            "name": f"Check-in {target_senior['name']} after {minutes}m",
                            "job_type": "inactivity_check",
                            "family_id": target_family["id"],
                            "target_chat_id": target_senior["chat_id"],
                            "interval_minutes": int(minutes),
                            "alert_family": alert_fam
                        }
                        res = requests.post(f"{BACKEND_URL}/api/automation", json=payload)
                        if res.status_code == 200:
                            st.success("Inactivity rule activated.")
                            time.sleep(1)
                            st.rerun()
                else:
                    # IMPROVED: Replaced time_input dropdown with a clean text_input + regex validation
                    cron_time_str = st.text_input("Scheduled Time (24h format HH:MM):", value="18:00", placeholder="e.g. 18:00")
                    time_valid = bool(TIME_PATTERN.match(cron_time_str.strip()))
                    
                    if not time_valid:
                        st.error("Please enter a valid 24h time format (e.g. 09:30 or 18:00)")
                    
                    # Submit button is disabled if the entered time format is invalid
                    if st.button("Activate Rule", disabled=not time_valid, use_container_width=True):
                        formatted_time = cron_time_str.strip()
                        payload = {
                            "name": f"Daily Prompt {target_senior['name']} @ {formatted_time}",
                            "job_type": "scheduled_prompt",
                            "family_id": target_family["id"],
                            "target_chat_id": target_senior["chat_id"],
                            "cron_time": formatted_time
                        }
                        res = requests.post(f"{BACKEND_URL}/api/automation", json=payload)
                        if res.status_code == 200:
                            st.success(f"Scheduled prompt activated at {formatted_time}")
                            time.sleep(1)
                            st.rerun()
                        
        # --- SCENARIO 3 FORM ---
        else:
            # Family Summary Digest
            cron_day = st.selectbox(
                "Select Day of Week:", 
                ["Every Day", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            )
            
            # IMPROVED: Replaced time_input dropdown with a clean text_input + regex validation
            cron_time_str = st.text_input("Select Report Time (24h format HH:MM):", value="18:00", placeholder="e.g. 18:00")
            time_valid = bool(TIME_PATTERN.match(cron_time_str.strip()))
            
            if not time_valid:
                st.error("Please enter a valid 24h time format (e.g. 09:30 or 18:00)")
            
            # Submit button is disabled if the entered time format is invalid
            if st.button("Activate Summary Rule", disabled=not time_valid, use_container_width=True):
                formatted_time = cron_time_str.strip()
                payload = {
                    "name": f"Digest: {target_family['name']} ({cron_day} @ {formatted_time})",
                    "job_type": "family_digest",
                    "family_id": target_family["id"],
                    "target_chat_id": "family",
                    "cron_time": formatted_time,
                    "cron_day_of_week": cron_day
                }
                res = requests.post(f"{BACKEND_URL}/api/automation", json=payload)
                if res.status_code == 200:
                    st.success("Summary digest activated.")
                    time.sleep(1)
                    st.rerun()