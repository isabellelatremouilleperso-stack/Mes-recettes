import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup

# ======================================================
# 1. CONFIGURATION & DESIGN
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

CSS_STYLE = """
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }
    .recipe-card {
        background-color: #1e2129; border: 1px solid #3d4455;
        border-radius: 12px; padding: 10px; height: 230px; 
        display: flex; flex-direction: column;
    }
    .recipe-img { width: 100%; height: 130px; object-fit: cover; border-radius: 8px; }
    .recipe-title {
        color: white; margin-top: 8px; font-size: 0.9rem; font-weight: bold;
        display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
        overflow: hidden; height: 2.6em; line-height: 1.3;
    }
    .app-header { display: flex; align-items: center; gap: 20px; }
    header {visibility: hidden;} .stDeployButton {display:none;}
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS (CORRIGÉES)
# ======================================================
def send_action(payload):
    with st.spinner("🚀 Action..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear(); time.sleep(0.5); return True
        except: pass
    return False

@st.cache_data(ttl=5)
def load_data():
    try:
        # On force les noms de colonnes pour qu'ils correspondent au code, peu importe le nom dans Excel
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}")
        
        # Liste des colonnes attendues par l'application
        new_cols = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires','Note']
        
        # On renomme par index (colonne 0, colonne 1, etc.) pour ne plus dépendre du texte exact
        df.columns = new_cols[:len(df.columns)]
        return df.fillna('')
    except Exception as e:
        st.error(f"Erreur de chargement: {e}")
        return pd.DataFrame()

if "page" not in st.session_state: st.session_state.page = "home"

# ======================================================
# 3. SIDEBAR
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning Repas", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Ma Liste d'épicerie", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER RECETTE", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("⭐ Play Store", use_container_width=True): st.session_state.page = "playstore"; st.rerun()

# ======================================================
# 4. PAGES
# ======================================================

# --- PLANNING (CORRIGÉ) ---
if st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data()
    if not df.empty:
        # On filtre les lignes où une date est saisie
        plan = df[df['Date_Prevue'] != ""].sort_values(by='Date_Prevue')
        if not plan.empty:
            for _, row in plan.iterrows():
                with st.expander(f"📌 {row['Date_Prevue']} : {row['Titre']}"):
                    if st.button("Voir la fiche", key=f"p_{row['Titre']}"):
                        st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
        else:
            st.info("Aucun repas planifié.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- PLAY STORE ---
elif st.session_state.page == "playstore":
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/100", width=100)
    st.markdown("### Mes Recettes Pro\n**Isabelle Latrémouille**\n⭐ 4.9 | 📥 1 000+")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("📥 Installer"): st.success("Installée !")
    st.divider()
    st.subheader("📸 Aperçu")
    c1, c2, c3 = st.columns(3)
    c1.image("https://via.placeholder.com/200x400")
    c2.image("https://via.placeholder.com/200x400")
    c3.image("https://via.placeholder.com/200x400")

# --- BIBLIOTHÈQUE ---
elif st.session_state.page == "home":
    c1, c2 = st.columns([4, 1])
    c1.header("📚 Bibliothèque")
    if c2.button("🔄"): st.cache_data.clear(); st.rerun()
    df = load_data()
    search = st.text_input("🔍 Rechercher...")
    if not df.empty:
        filtered = df[df['Titre'].str.contains(search, case=False)] if search else df
        rows = filtered.reset_index(drop=True)
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><div class="recipe-title">{row["Titre"]}</div></div>', unsafe_allow_html=True)
                        if st.button("Voir", key=f"btn_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

# --- AJOUTER (VRAC & MANUEL) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter")
    t1, t2 = st.tabs(["📝 Vrac", "⌨️ Manuel"])
    with t1:
        with st.form("vrac"):
            vt = st.text_input("Titre *")
            vc = st.multiselect("Catégories", CATEGORIES)
            c1, c2, c3 = st.columns(3)
            vp, vpre, vcu = c1.text_input("Portions"), c2.text_input("Prépa"), c3.text_input("Cuisson")
            vtxt = st.text_area("Texte")
            if st.form_submit_button("Sauver"):
                send_action({"action": "add", "titre": vt, "categorie": ", ".join(vc), "ingredients": vtxt, "portions": vp, "temps_prepa": vpre, "temps_cuisson": vcu, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()
    with t2:
        with st.form("manuel"):
            mt = st.text_input("Titre *")
            mi = st.text_area("Ingrédients")
            mp = st.text_area("Préparation")
            if st.form_submit_button("Enregistrer"):
                send_action({"action": "add", "titre": mt, "ingredients": mi, "preparation": mp, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

# --- DÉTAILS (ÉTOILES & NOTES) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    st.title(f"🍳 {r['Titre']}")
    # Note en étoiles
    try: nv = int(float(r.get('Note', 0)))
    except: nv = 0
    st.write("⭐" * nv + "☆" * (5 - nv))
    
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        new_n = st.selectbox("Note", [1,2,3,4,5], index=(nv-1 if 1<=nv<=5 else 4))
        new_c = st.text_area("Commentaires", value=r.get('Commentaires', ''))
        new_d = st.text_input("Date prévue", value=r.get('Date_Prevue', ''))
        if st.button("Enregistrer"):
            send_action({"action": "update_notes", "titre": r['Titre'], "date_prevue": new_d, "commentaires": new_c, "note": new_n})
            st.rerun()
    with c2:
        st.subheader("🛒 Ingrédients")
        for i, l in enumerate(str(r['Ingrédients']).split('\n')):
            if l.strip(): st.checkbox(l, key=f"i_{i}")
        st.divider()
        st.subheader("📝 Étapes")
        st.write(r['Préparation'])
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Liste d'épicerie")
    try:
        dfs = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        for idx, row in dfs.iterrows():
            if st.checkbox(row.iloc[0], key=f"s_{idx}"):
                send_action({"action": "remove_shop", "article": row.iloc[0]}); st.rerun()
    except: st.info("Liste vide.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
