import streamlit as st
import requests
import pandas as pd

# 1. CONFIGURATION DE BASE (Sans fioritures pour éviter les bugs)
st.set_page_config(page_title="Mon Livre de Recettes", layout="wide")

# Liens (Vérifie qu'il n'y a pas d'espace caché au début ou à la fin)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# Initialisation de la mémoire
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None

# 2. BARRE LATÉRALE
with st.sidebar:
    st.title("👩‍🍳 Menu")
    if st.button("📚 Bibliothèque"):
        st.session_state.page = "home"
        st.rerun()
    if st.button("➕ Ajouter une recette"):
        st.session_state.page = "ajouter"
        st.rerun()

# 3. PAGE : DÉTAILS
if st.session_state.page == "details":
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    
    st.title(res['Titre'])
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛒 Ingrédients")
        st.write(res['Ingrédients'])
    with col2:
        if str(res['Image']).startswith("http"):
            st.image(res['Image'], use_container_width=True)
    
    st.subheader("👨‍🍳 Préparation")
    st.info(res['Préparation'])

# 4. PAGE : AJOUTER
elif st.session_state.page == "ajouter":
    st.title("➕ Ajouter")
    with st.form("add_form"):
        t = st.text_input("Nom du plat")
        i = st.text_input("Lien image")
        ing = st.text_area("Ingrédients")
        pre = st.text_area("Préparation")
        if st.form_submit_button("Enregistrer"):
            try:
                requests.post(URL_SCRIPT, json={"titre":t, "image":i, "ingredients":ing, "preparation":pre})
                st.success("Réussi ! Attendez 1 min que Google mette à jour le fichier.")
            except Exception as e:
                st.error(f"Erreur d'envoi : {e}")

# 5. PAGE : ACCUEIL (BIBLIOTHÈQUE)
else:
    st.title("📚 Ma Bibliothèque")
    try:
        # TENTATIVE DE LECTURE DU CSV
        df = pd.read_csv(URL_CSV)
        
        # On vérifie si le tableau est vide
        if df.empty:
            st.warning("Le fichier Google Sheets est vide.")
        else:
            # On définit les colonnes (IMPORTANT : vérifie l'ordre dans ton Sheets)
            # Si ton Sheets a moins de 7 colonnes, ça plantera ici.
            df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
            
            cols = st.columns(3)
            for index, row in df.iterrows():
                with cols[index % 3]:
                    st.container(border=True).write(f"**{row['Titre']}**")
                    if str(row['Image']).startswith("http"):
                        st.image(row['Image'], use_container_width=True)
                    if st.button("Voir la fiche", key=f"btn_{index}"):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except Exception as e:
        st.error("❌ ERREUR DE CONNEXION")
        st.write("Voici le détail technique de l'erreur :")
        st.code(e)
        st.info("💡 Vérifie que ton Google Sheets est bien : Fichier > Partager > Publier sur le web > Format CSV")
