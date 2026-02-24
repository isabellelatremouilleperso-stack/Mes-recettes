import streamlit as st
import requests
import pandas as pd

# 1. CONFIGURATION (On laisse Streamlit gérer le thème pour éviter les bugs)
st.set_page_config(page_title="Livre de Recettes", layout="wide")

# Liens vérifiés
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# 2. MÉMOIRE
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None

# 3. BARRE LATÉRALE (Simple et propre)
with st.sidebar:
    st.title("👩‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("➕ Ajouter une recette", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()

# 4. PAGE : DÉTAILS
if st.session_state.page == "details" and st.session_state.recipe_data is not None:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    
    st.header(f"🍳 {res['Titre']}")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🛒 Ingrédients")
        # Affichage propre en liste
        for item in str(res['Ingrédients']).split('\n'):
            if item.strip():
                st.write(f"• {item.strip()}")
    
    with col2:
        if str(res['Image']).startswith("http"):
            st.image(res['Image'], caption=res['Titre'], use_container_width=True)
    
    st.subheader("👨‍🍳 Préparation")
    st.info(res['Préparation'])

# 5. PAGE : AJOUTER
elif st.session_state.page == "ajouter":
    st.title("➕ Nouvelle Recette")
    with st.form("form_v3"):
        t = st.text_input("Nom du plat")
        i = st.text_input("Lien de l'image")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Préparation")
        submit = st.form_submit_button("🚀 Enregistrer")
        
        if submit:
            if t:
                requests.post(URL_SCRIPT, json={"titre":t, "image":i, "ingredients":ing, "preparation":pre})
                st.success("Enregistré ! Rafraîchissez la bibliothèque dans une minute.")
            else:
                st.error("Le nom est obligatoire.")

# 6. PAGE : ACCUEIL
else:
    st.title("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV)
        # On force les noms de colonnes
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
        
        # On affiche sous forme de grille propre
        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                # Une boîte simple pour chaque recette
                with st.container(border=True):
                    img_url = row['Image'] if str(row['Image']).startswith("http") else "https://via.placeholder.com/200"
                    st.image(img_url, use_container_width=True)
                    st.subheader(row['Titre'])
                    if st.button("Voir la fiche", key=f"btn_{idx}"):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except Exception as e:
        st.error("⚠️ Impossible de charger les recettes.")
        st.write("Vérifiez la publication du Google Sheets.")
