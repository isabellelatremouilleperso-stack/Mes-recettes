import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ======================================================
# 1. CONFIGURATION & DESIGN
# ======================================================
st.set_page_config(page_title="Chef Master Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }
    .recipe-card {
        background-color: #1e2129; border: 1px solid #3d4455;
        border-radius: 15px; padding: 10px; transition: 0.3s;
    }
    .recipe-card:hover { border-color: #e67e22; transform: translateY(-5px); }
    .recipe-img { width: 100%; height: 160px; object-fit: cover; border-radius: 10px; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    /* Style pour le bouton source */
    .source-btn {
        background-color: #3d4455; color: white; text-align: center; 
        padding: 10px; border-radius: 8px; font-weight: bold; 
        margin-bottom: 15px; text-decoration: none; display: block;
    }
    .source-btn:hover { background-color: #e67e22; color: white; }
</style>
""", unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"
CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# ======================================================
# 2. FONCTIONS TECHNIQUES
# ======================================================
@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires']
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except:
        return pd.DataFrame()

def send_action(payload):
    with st.spinner("📦 Synchronisation..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=15)
            if "Success" in r.text:
                st.success("Réussi !")
                st.cache_data.clear()
                time.sleep(1)
                return True
            st.error(f"Erreur : {r.text}")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")
    return False

if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# ======================================================
# 3. BARRE LATÉRALE
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()

    st.divider()
    with st.expander("💡 Besoin d'aide ?"):
        aide_theme = st.selectbox("Thème :", ["Général", "Ajout", "Courses", "Calendrier"])
        if aide_theme == "Général": st.info("Naviguez via le menu latéral.")
        elif aide_theme == "Ajout": st.write("Collez le lien Instagram/TikTok dans le champ 'Source'.")
        elif aide_theme == "Courses": st.write("Cochez les ingrédients pour les envoyer à l'épicerie.")
        elif aide_theme == "Calendrier": st.write("Planifiez pour voir dans Google Calendar.")

# ======================================================
# 4. LOGIQUE DES PAGES
# ======================================================

# --- ACCUEIL ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("🔍 Rechercher...", placeholder="Ex: Lasagnes")
    cat_f = c2.selectbox("Filtrer", CATEGORIES)

    if not df.empty:
        filtered = df.copy()
        if search: filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": filtered = filtered[filtered['Catégorie'] == cat_f]
        
        rows = filtered.reset_index(drop=True)
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f"""
                        <div class="recipe-card" style="height: 380px; display: flex; flex-direction: column; justify-content: space-between;">
                            <div>
                                <img src="{img}" class="recipe-img">
                                <h4 style="margin: 10px 0 5px 0; font-size: 0.95rem; height: 60px; overflow-y: auto; color: white;">{row['Titre']}</h4>
                                <p style="color: #e67e22; font-size: 0.8rem; margin:0;">👥 {row['Portions']} | ⏱ {row['Temps_Prepa']}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Ouvrir", key=f"btn_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"; st.rerun()
    else: st.info("Votre bibliothèque est vide.")

# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    
    col_back, col_del = st.columns([5, 1])
    with col_back:
        if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    with col_del:
        if st.button("🗑️", help="Supprimer définitivement"):
            st.session_state.confirm_delete = True

    if st.session_state.get('confirm_delete', False):
        st.error(f"Voulez-vous vraiment supprimer '{r['Titre']}' ?")
        cb1, cb2 = st.columns(2)
        if cb1.button("✅ Oui, supprimer", type="primary"):
            if send_action({"action": "delete", "titre": r['Titre']}):
                st.session_state.confirm_delete = False
                st.session_state.page = "home"; st.rerun()
        if cb2.button("❌ Annuler"):
            st.session_state.confirm_delete = False; st.rerun()

    st.title(f"🍳 {r['Titre']}")
    st.info(f"💡 Portions : {r['Portions']} | Prépa : {r['Temps_Prepa']} | Cuisson : {r['Temps_Cuisson']}")
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        
        # --- BOUT
