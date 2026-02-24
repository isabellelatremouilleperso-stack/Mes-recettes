import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION ET DESIGN "GRILLE PARFAITE"
st.set_page_config(page_title="Mon Livre de Recettes", layout="wide")

st.markdown("""
    <style>
    /* Images uniformes : 200px de haut, recadrage intelligent */
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

# 2. GESTION DE LA MÉMOIRE (Session State)
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "bought_items" not in st.session_state: st.session_state.bought_items = {}

# 3. BARRE LATÉRALE (NAVIGATION SECONDAIRE)
with st.sidebar:
    st.title("👩‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", key="nav_home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("🛒 Liste d'épicerie", key="nav_shop", use_container_width=True):
        st.session_state.page = "shopping"
        st.rerun()
    st.write("---")
    st.metric("Articles à acheter", len(st.session_state.shopping_list))

# 4. BARRE SUPÉRIEURE (ACCÈS RAPIDE)
col_header, col_btn = st.columns([4, 1.2])
with col_header:
    st.title("📖 Mes Recettes")
with col_btn:
    st.write("") # Alignement vertical
    if st.button("➕ Nouvelle Recette", type="primary", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()

st.write("---")

# 5. LOGIQUE DES PAGES

# --- PAGE AJOUTER (Optimisée pour la collecte) ---
if st.session_state.page == "ajouter":
    st.subheader("🚀 Ajouter une nouvelle découverte")
    
    # Champ URL déconnecté du formulaire pour faciliter le copier-coller
    url_web = st.text_input("🔗 Lien du site (Optionnel)", placeholder="Collez l'URL de Marmiton, Ricardo, etc.")
    
    with st.form("form_add"):
        c1, c2 = st.columns(2)
        with c1:
            t = st.text_input("Nom du plat *")
            d = st.date_input("Date prévue", datetime.now())
            img = st.text_input("URL de l'image (Lien direct)")
        with c2:
            ing = st.text_area("Ingrédients (Collez tout le bloc ici) *", height=150)
            
        pre = st.text_area("Étapes de préparation")
        
        if st.form_submit_button("💾 Enregistrer la recette"):
            if t and ing:
                data = {
                    "titre": t, 
                    "date": d.strftime("%d/%m/%Y"), 
                    "image": img, 
                    "ingredients": ing, 
                    "preparation": pre,
                    "source": url_web # On garde l'URL en mémoire
                }
                requests.post(URL_SCRIPT, json=data)
                st.success(f"🎉 '{t}' ajouté avec succès !")
                st.session_state.page = "home"
                st.rerun()
            else:
                st.warning("Veuillez remplir au moins le titre et les ingrédients.")

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
                        st.toast(f"Ajouté : {item}")
    with col2:
        if str(res['Image']).startswith("http"):
            st.image(res['Image'], use_container_width=True)
        st.subheader("👨‍🍳 Préparation")
        st.info(res['Préparation'])

# --- PAGE ÉPICERIE ---
elif st.session_state.page == "shopping":
    st.title("🛒 Liste d'Épicerie")
    if not st.session_state.shopping_list:
        st.info("Votre liste est vide.")
    else:
        c1, c2 = st.columns(2)
        if c1.button("🧹 Supprimer les cochés", use_container_width=True):
            st.session_state.shopping_list = [i for i in st.session_state.shopping_list if not st.session_state.bought_items.get(i, False)]
            st.session_state.bought_items = {}
            st.rerun()
        if c2.button("🗑️ Tout vider", use_container_width=True):
            st.session_state.shopping_list = []
            st.session_state.bought_items = {}
            st.rerun()
        
        st.write("---")
        for item in st.session_state.shopping_list:
            st.session_state.bought_items[item] = st.checkbox(item, key=f"s_{item}", value=st.session_state.bought_items.get(item, False))

# --- PAGE ACCUEIL (Bibliothèque) ---
else:
    try:
        df = pd.read_csv(URL_CSV).dropna(subset=['Titre'])
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
        
        # Barre de recherche intégrée
        recherche = st.text_input("🔍 Rechercher une recette...", placeholder="Ex: Poulet, Lasagnes...")
        if recherche:
            df = df[df['Titre'].str.contains(recherche, case=False)]

        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    # Image avec fallback
                    img_url = str(row['Image']) if str(row['Image']).startswith("http") else "https://via.placeholder.com/250x200?text=Pas+d'image"
                    st.image(img_url, use_container_width=True)
                    
                    # Titre et date alignés
                    st.markdown(f'<div class="recipe-title">{row["Titre"]}</div>', unsafe_allow_html=True)
                    st.caption(f"📅 {row['Date']}" if pd.notna(row['Date']) else "📅 Non planifié")
                    
                    if st.button("Voir la fiche", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except Exception as e:
        st.info("Aucune recette trouvée ou erreur de chargement. Commencez par en ajouter une !")
