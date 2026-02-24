import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION ET DESIGN ABSOLU
st.set_page_config(page_title="Livre de Recettes", layout="wide")

st.markdown("""
    <style>
    /* 1. Fixer les images : 200px de haut, recadrage propre */
    [data-testid="stImage"] img {
        object-fit: cover;
        height: 200px !important;
        width: 100% !important;
        border-radius: 10px 10px 0 0;
    }
    
    /* 2. Fixer les boîtes pour qu'elles soient toutes égales */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        height: 480px !important; /* Hauteur totale de la carte */
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* 3. Fixer la zone du titre (max 3 lignes) pour éviter le décalage */
    .recipe-title {
        height: 85px; 
        overflow: hidden;
        margin-top: 10px;
        font-weight: bold;
        line-height: 1.2;
    }

    .stApp { color: white; }
    </style>
    """, unsafe_allow_html=True)

# Liens
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# 2. MÉMOIRE
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "bought_items" not in st.session_state: st.session_state.bought_items = {}

# 3. BARRE LATÉRALE
with st.sidebar:
    st.title("👩‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", key="side_bib", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("🛒 Ma Liste d'épicerie", key="side_shop", use_container_width=True):
        st.session_state.page = "shopping"
        st.rerun()
    if st.button("➕ Ajouter une recette", key="side_add", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()
    st.write("---")
    st.metric("Articles à acheter", len(st.session_state.shopping_list))

# 4. LOGIQUE DES PAGES
if st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    st.header(f"🍳 {res['Titre']}")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🛒 Ingrédients manquants ?")
        choix = []
        ings = str(res['Ingrédients']).split('\n')
        for i in ings:
            if i.strip() and st.checkbox(i.strip(), key=f"d_{i}"):
                choix.append(i.strip())
        if st.button("✅ Ajouter", type="primary"):
            for item in choix:
                if item not in st.session_state.shopping_list:
                    st.session_state.shopping_list.append(item)
            st.toast("Ajouté !")
    with col2:
        st.image(str(res['Image']), use_container_width=True)
        st.info(res['Préparation'])

elif st.session_state.page == "shopping":
    st.title("🛒 Ma Liste d'Épicerie")
    if not st.session_state.shopping_list:
        st.info("Liste vide")
    else:
        c1, c2 = st.columns(2)
        if c1.button("🧹 Supprimer cochés", use_container_width=True):
            st.session_state.shopping_list = [i for i in st.session_state.shopping_list if not st.session_state.bought_items.get(i, False)]
            st.session_state.bought_items = {}
            st.rerun()
        if c2.button("🗑️ Tout vider", use_container_width=True):
            st.session_state.shopping_list = []; st.session_state.bought_items = {}; st.rerun()
        for i in st.session_state.shopping_list:
            st.session_state.bought_items[i] = st.checkbox(i, key=f"s_{i}", value=st.session_state.bought_items.get(i, False))

elif st.session_state.page == "ajouter":
    st.title("➕ Ajouter")
    with st.form("add"):
        t = st.text_input("Plat"); d = st.date_input("Date"); img = st.text_input("Image URL")
        ing = st.text_area("Ingrédients"); pre = st.text_area("Préparation")
        if st.form_submit_button("🚀 Enregistrer"):
            requests.post(URL_SCRIPT, json={"titre":t, "date":d.strftime("%d/%m/%Y"), "image":img, "ingredients":ing, "preparation":pre})
            st.success("C'est fait !")

else:
    st.title("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV).dropna(subset=['Titre'])
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    # Image fixe
                    st.image(str(row['Image']) if str(row['Image']).startswith("http") else "https://via.placeholder.com/200")
                    
                    # Titre avec hauteur fixe (en HTML pour le CSS)
                    st.markdown(f'<div class="recipe-title">{row["Titre"]}</div>', unsafe_allow_html=True)
                    
                    # Date et Bouton (toujours calés au même endroit)
                    st.caption(f"📅 {row['Date']}" if pd.notna(row['Date']) else "📅 -")
                    if st.button("Voir la fiche", key=f"b_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
