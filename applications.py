import streamlit as st
import pandas as pd
from datetime import datetime

import streamlit as st

def check_password():
    def password_entered():
        if st.session_state["password"] == "patchestagio":
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False
            st.error("❌ Incorrect password")

    if "authenticated" not in st.session_state:
        st.text_input("🔐 Enter password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["authenticated"]:
        st.text_input("🔐 Enter password", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True

if not check_password():
    st.stop()


CSV_FILE = "applications.csv"

# --------------------------------------
# 📦 Load or Initialize Data
# --------------------------------------
def load_data():
    columns = ["Company", "Role", "Date Applied", "Status", "Response Date", "Last Contact", "Notes"]
    try:
        df = pd.read_csv(CSV_FILE)
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        return df[columns]
    except FileNotFoundError:
        return pd.DataFrame(columns=columns)

if "df" not in st.session_state:
    st.session_state.df = load_data()

df = st.session_state.df

st.title("📋 Job Application Tracker")

# --------------------------------------
# ➕ Add New Application
# --------------------------------------
st.header("➕ Add New Application")

with st.form("Add New"):
    company = st.text_input("Company")
    role = st.text_input("Role")
    date_applied = st.date_input("Date Applied", datetime.today())
    status = st.selectbox("Status", ["Applied", "Interviewing", "Rejected", "Offer"])
    response_received = st.checkbox("Received a response?")
    response_date = st.date_input("Response Date", datetime.today()) if response_received else ""
    last_contact = st.date_input("Last Contact", datetime.today())
    notes = st.text_area("Notes")

    submitted = st.form_submit_button("Add Application")
    if submitted:
        new_row = {
            "Company": company,
            "Role": role,
            "Date Applied": date_applied,
            "Status": status,
            "Response Date": response_date,
            "Last Contact": last_contact,
            "Notes": notes
        }
        st.session_state.df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.df.to_csv(CSV_FILE, index=False)
        st.success(f"✅ Added application for {company}")

# --------------------------------------
# ✏️ Edit Existing Application
# --------------------------------------
st.header("✏️ Edit Existing Application")

if not df.empty:
    selected_index = st.selectbox(
        "Select an application to edit",
        df.index,
        format_func=lambda i: f"{df.loc[i, 'Company']} – {df.loc[i, 'Role']}"
    )
    row = df.loc[selected_index]

    with st.form("Edit Application"):
        edit_company = st.text_input("Company", value=row["Company"])
        edit_role = st.text_input("Role", value=row["Role"])
        edit_date_applied = st.date_input(
            "Date Applied", 
            datetime.strptime(str(row["Date Applied"]), "%Y-%m-%d")
        )
        edit_status = st.selectbox(
            "Status", 
            ["Applied", "Interviewing", "Rejected", "Offer"],
            index=["Applied", "Interviewing", "Rejected", "Offer"].index(row["Status"])
        )
        edit_response_date = st.date_input(
            "Response Date",
            value=datetime.strptime(str(row["Response Date"]), "%Y-%m-%d") if pd.notnull(row["Response Date"]) and row["Response Date"] else datetime.today()
        )
        edit_last_contact = st.date_input(
            "Last Contact",
            value=datetime.strptime(str(row["Last Contact"]), "%Y-%m-%d") if pd.notnull(row["Last Contact"]) and row["Last Contact"] else datetime.today()
        )
        edit_notes = st.text_area("Notes", value=row["Notes"])

        save_edit = st.form_submit_button("💾 Save Changes")
        if save_edit:
            st.session_state.df.loc[selected_index] = {
                "Company": edit_company,
                "Role": edit_role,
                "Date Applied": edit_date_applied,
                "Status": edit_status,
                "Response Date": edit_response_date,
                "Last Contact": edit_last_contact,
                "Notes": edit_notes
            }
            st.session_state.df.to_csv(CSV_FILE, index=False)
            st.success(f"✅ Updated application for {edit_company}")

# --------------------------------------
# 📊 View All Applications
# --------------------------------------
st.header("📄 Applications Overview")
st.dataframe(st.session_state.df)