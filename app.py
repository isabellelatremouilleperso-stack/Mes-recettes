import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ======================================================
# 1. DESIGN "WOW" & CONFIGURATION
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    [data-testid="stSidebar"] { background-color: #161b22; border-right: 1px solid #30363d; }
    
    /* STYLE CARTES RECETTES */
    .recipe-card {
        background: #21262d; border: 1px solid #30363d; border-radius: 15px;
        padding: 10px; transition: 0.3s; height: 260px; text-align: center;
    }
    .recipe-card:hover { border-color: #58a6ff; transform: translateY(-5px); }
    .recipe-img { width: 100%; height: 140px; object-fit: cover; border-radius: 10px; }

    /* STYLE PLAY STORE PREMIUM */
    .ps-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 40px; border-radius: 20px; border: 1px solid #334155; text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .ps-logo { width: 120px; border-radius: 25px; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
    .ps-badge { background: #1e293b; color: #58a6ff; padding: 5px 15px; border-radius: 20px; font-weight: bold; }
    .ps-install-btn {
        background: #00e676; color: #000 !important; font-weight: 800;
        padding: 15px 50px; border-radius: 30px; text-decoration: none;
        display: inline-block; font-size: 20px; margin: 20px 0;
    }
    .ps-screenshot { border-radius: 12px; border: 2px solid #30363d; width: 100%; }
</style>
""", unsafe_allow_html=True)

# Liens Sheets
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# ======================================================
# 2. FONCTIONS
# ======================================================

def action(p):
    try:
        r = requests.post(URL_SCRIPT, json=p, timeout=15)
        if "Success" in r.text: st.cache_data.clear(); return True
    except: pass
    return False

@st.cache_data(ttl=5)
def get_data(url):
    try:
        df = pd.read_csv(f"{url}&nocache={time.time()}").fillna('')
        if "gid=0" in url:
            df.columns = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires','Note','Video'][:len(df.columns)]
        return df
    except: return pd.DataFrame()

# ======================================================
# 3. NAVIGATION
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"

with st.sidebar:
    st.markdown("## 👨‍🍳 Menu Gourmet")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    st.divider()
    if st.button("⭐ Play Store Wow", use_container_width=True): st.session_state.page = "playstore"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): st.session_state.page = "help"; st.rerun()

# ======================================================
# 4. PAGES
# ======================================================

# --- PLAY STORE WOW (LE DESIGN QUE TU VOULAIS) ---
if st.session_state.page == "playstore":
    st.markdown("""
    <div class="ps-header">
        <img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" class="ps-logo">
        <h1 style="margin:10px 0;">Mes Recettes Pro</h1>
        <p style="color:#8b949e; font-size:18px;">Par Isabelle Latrémouille</p>
        <div style="margin:15px 0;">
            <span class="ps-badge">⭐ 4.9</span> &nbsp; <span class="ps-badge">📥 10k+</span> &nbsp; <span class="ps-badge">🥗 Santé</span>
        </div>
        <a href="#" class="ps-install-btn">INSTALLER</a>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    st.subheader("📸 Aperçu de l'application")
    cA, cB, cC = st.columns(3)
    cA.markdown('<img src="https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg" class="ps-screenshot">', unsafe_allow_html=True)
    cB.markdown('<img src="https://i.postimg.cc/YCkg460C/shared-image-(5).jpg" class="ps-screenshot">', unsafe_allow_html=True)
    cC.markdown('<img src="https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg" class="ps-screenshot">', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📝 À propos de cette application")
    st.write("Gérez vos recettes comme un chef ! Planification intelligente, liste d'épicerie automatique et interface élégante.")
    
    if st.button("⬅ Retour à la cuisine"): st.session_state.page = "home"; st.rerun()

# --- AIDE & ASTUCES ---
elif st.session_state.page == "help":
    st.header("❓ Besoin d'aide ?")
    with st.expander("🛒 Comment faire ma liste d'épicerie ?"):
        st.write("Ouvrez une recette, cochez les ingrédients manquants et cliquez sur 'Envoyer à l'épicerie'.")
    with st.expander("🗑️ Comment supprimer une recette ?"):
        st.write("Dans la fiche détaillée d'une recette, vous trouverez un bouton poubelle rouge en haut à droite.")
    with st.expander("📅 Où est mon planning ?"):
        st.write("Les recettes planifiées apparaissent dans l'onglet 'Planning' (bientôt disponible en vue calendrier complète).")
    
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste")
    df_s = get_data(URL_CSV_SHOP)
    if not df_s.empty:
        for idx, row in df_s.iterrows():
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"⬜ **{row.iloc[0]}**")
            if c2.button("🗑️", key=f"s_{idx}"):
                if action({"action": "delete_shop", "article": row.iloc[0]}): st.rerun()
        if st.button("🧹 Vider tout"):
            if action({"action": "clear_shop"}): st.rerun()
    else: st.info("Votre liste est vide.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- BIBLIOTHÈQUE (PAR DÉFAUT) ---
else:
    st.header("📚 Ma Bibliothèque")
    df = get_data(URL_CSV)
    if not df.empty:
        search = st.text_input("🔍 Rechercher...")
        filtered = df[df['Titre'].str.contains(search, case=False)]
        for i in range(0, len(filtered), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(filtered):
                    r = filtered.iloc[i+j]
                    with cols[j]:
                        img = r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><br><b>{r["Titre"]}</b></div>', unsafe_allow_html=True)
                        if st.button("Détails", key=f"d_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = r.to_dict(); st.session_state.page = "details"; st.rerun()
