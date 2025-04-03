import streamlit as st
import pandas as pd
from datetime import datetime

# ----------------------
# 🔐 Password Protection
# ----------------------
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

# ----------------------
# 📦 Load or Initialize Data
# ----------------------
CSV_FILE = "applications.csv"

def load_data():
    columns = ["Colégio", "Último Contacto", "Psicólogo", "Diretor/a", "Local", "Valências", "Acordo Ordem", "Estado"]
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

st.title("🏫 Contato com Colégios")

# ----------------------
# ➕ Adicionar Novo Colégio
# ----------------------
st.header("➕ Adicionar Novo Contato")

with st.form("add_form"):
    colegio = st.text_input("Colégio")
    ultimo_contacto = st.date_input("Último Contacto", datetime.today())
    psicologo = st.text_input("Psicólogo")
    diretor = st.text_input("Diretor/a")
    local = st.text_input("Local")
    valencias = st.text_input("Valências")
    acordo = st.selectbox("Acordo Ordem", ["SIM", "NÃO"])
    estado = st.text_area("Estado")

    submitted = st.form_submit_button("Adicionar")
    if submitted:
        new_row = {
            "Colégio": colegio,
            "Último Contacto": ultimo_contacto,
            "Psicólogo": psicologo,
            "Diretor/a": diretor,
            "Local": local,
            "Valências": valencias,
            "Acordo Ordem": acordo,
            "Estado": estado
        }
        st.session_state.df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        st.session_state.df.to_csv(CSV_FILE, index=False)
        st.success(f"✅ Registo adicionado para {colegio}")

# ----------------------
# ✏️ Editar Colégio Existente
# ----------------------
st.header("✏️ Editar Contato Existente")

if not df.empty:
    selected_index = st.selectbox(
        "Selecionar colégio para editar",
        df.index,
        format_func=lambda i: f"{df.loc[i, 'Colégio']} – {df.loc[i, 'Local']}"
    )
    row = df.loc[selected_index]

    with st.form("edit_form"):
        edit_colegio = st.text_input("Colégio", value=row["Colégio"])
        edit_ultimo = st.date_input("Último Contacto", datetime.strptime(str(row["Último Contacto"]), "%Y-%m-%d"))
        edit_psicologo = st.text_input("Psicólogo", value=row["Psicólogo"])
        edit_diretor = st.text_input("Diretor/a", value=row["Diretor/a"])
        edit_local = st.text_input("Local", value=row["Local"])
        edit_valencias = st.text_input("Valências", value=row["Valências"])
        edit_acordo = st.selectbox("Acordo Ordem", ["SIM", "NÃO"], index=["SIM", "NÃO"].index(row["Acordo Ordem"]))
        edit_estado = st.text_area("Estado", value=row["Estado"])

        save = st.form_submit_button("💾 Guardar Alterações")
        if save:
            st.session_state.df.loc[selected_index] = {
                "Colégio": edit_colegio,
                "Último Contacto": edit_ultimo,
                "Psicólogo": edit_psicologo,
                "Diretor/a": edit_diretor,
                "Local": edit_local,
                "Valências": edit_valencias,
                "Acordo Ordem": edit_acordo,
                "Estado": edit_estado
            }
            st.session_state.df.to_csv(CSV_FILE, index=False)
            st.success(f"✅ Atualizado: {edit_colegio}")

# ----------------------
# 📄 Visualizar Tabela
# ----------------------
st.header("📊 Lista de Colégios")
st.dataframe(st.session_state.df)