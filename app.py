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
    
    st.divider()
    st.subheader("🔍 Google")
    q_google = st.text_input("Recette :")
    if q_google:
        link = f"https://www.google.com/search?q={urllib.parse.quote('recette ' + q_google)}"
        st.link_button("🌐 Chercher", link, use_container_width=True)

# ======================================================
# 4. PAGES
# ======================================================

# --- ACCUEIL (AVEC BOUTON ACTUALISER) ---
if st.session_state.page == "home":
    c1, c2 = st.columns([4, 1])
    c1.header("📚 Bibliothèque")
    if c2.button("🔄 Actualiser"): st.cache_data.clear(); st.rerun()
    
    df = load_data()
    search = st.text_input("🔍 Rechercher")
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

# --- ÉPICERIE (CASES À COCHER + SUPPRESSION SÉLECTIVE) ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    
    try:
        # On charge la liste actuelle
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}")
        if not df_s.empty:
            articles_selectionnes = []
            for idx, row in df_s.iterrows():
                article = row.iloc[0]
                # Chaque article a sa case à cocher
                if st.checkbox(f"{article}", key=f"shop_{idx}"):
                    articles_selectionnes.append(article)
            
            st.divider()
            col_del1, col_del2 = st.columns(2)
            
            # Bouton pour retirer seulement les cochés
            if col_del1.button("🗑 Retirer articles cochés", use_container_width=True):
                if articles_selectionnes:
                    for item in articles_selectionnes:
                        send_action({"action": "remove_shop", "article": item})
                    st.success("Articles retirés !"); time.sleep(0.5); st.rerun()
                else:
                    st.warning("Cochez des articles à supprimer.")
            
            # Bouton pour tout effacer (au cas où)
            if col_del2.button("🧨 TOUT EFFACER", type="secondary", use_container_width=True):
                send_action({"action": "clear_shop"}); st.rerun()
        else:
            st.info("Votre liste d'épicerie est vide.")
    except:
        st.info("Votre liste d'épicerie est vide.")

# --- PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning des Repas")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ""].sort_values(by='Date_Prevue')
        if not plan.empty:
            for _, row in plan.iterrows():
                with st.expander(f"{row['Date_Prevue']} - {row['Titre']}"):
                    if st.button("Voir la fiche", key=f"p_{row['Titre']}"):
                        st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
        else:
            st.info("Aucun repas planifié.")

# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    st.title(f"🍳 {r['Titre']}")
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        date_p = st.text_input("Date JJ/MM/AAAA", value=r.get('Date_Prevue', ''))
        if st.button("📅 Enregistrer au planning", use_container_width=True):
            send_action({"action": "update_notes", "titre": r['Titre'], "date_prevue": date_p}); st.rerun()
        
    with col_r:
        st.subheader("🛒 Ingrédients")
        lignes_ing = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        selection_recette = []
        for i, ligne in enumerate(lignes_ing):
            if st.checkbox(ligne, key=f"rec_{i}"): selection_recette.append(ligne)
        
        if st.button("📥 AJOUTER À L'ÉPICERIE", type="primary", use_container_width=True):
            if selection_recette:
                for item in selection_recette: send_action({"action": "add_shop", "article": item})
                st.success("Ajouté !"); time.sleep(0.5)

        st.divider()
        st.subheader("📝 Préparation")
        st.write(r['Préparation'])

# --- AJOUTER RECETTE ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    t1, t2, t3 = st.tabs(["🔗 URL", "📝 Vrac", "⌨️ Manuel"])
    with t3:
        with st.form("man"):
            m_t = st.text_input("Titre *")
            m_cats = st.multiselect("Catégories", CATEGORIES)
            c1, c2, c3 = st.columns(3)
            m_por = c1.text_input("Portions")
            m_pre = c2.text_input("Prépa")
            m_cui = c3.text_input("Cuisson")
            m_ing = st.text_area("Ingrédients (un par ligne)")
            m_eta = st.text_area("Préparation")
            m_img = st.text_input("URL Image")
            if st.form_submit_button("💾 Sauver"):
                send_action({"action": "add", "titre": m_t, "categorie": ", ".join(m_cats), "ingredients": m_ing, "preparation": m_eta, "portions": m_por, "temps_prepa": m_pre, "temps_cuisson": m_cui, "image": m_img, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

# --- AIDE ---
elif st.session_state.page == "help":
    st.title("❓ Aide")
    st.write("- **Actualiser** : met à jour la liste depuis Google Sheets.\n- **Épicerie** : cochez ce que vous avez acheté et cliquez sur 'Retirer articles cochés'.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
