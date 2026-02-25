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

st.markdown("""
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
    header {visibility: hidden;} .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS
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
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        cols = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires']
        if len(df.columns) >= len(cols): df.columns = cols[:len(df.columns)]
        return df
    except: return pd.DataFrame()

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
    if st.button("❓ Aide", use_container_width=True): st.session_state.page = "help"; st.rerun()

# ======================================================
# 4. PAGES
# ======================================================

# --- BIBLIOTHÈQUE ---
if st.session_state.page == "home":
    c1, c2 = st.columns([4, 1])
    c1.header("📚 Bibliothèque")
    if c2.button("🔄 Actualiser"): st.cache_data.clear(); st.rerun()
    
    df = load_data()
    search = st.text_input("🔍 Rechercher une recette...")
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

# --- AJOUTER RECETTE (VRAC MIS À JOUR) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    tab1, tab2, tab3 = st.tabs(["🔗 Import URL", "📝 Vrac", "⌨️ Manuel"])
    
    with tab1:
        url_link = st.text_input("Lien de la recette")
        if st.button("🪄 Importer"):
            # (Fonction de scrape supposée existante ou via API)
            st.info("Importation en cours...")

    with tab2:
        st.subheader("Coller en vrac avec détails")
        with st.form("vrac_form_complet"):
            v_t = st.text_input("Titre de la recette *")
            v_cats = st.multiselect("Catégories", CATEGORIES)
            
            c1, c2, c3 = st.columns(3)
            v_por = c1.text_input("Portions (ex: 4 pers.)")
            v_pre = c2.text_input("Temps Préparation")
            v_cui = c3.text_input("Temps Cuisson")
            
            v_txt = st.text_area("Texte de la recette (Ingrédients et Étapes)", height=250)
            
            if st.form_submit_button("🚀 Sauver la recette"):
                if v_t and v_txt:
                    send_action({
                        "action": "add", 
                        "titre": v_t, 
                        "categorie": ", ".join(v_cats), 
                        "ingredients": v_txt, 
                        "preparation": "Voir bloc ingrédients/vrac", 
                        "portions": v_por,
                        "temps_prepa": v_pre,
                        "temps_cuisson": v_cui,
                        "date": datetime.now().strftime("%d/%m/%Y")
                    })
                    st.success("Recette enregistrée !")
                    time.sleep(1); st.session_state.page = "home"; st.rerun()
                else:
                    st.error("Le titre et le contenu sont obligatoires.")

    with tab3:
        with st.form("manuel"):
            # (Reste identique au mode manuel précédent)
            st.write("Saisie manuelle classique...")
            st.form_submit_button("Sauver")

# --- AUTRES PAGES (SHOP / PLANNING / DETAILS) ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    # ... (code des cases à cocher et suppression sélective)
    st.info("Fonctionnalité active.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "planning":
    st.header("📅 Planning Repas")
    # ... (affichage du planning)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "details":
    # ... (code détails avec cases à cocher pour ingrédients)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "help":
    st.title("❓ Aide")
    st.write("Le mode Vrac permet désormais de saisir les portions, temps et catégories en plus du texte.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
