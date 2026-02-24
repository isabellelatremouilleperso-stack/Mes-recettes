import streamlit as st
import requests
import pandas as pd

# Config de la page
st.set_page_config(page_title="Mon Grimoire", page_icon="👩‍🍳", layout="wide")

# --- CONFIGURATION ---
# Ton lien Google Script (déjà à jour)
URL_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# !!! COLLE TON LIEN CSV ICI ENTRE LES GUILLEMETS !!!
URL_CSV_SHEETS = "TON_LIEN_CSV_PUBLIÉ_SUR_LE_WEB" 

st.title("🧙‍♀️ Mon Grimoire Numérique")

# Menu latéral (On ajoute "Ma Bibliothèque")
menu = st.sidebar.radio("Navigation", ["Ajouter une recette", "Ma Bibliothèque"])

if menu == "Ajouter une recette":
    st.subheader("📝 Nouvelle Recette")
    with st.form("form_recette", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            titre = st.text_input("Nom du plat *")
            source = st.text_input("Lien ou Source")
        with col2:
            date_plan = st.date_input("Planifier pour le (Calendrier)", value=None)
            
        ingredients = st.text_area("Ingrédients")
        preparation = st.text_area("Étapes de préparation")
        
        submit = st.form_submit_button("✨ Sauvegarder et Planifier")
        
        if submit and titre:
            payload = {
                "titre": titre, "source": source, "ingredients": ingredients,
                "preparation": preparation, "date_prevue": str(date_plan) if date_plan else ""
            }
            try:
                requests.post(URL_GOOGLE_SCRIPT, json=payload)
                st.success(f"'{titre}' ajouté avec succès !")
                st.balloons()
            except:
                st.error("Erreur de connexion avec Google.")

elif menu == "Ma Bibliothèque":
    st.subheader("📚 Consulter mes recettes")
    
    if URL_CSV_SHEETS == "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv":
        st.warning("⚠️ Tu dois encore coller ton lien CSV dans le code sur GitHub pour voir tes recettes !")
    else:
        try:
            # On lit le Sheets
            df = pd.read_csv(URL_CSV_SHEETS)
            
            # Barre de recherche
            recherche = st.text_input("🔍 Rechercher un plat ou un ingrédient...")
            
            if recherche:
                # On cherche dans la colonne Titre (index 1) et Ingrédients (index 3)
                mask = df.iloc[:, 1].str.contains(recherche, case=False, na=False) | \
                       df.iloc[:, 3].str.contains(recherche, case=False, na=False)
                df_to_show = df[mask]
            else:
                df_to_show = df

            # Affichage sous forme de jolies cartes
            for index, row in df_to_show.iterrows():
                with st.expander(f"🍴 {row.iloc[1]}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**📋 Ingrédients :**")
                        st.write(row.iloc[3])
                    with c2:
                        st.markdown("**👨‍🍳 Préparation :**")
                        st.write(row.iloc[4])
                    if pd.notset(row.iloc[2]):
                        st.caption(f"Source : {row.iloc[2]}")
        except Exception as e:
            st.error("Erreur de lecture. Vérifie que ton Sheets est bien 'Publié sur le web' en format CSV.")
