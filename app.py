import streamlit as st
import requests
import pandas as pd

# 1. Configuration de la page (Look Large)
st.set_page_config(page_title="Livre de Recettes Numérique", page_icon="👩‍🍳", layout="wide")

# 2. Le Design (CSS) pour créer les cartes blanches comme sur ton image
st.markdown("""
    <style>
    .recipe-card {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 1px solid #f0f2f6;
    }
    .recipe-title {
        font-size: 18px;
        font-weight: bold;
        color: #1f2937;
        margin-top: 10px;
    }
    .stButton>button {
        width: 100%;
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TES LIENS ---
URL_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"
URL_CSV_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"

st.title("👩‍🍳 Mon Livre de Recettes Numérique")

# Menu latéral
menu = st.sidebar.radio("Navigation", ["📚 Ma Bibliothèque", "➕ Ajouter une recette"])

if menu == "➕ Ajouter une recette":
    st.subheader("📝 Ajouter une nouvelle fiche")
    with st.form("new_recipe", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            titre = st.text_input("Nom du plat *")
            source = st.text_input("Lien ou Source")
            img_url = st.text_input("URL de l'image (Lien direct)")
        with col2:
            date_p = st.date_input("Planifier pour le", value=None)
            ing = st.text_area("Ingrédients")
        prep = st.text_area("Préparation")
        
        if st.form_submit_button("🚀 Enregistrer dans le livre"):
            if titre:
                payload = {"titre": titre, "source": source, "ingredients": ing, "preparation": prep, "date_prevue": str(date_p) if date_p else "", "image": img_url}
                requests.post(URL_GOOGLE_SCRIPT, json=payload)
                st.success("C'est ajouté ! Rafraîchis la bibliothèque dans 2 min.")
                st.balloons()

else:
    st.subheader("🍱 Mes Recettes")
    try:
        df = pd.read_csv(URL_CSV_SHEETS)
        recherche = st.text_input("🔍 Rechercher une recette...")
        
        if recherche:
            df = df[df.iloc[:, 1].str.contains(recherche, case=False, na=False)]

        # --- GRILLE DE 3 COLONNES ---
        cols = st.columns(3)
        for index, row in df.iterrows():
            with cols[index % 3]:
                # On crée la carte
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                
                # Image (Colonne G = Index 6)
                image_link = row.iloc[6] if len(row) > 6 else ""
                if pd.notna(image_link) and str(image_link).startswith("http"):
                    st.image(image_link, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x200?text=Pas+d'image", use_container_width=True)
                
                st.markdown(f'<div class="recipe-title">{row.iloc[1]}</div>', unsafe_allow_html=True)
                
                # Bouton de détails
                if st.button("Voir les détails", key=f"btn_{index}"):
                    st.info(f"**Ingrédients :**\n{row.iloc[3]}")
                    st.warning(f"**Préparation :**\n{row.iloc[4]}")
                
                st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.error("Connexion au livre en cours...")
