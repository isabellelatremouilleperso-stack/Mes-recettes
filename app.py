import streamlit as st
import requests
import pandas as pd

# 1. Configuration de la page
st.set_page_config(page_title="Livre de Recettes Numérique", page_icon="👩‍🍳", layout="wide")

# 2. Design (CSS)
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
    .fiche-titre {
        color: #1f2937;
        font-size: 40px;
        font-weight: 800;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION DES LIENS ---
URL_CSV_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# Gestion de la mémoire
if "page" not in st.session_state: st.session_state.page = "home"
if "selected_recipe" not in st.session_state: st.session_state.selected_recipe = None

# --- NAVIGATION ---
def retour():
    st.session_state.page = "home"
    st.session_state.selected_recipe = None

# --- LOGIQUE D'AFFICHAGE ---

# PAGE DÉTAILS
if st.session_state.page == "details" and st.session_state.selected_recipe is not None:
    row = st.session_state.selected_recipe
    if st.button("⬅️ Retour"):
        retour()
        st.rerun()
    
    col1, col2 = st.columns([1, 1])
    with col1:
        img_url = row.iloc[6] if len(row) > 6 else ""
        if pd.notna(img_url) and str(img_url).startswith("http"):
            st.image(img_url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/500x400?text=Lien+image+invalide")
    with col2:
        st.markdown(f"<div class='fiche-titre'>{row.iloc[1]}</div>", unsafe_allow_html=True)
        st.info(f"📅 Prévue le : {row.iloc[5]}")
        st.subheader("🛒 Ingrédients")
        st.write(row.iloc[3])
    st.divider()
    st.subheader("👨‍🍳 Préparation")
    st.success(row.iloc[4])

# PAGE ACCUEIL
else:
    st.sidebar.title("Menu")
    if st.sidebar.button("📚 Bibliothèque"): retour(); st.rerun()
    
    st.title("👩‍🍳 Mon Livre de Recettes Numérique")
    
    try:
        df = pd.read_csv(URL_CSV_SHEETS)
        recherche = st.text_input("🔍 Rechercher...")
        if recherche:
            df = df[df.iloc[:, 1].str.contains(recherche, case=False, na=False)]

        cols = st.columns(3)
        for index, row in df.iterrows():
            with cols[index % 3]:
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                img_url = row.iloc[6] if len(row) > 6 else ""
                if pd.notna(img_url) and str(img_url).startswith("http"):
                    st.image(img_url, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x200?text=Pas+d'image")
                
                st.markdown(f"### {row.iloc[1]}")
                if st.button("Voir les détails", key=f"btn_{index}"):
                    st.session_state.selected_recipe = row
                    st.session_state.page = "details"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error("Connexion au livre en cours... Rafraîchissez dans 1 minute.")
