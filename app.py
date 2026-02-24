import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION
st.set_page_config(page_title="Mon Livre de Recettes", layout="wide")

# Liens
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# 2. MÉMOIRE
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

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
if st.session_state.page == "details" and st.session_state.recipe_data is not None:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    
    st.header(f"🍳 {res['Titre']}")
    if pd.notna(res['Date']):
        st.write(f"📅 *Prévu pour le : {res['Date']}*")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🛒 Ingrédients manquants ?")
        choix_utilisateur = []
        ingredients_bruts = str(res['Ingrédients']).split('\n')
        for ing in ingredients_bruts:
            if ing.strip():
                if st.checkbox(ing.strip(), key=f"select_{ing.strip()}"):
                    choix_utilisateur.append(ing.strip())
        
        if st.button("🛒 Ajouter la sélection", type="primary"):
            if choix_utilisateur:
                for item in choix_utilisateur:
                    if item not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(item)
                st.toast("Ajouté !")
            else:
                st.warning("Cochez au moins un ingrédient.")
    
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
        if st.button("🗑️ Vider toute la liste"):
            st.session_state.shopping_list = []
            st.rerun()
        for i, article in enumerate(st.session_state.shopping_list):
            st.checkbox(article, key=f"final_{i}")

# 6. PAGE : AJOUTER (AVEC LE CHAMP DATE REPRÉSENTÉ)
elif st.session_state.page == "ajouter":
    st.title("➕ Nouvelle Recette")
    with st.form("form_add"):
        t = st.text_input("Nom du plat")
        d = st.date_input("Date prévue", datetime.now()) # LE CHAMP DATE EST ICI
        i = st.text_input("Lien de l'image (URL)")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Préparation")
        
        if st.form_submit_button("🚀 Enregistrer"):
            if t:
                # On envoie la date formatée en texte vers Google Sheets
                data_to_send = {
                    "titre": t, 
                    "date": d.strftime("%d/%m/%Y"), 
                    "image": i, 
                    "ingredients": ing, 
                    "preparation": pre
                }
                try:
                    requests.post(URL_SCRIPT, json=data_to_send)
                    st.success("Recette enregistrée avec la date ! 🎉")
                except:
                    st.error("Erreur de connexion.")
            else:
                st.error("Le nom du plat est obligatoire.")

# 7. PAGE : ACCUEIL
else:
    st.title("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
        
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    img_url = row['Image'] if str(row['Image']).startswith("http") else "https://via.placeholder.com/200"
                    st.image(img_url, use_container_width=True)
                    st.subheader(row['Titre'])
                    if pd.notna(row['Date']):
                        st.caption(f"📅 {row['Date']}")
                    
                    if st.button("Voir la fiche", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except Exception as e:
        st.error("⚠️ Erreur de chargement.")
