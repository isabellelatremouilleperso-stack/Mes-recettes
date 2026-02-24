import streamlit as st
import requests
import pandas as pd

# ==============================
# CONFIGURATION & DESIGN
# ==============================
st.set_page_config(page_title="Mon Livre de Recettes", page_icon="👩‍🍳", layout="wide")

st.markdown("""
    <style>
    /* Fond de page blanc pur */
    .stApp { background-color: #FFFFFF; }
    
    /* Force le texte en noir pour une lecture facile */
    .stApp p, .stApp div, .stApp span, .stApp label, .stApp h3 {
        color: #1f2937 !important;
    }

    /* Cartes de la bibliothèque */
    .recipe-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #f0f0f0;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* Titre de la fiche détaillée */
    .fiche-titre {
        font-size: 42px;
        font-weight: 800;
        color: #1f2937 !important;
        margin-bottom: 10px;
        line-height: 1.2;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# LIENS VERS TES DONNÉES
# ==============================
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# ==============================
# GESTION DE LA MÉMOIRE
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "recipe_data" not in st.session_state:
    st.session_state.recipe_data = None

if "liste_epicerie" not in st.session_state:
    st.session_state.liste_epicerie = []

# ==============================
# MENU LATÉRAL
# ==============================
with st.sidebar:
    st.title("👩‍🍳 Menu")
    
    # On définit l'index par défaut du menu selon la page actuelle
    idx = 0
    if st.session_state.page == "ajouter": idx = 1
    elif st.session_state.page == "liste": idx = 2

    choix = st.radio("Navigation", ["📚 Bibliothèque", "➕ Ajouter", "🛒 Épicerie"], index=idx)

    if choix == "📚 Bibliothèque" and st.session_state.page != "details":
        st.session_state.page = "home"
    elif choix == "➕ Ajouter":
        st.session_state.page = "ajouter"
    elif choix == "🛒 Épicerie":
        st.session_state.page = "liste"

# ==============================
# PAGE : AJOUTER UNE RECETTE
# ==============================
if st.session_state.page == "ajouter":
    st.title("➕ Nouvelle Recette")
    with st.form("form_add", clear_on_submit=True):
        t = st.text_input("Nom du plat *")
        img = st.text_input("Lien de l'image (URL)")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Préparation")
        
        if st.form_submit_button("🚀 Enregistrer dans mon livre"):
            if t:
                try:
                    res = requests.post(URL_SCRIPT, json={"titre": t, "image": img, "ingredients": ing, "preparation": pre})
                    if res.status_code == 200:
                        st.success("C'est enregistré ! 🎉")
                        st.balloons()
                    else: st.error("Erreur de sauvegarde.")
                except: st.error("Connexion au serveur impossible.")
            else: st.warning("Le nom du plat est obligatoire.")

# =
