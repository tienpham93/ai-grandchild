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

st.set_page_config(page_title="AI Grandchild - Account Management", page_icon="👥", layout="wide")

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")

# --- Custom CSS for Compact Tables and Smaller Text ---
st.markdown("""
<style>
.small-text {
    font-size: 12.5px !important;
    color: #cbd5e1;
}
.small-header {
    font-size: 12.5px !important;
    font-weight: bold;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
/* Reduce spacing and font sizes of standard Streamlit buttons */
div[data-testid="column"] button {
    padding: 2px 10px !important;
    font-size: 12px !important;
    min-height: 28px !important;
}
</style>
""", unsafe_allow_html=True)

st.header("👥 Account Management")
st.write("Examine, authorize, and structure family directories and members securely.")

# --- Cache and State Initializations ---
if "selected_family_id" not in st.session_state:
    st.session_state.selected_family_id = None
if "selected_family_name" not in st.session_state:
    st.session_state.selected_family_name = ""

# API wrappers
def fetch_families():
    try:
        res = requests.get(f"{BACKEND_URL}/api/families", timeout=2)
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

def fetch_members():
    try:
        res = requests.get(f"{BACKEND_URL}/api/members")
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

# Refresh data
families = fetch_families()
members = fetch_members()

# Layout columns
col_left, col_right = st.columns([1, 2])

# --- PANEL A: FAMILIES MANAGEMENT ---
with col_left:
    st.subheader("🏠 Registered Families")
    
    # Input to register new family
    new_fam_name = st.text_input("New Family Name:", placeholder="e.g. Gia đình Ngoại Bảy", key="new_fam_input")
    if st.button("➕ Register Family", use_container_width=True):
        if new_fam_name:
            res = requests.post(f"{BACKEND_URL}/api/families", json={"name": new_fam_name})
            if res.status_code == 200:
                st.success(f"Successfully created family '{new_fam_name}'")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Error creating family directory.")

    st.write("---")

    # Pagination for Families (Max 20 rows)
    fam_limit = 20
    num_families = len(families)
    num_pages = max(1, (num_families + fam_limit - 1) // fam_limit)
    
    if num_families > fam_limit:
        fam_page = st.number_input("Family Page:", min_value=1, max_value=num_pages, step=1, key="fam_page_nav")
    else:
        fam_page = 1
        
    start_idx = (fam_page - 1) * fam_limit
    end_idx = min(start_idx + fam_limit, num_families)
    page_families = families[start_idx:end_idx]

    # Custom Confirmation Dialog for deleting family
    if "confirm_delete_fam_id" in st.session_state:
        st.warning(f"⚠️ **Are you sure you want to delete this family?** All associated members will also be deleted.")
        c_del, c_can = st.columns(2)
        if c_del.button("🗑️ Yes, Delete Entire Family", use_container_width=True):
            requests.delete(f"{BACKEND_URL}/api/families/{st.session_state.confirm_delete_fam_id}")
            if st.session_state.selected_family_id == st.session_state.confirm_delete_fam_id:
                st.session_state.selected_family_id = None
            del st.session_state.confirm_delete_fam_id
            st.rerun()
        if c_can.button("❌ Cancel", use_container_width=True):
            del st.session_state.confirm_delete_fam_id
            st.rerun()

    # Render Family grid headers with smaller font size
    grid_header = st.columns([1, 3, 2, 2])
    grid_header[0].markdown("<div class='small-header'>ID</div>", unsafe_allow_html=True)
    grid_header[1].markdown("<div class='small-header'>Family Directory Name</div>", unsafe_allow_html=True)
    grid_header[2].markdown("<div class='small-header'>View</div>", unsafe_allow_html=True)
    grid_header[3].markdown("<div class='small-header'>Remove</div>", unsafe_allow_html=True)
    st.write("---")

    # Render Family rows with smaller font size
    if page_families:
        for fam in page_families:
            grid_row = st.columns([1, 3, 2, 2])
            grid_row[0].markdown(f"<div class='small-text'>{fam['id']}</div>", unsafe_allow_html=True)
            grid_row[1].markdown(f"<div class='small-text'>{fam['name']}</div>", unsafe_allow_html=True)
            
            if grid_row[2].button("🔍 View", key=f"v_fam_{fam['id']}"):
                st.session_state.selected_family_id = fam["id"]
                st.session_state.selected_family_name = fam["name"]
                st.rerun()
                
            if grid_row[3].button("🗑️ Delete", key=f"d_fam_{fam['id']}"):
                st.session_state.confirm_delete_fam_id = fam["id"]
                st.rerun()
    else:
        st.info("No registered families found.")

# --- PANEL B: MEMBERS MANAGEMENT (ACTIVE FAMILIES SUB-GRID WITH BORDER) ---
with col_right:
    if not st.session_state.selected_family_id:
        st.subheader("👥 Family Member Management")
        st.info("👈 Please click the '🔍 View' button on any Family Directory row to manage its authorized member list.")
    else:
        # Wrap the entire Member Directory inside a clean border container
        with st.container(border=True):
            st.subheader(f"👥 Member Directory: {st.session_state.selected_family_name}")

            family_id = st.session_state.selected_family_id
            fam_members = [m for m in members if m["family_id"] == family_id]

            # Modals/Dialog states
            if "show_add_member_form" not in st.session_state:
                st.session_state.show_add_member_form = False
            if "edit_member_target" not in st.session_state:
                st.session_state.edit_member_target = None

            # Action buttons aligned left using small columns
            c_act1, _ = st.columns([1.5, 4])
            if c_act1.button("➕ Add Member", use_container_width=True):
                st.session_state.show_add_member_form = True
                st.session_state.edit_member_target = None

            # MODAL WINDOW 1: Add Member Form
            if st.session_state.show_add_member_form:
                with st.container(border=True):
                    st.markdown("### Create New Family Member")
                    m_chat_id = st.text_input("Telegram Chat ID (Required):")
                    m_name = st.text_input("Display Name (Required):")
                    m_type = st.selectbox("Role Classification:", ["senior", "non_senior"])
                    m_role = st.selectbox("Role Identity:", ["grandpa", "grandma", "mom", "dad", "son", "daughter"])
                    
                    m_bank = ""
                    if m_type == "senior":
                        m_bank = st.text_input("Link Bank Account (Optional):")
                    
                    form_valid = bool(m_chat_id.strip() and m_name.strip() and m_type and m_role)
                    
                    c_create, c_cancel = st.columns(2)
                    if c_create.button("✔️ Create", disabled=not form_valid, use_container_width=True):
                        payload = {
                            "chat_id": m_chat_id.strip(),
                            "name": m_name.strip(),
                            "family_id": family_id,
                            "member_type": m_type,
                            "member_role": m_role,
                            "bank_account": m_bank.strip() if m_bank.strip() else None
                        }
                        res = requests.post(f"{BACKEND_URL}/api/members", json=payload)
                        if res.status_code == 200:
                            st.success(f"Authorized {m_name} successfully.")
                            st.session_state.show_add_member_form = False
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Error creating member profile.")
                    
                    if c_cancel.button("❌ Cancel", use_container_width=True):
                        st.session_state.show_add_member_form = False
                        st.rerun()

            # MODAL WINDOW 2: Edit Member Form
            if st.session_state.edit_member_target:
                curr_mem = st.session_state.edit_member_target
                with st.container(border=True):
                    st.markdown(f"### Edit Member Profile: {curr_mem['name']}")
                    edit_type = st.selectbox("Role Classification:", ["senior", "non_senior"], index=0 if curr_mem["member_type"] == "senior" else 1)
                    roles_list = ["grandpa", "grandma", "mom", "dad", "son", "daughter"]
                    try:
                        r_idx = roles_list.index(curr_mem["member_role"])
                    except ValueError:
                        r_idx = 0
                    edit_role = st.selectbox("Role Identity:", roles_list, index=r_idx)
                    edit_name = st.text_input("Display Name:", value=curr_mem["name"])
                    edit_bank = st.text_input("Link Bank Account Number:", value=curr_mem.get("bank_account", "") or "")

                    c_save, c_cancel_ed = st.columns(2)
                    if c_save.button("💾 Save Changes", use_container_width=True):
                        payload = {
                            "member_type": edit_type,
                            "member_role": edit_role,
                            "name": edit_name,
                            "bank_account": edit_bank.strip() if edit_bank.strip() else None
                        }
                        res = requests.put(f"{BACKEND_URL}/api/members/{curr_mem['chat_id']}", json=payload)
                        if res.status_code == 200:
                            st.success("Updated successfully.")
                            st.session_state.edit_member_target = None
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Failed to update profile.")
                    
                    if c_cancel_ed.button("❌ Cancel", use_container_width=True):
                        st.session_state.edit_member_target = None
                        st.rerun()

            # MODAL WINDOW 3: Delete Member Confirmation
            if "confirm_delete_mem_id" in st.session_state:
                st.warning(f"⚠️ **Are you sure you want to revoke this member's access privileges?**")
                c_del_m, c_can_m = st.columns(2)
                if c_del_m.button("🗑️ Yes, Revoke Access", use_container_width=True):
                    requests.delete(f"{BACKEND_URL}/api/members/{st.session_state.confirm_delete_mem_id}")
                    del st.session_state.confirm_delete_mem_id
                    st.rerun()
                if c_can_m.button("Cancel", use_container_width=True):
                    del st.session_state.confirm_delete_mem_id
                    st.rerun()

            # Pagination for Members (Max 20 rows)
            mem_limit = 20
            num_members = len(fam_members)
            num_m_pages = max(1, (num_members + mem_limit - 1) // mem_limit)
            
            if num_members > mem_limit:
                mem_page = st.number_input("Member Page:", min_value=1, max_value=num_m_pages, step=1, key="mem_page_nav")
            else:
                mem_page = 1
                
            start_m_idx = (mem_page - 1) * mem_limit
            end_m_idx = min(start_m_idx + mem_limit, num_members)
            page_members = fam_members[start_m_idx:end_m_idx]

            # Render Member sub-grid headers
            m_header = st.columns([2, 1, 2, 2, 1, 1])
            m_header[0].markdown("<div class='small-header'>Name</div>", unsafe_allow_html=True)
            m_header[1].markdown("<div class='small-header'>Role</div>", unsafe_allow_html=True)
            m_header[2].markdown("<div class='small-header'>Telegram ID</div>", unsafe_allow_html=True)
            m_header[3].markdown("<div class='small-header'>Linked Bank Account</div>", unsafe_allow_html=True)
            m_header[4].markdown("<div class='small-header'>Edit</div>", unsafe_allow_html=True)
            m_header[5].markdown("<div class='small-header'>Delete</div>", unsafe_allow_html=True)
            st.write("---")

            # Render Member rows
            if page_members:
                for mem in page_members:
                    m_row = st.columns([2, 1, 2, 2, 1, 1])
                    m_row[0].markdown(f"<div class='small-text'>{mem['name']}</div>", unsafe_allow_html=True)
                    m_row[1].markdown(f"<div class='small-text'>{mem['member_role']}</div>", unsafe_allow_html=True)
                    m_row[2].markdown(f"<div class='small-text'><code>{mem['chat_id']}</code></div>", unsafe_allow_html=True)
                    
                    b_acc = mem.get("bank_account")
                    m_row[3].markdown(f"<div class='small-text'><code>{b_acc if b_acc else 'N/A'}</code></div>", unsafe_allow_html=True)
                    
                    if m_row[4].button("✏️ Edit", key=f"e_mem_{mem['chat_id']}"):
                        st.session_state.edit_member_target = mem
                        st.session_state.show_add_member_form = False
                        st.rerun()
                        
                    if m_row[5].button("🗑️ Delete", key=f"del_mem_{mem['chat_id']}"):
                        st.session_state.confirm_delete_mem_id = mem["chat_id"]
                        st.rerun()
            else:
                st.info("This family has no whitelisted members assigned yet. Use the 'Add Member' button above to populate.")