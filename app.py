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
    .recipe-card {
        background-color: #1e2129; border: 1px solid #3d4455;
        border-radius: 12px; padding: 10px; height: 230px; 
        display: flex; flex-direction: column;
    }
    .recipe-img { width: 100%; height: 130px; object-fit: cover; border-radius: 8px; }
    .recipe-title {
        color: white; margin-top: 8px; font-size: 0.95rem; font-weight: bold;
        text-align: center; display: flex; align-items: center; justify-content: center;
        height: 2.5em; line-height: 1.2;
    }
    .logo-playstore { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid #e67e22; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
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
        port_match = re.search(r'(\d+)\s*(pers|port|conv)', l_low)
        if port_match: data["port"] = port_match.group(1)
        if any(x in l_low for x in ["ingrédient", "ingredien", "liste"]): mode = "ing"; continue
        if any(x in l_low for x in ["préparation", "etapes", "instruction", "recette :"]): mode = "prep"; continue
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
# 3. MENU LATÉRAL
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"

with st.sidebar:
    st.title("👨‍🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning Repas", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Ma Liste d'épicerie", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER RECETTE", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    st.divider()
    if st.button("⭐ Play Store", use_container_width=True): st.session_state.page = "playstore"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): st.session_state.page = "help"; st.rerun()

# ======================================================
# 4. PAGES
# ======================================================

# --- PLANNING ---
if st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'].astype(str).str.strip() != ""]
        for _, row in plan.iterrows():
            with st.expander(f"📌 {row['Date_Prevue']} : {row['Titre']}"):
                if st.button("Voir", key=f"p_{row['Titre']}"):
                    st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- DÉTAILS (AVEC NOTES & ÉTOILES) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.header(f"📖 {r['Titre']}")
    if r.get('Video') and "http" in str(r['Video']): st.video(r['Video'])
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        
        # --- SYSTÈME DE NOTES ET ÉTOILES ---
        st.subheader("⭐ Ma Note")
        # Conversion sécurisée de la note en entier pour le slider
        try: current_note = int(float(r.get('Note', 0)))
        except: current_note = 0
            
        n_note = st.slider("Note sur 5", 0, 5, current_note)
        n_comm = st.text_area("Mes commentaires perso", value=str(r.get('Commentaires', "")))
        
        if st.button("💾 Sauvegarder mon avis"):
            if send_action({"action": "edit", "titre": r['Titre'], "Note": n_note, "Commentaires": n_comm}):
                st.toast("Avis enregistré ! ⭐")
        
        st.divider()
        st.subheader("📅 Planifier")
        d_plan = st.date_input("Date du repas")
        if st.button("Ajouter au calendrier"):
            send_action({"action": "edit", "titre": r['Titre'], "Date_Prevue": d_plan.strftime("%Y-%m-%d")})

    with col_r:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        sel = []
        for i, it in enumerate(ings):
            if st.checkbox(it, key=f"c_{i}"): sel.append(it)
        if st.button("📥 Envoyer à l'épicerie"):
            for it in sel: send_action({"action": "add_shop", "article": it})
            st.toast("Liste mise à jour !"); time.sleep(0.5); st.session_state.page = "shop"; st.rerun()

    st.divider()
    st.subheader("📝 Préparation")
    st.info(r['Préparation'])

# --- AJOUTER (AVEC VENTILATION) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter")
    t1, t2 = st.tabs(["1. Import", "2. Ventilation"])
    with t1:
        u = st.text_input("URL")
        if st.button("Extraire"): # Logique simplifiée pour l'exemple
            st.session_state.temp_source = u
            st.success("Lien mémorisé !")
        v = st.text_area("Texte brut")
        if st.button("Analyser"):
            res = ventiler_vrac(v)
            st.session_state.update(res)
    with t2:
        with st.form("f"):
            f_t = st.text_input("Titre", value=st.session_state.get('temp_titre', ""))
            f_cat = st.selectbox("Catégorie", CATEGORIES)
            f_src = st.text_input("Lien Source", value=st.session_state.get('temp_source', ""))
            f_vid = st.text_input("Lien Vidéo")
            f_ing = st.text_area("Ingrédients", value=st.session_state.get('ing', ""))
            f_pre = st.text_area("Préparation", value=st.session_state.get('prep', ""))
            if st.form_submit_button("Enregistrer"):
                payload = {"action":"add","titre":f_t,"categorie":f_cat,"source":f_src,"video":f_vid,"ingredients":f_ing,"preparation":f_pre,"date":datetime.now().strftime("%d/%m/%Y")}
                if send_action(payload): st.session_state.page="home"; st.rerun()

# --- BIBLIOTHÈQUE (ACCUEIL) ---
elif st.session_state.page == "home":
    st.header("📚 Bibliothèque")
    df = load_data()
    if not df.empty:
        for i in range(0, len(df), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(df):
                    row = df.iloc[i+j]
                    with cols[j]:
                        st.markdown(f'<div class="recipe-card"><div class="recipe-title">{row["Titre"]}</div></div>', unsafe_allow_html=True)
                        if st.button("Ouvrir", key=f"b_{i+j}"):
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

# --- PLAYSTORE ---
elif st.session_state.page == "playstore":
    st.markdown("### Play Store")
    c1, c2, c3 = st.columns(3)
    c1.image("https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg")
    c2.image("https://i.postimg.cc/YCkg460C/shared-image-(5).jpg")
    c3.image("https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- ÉPICERIE / AIDE ---
elif st.session_state.page == "shop":
    st.header("🛒 Liste d'épicerie")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    # Logique d'affichage simplifiée ici pour la démo
