import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup
import re
import json

# ======================================================
# 1. CONFIGURATION & DESIGN
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }
    .stCheckbox label p { color: white !important; font-size: 1.1rem !important; font-weight: 500 !important; }
    input, select, textarea, div[data-baseweb="select"] { color: white !important; background-color: #1e2129 !important; }
    label, .stMarkdown p { color: white !important; }
    
    /* CARTES RECETTES */
    .recipe-card {
        background-color: #1e2129; border: 1px solid #3d4455;
        border-radius: 12px; padding: 10px; height: 230px; 
        display: flex; flex-direction: column;
    }
    .recipe-img { width: 100%; height: 130px; object-fit: cover; border-radius: 8px; }
    .recipe-title {
        color: white; margin-top: 8px; font-size: 0.95rem; font-weight: bold;
        text-align: center; height: 2.5em; line-height: 1.2;
    }

    /* DESIGN PLAY STORE WOW */
    .store-card {
        background-color: #161b22; padding: 30px; border-radius: 20px;
        box-shadow: 0 0 25px rgba(0,0,0,0.5); border: 1px solid #30363d;
    }
    .install-btn {
        background: linear-gradient(90deg, #00c853, #64dd17);
        color: white !important; padding: 12px 35px; border-radius: 12px;
        font-size: 18px; font-weight: bold; text-align: center; display: inline-block;
        text-decoration: none;
    }
</style>
""", unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS
# ======================================================

def ventiler_vrac(texte_brut):
    data = {"ing": "", "prep": "", "t_prepa": "", "t_cuisson": "", "port": ""}
    lignes = texte_brut.split('\n')
    mode = None
    for l in lignes:
        l_low = l.lower().strip()
        if not l_low: continue
        time_match = re.search(r'(\d+\s*(min|h|heure))', l_low)
        if "prep" in l_low and time_match: data["t_prepa"] = time_match.group(1)
        elif "cuisson" in l_low and time_match: data["t_cuisson"] = time_match.group(1)
        if any(x in l_low for x in ["ingrédient", "ingredien", "liste"]): mode = "ing"; continue
        if any(x in l_low for x in ["préparation", "etapes", "instruction"]): mode = "prep"; continue
        if mode == "ing": data["ing"] += l + "\n"
        elif mode == "prep": data["prep"] += l + "\n"
        else: data["ing"] += l + "\n"
    return data

def send_action(payload):
    with st.spinner("🚀 Synchronisation..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear(); return True
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

# ======================================================
# 3. NAVIGATION
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"

with st.sidebar:
    st.title("👨‍🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning Repas", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER RECETTE", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    st.divider()
    if st.button("⭐ Play Store Wow", use_container_width=True): st.session_state.page = "playstore"; st.rerun()

# ======================================================
# 4. PAGES
# ======================================================

# --- BIBLIOTHÈQUE ---
if st.session_state.page == "home":
    st.header("📚 Bibliothèque")
    df = load_data()
    if not df.empty:
        search = st.text_input("🔍 Rechercher une recette...")
        rows = df[df['Titre'].str.contains(search, case=False)]
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(rows):
                    row = rows.iloc[i+j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><div class="recipe-title">{row["Titre"]}</div></div>', unsafe_allow_html=True)
                        if st.button("Ouvrir", key=f"b_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

# --- DÉTAILS (MODIFICATION & SUPPRESSION) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    c_nav, c_del = st.columns([4, 1])
    if c_nav.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    if c_del.button("🗑️ Supprimer"):
        if send_action({"action": "delete", "titre": r['Titre']}):
            st.success("Supprimé !"); time.sleep(1); st.session_state.page = "home"; st.rerun()

    st.header(f"📖 {r['Titre']}")
    if r.get('Video') and "http" in str(r['Video']): st.video(r['Video'])

    with st.form("edit_recipe"):
        col_l, col_r = st.columns([1, 1.2])
        with col_l:
            st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
            st.subheader("⭐ Note & Avis")
            try: cur_note = int(float(r.get('Note', 0)))
            except: cur_note = 0
            n_note = st.slider("Étoiles", 0, 5, cur_note)
            n_comm = st.text_area("Mes commentaires", value=str(r.get('Commentaires', "")))
            
            st.divider()
            st.subheader("📅 Planning")
            d_plan = st.date_input("Date prévue")
        
        with col_r:
            st.subheader("🛒 Ingrédients")
            n_ing = st.text_area("Liste des ingrédients", value=r['Ingrédients'], height=250)
            st.subheader("📝 Préparation")
            n_prep = st.text_area("Instructions", value=r['Préparation'], height=250)

        if st.form_submit_button("💾 Enregistrer les modifications"):
            payload = {
                "action": "edit", "titre": r['Titre'], "ingredients": n_ing, 
                "preparation": n_prep, "Note": n_note, "Commentaires": n_comm,
                "Date_Prevue": d_plan.strftime("%Y-%m-%d")
            }
            if send_action(payload):
                st.success("Mis à jour !"); time.sleep(1); st.session_state.page = "home"; st.rerun()

# --- PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning des Repas")
    df = load_data()
    plan = df[df['Date_Prevue'].astype(str).str.strip() != ""]
    if not plan.empty:
        for _, row in plan.iterrows():
            with st.expander(f"📌 {row['Date_Prevue']} : {row['Titre']}"):
                if st.button("Voir la fiche", key=f"plan_{row['Titre']}"):
                    st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
    else:
        st.info("Aucun repas planifié.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- PLAY STORE WOW (DESIGN PREMIUM) ---
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
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- AJOUTER RECETTE ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    v_in = st.text_area("Collez le texte brut ici pour ventiler")
    if st.button("Analyser"):
        st.session_state.v_res = ventiler_vrac(v_in)
    
    with st.form("add_f"):
        v = st.session_state.get('v_res', {"ing":"","prep":""})
        f_t = st.text_input("Titre")
        f_ing = st.text_area("Ingrédients", value=v['ing'])
        f_pre = st.text_area("Préparation", value=v['prep'])
        f_img = st.text_input("Lien Image")
        if st.form_submit_button("Enregistrer"):
            payload = {"action":"add", "titre":f_t, "ingredients":f_ing, "preparation":f_pre, "image":f_img, "date":datetime.now().strftime("%d/%m/%Y")}
            if send_action(payload): st.session_state.page="home"; st.rerun()
