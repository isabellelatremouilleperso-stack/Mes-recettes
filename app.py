import streamlit as st
import requests
import pandas as pd

# ==============================
# CONFIGURATION & DESIGN
# ==============================
st.set_page_config(page_title="Mon Livre de Recettes", page_icon="👩‍🍳", layout="wide")

# STYLE RADICAL POUR LA VISIBILITÉ
st.markdown("""
    <style>
    /* 1. Fond de la page en blanc */
    .stApp { background-color: white !important; }
    
    /* 2. Force le texte en NOIR uniquement dans la partie centrale */
    section[data-testid="stMainView"] .stMarkdown, 
    section[data-testid="stMainView"] p, 
    section[data-testid="stMainView"] h1, 
    section[data-testid="stMainView"] h2, 
    section[data-testid="stMainView"] h3,
    section[data-testid="stMainView"] label {
        color: black !important;
    }

    /* 3. Style des cartes bibliothèque */
    .recipe-card {
        background-color: #ffffff;
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# LIENS
# ==============================
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# ==============================
# MÉMOIRE
# ==============================
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "liste_epicerie" not in st.session_state: st.session_state.liste_epicerie = []

# ==============================
# MENU LATÉRAL
# ==============================
with st.sidebar:
    st.title("👨‍🍳 Menu")
    if st.button("📚 Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("➕ Ajouter une recette", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True):
        st.session_state.page = "liste"
        st.rerun()

# ==============================
# PAGE : DÉTAILS (C'est ici que ça bloquait)
# ==============================
if st.session_state.page == "details" and st.session_state.recipe_data:
    row = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()

    st.header(row['Titre'])
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🛒 Ingrédients")
        # On affiche chaque ingrédient avec un point noir bien visible
        items = str(row['Ingrédients']).split('\n')
        for item in items:
            if item.strip():
                st.markdown(f"**• {item.strip()}**") # Mis en gras pour être sûr de voir
        
        if st.button("🛒 Ajouter à ma liste"):
            st.session_state.liste_epicerie.append({"t": row['Titre'], "i": row['Ingrédients']})
            st.toast("Ajouté !")

    with col2:
        if str(row['Image']).startswith("http"):
            st.image(row['Image'], use_container_width=True)

    st.subheader("👨‍🍳 Préparation")
    st.info(row['Préparation'])

# ==============================
# PAGE : AJOUTER
# ==============================
elif st.session_state.page == "ajouter":
    st.title("➕ Ajouter")
    with st.form("add"):
        t = st.text_input("Plat")
        i = st.text_input("Lien image")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Préparation")
        if st.form_submit_button("Enregistrer"):
            requests.post(URL_SCRIPT, json={"titre":t, "image":i, "ingredients":ing, "preparation":pre})
            st.success("Enregistré !")

# ==============================
# PAGE : ACCUEIL
# ==============================
else:
    st.title("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
        
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                img = row['Image'] if str(row['Image']).startswith("http") else "https://via.placeholder.com/200"
                st.image(img, use_container_width=True)
                st.write(f"**{row['Titre']}**")
                if st.button("Voir la fiche", key=f"btn_{idx}"):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.error("Connexion au livre impossible.")
