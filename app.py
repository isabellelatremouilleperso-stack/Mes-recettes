import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ==============================
# CONFIGURATION & STYLE (BLANC & NOIR)
# ==============================
st.set_page_config(page_title="Mon Livre de Recettes", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: white !important; }
    section[data-testid="stSidebar"] { background-color: white !important; border-right: 1px solid #eee; }
    
    /* Force le texte en noir partout pour la visibilité */
    .stApp p, .stApp div, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3 {
        color: black !important;
    }
    
    /* Style des cartes de recettes */
    .recipe-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        background-color: #f9f9f9;
    }
    </style>
    """, unsafe_allow_html=True)

# Liens
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# MÉMOIRE
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# ==============================
# MENU LATÉRAL
# ==============================
with st.sidebar:
    st.title("👩‍🍳 Menu")
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

# ==============================
# PAGE : DÉTAILS (AVEC SÉLECTION)
# ==============================
if st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    
    st.header(f"🍳 {res['Titre']}")
    if pd.notna(res['Date']): st.info(f"📅 Prévu le : {res['Date']}")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🛒 Ingrédients manquants ?")
        
        # Le bouton est placé en haut pour être visible de suite
        choix_utilisateur = []
        ingredients_bruts = str(res['Ingrédients']).split('\n')
        
        # Bouton d'ajout
        if st.button("✅ Ajouter les articles cochés", type="primary"):
            if choix_utilisateur:
                for item in choix_utilisateur:
                    if item not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(item)
                st.toast("Ajouté à la liste !")
            else:
                st.warning("Cochez des articles d'abord !")

        # Liste des cases à cocher
        for ing in ingredients_bruts:
            if ing.strip():
                if st.checkbox(ing.strip(), key=f"sel_{ing.strip()}"):
                    choix_utilisateur.append(ing.strip())
    
    with col2:
        if str(res['Image']).startswith("http"):
            st.image(res['Image'], use_container_width=True)
        st.subheader("👨‍🍳 Préparation")
        st.write(res['Préparation'])

# ==============================
# PAGE : LISTE D'ÉPICERIE (MAGASIN)
# ==============================
elif st.session_state.page == "shopping":
    st.title("🛒 Ma Liste d'Épicerie")
    st.write("Cochez les articles au magasin pour les barrer de votre liste.")
    
    if not st.session_state.shopping_list:
        st.info("Votre liste est vide.")
    else:
        if st.button("🗑️ Vider toute la liste"):
            st.session_state.shopping_list = []
            st.rerun()
        
        st.write("---")
        # Ici on crée la liste interactive pour le magasin
        for i, article in enumerate(st.session_state.shopping_list):
            st.checkbox(f"{article}", key=f"shop_{i}_{article}")

# ==============================
# PAGE : AJOUTER (AVEC DATE)
# ==============================
elif st.session_state.page == "ajouter":
    st.title("➕ Ajouter une recette")
    with st.form("form_add"):
        t = st.text_input("Nom du plat")
        d = st.date_input("Date", datetime.now())
        i = st.text_input("Lien Image (URL)")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Préparation")
        if st.form_submit_button("🚀 Enregistrer"):
            if t:
                data = {"titre":t, "date":d.strftime("%d/%m/%Y"), "image":i, "ingredients":ing, "preparation":pre}
                requests.post(URL_SCRIPT, json=data)
                st.success("C'est enregistré ! 🎉")

# ==============================
# PAGE : ACCUEIL
# ==============================
else:
    st.title("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    img = row['Image'] if str(row['Image']).startswith("http") else "https://via.placeholder.com/200"
                    st.image(img, use_container_width=True)
                    st.subheader(row['Titre'])
                    if st.button("Voir la fiche", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except:
        st.error("Erreur de connexion au livre.")
