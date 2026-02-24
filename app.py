import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION ET DESIGN
st.set_page_config(page_title="Mon Livre de Recettes", layout="wide")

st.markdown("""
    <style>
    /* Images uniformes : 200px de haut, recadrage propre */
    [data-testid="stImage"] img {
        object-fit: cover;
        height: 200px !important;
        width: 100% !important;
        border-radius: 10px 10px 0 0;
    }
    
    /* Boîtes de recettes de hauteur égale */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        height: 480px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Fixer la zone du titre pour l'alignement horizontal */
    .recipe-title {
        height: 75px; 
        overflow: hidden;
        font-weight: bold;
        line-height: 1.2;
        margin-top: 5px;
    }

    .stApp { color: white; }
    </style>
    """, unsafe_allow_html=True)

# Liens de connexion
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# 2. GESTION DE LA MÉMOIRE
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "bought_items" not in st.session_state: st.session_state.bought_items = {}

# 3. BARRE LATÉRALE (Bouton AJOUTER remis ici)
with st.sidebar:
    st.title("👩‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", key="nav_home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    
    # TON BOUTON PRÉFÉRÉ EST DE RETOUR ICI :
    if st.button("➕ Ajouter une recette", key="nav_add", type="primary", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()
        
    if st.button("🛒 Liste d'épicerie", key="nav_shop", use_container_width=True):
        st.session_state.page = "shopping"
        st.rerun()
        
    st.write("---")
    st.metric("Articles à acheter", len(st.session_state.shopping_list))

# 4. TITRE DE LA PAGE
st.title("📖 Mes Recettes")
st.write("---")

# 5. LOGIQUE DES PAGES

# --- PAGE AJOUTER ---
if st.session_state.page == "ajouter":
    st.subheader("🚀 Ajouter une nouvelle recette")
    url_web = st.text_input("🔗 Lien du site (ex: Marmiton, Ricardo...)")
    
    with st.form("form_add"):
        c1, c2 = st.columns(2)
        with c1:
            t = st.text_input("Nom du plat *")
            d = st.date_input("Date prévue", datetime.now())
            img = st.text_input("URL de l'image")
        with c2:
            ing = st.text_area("Ingrédients (Colle ta liste ici) *", height=150)
            
        pre = st.text_area("Préparation")
        
        if st.form_submit_button("💾 Enregistrer dans la bibliothèque"):
            if t and ing:
                data = {"titre":t, "date":d.strftime("%d/%m/%Y"), "image":img, "ingredients":ing, "preparation":pre, "source":url_web}
                requests.post(URL_SCRIPT, json=data)
                st.success("Recette enregistrée !")
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("Le titre et les ingrédients sont requis.")

# --- PAGE DÉTAILS ---
elif st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    st.header(f"🍳 {res['Titre']}")
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("🛒 Ingrédients")
        ings = str(res['Ingrédients']).split('\n')
        for i in ings:
            item = i.strip()
            if item:
                if st.checkbox(item, key=f"d_{item}"):
                    if item not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(item)
    with col2:
        if str(res['Image']).startswith("http"):
            st.image(res['Image'], use_container_width=True)
        st.info(res['Préparation'])

# --- PAGE ÉPICERIE ---
elif st.session_state.page == "shopping":
    st.title("🛒 Ma Liste")
    if not st.session_state.shopping_list:
        st.info("Votre liste est vide.")
    else:
        if st.button("🗑️ Tout vider"):
            st.session_state.shopping_list = []
            st.rerun()
        for item in st.session_state.shopping_list:
            st.checkbox(item, key=f"shop_{item}")

# --- PAGE ACCUEIL ---
else:
    try:
        df = pd.read_csv(URL_CSV).dropna(subset=['Titre'])
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
        
        recherche = st.text_input("🔍 Rechercher...")
        if recherche:
            df = df[df['Titre'].str.contains(recherche, case=False)]

        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    img_url = str(row['Image']) if str(row['Image']).startswith("http") else "https://via.placeholder.com/200"
                    st.image(img_url, use_container_width=True)
                    st.markdown(f'<div class="recipe-title">{row["Titre"]}</div>', unsafe_allow_html=True)
                    st.caption(f"📅 {row['Date']}")
                    if st.button("Voir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except:
        st.info("Bienvenue ! Utilisez le menu à gauche pour ajouter votre première recette.")
