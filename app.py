import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. STYLE ET DESIGN (CORRIGÉ)
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

# Liens
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet", "Bœuf", "Porc", "Soupe", "Pâtes", "Entrée", "Plat Principal", "Dessert", "Petit-déjeuner", "Autre"]

# 2. GESTION MÉMOIRE
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# 3. MENU LATÉRAL
with st.sidebar:
    st.title("👩‍🍳 Menu")
    if st.button("📚 Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("➕ Ajouter", type="primary", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True):
        st.session_state.page = "shopping"
        st.rerun()
    st.write("---")
    st.metric("Articles", len(st.session_state.shopping_list))

# 4. LOGIQUE DES PAGES

# --- PAGE DÉTAILS (SYNTAXE ET ACCENTS CORRIGÉS) ---
if st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    
    st.header(f"🍳 {res['Titre']}")
    
    # Boutons de liens sociaux
    s_url = str(res.get('Source', ''))
    if "instagram.com" in s_url:
        st.link_button("📸 Instagram", s_url, type="primary", use_container_width=True)
    elif "facebook.com" in s_url:
        st.link_button("💙 Facebook", s_url, type="primary", use_container_width=True)
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("🛒 Ingrédients")
        liste_ing = str(res['Ingrédients']).split('\n')
        selection = []
        for i in liste_ing:
            nom = i.strip()
            if nom:
                # CORRECTION LIGNE 114
                if st.checkbox(nom, key=f"sel_{nom}"):
                    selection.append(nom)
        
        if st.button("➕ Valider la sélection", type="primary", use_container_width=True):
            for item in selection:
                if item not in st.session_state.shopping_list:
                    st.session_state.shopping_list.append(item)
            st.toast("Ajouté à l'épicerie !")

    with col2:
        img_url = res['Image'] if "http" in str(res['Image']) else "https://via.placeholder.com/200"
        st.image(img_url, use_container_width=True)
        st.subheader("👨‍🍳 Préparation")
        # GESTION DE L'ACCENT
        prep = res.get('Préparation', res.get('Preparation', 'Non renseigné'))
        st.info(prep)

# --- PAGE BIBLIOTHÈQUE (ANTI-NAN) ---
elif st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV).fillna('') # NETTOYAGE DES NAN
        df = df[df.iloc[:, 1] != '']
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image', 'Catégorie']
        
        c1, c2 = st.columns([2, 1])
        search = c1.text_input("🔍 Rechercher...")
        f_cat = c2.selectbox("📂 Catégorie", ["Toutes"] + CATEGORIES)
        
        if search: df = df[df['Titre'].str.contains(search, case=False)]
        if f_cat != "Toutes": df = df[df['Catégorie'] == f_cat]

        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    im = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/200"
                    st.image(im, use_container_width=True)
                    if row['Catégorie']:
                        st.markdown(f"<span class='cat-badge'>{row['Catégorie']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Voir la fiche", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except Exception as e:
        st.info("Ajoutez une recette pour commencer.")

# --- PAGE AJOUTER ---
elif st.session_state.page == "ajouter":
    st.header("➕ Nouvelle Recette")
    with st.form("add_form"):
        t = st.text_input("Nom du plat *")
        col1, col2 = st.columns(2)
        with col1: cat = st.selectbox("Catégorie", CATEGORIES)
        with col2: d = st.date_input("Date", datetime.now())
        img = st.text_input("Lien de l'image")
        src = st.text_input("Lien source (Insta/FB)")
        ing = st.text_area("Ingrédients (un par ligne) *")
        pre = st.text_area("Préparation")
        if st.form_submit_button("Enregistrer"):
            if t and ing:
                data = {"titre":t, "categorie":cat, "date":d.strftime("%d/%m/%Y"), "image":img, "ingredients":ing, "preparation":pre, "source":src}
                requests.post(URL_SCRIPT, json=data)
                st.success("C'est enregistré !")
                st.session_state.page = "home"
                st.rerun()

# --- PAGE SHOPPING ---
elif st.session_state.page == "shopping":
    st.title("🛒 Épicerie")
    if st.button("🗑️ Vider tout"):
        st.session_state.shopping_list = []
        st.rerun()
    for idx, it in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([4, 1])
        c1.write(f"• {it}")
        if c2.button("❌", key=f"d_{idx}"):
            st.session_state.shopping_list.pop(idx)
            st.rerun()
