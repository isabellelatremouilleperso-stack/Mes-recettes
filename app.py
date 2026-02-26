import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup
import re
import json

# ======================================================
# 1. CONFIGURATION & DESIGN GLOBAL
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }
    .stCheckbox label p { color: white !important; font-size: 1.1rem !important; }
    
    /* STYLE DE TON ONGLET PLAY STORE WOW */
    .store-card {
        background-color: #161b22;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 0 25px rgba(0,0,0,0.5);
        border: 1px solid #30363d;
    }
    .install-btn {
        background: linear-gradient(90deg, #00c853, #64dd17);
        color: white !important;
        padding: 12px 35px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        display: inline-block;
        text-decoration: none;
    }
    
    /* CARTES BIBLIOTHÈQUE */
    .recipe-card {
        background-color: #1e2129; border: 1px solid #3d4455;
        border-radius: 12px; padding: 10px; height: 250px; 
        display: flex; flex-direction: column; align-items: center;
    }
    .recipe-img { width: 100%; height: 140px; object-fit: cover; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Tes accès Google Sheets
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Dessert","Autre"]

# ======================================================
# 2. FONCTIONS TECHNIQUES (MOTEUR)
# ======================================================

def send_action(payload):
    try:
        r = requests.post(URL_SCRIPT, json=payload, timeout=20)
        if "Success" in r.text:
            st.cache_data.clear()
            return True
    except: pass
    return False

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        cols = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires','Note','Video']
        df.columns = cols[:len(df.columns)]
        return df
    except: return pd.DataFrame()

def ventiler_vrac(texte):
    data = {"ing": "", "prep": "", "t_prepa": "", "t_cuisson": "", "port": ""}
    lines = texte.split('\n')
    mode = "ing"
    for l in lines:
        l_low = l.lower()
        if "préparation" in l_low or "etapes" in l_low: mode = "prep"; continue
        if mode == "ing": data["ing"] += l + "\n"
        else: data["prep"] += l + "\n"
    return data

# ======================================================
# 3. NAVIGATION & LOGIQUE DE PAGES
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"

with st.sidebar:
    st.title("🍳 Menu")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"
    if st.button("📅 Planning", use_container_width=True): st.session_state.page = "planning"
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page = "shop"
    st.divider()
    if st.button("➕ AJOUTER", type="primary", use_container_width=True): st.session_state.page = "add"
    st.divider()
    if st.button("⭐ Play Store", use_container_width=True): st.session_state.page = "playstore"

# ======================================================
# 4. LE RESTE DU CODE (LES PAGES)
# ======================================================

# --- PAGE ACCUEIL / BIBLIOTHÈQUE ---
if st.session_state.page == "home":
    st.header("📚 Mes Recettes")
    df = load_data()
    if not df.empty:
        search = st.text_input("🔍 Rechercher une recette...")
        rows = df[df['Titre'].str.contains(search, case=False)]
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(rows):
                    r = rows.iloc[i+j]
                    with cols[j]:
                        img_url = r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img_url}" class="recipe-img"><br><b>{r["Titre"]}</b></div>', unsafe_allow_html=True)
                        if st.button("Ouvrir", key=f"open_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = r.to_dict(); st.session_state.page = "details"; st.rerun()

# --- PAGE DÉTAILS (AVEC NOTES ET ÉTOILES) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.title(f"🍳 {r['Titre']}")
    if r.get('Video'): st.video(r['Video'])
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        st.subheader("⭐ Ma Note")
        try: current_n = int(float(r.get('Note', 0)))
        except: current_n = 0
        note = st.slider("Étoiles", 0, 5, current_n)
        comm = st.text_area("Mes commentaires", value=str(r.get('Commentaires', "")))
        if st.button("💾 Enregistrer mon avis"):
            send_action({"action": "edit", "titre": r['Titre'], "Note": note, "Commentaires": comm})
            st.toast("Avis mis à jour !")
            
    with col2:
        st.subheader("🛒 Ingrédients")
        for ing in str(r['Ingrédients']).split('\n'):
            if ing.strip(): st.checkbox(ing, key=f"ing_{ing}")
        st.divider()
        st.subheader("📝 Préparation")
        st.write(r['Préparation'])

# --- PAGE AJOUTER (AVEC VENTILATION) ---
elif st.session_state.page == "add":
    st.header("➕ Nouvelle Recette")
    txt_vrac = st.text_area("Collez votre recette ici (Vrac)", height=200)
    if st.button("🧬 Ventiler Automatiquement"):
        st.session_state.ventilation = ventiler_vrac(txt_vrac)
    
    with st.form("add_form"):
        v = st.session_state.get('ventilation', {})
        f_titre = st.text_input("Titre", value="")
        f_ing = st.text_area("Ingrédients", value=v.get('ing', ""))
        f_prep = st.text_area("Préparation", value=v.get('prep', ""))
        f_img = st.text_input("Lien Image URL")
        f_vid = st.text_input("Lien Vidéo (YouTube/TikTok)")
        if st.form_submit_button("🚀 Sauvegarder dans Google Sheets"):
            payload = {"action": "add", "titre": f_titre, "ingredients": f_ing, "preparation": f_prep, "image": f_img, "video": f_vid, "date": datetime.now().strftime("%d/%m/%Y")}
            if send_action(payload): st.session_state.page = "home"; st.rerun()

# --- TON ONGLET PLAY STORE WOW ---
elif st.session_state.page == "playstore":
    st.markdown("<div class='store-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([1,3])
    with c1: st.image("https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png", width=140)
    with c2:
        st.markdown("## 🍳 Mes Recettes Pro")
        st.markdown("### 👩‍🍳 Isabelle Latrémouille")
        st.markdown("⭐ **4.9** (2 847 avis) | 📥 10 000+")
        st.markdown("<br><div class='install-btn'>Installer</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 📸 Aperçu")
    cA, cB, cC = st.columns(3)
    cA.image("https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg")
    cB.image("https://i.postimg.cc/YCkg460C/shared-image-(5).jpg")
    cC.image("https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg")
    st.markdown("</div>", unsafe_allow_html=True)

# --- PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning Repas")
    df = load_data()
    # Logique d'affichage par date simplifiée
    st.info("Sélectionnez une date dans la fiche d'une recette pour l'afficher ici.")
