import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ======================================================
# 1. DESIGN & CONFIGURATION
# ======================================================
st.set_page_config(page_title="Mes Recettes", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }
    
    /* Cartes Bibliothèque */
    .recipe-card {
        background-color: #1e2129;
        border: 1px solid #3d4455;
        border-radius: 15px;
        padding: 10px;
        transition: 0.3s;
        text-align: center;
    }
    .recipe-card:hover { border-color: #e67e22; transform: translateY(-3px); }
    .recipe-img { width: 100%; height: 160px; object-fit: cover; border-radius: 10px; }

    /* Liste de courses style */
    .shop-item { display: flex; justify-content: space-between; align-items: center; 
                 background: #262730; padding: 10px; border-radius: 8px; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# CONFIG URLS
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"
CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# ======================================================
# 2. LOGIQUE TECHNIQUE
# ======================================================
@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= len(expected): df.columns = expected[:len(df.columns)]
        return df
    except: return pd.DataFrame()

def send_action(payload):
    with st.spinner("📦 Synchronisation..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=15)
            if "Success" in r.text:
                st.success("Enregistré avec succès !")
                st.cache_data.clear()
                time.sleep(1)
                return True
        except Exception as e: st.error(f"Erreur : {e}")
    return False

# Session States
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# ======================================================
# 3. SIDEBAR NAVIGATION
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page="home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page="planning"; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): st.session_state.page="shop"; st.rerun()
    st.divider()
    if st.button("➕ Ajouter", type="primary", use_container_width=True): st.session_state.page="add"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()

# ======================================================
# 4. PAGES
# ======================================================

# --- PAGE: BIBLIOTHÈQUE ---
if st.session_state.page == "home":
    st.title("📚 Ma Bibliothèque")
    df = load_data()
    c_s, c_f = st.columns([2,1])
    search = c_s.text_input("🔍 Rechercher...", placeholder="Nom de recette")
    cat_f = c_f.selectbox("Catégorie", CATEGORIES)

    if not df.empty:
        filtered = df.copy()
        if search: filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": filtered = filtered[filtered['Catégorie'] == cat_f]
        
        cols = st.columns(3)
        for idx, row in filtered.reset_index(drop=True).iterrows():
            with cols[idx % 3]:
                st.markdown(f"""<div class="recipe-card">
                    <img src="{row['Image'] if 'http' in str(row['Image']) else 'https://via.placeholder.com/150'}" class="recipe-img">
                    <h4>{row['Titre']}</h4></div>""", unsafe_allow_html=True)
                if st.button("Ouvrir", key=f"view_{idx}", use_container_width=True):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"; st.rerun()
    else: st.info("Aucune recette trouvée.")

# --- PAGE: DETAILS (ÉTOILES & COMMENTAIRES RESTAURÉS) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page="home"; st.rerun()
    
    st.title(f"🍳 {r['Titre']}")
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        
        # --- BLOC ÉTOILES & NOTES ---
        st.subheader("⭐ Avis & Notes")
        note = st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"])
        mes_notes = st.text_area("Mes astuces personnelles", value=r.get('Commentaires',''))
        
        if st.button("💾 Sauvegarder Note & Commentaires"):
            if send_action({"action":"update_notes", "titre": r['Titre'], "commentaires": mes_notes}):
                st.toast("Commentaires enregistrés !")

        st.divider()
        st.subheader("📅 Planifier")
        d_p = st.date_input("Date prévue", value=datetime.now())
        if st.button("Ajouter au calendrier"):
            if send_action({"action":"update", "titre_original": r['Titre'], "date_prevue": d_p.strftime("%d/%m/%Y")}):
                st.rerun()

    with col2:
        st.subheader("🛒 Ingrédients")
        ing_list = str(r['Ingrédients']).split("\n")
        to_add = []
        for i, item in enumerate(ing_list):
            if item.strip():
                if st.checkbox(item, key=f"ing_{i}"): to_add.append(item)
        
        if st.button("➕ Ajouter à la liste de courses", use_container_width=True):
            st.session_state.shopping_list.extend([x for x in to_add if x not in st.session_state.shopping_list])
            st.toast("Ajouté !")

        st.divider()
        st.subheader("📝 Préparation")
        st.info(r['Préparation'])

# --- PAGE: SHOPPING (BOUTONS X RESTAURÉS) ---
elif st.session_state.page == "shop":
    st.title("🛒 Liste de courses")
    if st.button("🗑 Tout vider"): st.session_state.shopping_list = []; st.rerun()
    
    for idx, item in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([0.85, 0.15])
        c1.markdown(f"✅ **{item}**")
        if c2.button("❌", key=f"del_{idx}"):
            st.session_state.shopping_list.pop(idx)
            st.rerun()

# --- PAGE: AJOUTER ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    with st.form("add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            t = st.text_input("Titre *")
            cat = st.selectbox("Catégorie", CATEGORIES[1:])
        with c2:
            src = st.text_input("Source")
            img = st.text_input("URL Image")
        ing = st.text_area("Ingrédients (un par ligne) *")
        pre = st.text_area("Préparation")
        if st.form_submit_button("Enregistrer"):
            if t and ing:
                p = {"action":"add", "titre":t, "categorie":cat, "source":src, "image":img, "ingredients":ing, "preparation":pre, "date":datetime.now().strftime("%d/%m/%Y")}
                if send_action(p): st.session_state.page="home"; st.rerun()

# --- PAGE: PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Mon Planning")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ''].sort_values('Date_Prevue')
        if plan.empty: st.info("Aucun repas planifié.")
        else:
            for _, row in plan.iterrows():
                st.write(f"🗓 **{row['Date_Prevue']}** — {row['Titre']}")
