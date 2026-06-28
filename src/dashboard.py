# src/dashboard.py
import streamlit as st
import requests

st.set_page_config(page_title="AI Grandchild Control Center", page_icon="⚙️", layout="wide")

BACKEND_URL = "http://backend:8000"

st.title("⚙️ AI Grandchild Relational Database Manager")
st.markdown("Control whitelists, manage family associations, and simulate bank webhook integrations.")

# API Fetch functions
def fetch_families():
    try:
        res = requests.get(f"{BACKEND_URL}/api/families")
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

def fetch_members():
    try:
        res = requests.get(f"{BACKEND_URL}/api/members")
        return res.json() if res.status_code == 200 else []
    except Exception:
        return []

families = fetch_families()
members = fetch_members()

tab_families, tab_members, tab_scenarios = st.tabs(["🏠 Manage Families", "👥 Manage Members", "🧪 Bank SMS Simulator"])

# --- TAB 1: FAMILIES ---
with tab_families:
    st.header("Active Family Directories")
    col_list, col_add = st.columns([2, 1])
    
    with col_list:
        if families:
            for fam in families:
                c_lbl, c_btn = st.columns([3, 1])
                c_lbl.write(f"🏠 **ID {fam['id']}:** {fam['name']}")
                if c_btn.button("Delete Family", key=f"del_fam_{fam['id']}"):
                    requests.delete(f"{BACKEND_URL}/api/families/{fam['id']}")
                    st.rerun()
        else:
            st.info("No families registered yet.")

    with col_add:
        st.subheader("Add New Family")
        new_fam_name = st.text_input("Family Directory Name (e.g. 'Gia đình Ngoại Bảy'):")
        if st.button("Register Family"):
            if new_fam_name:
                res = requests.post(f"{BACKEND_URL}/api/families", json={"name": new_fam_name})
                if res.status_code == 200:
                    st.success("Family added successfully!")
                    st.rerun()

# --- TAB 2: MEMBERS ---
with tab_members:
    st.header("Whitelisted Members")
    col_mem_list, col_mem_add = st.columns([2, 1])
    
    with col_mem_list:
        if members:
            for mem in members:
                c_lbl, c_btn = st.columns([3, 1])
                fam_name = next((f["name"] for f in families if f["id"] == mem["family_id"]), "Unknown")
                bank_info = f" | Bank Account: `{mem['bank_account']}`" if mem.get('bank_account') else ""
                c_lbl.write(
                    f"• **{mem['name']}** ({mem['member_role']}) - ChatID: `{mem['chat_id']}`"
                    f" | Family: {fam_name} | Type: `{mem['member_type']}`{bank_info}"
                )
                if c_btn.button("Revoke Member", key=f"del_mem_{mem['chat_id']}"):
                    requests.delete(f"{BACKEND_URL}/api/members/{mem['chat_id']}")
                    st.rerun()
        else:
            st.info("No members configured yet.")

    with col_mem_add:
        st.subheader("Add Member to Whitelist")
        if not families:
            st.warning("Please register a Family first.")
        else:
            m_chat_id = st.text_input("Telegram Chat ID:")
            m_name = st.text_input("Display Name:")
            m_family = st.selectbox("Assign to Family:", options=families, format_func=lambda x: x["name"])
            m_type = st.selectbox("Role Classification:", ["senior", "non_senior"])
            m_role = st.selectbox("Role Identity:", ["grandpa", "grandma", "mom", "dad", "son", "daughter"])
            
            # Conditionally display Bank Account input if senior
            m_bank_account = ""
            if m_type == "senior":
                m_bank_account = st.text_input("Link Bank Account Number (Optional):")
            
            if st.button("Authorize Member"):
                if m_chat_id and m_name:
                    payload = {
                        "chat_id": m_chat_id,
                        "name": m_name,
                        "family_id": m_family["id"],
                        "member_type": m_type,
                        "member_role": m_role,
                        "bank_account": m_bank_account if m_bank_account else None
                    }
                    res = requests.post(f"{BACKEND_URL}/api/members", json=payload)
                    if res.status_code == 200:
                        st.success("Authorized successfully!")
                        st.rerun()

# --- TAB 3: BANK WEBHOOK SIMULATOR ---
with tab_scenarios:
    st.header("Simulate Inbound Bank Webhook Event")
    st.markdown("Simulate a live API request sent from a commercial bank provider (e.g. HSBC/Văn phòng Thanh toán).")
    
    seniors_with_banks = [m for m in members if m["member_type"] == "senior" and m.get("bank_account")]
    
    if not seniors_with_banks:
        st.warning("Please authorize at least one 'senior' member and link their **Bank Account Number** in the 'Manage Members' tab first.")
    else:
        # Form to simulate transaction
        col_bank, col_txn = st.columns(2)
        
        with col_bank:
            selected_senior = st.selectbox(
                "Select Senior Target:", 
                options=seniors_with_banks, 
                format_func=lambda x: f"{x['name']} (Bank Account: {x['bank_account']})"
            )
            sim_bank_app_id = st.selectbox("Bank App Identity:", ["hsbc_vn", "techcombank", "vietcombank"])
            
        with col_txn:
            sim_txn_id = st.text_input("Simulated Transaction ID:", value="TXN_9821038201")
            sim_amount = st.selectbox("Simulated Transaction Amount:", ["100,000,000", "50,000,000", "500,000"])

        # Construct the realistic mock SMS content
        sms_template = f"TK {selected_senior['bank_account']}: -{sim_amount} VND tai CONG TY DU LICH TOAN CAU vào lúc 14:30. So CCCD cua ngoai la 079123456789."
        st.text_area("Simulated SMS Content (Generated):", value=sms_template, disabled=True)
        
        if st.button("Send Simulated Bank Webhook"):
            payload = {
                "bank_app_id": sim_bank_app_id,
                "bank_account": selected_senior["bank_account"],
                "transaction_id": sim_txn_id,
                "sms_content": sms_template
            }
            try:
                res = requests.post(f"{BACKEND_URL}/test/bank_sms_webhook", json=payload)
                if res.status_code == 200:
                    st.success("Bank transaction webhook simulated successfully! Look at your backend logs or Telegram chats.")
                else:
                    st.error(f"Failed to simulate: {res.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Connection error to backend: {e}")