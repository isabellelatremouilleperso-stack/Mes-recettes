import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION ET STYLE
st.set_page_config(page_title="Mes Recettes", layout="wide")

st.markdown("""
    <style>
    [data-testid="stImage"] img {
        object-fit: cover;
        height: 200px !important;
        width: 100% !important;
        border-radius: 10px 10px 0 0;
    }
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        height: 540px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .recipe-title {
        height: 80px; 
        overflow: hidden;
        font-weight: bold;
        font-size: 1.1em;
        line-height: 1.2;
    }
    .cat-badge {
        background-color: #333;
        color: #ffca28;
        padding: 2px 10px;
        border-radius: 15px;
        font-size: 0.8em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Liens de configuration
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet", "Bœuf", "Porc", "Soupe", "Pâtes", "Entrée", "Plat Principal", "Dessert", "Petit-déjeuner", "Autre"]

# 2. GESTION DE LA MÉMOIRE
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# 3. BARRE LATÉRALE
with st.sidebar:
    st.title("👩‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("➕ Ajouter une recette", type="primary", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()
    if st.button("🛒 Liste d'épicerie", use_container_width=True):
        st.session_state.page = "shopping"
        st.rerun()
    st.write("---")
    st.metric("Articles à acheter", len(st.session_state.shopping_list))

# 4. LOGIQUE DES PAGES

# --- PAGE DÉTAILS (Avec détection Instagram/Facebook) ---
if st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    
    st.header(f"🍳 {res['Titre']}")
    
    # --- SECTION LIENS RÉSEAUX SOCIAUX ---
    source_url = str(res.get('Source', ''))
    if "instagram.com" in source_url:
        st.link_button("📸 Voir la vidéo sur Instagram", source_url, type="primary", use_container_width=True)
    elif "facebook.com" in source_url:
        st.link_button("💙 Voir la publication Facebook", source_url, type="primary", use_container_width=True)
    elif "http" in source_url:
        st.link_button("🔗 Voir le site d'origine", source_url, use_container_width=True)
    
    st.write("---")
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("🛒 Ingrédients")
        liste_ing = str(res['Ingrédients']).split('\n')
        selection = []
        for i in liste_ing:
            nom = i.strip()
            if nom:
                if st.checkbox(nom, key=f"sel_{nom}"):
                    selection.append(nom)
        
        if st.button("➕ Ajouter la sélection à l'épicerie", type="primary", use_container_width=True):
            if selection:
                for item in selection:
                    if item not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(item)
                st.toast(f"✅ {len(selection)} articles ajoutés !")
            else:
                st.warning("Cochez au moins un ingrédient.")

    with col2:
        img_url = row['Image'] if "http" in str(res['Image']) else "https://via.placeholder.com/200"
        st.image(img_url, use_container_width=True)
        st.subheader("👨‍🍳 Préparation")
        prep = res.get('Préparation', res.get('Preparation', 'Étapes non disponibles'))
        st.info(prep)

# --- PAGE AJOUTER ---
elif st.session_state.page == "ajouter":
    st.header("➕ Nouvelle Recette")
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            t = st.text_input("Nom du plat *")
            cat = st.selectbox("Catégorie", CATEGORIES)
            d = st.date_input("Date prévue", datetime.now())
        with col2:
            img = st.text_input("URL de l'image (Lien direct)")
            src = st.text_input("Lien source (Instagram, FB, Web)")
        ing = st.text_area("Ingrédients (un par ligne) *")
        pre = st.text_area("Préparation")
        if st.form_submit_button("💾 Enregistrer la recette"):
            if t and ing:
                data = {"titre":t, "categorie":cat, "date":d.strftime("%d/%m/%Y"), "image":img, "ingredients":ing, "preparation":pre, "source":src}
                requests.post(URL_SCRIPT, json=data)
                st.success("Recette envoyée au grimoire !")
                st.session_state.page = "home"
                st.rerun()

# --- PAGE ÉPICERIE ---
elif st.session_state.page == "
