import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION & DESIGN MODE SOMBRE
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    /* Force le fond noir sur toute l'application */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Cartes Bibliothèque style Sombre */
    .recipe-card-box {
        background-color: #1e2129;
        border-radius: 15px;
        padding: 0px;
        border: 1px solid #3d4455;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .recipe-img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 15px 15px 0 0;
    }
    .recipe-title-text {
        font-weight: 700;
        font-size: 1.1rem;
        color: #ffffff;
        padding: 15px;
        text-align: center;
        min-height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Boîtes d'Aide adaptées au fond noir */
    .help-box { 
        background-color: #262730; 
        color: #ffffff !important; 
        padding: 25px; 
        border-radius: 12px; 
        border-left: 10px solid #e67e22; 
        margin-bottom: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .help-box h3 { color: #e67e22 !important; font-weight: 700; }
    .help-box p { color: #e0e0e0 !important; }

    /* Inputs et Formulaires */
    div[data-baseweb="input"] { background-color: #262730 !important; }
</style>
""", unsafe_allow_html=True)

# --- CONFIG URLs ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

def load_data():
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= len(expected): df.columns = expected[:len(df.columns)]
        return df
    except: return pd.DataFrame()

# Session States
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "page" not in st.session_state: st.session_state.page = "home"

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True): 
        st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): 
        st.session_state.page = "planning"; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): 
        st.session_state.page = "shopping"; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter", use_container_width=True, type="primary"): 
        st.session_state.page = "add"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): 
        st.session_state.page = "aide"; st.rerun()

# ======================================================
# PAGE : BIBLIOTHÈQUE (MODE SOMBRE)
# ======================================================
if st.session_state.page ==
