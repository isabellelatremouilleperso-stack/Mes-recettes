import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
import re

# ======================================================
# 1. CONFIGURATION & DESIGN
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }
    .stCheckbox label p { color: white !important; font-size: 1.1rem !important; }
    .recipe-card {
        background-color: #1e2129; border: 1px solid #3d4455;
        border-radius: 12px; padding: 10px; height: 230px; 
        display: flex; flex-direction: column; align-items: center;
    }
    .recipe-img { width: 100%; height: 130px; object-fit: cover; border-radius: 8px; }
    .store-card {
        background-color: #161b22; padding: 30px; border-radius: 20px;
        box-shadow: 0 0 25px rgba(0,0,0,0.5); border: 1px solid #30363d;
    }
    .install-btn {
        background: linear-gradient(90deg, #00c853, #64dd17);
        color: white !important; padding: 12px 35px; border-radius: 12px;
        font-size: 18px; font-weight: bold; text-align: center; display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Tes URLs Google Sheets
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# ======================================================
# 2. FONCTIONS TECHNIQUES
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
def load_data(url):
    try:
        df = pd.read_csv(f"{url}&nocache={time.time()}").fillna('')
        return df
    except: return pd.DataFrame()

# ======================================================
# 3. NAVIGATION
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"

with st.sidebar:
    st.title("👨‍🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    st.divider()
    if st.button("⭐ Play Store Wow", use_container_width=True): st.session_state.page = "playstore"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): st.session_state.page = "help"; st.rerun()

# ======================================================
# 4. PAGES
# ======================================================

# --- BIBLIOTHÈQUE ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data(URL_CSV)
    if not df.empty:
        search = st.text_input("🔍 Rechercher...")
        rows = df[df.iloc[:,1].str.contains(search, case=False)]
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(rows):
                    r = rows.iloc[i+j]
                    with cols[j]:
                        img = r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><b>{r.iloc[1]}</b></div>', unsafe_allow_html=True)
                        if st.button("Ouvrir", key=f"o_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = r.to_dict(); st.session_state.page = "details"; st.rerun()

# --- DÉTAILS (ÉDITION / SUPPRESSION / ENVOI ÉPICERIE) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    c1, c2, c3 = st.columns([2,1,1])
    if c1.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    if c3.button("🗑️ Supprimer"):
        if send_action({"action": "delete", "titre": r.iloc[1]}): st.session_state.page = "home"; st.rerun()

    with st.form("edit"):
        colL, colR = st.columns([1, 1.2])
        with colL:
            st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
            n_note = st.slider("Note", 0, 5, int(float(r.get('Note', 0) or 0)))
            n_comm = st.text_area("Notes perso", value=r.get('Commentaires', ""))
            d_plan = st.date_input("Planifier")
        with colR:
            st.subheader("🛒 Ingrédients")
            # Système de sélection pour l'épicerie
            ings = [l.strip() for l in str(r.iloc[3]).split('\n') if l.strip()]
            to_shop = []
            for i, ing in enumerate(ings):
                if st.checkbox(ing, key=f"ing_{i}"): to_shop.append(ing)
            
            if st.form_submit_button("💾 Sauver & 📥 Épicerie"):
                # Sauvegarde recette
                send_action({"action": "edit", "titre": r.iloc[1], "Note": n_note, "Commentaires": n_comm, "Date_Prevue": d_plan.strftime("%Y-%m-%d")})
                # Envoi à l'épicerie
                for item in to_shop: send_action({"action": "add_shop", "article": item})
                st.success("Modifications et liste d'épicerie mises à jour !"); st.rerun()
        
        st.subheader("📝 Préparation")
        st.write(r.iloc[4])

# --- 🛒 PAGE ÉPICERIE (RESTAURÉE) ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    df_shop = load_data(URL_CSV_SHOP)
    if not df_shop.empty:
        for idx, row in df_shop.iterrows():
            col_item, col_btn = st.columns([4, 1])
            col_item.write(f"⬜ {row.iloc[0]}")
            if col_btn.button("🗑️", key=f"del_shop_{idx}"):
                if send_action({"action": "delete_shop", "article": row.iloc[0]}): st.rerun()
        if st.button("🧹 Tout effacer"):
            if send_action({"action": "clear_shop"}): st.rerun()
    else:
        st.info("Ta liste est vide !")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- ❓ PAGE AIDE (RESTAURÉE) ---
elif st.session_state.page == "help":
    st.header("❓ Aide & Astuces")
    st.markdown("""
    ### Comment ça marche ?
    1. **Bibliothèque** : Clique sur une recette pour voir les détails.
    2. **Édition** : Dans la fiche, tu peux changer la note, le planning ou les ingrédients.
    3. **Épicerie** : Coche les ingrédients manquants dans une recette et clique sur 'Sauver & Épicerie'.
    4. **Ajouter** : Utilise le bouton 'AJOUTER' pour créer une recette manuellement ou via le mode vrac.
    
    ### Problèmes fréquents ?
    * **Image absente** : Vérifie que le lien finit bien par `.jpg` ou `.png`.
    * **Sync** : La synchronisation prend environ 2 à 5 secondes avec Google Sheets.
    """)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- PLAY STORE WOW (DESIGN PREMIUM) ---
elif st.session_state.page == "playstore":
    st.markdown("<div class='store-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([1,3])
    with c1: st.image("https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png", width=140)
    with c2:
        st.markdown("## 🍳 Mes Recettes Pro\n⭐ **4.9** | 📥 10 000+\n<br><div class='install-btn'>Installer</div>", unsafe_allow_html=True)
    st.markdown("---")
    cA, cB, cC = st.columns(3)
    cA.image("https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg")
    cB.image("https://i.postimg.cc/YCkg460C/shared-image-(5).jpg")
    cC.image("https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg")
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- AJOUTER ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter")
    # ... (Logique d'ajout simplifiée pour gagner de la place ici)
    with st.form("new_r"):
        t = st.text_input("Titre")
        i = st.text_area("Ingrédients")
        p = st.text_area("Préparation")
        if st.form_submit_button("🚀 Créer"):
            if send_action({"action":"add","titre":t,"ingredients":i,"preparation":p,"date":datetime.now().strftime("%d/%m/%Y")}):
                st.session_state.page="home"; st.rerun()
