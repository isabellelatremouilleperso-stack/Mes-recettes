import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION & DESIGN
st.set_page_config(page_title="Dessin", layout="wide", page_icon="🎨")

st.markdown("""
    <style>
    [data-testid="stImage"] img { object-fit: cover; height: 200px !important; width: 100% !important; border-radius: 10px 10px 0 0; }
    [data-testid="stVerticalBlockBorderWrapper"] > div { height: 540px !important; display: flex; flex-direction: column; justify-content: space-between; }
    .recipe-title { height: 80px; overflow: hidden; font-weight: bold; font-size: 1.1em; line-height: 1.2; color: #ffffff; }
    .cat-badge { background-color: #ffca28; color: #000; padding: 2px 10px; border-radius: 15px; font-size: 0.8em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# Liens (Vérifie bien que ce sont les tiens)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet", "Bœuf", "Porc", "Soupe", "Pâtes", "Entrée", "Plat Principal", "Dessert", "Petit-déjeuner", "Autre"]

# 2. GESTION DE L'ÉTAT (MÉMOIRE)
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# 3. BARRE LATÉRALE
with st.sidebar:
    st.title("🎨 Dessin & Cuisine")
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
    if st.button("❓ Aide & Tuto", use_container_width=True):
        st.session_state.page = "aide"
        st.rerun()
    st.write("---")
    st.metric("Articles à acheter", len(st.session_state.shopping_list))

# 4. LOGIQUE DES PAGES

# --- PAGE AIDE ---
if st.session_state.page == "aide":
    st.header("📖 Mode d'Emploi")
    with st.expander("📸 Instagram & Facebook", expanded=True):
        st.write("Copie le lien d'un Reel ou d'une vidéo et colle-le dans 'Lien source'. Un bouton apparaîtra sur la fiche !")
    with st.expander("🛒 Liste d'épicerie"):
        st.write("Coche les ingrédients manquants dans une fiche recette et clique sur 'Valider la sélection'.")
    with st.expander("📲 Installer sur la tablette"):
        st.write("Dans Chrome, appuie sur les 3 points (⋮) puis 'Ajouter à l'écran d'accueil'. Renomme-le en 'Dessin'.")

# --- PAGE DÉTAILS ---
elif st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    
    st.header(f"🍳 {res['Titre']}")
    
    # Boutons de liens sociaux
    s_url = str(res.get('Source', ''))
    if "instagram.com" in s_url:
        st.link_button("📸 Voir la vidéo Instagram", s_url, type="primary", use_container_width=True)
    elif "facebook.com" in s_url:
        st.link_button("💙 Voir la vidéo Facebook", s_url, type="primary", use_container_width=True)
    elif "http" in s_url:
        st.link_button("🔗 Voir le site d'origine", s_url, use_container_width=True)
    
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
        
        if st.button("➕ Valider la sélection", type="primary", use_container_width=True):
            for it in selection:
                if it not in st.session_state.shopping_list:
                    st.session_state.shopping_list.append(it)
            st.toast("Ajouté à la liste !")

    with col2:
        img_url = res['Image'] if "http" in str(res['Image']) else "https://via.placeholder.com/200"
        st.image(img_url, use_container_width=True)
        st.subheader("👨‍🍳 Préparation")
        st.info(res.get('Préparation', 'Étapes non disponibles'))

# --- PAGE AJOUTER (ORDRE DES COLONNES FIXÉ) ---
elif st.session_state.page == "ajouter":
    st.header("➕ Nouvelle Recette")
    with st.form("add_form"):
        t = st.text_input("Nom du plat *")
        col1, col2 = st.columns(2)
        with col1: cat = st.selectbox("Catégorie", CATEGORIES)
        with col2: d = st.date_input("Date prévue", datetime.now())
        img = st.text_input("Lien de l'image (URL)")
        src = st.text_input("Lien source (Instagram, FB, Web)")
        ing = st.text_area("Ingrédients (un par ligne) *")
        pre = st.text_area("Préparation")
        
        if st.form_submit_button("💾 Enregistrer la recette"):
            if t and ing:
                # CORRESPONDANCE COLONNES A, B, C, D, E, F, G, H
                data = {
                    "date_envoi": datetime.now().strftime("%d/%m/%Y"), # A
                    "titre": t,                                        # B
                    "source": src,                                     # C
                    "ingredients": ing,                                # D
                    "preparation": pre,                                # E
                    "date_prevue": d.strftime("%d/%m/%Y"),             # F
                    "image": img,                                      # G
                    "categorie": cat                                   # H
                }
                requests.post(URL_SCRIPT, json=data)
                st.success("✅ Recette ajoutée avec succès !")
                st.session_state.page = "home"
                st.rerun()

# --- PAGE ÉPICERIE ---
elif st.session_state.page == "shopping":
    st.title("🛒 Liste d'épicerie")
    if st.button("🗑️ Vider la liste"):
        st.session_state.shopping_list = []
        st.rerun()
    for idx, item in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([4, 1])
        c1.write(f"- {item}")
        if c2.button("❌", key=f"del_{idx}"):
            st.session_state.shopping_list.pop(idx)
            st.rerun()

# --- PAGE BIBLIOTHÈQUE ---
else:
    st.header("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        df = df[df.iloc[:, 1] != '']
        df.columns = ['Date_Envoi', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date_Prevue', 'Image', 'Catégorie']
        
        c1, c2 = st.columns([2, 1])
        search = c1.text_input("🔍 Rechercher...")
        f_cat = c2.selectbox("📂 Filtre", ["Toutes"] + CATEGORIES)
        
        if search: df = df[df['Titre'].str.contains(search, case=False)]
        if f_cat != "Toutes": df = df[df['Catégorie'] == f_cat]

        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    im = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/200"
                    st.image(im, use_container_width=True)
                    if row['Catégorie']: st.markdown(f"<span class='cat-badge'>{row['Catégorie']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Voir la fiche", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except:
        st.info("Bienvenue ! Commencez par ajouter votre première recette.")
