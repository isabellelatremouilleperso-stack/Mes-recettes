import streamlit as st
import requests
import pandas as pd

# 1. Config
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
    .recipe-title-card {
        font-size: 18px;
        font-weight: bold;
        margin: 10px 0px;
    }
    .fiche-titre {
        color: #1f2937;
        font-size: 40px;
        font-weight: 800;
    }
    .badge-date {
        background-color: #3b82f6;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION ---
URL_CSV_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# Gestion de la mémoire de l'application
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None

# --- FONCTIONS DE NAVIGATION ---
def voir_fiche(row):
    st.session_state.selected_recipe = row
    st.session_state.page = "details"

def retour_accueil():
    st.session_state.page = "home"
    st.session_state.selected_recipe = None

# --- BARRE LATÉRALE ---
st.sidebar.title("Menu")
if st.sidebar.button("📚 Ma Bibliothèque"):
    retour_accueil()
    st.rerun()

if st.sidebar.button("➕ Ajouter une recette"):
    st.session_state.page = "ajouter"
    st.rerun()

# --- LOGIQUE D'AFFICHAGE ---

# 1. PAGE DÉTAILS (Le beau visuel)
if st.session_state.page == "details" and st.session_state.selected_recipe is not None:
    row = st.session_state.selected_recipe
    
    if st.button("⬅️ Retour"):
        retour_accueil()
        st.rerun()

    col_img, col_info = st.columns([1, 1])
    
    with col_img:
        img_link = row.iloc[6] if len(row) > 6 else ""
        if pd.notna(img_link) and str(img_link).startswith("http"):
            st.image(img_link, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/500x400?text=Image+non+disponible")

    with col_info:
        st.markdown(f"<div class='fiche-titre'>{row.iloc[1]}</div>", unsafe_allow_html=True)
        if pd.notna(row.iloc[2]) and str(row.iloc[2]).startswith("http"):
            st.link_button("🌐 Voir la source originale", row.iloc[2])
        
        st.write("---")
        st.markdown(f"<span class='badge-date'>📅 Prévue le : {row.iloc[5]}</span>", unsafe_allow_html=True)
        
        st.subheader("🛒 Ingrédients")
        st.write(row.iloc[3])

    st.write("---")
    st.subheader("👨‍🍳 Préparation")
    st.info(row.iloc[4])

# 2. PAGE AJOUTER
elif st.session_state.page == "ajouter":
    st.subheader("📝 Créer une nouvelle fiche")
    with st.form("form_add", clear_on_submit=True):
        t = st.text_input("Nom du plat")
        s = st.text_input("Lien source")
        i = st.text_input("URL de l'image")
        d = st.date_input("Date")
        ing = st.text_area("Ingrédients")
        pre = st.text_area("Préparation")
        if st.form_submit_button("Enregistrer"):
            payload = {"titre": t, "source": s, "ingredients": ing, "preparation": pre, "date_prevue": str(d), "image": i}
            requests.post(URL_GOOGLE_SCRIPT, json=payload)
            st.success("Réussi !")

# 3. PAGE ACCUEIL (Bibliothèque)
else:
    st.title("👩‍🍳 Ma Bibliothèque Numérique")
    try:
        df = pd.read_csv(URL_CSV_SHEETS)
        
        # Barre de recherche
        recherche = st.text_input
st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error("Synchronisation avec Google Sheets en cours... Patience !")
