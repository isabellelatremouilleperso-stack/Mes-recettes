import streamlit as st
import requests
import pandas as pd

# Configuration de la page
st.set_page_config(page_title="Mon Grimoire", page_icon="👩‍🍳", layout="wide")

# --- CONFIGURATION ---
# REMPLACE PAR TON NOUVEAU LIEN /EXEC CI-DESSOUS
URL_GOOGLE = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

st.title("🧙‍♀️ Mon Grimoire Numérique")

# --- NAVIGATION ---
menu = ["Ajouter une recette", "Voir mes recettes"]
choix = st.sidebar.selectbox("Menu", menu)

if choix == "Ajouter une recette":
    st.subheader("📝 Nouvelle Recette")
    
    with st.form("form_recette", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            titre = st.text_input("Nom du plat *")
            source = st.text_input("Source (Lien ou livre)")
        with col2:
            date_plan = st.date_input("Planifier pour le (Calendrier)", value=None)
            
        ingredients = st.text_area("Ingrédients (un par ligne)")
        preparation = st.text_area("Étapes de préparation")
        
        submit = st.form_submit_button("✨ Sauvegarder dans mon Grimoire")
        
        if submit:
            if titre:
                payload = {
                    "titre": titre,
                    "source": source,
                    "ingredients": ingredients,
                    "preparation": preparation,
                    "date_prevue": str(date_plan) if date_plan else ""
                }
                res = requests.post(URL_GOOGLE, json=payload)
                if res.status_code == 200:
                    st.success(f"Bravo ! '{titre}' est enregistré.")
                    st.balloons()
                else:
                    st.error("Erreur de connexion.")
            else:
                st.warning("Donne au moins un nom à ton plat !")

elif choix == "Voir mes recettes":
    st.subheader("🔍 Bibliothèque de saveurs")
    # Note : Pour afficher les données ici, il faudrait lire le CSV ou le lien JSON du Sheets.
    # Pour l'instant, on se concentre sur l'envoi réussi.
    st.info("Consulte ton Google Sheets pour voir ta liste complète !")



