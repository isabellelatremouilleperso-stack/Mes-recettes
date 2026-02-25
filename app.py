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

# Style CSS regroupé pour éviter les erreurs de syntaxe
CSS_STYLE = """
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }
    .recipe-card {
        background-color: #1e2129; 
        border: 1px solid #3d4455;
        border-radius: 12px; 
        padding: 10px; 
        height: 230px; 
        display: flex; 
        flex-direction: column;
    }
    .recipe-img { width: 100%; height: 130px; object-fit: cover; border-radius: 8px; }
    .recipe-title {
        color: white; margin-top: 8px; font-size: 0.9rem; font-weight: bold;
        display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
        overflow: hidden; height: 2.6em; line-height: 1.3;
    }
    .app-header { display: flex; align-items: center; gap: 20px; }
    header {visibility: hidden;} 
    .stDeployButton {display:none;}
</style>
"""
st.markdown(CSS_STYLE, unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS DE BASE
# ======================================================
def send_action(payload):
    with st.spinner("🚀 Action..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear()
                time.sleep(0.5)
                return True
        except: pass
    return False

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        cols = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires','Note']
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
    if st.button("⭐ Play Store", use_container_width=True): st.session_state.page = "playstore"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): st.session_state.page = "help"; st.rerun()

# ======================================================
# 4. PAGES
# ======================================================

# --- PAGE PLAY STORE ---
if st.session_state.page == "playstore":
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    st.image("https://via.placeholder.com/100", width=100)
    st.markdown("""
    ### Mes Recettes Pro  
    👩‍🍳 Isabelle Latrémouille  
    ⭐ 4.9 ★ (128 avis)  
    📥 1 000+ téléchargements  
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, _ = st.columns([1,3])
    with col1:
        if st.button("📥 Installer", use_container_width=True):
            st.success("Application installée avec succès ! 🎉")

    st.divider()
    st.subheader("📸 Aperçu")
    c1, c2, c3 = st.columns(3)
    c1.image("https://via.placeholder.com/250x500")
    c2.image("https://via.placeholder.com/250x500")
    c3.image("https://via.placeholder.com/250x500")

    st.divider()
    st.subheader("📝 À propos de cette application")
    st.write("Mes Recettes Pro est une application complète de gestion culinaire.")
    st.write("✔ Gestion des recettes | ✔ Système de notes ⭐ | ✔ Planning intégré 📅 | ✔ Liste d'épicerie intelligente 🛒")

    st.divider()
    st.subheader("ℹ️ Informations")
    st.write("Version : 2.0 Premium | Mise à jour : Février 2026 | Développeur : Isabelle Latrémouille")

# --- BIBLIOTHÈQUE ---
elif st.session_state.page == "home":
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

# --- AJOUTER RECETTE ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    t1, t2, t3 = st.tabs(["🔗 URL", "📝 Vrac", "⌨️ Manuel"])
    
    with t2: # Focus sur le Vrac complet
        with st.form("vrac_v3"):
            v_t = st.text_input("Titre *")
            v_cats = st.multiselect("Catégories", CATEGORIES)
            c1, c2, c3 = st.columns(3)
            v_por = c1.text_input("Portions")
            v_pre = c2.text_input("Préparation")
            v_cui = c3.text_input("Cuisson")
            v_txt = st.text_area("Ingrédients et Étapes", height=200)
            if st.form_submit_button("🚀 Sauver"):
                send_action({"action": "add", "titre": v_t, "categorie": ", ".join(v_cats), "ingredients": v_txt, "portions": v_por, "temps_prepa": v_pre, "temps_cuisson": v_cui, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

    with t3: # Manuel complet
        with st.form("manuel_v3"):
            m_t = st.text_input("Titre de la recette *")
            m_cats = st.multiselect("Catégories", CATEGORIES)
            c1, c2, c3 = st.columns(3)
            m_por = c1.text_input("Portions")
            m_pre = c2.text_input("Temps Prépa")
            m_cui = c3.text_input("Temps Cuisson")
            m_ing = st.text_area("Ingrédients")
            m_prepa = st.text_area("Préparation")
            m_img = st.text_input("URL Image")
            if st.form_submit_button("💾 Enregistrer"):
                send_action({"action": "add", "titre": m_t, "categorie": ", ".join(m_cats), "ingredients": m_ing, "preparation": m_prepa, "portions": m_por, "temps_prepa": m_pre, "temps_cuisson": m_cui, "image": m_img, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

# --- DÉTAILS (ÉTOILES ET NOTES) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.title(f"🍳 {r['Titre']}")
    # Affichage des étoiles
    try: n_val = int(float(r.get('Note', 0)))
    except: n_val = 0
    st.write("⭐" * n_val + "☆" * (5 - n_val))

    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        st.divider()
        new_note = st.selectbox("Ma note", [1, 2, 3, 4, 5], index=(n_val-1 if 1<=n_val<=5 else 4))
        new_comm = st.text_area("Commentaires", value=r.get('Commentaires', ''))
        new_plan = st.text_input("Planning (JJ/MM/AAAA)", value=r.get('Date_Prevue', ''))
        if st.button("💾 Sauvegarder les notes/planning", use_container_width=True):
            send_action({"action": "update_notes", "titre": r['Titre'], "date_prevue": new_plan, "commentaires": new_comm, "note": new_note})
            st.rerun()

    with c2:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        sel_ing = []
        for i, l in enumerate(ings):
            if st.checkbox(l, key=f"ing_{i}"): sel_ing.append(l)
        if st.button("📥 Ajouter à l'épicerie"):
            for x in sel_ing: send_action({"action": "add_shop", "article": x})
            st.success("Ajouté !")
        st.divider()
        st.subheader("📝 Étapes")
        st.write(r['Préparation'])

# --- ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    try:
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        if not df_s.empty:
            to_del = []
            for idx, row in df_s.iterrows():
                if st.checkbox(row.iloc[0], key=f"shop_{idx}"): to_del.append(row.iloc[0])
            if st.button("🗑 Retirer articles cochés"):
                for item in to_del: send_action({"action": "remove_shop", "article": item})
                st.rerun()
    except: st.info("Liste vide.")

# --- PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ""].sort_values(by='Date_Prevue')
        for _, row in plan.iterrows():
            st.write(f"📌 **{row['Date_Prevue']}** : {row['Titre']}")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- AIDE ---
elif st.session_state.page == "help":
    st.title("❓ Aide")
    st.write("Utilisez le menu pour naviguer. La page Play Store simule l'installation de votre application.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
