import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ======================================================
# 1. CONFIGURATION & DESIGN PREMIUM
# ======================================================
st.set_page_config(page_title="Chef Master Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    /* Fond sombre global */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }
    
    /* Cartes de la bibliothèque */
    .recipe-card {
        background-color: #1e2129;
        border: 1px solid #3d4455;
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        transition: 0.3s;
        margin-bottom: 20px;
    }
    .recipe-card:hover { border-color: #e67e22; transform: translateY(-5px); }
    .recipe-img { width: 100%; height: 180px; object-fit: cover; border-radius: 10px; }
    
    /* Boutons et Inputs */
    .stButton>button { border-radius: 8px; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #262730 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# CONFIGURATION DES URLS
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# ======================================================
# 2. FONCTIONS DE SYNCHRONISATION
# ======================================================
@st.cache_data(ttl=5)
def load_data():
    try:
        # Ajout d'un paramètre aléatoire pour éviter le cache Google
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except:
        return pd.DataFrame()

def send_action(payload):
    with st.spinner("📦 Synchronisation avec le Cloud..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=15)
            if "Success" in r.text:
                st.success("Action enregistrée !")
                st.cache_data.clear()
                time.sleep(1)
                return True
            else:
                st.error(f"Erreur Google : {r.text}")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")
    return False

# Initialisation du Session State
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# ======================================================
# 3. BARRE LATÉRALE (NAVIGATION)
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()

# ======================================================
# 4. LOGIQUE DES PAGES
# ======================================================

# --- PAGE: BIBLIOTHÈQUE ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    
    col_search, col_filter = st.columns([2, 1])
    search = col_search.text_input("🔍 Rechercher une recette...", placeholder="Ex: Poulet Coco")
    cat_f = col_filter.selectbox("Filtrer par catégorie", CATEGORIES)

    if not df.empty:
        filtered = df.copy()
        if search: filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": filtered = filtered[filtered['Catégorie'] == cat_f]
        
        cols = st.columns(3)
        for idx, row in filtered.reset_index(drop=True).iterrows():
            with cols[idx % 3]:
                img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                st.markdown(f"""
                <div class="recipe-card">
                    <img src="{img}" class="recipe-img">
                    <h4>{row['Titre']}</h4>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"; st.rerun()
    else:
        st.info("Votre bibliothèque est vide.")

# --- PAGE: DÉTAILS (NOTES, ÉTOILES, ÉPICERIE) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.title(f"🍳 {r['Titre']}")
    c1, c2 = st.columns([1, 1.2])

    with c1:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        
        # NOTES ET ÉTOILES
        st.subheader("⭐ Avis & Notes")
        note = st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"])
        comm = st.text_area("Mes astuces personnelles", value=r.get('Commentaires',''))
        if st.button("💾 Sauvegarder l'avis"):
            send_action({"action":"update_notes", "titre": r['Titre'], "commentaires": comm})

        st.write("---")
        st.subheader("📅 Planification")
        d_p = st.date_input("Planifier pour le :", value=datetime.now())
        if st.button("📅 Envoyer au Planning & Calendrier"):
            f_date = d_p.strftime("%d/%m/%Y")
            if send_action({"action":"update", "titre_original": r['Titre'], "date_prevue": f_date}):
                send_action({"action":"calendar", "titre": r['Titre'], "date_prevue": f_date, "ingredients": r['Ingrédients']})
                st.rerun()

    with c2:
        st.subheader("🛒 Ingrédients")
        ing_list = str(r['Ingrédients']).split("\n")
        to_buy = []
        for i, item in enumerate(ing_list):
            if item.strip():
                if st.checkbox(item.strip(), key=f"ing_{i}"): to_buy.append(item.strip())
        
        if st.button("➕ Ajouter à la liste d'épicerie", use_container_width=True):
            st.session_state.shopping_list.extend([x for x in to_buy if x not in st.session_state.shopping_list])
            st.toast("Ingrédients ajoutés !")

        st.write("---")
        st.subheader("📝 Préparation")
        st.info(r['Préparation'])

# --- PAGE: AJOUTER (AVEC OPTION PLANNING DIRECT) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    with st.form("form_add", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t = st.text_input("Titre de la recette *")
            cat = st.selectbox("Catégorie", CATEGORIES[1:])
        with col2:
            src = st.text_input("Source (Instagram, TikTok...)")
            img = st.text_input("URL de l'image")
        
        ing = st.text_area("Ingrédients (un par ligne) *")
        pre = st.text_area("Préparation")
        
        st.write("---")
        st.subheader("📅 Planifier immédiatement ?")
        c_check, c_date = st.columns([1, 2])
        plan_now = c_check.checkbox("Ajouter aussi au calendrier")
        date_plan = c_date.date_input("Date choisie", value=datetime.now())

        if st.form_submit_button("💾 Enregistrer la recette", use_container_width=True):
            if t and ing:
                f_date = date_plan.strftime("%d/%m/%Y")
                # 1. Envoi au Google Sheet
                payload = {
                    "action": "add", "titre": t, "categorie": cat, "source": src,
                    "image": img, "ingredients": ing, "preparation": pre,
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "date_prevue": f_date if plan_now else ""
                }
                if send_action(payload):
                    # 2. Envoi Calendrier si coché
                    if plan_now:
                        send_action({"action":"calendar", "titre": t, "date_prevue": f_date, "ingredients": ing})
                    st.session_state.page = "home"
                    st.rerun()
            else:
                st.error("Le titre et les ingrédients sont obligatoires.")

# --- PAGE: ÉPICERIE (AVEC SUPPRESSION ❌) ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste de Courses")
    if st.button("🗑 Tout vider"): st.session_state.shopping_list = []; st.rerun()
    
    for idx, item in enumerate(st.session_state.shopping_list):
        col_txt, col_del = st.columns([0.85, 0.15])
        col_txt.write(f"✅ **{item}**")
        if col_del.button("❌", key=f"del_{idx}"):
            st.session_state.shopping_list.pop(idx)
            st.rerun()

# --- PAGE: PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning des repas")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ''].sort_values('Date_Prevue')
        if plan.empty: st.info("Aucun repas planifié pour le moment.")
        else:
            for _, row in plan.iterrows():
                st.write(f"🗓 **{row['Date_Prevue']}** — {row['Titre']}")
