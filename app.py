import streamlit as st
import requests
import pandas as pd

# CONFIGURATION
st.set_page_config(page_title="Livre de Recettes", layout="wide")

# TON NOUVEAU STYLE (CORRIGÉ ET TESTÉ)
st.markdown("""
    <style>
    /* Fond général */
    .stApp { background-color: white !important; }

    /* Sidebar en blanc */
    section[data-testid="stSidebar"] {
        background-color: white !important;
        border-right: 1px solid #f0f0f0;
    }

    /* Texte sidebar en noir */
    section[data-testid="stSidebar"] * { color: black !important; }

    /* Texte zone principale en noir */
    section[data-testid="stMainView"] * { color: black !important; }

    /* Cartes recettes */
    .recipe-card {
        background-color: #ffffff;
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# LIENS
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# MÉMOIRE
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None

# MENU
with st.sidebar:
    st.title("👩‍🍳 Menu")
    if st.button("📚 Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("➕ Ajouter", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()

# LOGIQUE DES PAGES
if st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    st.header(res['Titre'])
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛒 Ingrédients")
        for i in str(res['Ingrédients']).split('\n'):
            if i.strip(): st.write(f"• {i.strip()}")
    with col2:
        if str(res['Image']).startswith("http"): st.image(res['Image'], use_container_width=True)
    st.subheader("👨‍🍳 Préparation")
    st.write(res['Préparation'])

elif st.session_state.page == "ajouter":
    st.title("➕ Ajouter")
    with st.form("add"):
        t = st.text_input("Nom")
        img = st.text_input("Image (URL)")
        ing = st.text_area("Ingrédients")
        pre = st.text_area("Préparation")
        if st.form_submit_button("Enregistrer"):
            requests.post(URL_SCRIPT, json={"titre":t, "image":img, "ingredients":ing, "preparation":pre})
            st.success("Envoyé !")

else:
    st.title("📚 Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                st.image(row['Image'] if str(row['Image']).startswith("http") else "https://via.placeholder.com/200", use_container_width=True)
                st.write(f"**{row['Titre']}**")
                if st.button("Voir la fiche", key=f"btn_{idx}"):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.error("Connexion impossible au Sheets.")
