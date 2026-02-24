import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION
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

CATEGORIES = ["Poulet", "Bœuf", "Porc", "Poisson", "Pâtes", "Riz", "Soupe", "Salade", "Entrée", "Plat Principal", "Accompagnement", "Dessert", "Petit-déjeuner", "Autre"]

if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "checked_items" not in st.session_state: st.session_state.checked_items = []

# 2. BARRE LATÉRALE
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

# 3. PAGES

# --- PAGE ACCUEIL ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        if len(df) > 0:
            df.columns = ['Date', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date_Prevue', 'Image', 'Catégorie']
            df = df[df['Titre'] != '']
            
            search = st.text_input("🔍 Rechercher...")
            if search:
                df = df[df['Titre'].str.contains(search, case=False)]

            grid = st.columns(3)
            for idx, row in df.reset_index(drop=True).iterrows():
                with grid[idx % 3]:
                    with st.container(border=True):
                        pic = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/200"
                        st.image(pic, use_container_width=True)
                        if row['Catégorie']:
                            st.markdown(f"<span class='cat-badge'>{row['Catégorie']}</span>", unsafe_allow_html=True)
                        st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                        if st.button("Ouvrir", key=f"v_{idx}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"
                            st.rerun()
        else:
            st.info("Aucune recette trouvée dans le fichier.")
    except Exception as e:
        st.error("Impossible de lire les recettes. Vérifiez la publication du Google Sheets.")

# --- PAGE AJOUTER ---
elif st.session_state.page == "ajouter":
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
            st.write("🔍 Aperçu :")
            st.image(img_url, width=200)

        if st.form_submit_button("💾 Enregistrer"):
            if titre and ingr:
                data = {"date": datetime.now().strftime("%d/%m/%Y"), "titre": titre, "source": source, "ingredients": ingr, "preparation": prep, "date_prevue": date_p.strftime("%d/%m/%Y"), "image": img_url, "categorie": cat}
                requests.post(URL_SCRIPT, json=data)
                st.success("Enregistré !")
                st.session_state.page = "home"
                st.rerun()

# --- PAGE DÉTAILS ---
elif st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    st.header(f"🍳 {res['Titre']}")
    
    src = str(res.get('Source', ''))
    if "instagram.com" in src: st.link_button("📸 Instagram", src)
    elif "facebook.com" in src: st.link_button("💙 Facebook", src)

    col_a, col_b = st.columns([1, 1.2])
    with col_a:
        st.subheader("🛒 Ingrédients")
        for i in str(res['Ingrédients']).split('\n'):
            if i.strip():
                if st.checkbox(i.strip(), key=f"det_{i}"):
                    if i.strip() not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(i.strip())
        if st.button("➕ Ajouter à l'épicerie"): st.toast("Ajouté !")
    with col_b:
        st.image(res['Image'] if "http" in str(res['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        st.info(res.get('Préparation', 'Pas de détails'))

# --- PAGE ÉPICERIE ---
elif st.session_state.page == "shopping":
    st.header("🛒 Liste d'épicerie")
    if not st.session_state.shopping_list:
        st.info("Liste vide.")
    else:
        c_btn1, c_btn2 = st.columns(2)
        if c_btn1.button("🗑️ Vider les cochés", use_container_width=True):
            st.session_state.shopping_list = [item for item in st.session_state.shopping_list if item not in st.session_state.checked_items]
            st.session_state.checked_items = []
            st.rerun()
        if c_btn2.button("🚫 Tout vider", use_container_width=True):
            st.session_state.shopping_list = []
            st.session_state.checked_items = []
            st.rerun()

        for idx, item in enumerate(st.session_state.shopping_list):
            cols = st.columns([0.5, 4, 1])
            if cols[0].checkbox("", key=f"shop_chk_{idx}"):
                if item not in st.session_state.checked_items: st.session_state.checked_items.append(item)
            else:
                if item in st.session_state.checked_items: st.session_state.checked_items.remove(item)
            cols[1].write(item)
            if cols[2].button("❌", key=f"shop_del_{idx}"):
                st.session_state.shopping_list.pop(idx)
                st.rerun()

# --- PAGE AIDE ---
elif st.session_state.page == "aide":
    st.header("📖 Aide & Tuto")
    st.write("### 🛒 Épicerie")
    st.write("- Cochez les articles pour les marquer. Cliquez sur **'Vider les cochés'** pour les supprimer d'un coup.")
    st.write("- Cliquez sur le **'X'** pour supprimer un article seul.")
    st.write("### 📸 Vidéos Instagram & Facebook")
    st.write("- Collez le lien du Reel dans 'Lien source' pour avoir un bouton direct sur la fiche.")
    st.write("### 🖼️ Images")
    st.write("- Collez un lien finissant par .jpg ou .png pour l'image. L'aperçu s'affiche lors de l'ajout.")
    st.write("### 📲 Installation Tablette")
    st.write("- Dans Chrome, menu (3 points) > 'Ajouter à l'écran d'accueil'. Nommez-le **'Mes Recettes'**.")
