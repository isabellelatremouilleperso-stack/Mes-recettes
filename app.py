import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup
import urllib.parse

# ======================================================
# 1. CONFIGURATION & DESIGN
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

# CSS global
st.markdown("""
<style>
    /* Fond général */
    .stApp { background-color: #0e1117; color: #e0e0e0; }

    /* Titres */
    h1, h2, h3 { color: #e67e22 !important; }

    /* Sidebar stylisée */
    [data-testid="stSidebar"] { background-color: #1e2129; color: white; }
    [data-testid="stSidebar"] .css-1d391kg { color: white; }

    /* Boutons et input */
    input, select, textarea, div[data-baseweb="select"] { color: white !important; background-color: #1e2129 !important; }
    .stButton button { background-color: #e67e22; color: white; }

    /* Liste d'épicerie et checkboxes */
    .stCheckbox label p { color: white !important; font-size: 1.1rem !important; font-weight: 500 !important; }

    /* Cartes recettes */
    .recipe-card {
        background-color: #1e2129; border: 1px solid #3d4455;
        border-radius: 12px; padding: 10px; height: 230px; 
        display: flex; flex-direction: column; justify-content: space-between;
    }
    .recipe-img { width: 100%; height: 130px; object-fit: cover; border-radius: 8px; }
    .recipe-title {
        color: white; margin-top: 8px; font-size: 0.95rem; font-weight: bold;
        text-align: center; display: flex; align-items: center; justify-content: center;
        height: 2.5em; line-height: 1.2;
    }

    /* Boîtes Aide */
    .help-box {
        background-color: #1e2130; padding: 15px;
        border-radius: 15px; border-left: 5px solid #e67e22; margin-bottom: 20px;
    }
    .help-box h3 { color: #e67e22; margin-top: 0; }

    /* Playstore */
    .playstore-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; width: 100%; margin-bottom: 20px; }
    .logo-rond-centre { width: 120px !important; height: 120px !important; border-radius: 50% !important; object-fit: cover; border: 4px solid #e67e22; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 2. CONSTANTES
# ======================================================
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 3. FONCTIONS
# ======================================================
def send_action(payload):
    with st.spinner("🚀 Action..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear(); time.sleep(0.5); return True
        except: pass
    return False

def scrape_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "Recette Importée"
        elements = soup.find_all(['li', 'p'])
        content = "\n".join(dict.fromkeys([el.text.strip() for el in elements if 10 < len(el.text.strip()) < 500]))
        return title, content
    except: return None, None

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        cols = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires','Note']
        df.columns = cols[:len(df.columns)]
        return df
    except: return pd.DataFrame()

# ======================================================
# 4. SESSION
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"

# ======================================================
# 5. SIDEBAR
# ======================================================
with st.sidebar:
    st.image("https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png", width=100)
    st.title("🍳 Mes Recettes")

    if st.button("📚 Bibliothèque", use_container_width=True, key="side_home"): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning Repas", use_container_width=True, key="side_plan"): st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Ma Liste d'épicerie", use_container_width=True, key="side_shop"): st.session_state.page = "shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER RECETTE", use_container_width=True, key="side_add"): st.session_state.page = "add"; st.rerun()
    if st.button("⭐ Play Store", use_container_width=True, key="side_play"): st.session_state.page = "playstore"; st.rerun()
    if st.button("❓ Aide", use_container_width=True, key="side_help"): st.session_state.page = "help"; st.rerun()

# ======================================================
# 6. PAGES
# ======================================================

# Ici tu peux continuer à copier le code complet des pages:
# - Home / Bibliothèque
# - Détails recette
# - Ajouter recette (URL / Vidéo / Vrac)
# - Épicerie
# - Planning
# - Play Store
# - Aide complète (celle que tu as validée)

# Je peux te fournir **la suite complète avec toutes les pages intégrées**, si tu veux que je fasse **le fichier entier prêt à lancer**.
