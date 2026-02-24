import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION (Nom rétabli : Mes Recettes)
st.set_page_config(page_title="Mes Recettes", layout="wide", page_icon="🎨")

st.markdown("""
    <style>
    [data-testid="stImage"] img { object-fit: cover; height: 200px !important; width: 100% !important; border-radius: 10px; }
    .recipe-title { height: 60px; overflow: hidden; font-weight: bold; font-size: 1.2em; color: #ffffff; margin-top: 10px; }
    .cat-badge { background-color: #ffca28; color: #000; padding: 2px 12px; border-radius: 15px; font-size: 0.8em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = [
    "Poulet", "Bœuf", "Porc", "Poisson", "Pâtes", "Riz", 
    "Soupe", "Salade", "Entrée", "Plat Principal", 
    "Accompagnement", "Dessert", "Petit-déjeuner", "Autre"
]

if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
# Pour gérer les coches dans l'épicerie
if "checked_items" not in st.session_state: st.session_state.checked_items = {}

# 2. MENU LATÉRAL
with st.sidebar:
    st.title("👨‍🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("➕ Ajouter une recette", type="primary", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True):
        st.session_state.page = "shopping"
        st.rerun()
    st.write("---")
    if st.button("❓ Aide & Tuto", use_container_width=True):
        st.session_state.page = "aide"
        st.rerun()

# --- PAGE AJOUTER ---
if st.session_state.page == "ajouter":
    st.header("➕ Nouvelle Recette")
    with st.form("add_form"):
        titre = st.text_input("Nom du plat *")
        col1, col2 = st.columns(2)
        with col1:
            cat = st.selectbox("Catégorie", CATEGORIES)
            img_url = st.text_input("Lien de l'image (URL)")
        with col2:
            date_p = st.date_input("Date prévue", datetime.now())
            source = st.text_input("Lien Instagram / Facebook")
        ingr = st.text_area("Ingrédients (un par ligne) *")
        prep = st.text_area("Préparation")
        
        if img_url:
            st.image(img_url, width=200, caption="Aperçu")

        if st.form_submit_button("💾 Enregistrer"):
            if titre and ingr:
                data = {"date": datetime.now().strftime("%d/%m/%Y"), "titre": titre, "source": source, "ingredients": ingr, "preparation": prep, "date_prevue": date_p.strftime("%d/%m/%Y"), "image": img_url, "categorie": cat}
                requests.post(URL_SCRIPT, json=data)
                st.success("Enregistré !")
                st.session_state.page = "home"
                st.rerun()

# --- PAGE ÉPICERIE (X et SUPPRESSION COCHÉS) ---
elif st.session_state.page == "shopping":
    st.header("🛒 Liste d'épicerie")
    
    if not st.session_state.shopping_list:
        st.info("Votre liste est vide.")
    else:
        col_btn1, col_btn2 = st.columns(2)
        if col_btn1.button("🗑️ Vider les articles cochés", use_container_width=True):
            # On ne garde que ceux qui ne sont pas cochés
            st.session_state.shopping_list = [item for item in st.session_state.shopping_list if not st.session_state.checked_items.get(item, False)]
            st.session_state.checked_items = {} # Reset des coches
            st.rerun()
        
        if col_btn2.button("🚫 Tout vider", use_container_width=True):
            st.session_state.shopping_list = []
            st.session_state.checked_items = {}
            st.rerun()
        
        st.write("---")
        
        # Affichage des articles avec une coche et un X
        for idx, item in enumerate(st.session_state.shopping_list):
            c1, c2, c3 = st.columns([0.5, 4, 1])
            # Case à cocher pour "sélectionner" (ceux à vider)
            st.session_state.checked_items[item] = c1.checkbox("", value=st.session_state.checked_items.get(item, False), key=f"chk_{idx}")
            c2.write(item)
            # Bouton X pour supprimer direct
            if c3.button("❌", key=f"del_{idx}"):
                st.session_state.shopping_list.pop(idx)
                st.rerun()

# --- PAGE DÉTAILS ---
elif st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    st.header(f"🍳 {res['Titre']}")
    
    s_url = str(res.get('Source', ''))
    if "instagram.com" in s_url: st.link_button("📸 Instagram", s_url)
    elif "facebook.com" in s_url: st.link_button("💙 Facebook", s_url)

    col_a, col_b = st.columns([1, 1.2])
    with col_a:
        st.subheader("🛒 Ingrédients")
        for i in str(res['Ingrédients']).split('\n'):
            ing = i.strip()
            if ing:
                if st.checkbox(ing, key=f"ing_{ing}"):
                    if ing not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(ing)
        if st.button("➕ Ajouter à l'épicerie"): st.toast("Ajouté !")

    with col_b:
        pic = res['Image'] if "http" in str(res['Image']) else "https://via.placeholder.com/400"
        st.image(pic, use_container_width=True)
        st.info(res.get('Préparation', 'Pas de détails'))

# --- PAGE ACCUEIL ---
elif st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        df.columns = ['Date', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date_Prevue', 'Image', 'Catégorie']
        df = df[df['Titre'] != '']
        search = st.text_input("🔍 Rechercher...")
        if search: df = df[df['Titre'].str.contains(search, case=False)]
        
        grid = st.columns(3)
        for idx, row in df.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    im = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/200"
                    st.image(im, use_container_width=True)
                    st.markdown(f"<span class='cat-badge'>{row['Catégorie']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Ouvrir", key=f"v_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except: st.info("Aucune recette.")

# --- PAGE AIDE ---
elif st.session_state.page == "aide":
    st.header("📖 Aide")
    st.write("- **Épicerie** : Cochez les articles que vous avez trouvés en magasin, puis cliquez sur 'Vider les articles cochés' pour nettoyer votre liste. Utilisez le 'X' pour supprimer un article par erreur.")
    st.write("- **Images** : Collez un lien direct se terminant par .jpg ou .png.")
