import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# CONFIGURATION
st.set_page_config(page_title="Chef Master Pro", layout="wide", page_icon="🍳")

# DESIGN
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .recipe-card {
        background-color: #1e2129; border-radius: 15px;
        border: 1px solid #3d4455; padding: 10px; margin-bottom: 20px;
    }
    h1, h2, h3 { color: #e67e22 !important; }
    .stButton>button { border-radius: 8px; width: 100%; }
</style>
""", unsafe_allow_html=True)

# URLS
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# FONCTIONS
@st.cache_data(ttl=10) # Cache très court pour voir les changements
def load_data():
    try:
        # Ajout d'un paramètre aléatoire pour forcer Google à ne pas servir une version cachée
        df = pd.read_csv(f"{URL_CSV}&cachebust={time.time()}").fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except:
        return pd.DataFrame()

def run_action(payload):
    with st.spinner("Mise à jour du grimoire..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=15)
            if "Success" in r.text:
                st.success("Synchronisation réussie !")
                st.cache_data.clear() # Vider le cache Streamlit
                time.sleep(2)         # Attendre que Google publie le CSV
                return True
            else:
                st.error(f"Erreur Google : {r.text}")
        except Exception as e:
            st.error(f"Erreur connexion : {e}")
    return False

# SESSION STATE
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}
if "shop" not in st.session_state: st.session_state.shop = []

# SIDEBAR
with st.sidebar:
    st.title("👨‍🍳 Menu")
    if st.button("📚 Bibliothèque"): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning"): st.session_state.page = "planning"; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shop)})"): st.session_state.page = "shop"; st.rerun()
    st.divider()
    if st.button("➕ Ajouter", type="primary"): st.session_state.page = "add"; st.rerun()
    if st.button("🔄 Actualiser"): st.cache_data.clear(); st.rerun()

# --- PAGES ---

if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    search = st.text_input("🔍 Rechercher...", placeholder="Nom d'une recette")
    
    if not df.empty:
        filtered = df[df['Titre'].str.contains(search, case=False)] if search else df
        cols = st.columns(3)
        for idx, row in filtered.reset_index(drop=True).iterrows():
            with cols[idx%3]:
                st.markdown(f'<div class="recipe-card">', unsafe_allow_html=True)
                img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/300"
                st.image(img, use_container_width=True)
                st.subheader(row['Titre'])
                if st.button("Ouvrir", key=f"btn_{idx}"):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.title(r['Titre'])
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        date_p = st.date_input("Planifier pour le :")
        if st.button("📅 Ajouter au Planning"):
            if run_action({"action":"update", "titre_original": r['Titre'], "date_prevue": date_p.strftime("%d/%m/%Y")}):
                st.rerun()

    with c2:
        st.subheader("🛒 Ingrédients")
        ings = str(r['Ingrédients']).split('\n')
        for ing in ings:
            if ing.strip():
                if st.checkbox(ing, key=f"check_{ing}"):
                    if ing not in st.session_state.shop: st.session_state.shop.append(ing)
        
        st.divider()
        st.subheader("📝 Préparation")
        st.write(r['Préparation'])

elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    with st.form("new_recipe"):
        t = st.text_input("Titre *")
        cat = st.selectbox("Catégorie", CATEGORIES[1:])
        src = st.text_input("Source")
        img = st.text_input("URL Image")
        ing = st.text_area("Ingrédients (un par ligne) *")
        pre = st.text_area("Préparation")
        
        if st.form_submit_button("Enregistrer"):
            if t and ing:
                payload = {
                    "action": "add", "titre": t, "categorie": cat, "source": src,
                    "image": img, "ingredients": ing, "preparation": pre,
                    "date": datetime.now().strftime("%d/%m/%Y")
                }
                if run_action(payload):
                    st.session_state.page = "home"; st.rerun()
            else:
                st.warning("Titre et Ingrédients requis.")

elif st.session_state.page == "planning":
    st.header("📅 Mon Planning")
    df = load_data()
    plan = df[df['Date_Prevue'] != '']
    if plan.empty: st.info("Aucun repas planifié.")
    for _, row in plan.iterrows():
        st.write(f"🗓 **{row['Date_Prevue']}** : {row['Titre']}")

elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste")
    if st.button("🗑 Vider"): st.session_state.shop = []; st.rerun()
    for item in st.session_state.shop:
        st.write(f"✅ {item}")
