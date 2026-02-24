import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. DESIGN ET GRILLE UNIFORME
st.set_page_config(page_title="Mes Recettes", layout="wide")

st.markdown("""
    <style>
    /* Images : 200px de haut, recadrage net pour éviter les décalages */
    [data-testid="stImage"] img {
        object-fit: cover;
        height: 200px !important;
        width: 100% !important;
        border-radius: 10px 10px 0 0;
    }
    
    /* Cartes : Hauteur fixe pour que tout soit aligné horizontalement */
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        height: 520px !important;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    /* Titres : Espace réservé pour 3 lignes max */
    .recipe-title {
        height: 80px; 
        overflow: hidden;
        font-weight: bold;
        font-size: 1.1em;
        line-height: 1.2;
    }

    /* Badge catégorie */
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

CATEGORIES = ["Entrée", "Plat Principal", "Dessert", "Petit-déjeuner", "Collation", "Apéro"]

# 2. MÉMOIRE
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "bought_items" not in st.session_state: st.session_state.bought_items = {}

# 3. MENU LATÉRAL
with st.sidebar:
    st.title("👩‍🍳 Menu")
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

# --- AJOUTER ---
if st.session_state.page == "ajouter":
    st.header("➕ Nouvelle Recette")
    with st.form("add_form"):
        col1, col2 = st.columns(2)
        with col1:
            t = st.text_input("Nom du plat *")
            cat = st.selectbox("Catégorie", CATEGORIES)
            d = st.date_input("Date prévue", datetime.now())
        with col2:
            img = st.text_input("URL de l'image (Lien)")
            src = st.text_input("Lien source (URL site)")
        
        ing = st.text_area("Ingrédients (Copier-Coller) *")
        pre = st.text_area("Préparation")
        
        if st.form_submit_button("💾 Enregistrer"):
            if t and ing:
                data = {"titre":t, "categorie":cat, "date":d.strftime("%d/%m/%Y"), "image":img, "ingredients":ing, "preparation":pre, "source":src}
                requests.post(URL_SCRIPT, json=data)
                st.success("Recette ajoutée avec succès !")
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("Le titre et les ingrédients sont obligatoires.")

# --- DÉTAILS ---
elif st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    
    st.header(f"🍳 {res['Titre']}")
    st.markdown(f"<span class='cat-badge'>{res.get('Catégorie', 'Plat')}</span>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.subheader("🛒 Ingrédients")
        for i in str(res['Ingrédients']).split('\n'):
            item = i.strip()
            if item:
                if st.checkbox(item, key=f"d_{item}"):
                    if item not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(item)
    with col2:
        if "http" in str(res['Image']):
            st.image(res['Image'], use_container_width=True)
        st.subheader("👨‍🍳 Préparation")
        st.info(res['Préparation'])

# --- SHOPPING ---
elif st.session_state.page == "shopping":
    st.title("🛒 Liste d'épicerie")
    if not st.session_state.shopping_list:
        st.info("Votre liste est vide.")
    else:
        if st.button("🗑️ Tout vider"):
            st.session_state.shopping_list = []
            st.rerun()
        for item in st.session_state.shopping_list:
            st.checkbox(item, key=f"s_{item}")

# --- BIBLIOTHÈQUE ---
else:
    st.header("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV)
        # Nettoyage des colonnes (8 colonnes attendues)
        df = df[df.iloc[:, 1].notna()]
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image', 'Catégorie']
        
        # Filtres
        c1, c2 = st.columns([2, 1])
        search = c1.text_input("🔍 Rechercher...")
        f_cat = c2.selectbox("📂 Filtrer par catégorie", ["Toutes"] + CATEGORIES)
        
        if search:
            df = df[df['Titre'].str.contains(search, case=False)]
        if f_cat != "Toutes":
            df = df[df['Catégorie'] == f_cat]

        st.write("---")
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    # Image
                    img_url = str(row['Image']) if "http" in str(row['Image']) else "https://via.placeholder.com/200"
                    st.image(img_url, use_container_width=True)
                    
                    # Infos
                    st.markdown(f"<span class='cat-badge'>{row.get('Catégorie', 'Plat')}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    st.caption(f"📅 {row['Date']}")
                    
                    if st.button("Voir la fiche", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except Exception as e:
        st.info("Aucune recette. Ajoutez-en une via le menu latéral !")
