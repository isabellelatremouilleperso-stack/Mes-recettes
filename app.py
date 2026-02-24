import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION ET DESIGN DE LA GRILLE
st.set_page_config(page_title="Livre de Recettes", layout="wide")

st.markdown("""
    <style>
    /* Uniformisation des images : 200px de haut, recadrage propre */
    [data-testid="stImage"] img {
        object-fit: cover;
        height: 200px !important;
        width: 100% !important;
        border-radius: 10px;
    }
    
    /* On harmonise la couleur du texte */
    .stApp { color: white; }
    
    /* Optionnel : fixe la hauteur minimale des titres pour l'alignement */
    .recipe-title {
        height: 60px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)

# Liens
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# 2. MÉMOIRE DE L'APPLI
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "bought_items" not in st.session_state: st.session_state.bought_items = {}

# 3. BARRE LATÉRALE
with st.sidebar:
    st.title("👩‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("🛒 Ma Liste d'épicerie", use_container_width=True):
        st.session_state.page = "shopping"
        st.rerun()
    if st.button("➕ Ajouter une recette", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()
    
    st.write("---")
    st.metric("Articles à acheter", len(st.session_state.shopping_list))

# 4. PAGE : DÉTAILS
if st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    
    st.header(f"🍳 {res['Titre']}")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🛒 Ingrédients manquants ?")
        choix_utilisateur = []
        ingredients_bruts = str(res['Ingrédients']).split('\n')
        for ing in ingredients_bruts:
            item = ing.strip()
            if item:
                if st.checkbox(item, key=f"sel_{item}"):
                    choix_utilisateur.append(item)
        
        if st.button("✅ Ajouter la sélection", type="primary"):
            if choix_utilisateur:
                for item in choix_utilisateur:
                    if item not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(item)
                st.toast("Ajouté !")

    with col2:
        if str(res['Image']).startswith("http"):
            st.image(res['Image'], use_container_width=True)
        st.subheader("👨‍🍳 Préparation")
        st.info(res['Préparation'])

# 5. PAGE : LISTE D'ÉPICERIE
elif st.session_state.page == "shopping":
    st.title("🛒 Ma Liste d'Épicerie")
    if not st.session_state.shopping_list:
        st.info("Votre liste est vide.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧹 Supprimer articles cochés", use_container_width=True):
                st.session_state.shopping_list = [i for i in st.session_state.shopping_list if not st.session_state.bought_items.get(i, False)]
                st.session_state.bought_items = {i: False for i in st.session_state.shopping_list}
                st.rerun()
        with col2:
            if st.button("🗑️ Tout vider", use_container_width=True):
                st.session_state.shopping_list = []
                st.session_state.bought_items = {}
                st.rerun()
        st.write("---")
        for item in st.session_state.shopping_list:
            is_checked = st.session_state.bought_items.get(item, False)
            if st.checkbox(f"{item}", value=is_checked, key=f"shop_{item}"):
                st.session_state.bought_items[item] = True
            else:
                st.session_state.bought_items[item] = False

# 6. PAGE : AJOUTER
elif st.session_state.page == "ajouter":
    st.title("➕ Ajouter une recette")
    with st.form("form_add"):
        t = st.text_input("Nom du plat")
        d = st.date_input("Date prévue", datetime.now())
        i = st.text_input("Lien Image (URL)")
        ing = st.text_area("Ingrédients")
        pre = st.text_area("Préparation")
        if st.form_submit_button("🚀 Enregistrer"):
            if t:
                data = {"titre":t, "date":d.strftime("%d/%m/%Y"), "image":i, "ingredients":ing, "preparation":pre}
                requests.post(URL_SCRIPT, json=data)
                st.success("Enregistré !")

# 7. PAGE : ACCUEIL (LA GRILLE PARFAITE)
else:
    st.title("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV)
        # Nettoyage des données pour éviter les blocs vides
        df = df[df['Titre'].notna() & (df['Titre'].str.strip() != "")]
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
        
        cols = st.columns(3)
        for idx, (_, row) in enumerate(df.iterrows()):
            with cols[idx % 3]:
                with st.container(border=True):
                    # Correction de la syntaxe de la ligne 141
                    img_url = str(row['Image']) if str(row['Image']).startswith("http") else "https://via.placeholder.com/200"
                    st.image(img_url, use_container_width=True)
                    
                    st.markdown(f"### {row['Titre']}")
                    if pd.not
