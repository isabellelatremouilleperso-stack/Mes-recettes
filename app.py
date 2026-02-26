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
        border-radius: 12px; padding: 10px; height: 260px; 
        display: flex; flex-direction: column; align-items: center;
    }
    .recipe-img-card { width: 100%; height: 140px; object-fit: cover; border-radius: 8px; margin-bottom: 10px; }
    .recipe-title {
        color: white; font-size: 1rem; font-weight: bold;
        text-align: center; height: 2.5em; overflow: hidden;
    }
    
    /* Design Play Store Wow */
    .store-container {
        background-color: #161b22; padding: 30px; border-radius: 20px;
        border: 1px solid #30363d; text-align: center;
    }
    .install-btn {
        background: linear-gradient(90deg, #00c853, #64dd17);
        color: white !important; padding: 12px 40px; border-radius: 10px;
        font-weight: bold; text-decoration: none; display: inline-block; margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Connexions
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS
# ======================================================

def send_action(payload):
    with st.spinner("🚀 Synchronisation..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear()
                return True
        except: pass
    return False

@st.cache_data(ttl=5)
def load_data(url):
    try:
        df = pd.read_csv(f"{url}&nocache={time.time()}").fillna('')
        if url == URL_CSV:
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
    if st.button("🛒 Ma Liste d'épicerie", use_container_width=True): st.session_state.page = "shop"; st.rerun()
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
    df = load_data(URL_CSV)
    if not df.empty:
        search = st.text_input("🔍 Rechercher une recette...")
        filtered_df = df[df['Titre'].str.contains(search, case=False)]
        
        for i in range(0, len(filtered_df), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(filtered_df):
                    row = filtered_df.iloc[i+j]
                    with cols[j]:
                        img_url = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f"""
                            <div class="recipe-card">
                                <img src="{img_url}" class="recipe-img-card">
                                <div class="recipe-title">{row['Titre']}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Ouvrir", key=f"b_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"
                            st.rerun()

# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    col_back, col_del = st.columns([4, 1])
    if col_back.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    # Bouton Supprimer
    if col_del.button("🗑️ Supprimer"):
        if send_action({"action": "delete", "titre": r['Titre']}):
            st.success("Recette supprimée !"); time.sleep(1); st.session_state.page = "home"; st.rerun()

    st.header(f"📖 {r['Titre']}")
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        
        # --- NOTES ---
        st.subheader("⭐ Ma Note")
        try: current_note = int(float(r.get('Note', 0)))
        except: current_note = 0
        n_note = st.slider("Note sur 5", 0, 5, current_note)
        n_comm = st.text_area("Mes commentaires perso", value=str(r.get('Commentaires', "")))
        
        if st.button("💾 Sauvegarder mon avis"):
            send_action({"action": "edit", "titre": r['Titre'], "Note": n_note, "Commentaires": n_comm})
            st.toast("Avis enregistré ! ⭐")
        
        st.divider()
        st.subheader("📅 Planifier")
        d_plan = st.date_input("Date du repas")
        if st.button("Ajouter au planning"):
            send_action({"action": "edit", "titre": r['Titre'], "Date_Prevue": d_plan.strftime("%Y-%m-%d")})
            st.success("Planifié !")

    with col_r:
        if r.get('Video') and "http" in str(r['Video']): st.video(r['Video'])
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        sel = []
        for i, it in enumerate(ings):
            if st.checkbox(it, key=f"c_{i}"): sel.append(it)
        if st.button("📥 Envoyer à l'épicerie"):
            for it in sel: send_action({"action": "add_shop", "article": it})
            st.toast("Envoyé !"); time.sleep(0.5); st.session_state.page = "shop"; st.rerun()

    st.divider()
    st.subheader("📝 Préparation")
    st.info(r['Préparation'])

# --- PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data(URL_CSV)
    plan = df[df['Date_Prevue'].astype(str).str.strip() != ""]
    if not plan.empty:
        plan = plan.sort_values(by='Date_Prevue')
        for _, row in plan.iterrows():
            with st.expander(f"📌 {row['Date_Prevue']} : {row['Titre']}"):
                if st.button("Voir la fiche", key=f"p_{row['Titre']}"):
                    st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
    else:
        st.info("Aucun repas planifié pour le moment.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Liste d'épicerie")
    df_shop = load_data(URL_CSV_SHOP)
    if not df_shop.empty:
        for idx, row in df_shop.iterrows():
            c1, c2 = st.columns([4, 1])
            c1.write(f"• {row.iloc[0]}")
            if c2.button("🗑️", key=f"del_{idx}"):
                send_action({"action": "delete_shop", "article": row.iloc[0]})
                st.rerun()
    else:
        st.info("La liste est vide.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- PLAY STORE WOW ---
elif st.session_state.page == "playstore":
    st.markdown("""
        <div class="store-container">
            <h1>🍳 Mes Recettes Pro</h1>
            <p>L'application culinaire n°1 pour organiser votre cuisine.</p>
            <a href="#" class="install-btn">INSTALLER</a>
            <div style="display: flex; justify-content: center; gap: 10px; margin-top: 20px;">
                <img src="https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg" width="200" style="border-radius:10px">
                <img src="https://i.postimg.cc/YCkg460C/shared-image-(5).jpg" width="200" style="border-radius:10px">
                <img src="https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg" width="200" style="border-radius:10px">
            </div>
        </div>
    """, unsafe_allow_html=True)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- AJOUTER ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    with st.form("add_form"):
        f_t = st.text_input("Titre")
        f_cat = st.selectbox("Catégorie", CATEGORIES)
        f_ing = st.text_area("Ingrédients (un par ligne)")
        f_pre = st.text_area("Préparation")
        f_img = st.text_input("Lien Image URL")
        if st.form_submit_button("Enregistrer"):
            payload = {"action":"add","titre":f_t,"categorie":f_cat,"ingredients":f_ing,"preparation":f_pre,"image":f_img,"date":datetime.now().strftime("%d/%m/%Y")}
            if send_action(payload): st.session_state.page="home"; st.rerun()

# ... (Partie imports et style identique au message précédent)

# ======================================================
# 4. LES PAGES (LOGIQUE COMPLÈTE)
# ======================================================

# --- PAGE ÉPICERIE (FONCTIONNELLE) ---
if st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    df_shop = load_data(URL_CSV_SHOP)
    
    if not df_shop.empty:
        # Affichage propre avec bouton de suppression pour chaque item
        for idx, row in df_shop.iterrows():
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"✅ **{row.iloc[0]}**")
            if c2.button("🗑️", key=f"del_{idx}"):
                if send_action({"action": "delete_shop", "article": row.iloc[0]}):
                    st.rerun()
        
        st.divider()
        if st.button("🧹 Vider toute la liste", type="secondary"):
            if send_action({"action": "clear_shop"}):
                st.rerun()
    else:
        st.info("Votre liste d'épicerie est vide. Ajoutez des ingrédients depuis une fiche recette !")
    
    if st.button("⬅ Retour à la bibliothèque"):
        st.session_state.page = "home"; st.rerun()

# --- PAGE AIDE (DÉTAILLÉE) ---
elif st.session_state.page == "help":
    st.header("❓ Centre d'aide")
    
    st.subheader("1. Comment ajouter des ingrédients à l'épicerie ?")
    st.write("Ouvrez une recette, cochez les cases à côté des ingrédients dont vous avez besoin, puis cliquez sur le bouton **'Envoyer à l'épicerie'**.")
    
    st.subheader("2. Comment planifier un repas ?")
    st.write("Dans la fiche recette, utilisez le calendrier pour choisir une date et cliquez sur **'Ajouter au planning'**. Vous retrouverez tous vos repas dans l'onglet **'Planning Repas'** du menu latéral.")
    
    st.subheader("3. Sauvegarder en PDF")
    st.info("Pour garder une copie physique : ouvrez une recette, faites un clic droit sur la page et choisissez 'Imprimer' > 'Enregistrer au format PDF'.")
    
    if st.button("⬅ Retour"):
        st.session_state.page = "home"; st.rerun()

# --- PAGE DÉTAILS (CORRIGÉE AVEC LIEN ÉPICERIE) ---
elif st.session_state.page == "details":
    # (Ici se trouve le code que je t'ai donné précédemment avec le bouton "Envoyer à l'épicerie")
    # Assure-toi que la variable 'sel' accumule bien les ingrédients cochés.
