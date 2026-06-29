import os
import sys
import requests
import streamlit as st
import time

# Resolve directory pathing to import auth correctly from parent folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth import check_auth
if not check_auth():
    st.stop()

st.set_page_config(page_title="AI Grandchild - Agents Portals", page_icon="🤖", layout="wide")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")

st.header("🤖 Agents Management")

# --- SECTION 1: AGENTIC WORKFLOW DIAGRAM ---
st.subheader("📊 Agentic Pipeline Architecture")
st.markdown("This flowchart illustrates how raw incoming Telegram events propagate through your safety pipeline, trigger analysis, and dispatch warning alerts.")

# Render high-quality horizontal vector flowchart
st.graphviz_chart("""
digraph G {
    rankdir=LR;
    node [shape=box, style="filled,rounded", fontname="Arial", fontsize=11, margin="0.25,0.15", color="none"];
    edge [fontname="Arial", fontsize=9, color="#7f8c8d", arrowhead=vee];

    // Node definitions & professional coloring
    Inbound      [label="📥 Telegram Inbound\\n(User/Grandpa Message)", fillcolor="#34495e", fontcolor="white"];
    Anonymizer   [label="🛡️ Anonymizer Skill\\n(PII Regex Scrubbing)", fillcolor="#2980b9", fontcolor="white"];
    Investigator [label="🔍 Investigator Agent\\n(Cynical Risk Analysis)", fillcolor="#e67e22", fontcolor="white"];
    Companion    [label="💬 Companion Agent\\n(Warm Grandchild Reply)", fillcolor="#27ae60", fontcolor="white"];
    Bridge       [label="🚨 Bridge Agent\\n(Emergency SMS Alert)", fillcolor="#c0392b", fontcolor="white"];

    // Node connections and labels
    Inbound -> Anonymizer [label="Raw Text"];
    Anonymizer -> Investigator [label="PII Scrubbed"];
    Investigator -> Companion [label="All Risks"];
    Investigator -> Bridge [label="Only on HIGH Risk"];
}
""")

st.write("---")

# --- SECTION 2: AGENT SETTINGS ---
st.subheader("⚙️ Agent Settings")

# API wrappers
def fetch_agents():
    try:
        res = requests.get(f"{BACKEND_URL}/api/agents", timeout=2)
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

agents = fetch_agents()

if not agents:
    st.info("No agents found or backend is currently offline.")
else:
    for agent in agents:
        agent_id = agent["id"]
        
        # Display each agent inside an expander component
        with st.expander(f"⚙️ **{agent['name']}** (ID: `{agent_id}`)", expanded=False):
            st.markdown("**Active System Prompt (Instruction):**")
            edited_prompt = st.text_area(
                "System Prompt Instruction:", 
                value=agent["system_prompt"], 
                height=220, 
                key=f"prompt_area_{agent_id}",
                label_visibility="collapsed"
            )
            
            edited_goal = st.text_input(
                "Agent Goal Description:", 
                value=agent["goal"], 
                key=f"goal_input_{agent_id}"
            )
            
            c_save, _ = st.columns([1.5, 4])
            if c_save.button("💾 Save Prompt Changes", key=f"save_btn_{agent_id}", use_container_width=True):
                payload = {
                    "system_prompt": edited_prompt,
                    "goal": edited_goal
                }
                res = requests.put(f"{BACKEND_URL}/api/agents/{agent_id}", json=payload)
                if res.status_code == 200:
                    st.success(f"Successfully updated {agent['name']} behavior!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Failed to commit behavioral adjustments.")