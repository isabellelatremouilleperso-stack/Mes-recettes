import streamlit as st
import requests
import pandas as pd

# 1. Config
st.set_page_config(page_title="Livre de Recettes Numérique", page_icon="👩‍🍳", layout="wide")

# 2. Design Amélioré (CSS)
st.markdown("""
    <style>
    .recipe-card {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        text-align: center;
    }
    .main-img {
        border-radius: 15px;
        object-fit: cover;
        width: 100%;
        max-height: 400px;
    }
    .badge {
        background-color: #3b82f6;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION ---
URL_CSV_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# Gestion de la page active (Mémoire de l'appli)
if "recipe_selected" not in st.session_state:
    st.session_state.recipe_selected = None

# FONCTION POUR REVENIR À LA LISTE
def go_back():
    st.session_state.recipe_selected = None

# --- AFFICHAGE ---

# CAS 1 : On regarde les détails d'une recette précise
if st.session_state.recipe_selected is not None:
    row = st.session_state.recipe_selected
    if st.button("⬅️ Retour à la bibliothèque"):
        go_back()
        st.rerun()

    st.divider()
    
    col_img, col_info = st.columns([1, 1])
    
    with col_img:
        img_link = row.iloc[6] if len(row) > 6 else ""
        if pd.notna(img_link) and str(img_link).startswith("http"):
            st.image(img_link, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/500x400?text=Pas+d'image")

    with col_info:
        st.title(row.iloc[1])
        if pd.notna(row.iloc[2]):
            st.caption(f"🌐 Source : {row.iloc[2]}")
        
        st.markdown(f"<span class='badge'>📅 Prévue le : {row.iloc[5]}</span>", unsafe_allow_html=True)
        
        st.subheader("🛒 Ingrédients")
        st.write(row.iloc[3])

    st.subheader("👨‍🍳 Préparation")
    st.info(row.iloc[4])

# CAS 2 : On affiche la bibliothèque ou le formulaire
else:
    menu = st.sidebar.radio("Navigation", ["📚 Ma Bibliothèque", "➕ Ajouter une recette"])

    if menu == "➕ Ajouter une recette":
        st.subheader("📝 Nouvelle Fiche Recette")
        # ... (Ton formulaire reste le même ici)
        with st.form("new_recipe", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                titre = st.text_input("Nom du plat *")
                source = st.text_input("Lien ou Source")
                img_url = st.text_input("URL de l'image")
            with col2:
                date_p = st.date_input("Planifier pour le", value=None)
                ing = st.text_area("Ingrédients")
            prep = st.text_area("Préparation")
            if st.form_submit_button("🚀 Enregistrer"):
                if titre:
                    payload = {"titre": titre, "source": source, "ingredients": ing, "preparation": prep, "date_prevue": str(date_p) if date_p else "", "image": img_url}
                    requests.post(URL_GOOGLE_SCRIPT, json=payload)
                    st.success("Ajouté !")

    else:
        st.title("👩‍🍳 Mon Livre de Recettes")
        try:
            df = pd.read_csv(URL_CSV_SHEETS)
            recherche = st.text_input("🔍 Rechercher...")
            if recherche:
                df = df[df.iloc[:, 1].str.contains(recherche, case=False, na=False)]

            cols = st.columns(3)
            for index, row in df.iterrows():
                with cols[index % 3]:
                    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                    
                    img_link = row.iloc[6] if len(row) > 6 else ""
                    if pd.notna(img_link) and str(img_link).startswith("http"):
                        st.image(img_link, use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x200?text=Image")
                    
                    st.markdown(f"**{row.iloc[1]}**")
                    
                    if st.button("Voir la fiche complète", key=f"btn_{index}"):
                        st.session_state.recipe_selected = row
                        st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        except:
            st.error("Chargement du livre...")
