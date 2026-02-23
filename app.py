import streamlit as st
import requests
import json
from datetime import datetime

st.set_page_config(page_title="Mon Grimoire Cuisine", page_icon="📖")
st.title("📖 Mon Grimoire de Recettes Perso")

# --- TON URL ICI ---
URL_GOOGLE = "https://script.google.com/macros/s/AKfycbyNPr1duyUQVBfpLrC9qIcqv8M6pW6ptjdZaYYoFCzfpaKllLGBY3SGSqs7ccUS75L_/exec"

# Saisie des informations
titre = st.text_input("Nom de la recette :")
lien_source = st.text_input("🔗 Lien de la source (optionnel) :", placeholder="https://...")

col_gauche, col_droite = st.columns(2)
with col_gauche:
    ingredients_bruts = st.text_area("🛒 Ingrédients :", height=200)
with col_droite:
    etapes_brutes = st.text_area("📝 Étapes :", height=200)

if st.button("✨ Sauvegarder la recette"):
    if titre:
        date_aujourdhui = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # --- ENVOI GOOGLE SHEETS ---
        try:
            donnees = {
                "date": date_aujourdhui,
                "titre": titre,
                "source": lien_source,
                "ingredients": ingredients_bruts,
                "preparation": etapes_brutes
            }
            requests.post(URL_GOOGLE, data=json.dumps(donnees))
            st.success(f"✅ Ajouté le {date_aujourdhui} !")
            st.balloons()
        except Exception as e:
            st.error(f"Erreur : {e}")
    else:
        st.warning("Donnez un titre !")