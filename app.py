import streamlit as st
import requests
import pandas as pd

# Config de la page
st.set_page_config(page_title="Livre de recettes", page_icon="👩‍🍳", layout="wide")

# --- CONFIGURATION ---
URL_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"
URL_CSV_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"

st.title("👩‍🍳 Mon Livre de Recettes Numérique")

# Menu latéral
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
                st.success(f"'{titre}' a été ajouté à ton livre !")
                st.balloons()
            except:
                st.error("Erreur de connexion avec Google.")

elif menu == "Ma Bibliothèque":
    st.subheader("📚 Consulter mes recettes")
    
    try:
        # Lecture du Sheets via ton lien CSV
        df = pd.read_csv(URL_CSV_SHEETS)
        
        # Barre de recherche
        recherche = st.text_input("🔍 Rechercher un plat ou un ingrédient...")
        
        if recherche:
            # Recherche dans les colonnes Titre (index 1) et Ingrédients (index 3)
            mask = df.iloc[:, 1].str.contains(recherche, case=False, na=False) | \
                   df.iloc[:, 3].str.contains(recherche, case=False, na=False)
            df_to_show = df[mask]
        else:
            df_to_show = df

        # Affichage des recettes
        if df_to_show.empty:
            st.info("Aucune recette trouvée.")
        else:
            for index, row in df_to_show.iterrows():
                # On utilise la colonne index 1 pour le titre
                with st.expander(f"🍴 {row.iloc[1]}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown("**📋 Ingrédients :**")
                        st.write(row.iloc[3] if pd.notna(row.iloc[3]) else "Non précisé")
                    with c2:
                        st.markdown("**👨‍🍳 Préparation :**")
                        st.write(row.iloc[4] if pd.notna(row.iloc[4]) else "Non précisé")
                    if pd.notna(row.iloc[2]):
                        st.caption(f"Source : {row.iloc[2]}")
    except Exception as e:
        st.error("Le livre est vide ou le lien est en cours de mise à jour par Google. Réessaie dans 1 minute.")
