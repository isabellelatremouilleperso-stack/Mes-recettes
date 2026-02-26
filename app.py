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

# Liens de données
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS DE GESTION
# ======================================================
def send_action(payload):
    with st.spinner("🚀 Action..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear(); time.sleep(0.5); return True
        except: pass
    return False

import json

def scrape_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # --- TENTATIVE 1 : Données structurées JSON-LD (La plus propre) ---
        json_data = soup.find('script', type='application/ld+json')
        if json_data:
            try:
                data = json.loads(json_data.string)
                # Parfois c'est une liste, on cherche l'objet 'Recipe'
                recipe = data if not isinstance(data, list) else next((item for item in data if item.get('@type') == 'Recipe'), None)
                
                if recipe:
                    title = recipe.get('name', '')
                    ingredients = "\n".join(recipe.get('recipeIngredient', []))
                    # La préparation peut être une liste d'étapes
                    steps = recipe.get('recipeInstructions', [])
                    if isinstance(steps, list):
                        prep = "\n".join([s.get('text', str(s)) for s in steps])
                    else:
                        prep = str(steps)
                    
                    full_content = f"🛒 INGRÉDIENTS :\n{ingredients}\n\n📝 PRÉPARATION :\n{prep}"
                    return title, full_content
            except: pass

        # --- TENTATIVE 2 : Sélecteurs classiques (Si JSON-LD échoue) ---
        title = soup.find('h1').text.strip() if soup.find('h1') else "Recette Importée"
        
        # On cherche spécifiquement les zones d'ingrédients souvent nommées par classe
        ingredients_tags = soup.select('[class*="ingredient"], [class*="list-ing"]')
        prep_tags = soup.select('[class*="instruction"], [class*="preparation"], [class*="step"]')
        
        if ingredients_tags or prep_tags:
            ing_text = "\n".join([el.text.strip() for el in ingredients_tags])
            prep_text = "\n".join([el.text.strip() for el in prep_tags])
            return title, f"🛒 INGRÉDIENTS :\n{ing_text}\n\n📝 PRÉPARATION :\n{prep_text}"

        # --- TENTATIVE 3 : Extraction brute (Dernier recours) ---
        elements = soup.find_all(['li', 'p'])
        content = "\n".join(dict.fromkeys([el.text.strip() for el in elements if 10 < len(el.text.strip()) < 500]))
        return title, content

    except Exception as e:
        return f"Erreur : {str(e)}", None

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        cols = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires','Note']
        df.columns = cols[:len(df.columns)]
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

# --- PLAYSTORE ---
if st.session_state.page == "playstore":
    st.markdown(f'<center><img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" class="logo-playstore"></center>', unsafe_allow_html=True)
    st.markdown("### Mes Recettes Pro\n👩‍🍳 Isabelle Latrémouille\n⭐ 4.9 ★ (128 avis)\n📥 1 000+ téléchargements")
    if st.button("📥 Installer", use_container_width=True): st.success("Application installée ! 🎉")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.image("https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg")
    c2.image("https://i.postimg.cc/YCkg460C/shared-image-(5).jpg")
    c3.image("https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg")

# --- PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning des Repas")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'].astype(str).str.strip() != ""].sort_values(by='Date_Prevue')
        for _, row in plan.iterrows():
            with st.expander(f"📌 {row['Date_Prevue']} : {row['Titre']}"):
                if st.button("Voir la fiche", key=f"p_{row['Titre']}"):
                    st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- BIBLIOTHÈQUE (ACCUEIL) ---
elif st.session_state.page == "home":
    c1, c2 = st.columns([4, 1])
    c1.header("📚 Ma Bibliothèque")
    if c2.button("🔄 Actualiser"): st.cache_data.clear(); st.rerun()
    st.divider()
    df = load_data()
    if not df.empty:
        col_search, col_cat = st.columns([2, 1])
        search = col_search.text_input("🔍 Rechercher...", placeholder="Ex: Lasagne...")
        liste_categories = ["Toutes"] + sorted([str(c) for c in df['Catégorie'].unique() if c])
        cat_choisie = col_cat.selectbox("📁 Catégorie", liste_categories)
        
        mask = df['Titre'].str.contains(search, case=False, na=False)
        if cat_choisie != "Toutes": mask = mask & (df['Catégorie'] == cat_choisie)
        rows = df[mask].reset_index(drop=True)
        
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><div class="recipe-title">{row["Titre"]}</div></div>', unsafe_allow_html=True)
                        if st.button("Voir la recette", key=f"v_{i+j}", use_container_width=True, type="primary"):
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

# --- AJOUTER ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    st.markdown('<a href="https://www.google.com/search?q=recettes+de+cuisine" target="_blank" style="text-decoration:none;"><div style="background-color:#4285F4;color:white;padding:10px;border-radius:10px;text-align:center;font-weight:bold;margin-bottom:20px;">🔍 Chercher une idée sur Google</div></a>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔗 1. Import URL", "📝 2. Tri & Vrac", "⌨️ 3. Manuel"])
    if 'temp_titre' not in st.session_state: st.session_state.temp_titre = ""
    if 'temp_content' not in st.session_state: st.session_state.temp_content = ""
    if 'temp_url' not in st.session_state: st.session_state.temp_url = ""

    with tab1:
        url_link = st.text_input("Collez le lien ici")
        if st.button("🪄 Extraire"):
            t, c = scrape_url(url_link)
            if t:
                st.session_state.temp_titre, st.session_state.temp_content, st.session_state.temp_url = t, c, url_link
                st.success("Extrait ! Passez à l'onglet 2.")

    with tab2:
        with st.form("v_f"):
            v_t = st.text_input("Titre *", value=st.session_state.temp_titre)
            v_cats = st.multiselect("Catégories", CATEGORIES)
            v_txt = st.text_area("Contenu", value=st.session_state.temp_content, height=250)
            v_src = st.text_input("Source", value=st.session_state.temp_url)
            if st.form_submit_button("🚀 Enregistrer"):
                send_action({"action": "add", "titre": v_t, "categorie": ", ".join(v_cats), "ingredients": v_txt, "preparation": "Import Vrac", "source": v_src, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

    with tab3:
        with st.form("m_f"):
            m_t = st.text_input("Titre *")
            m_cat = st.selectbox("Catégorie", CATEGORIES)
            m_ing = st.text_area("Ingrédients")
            m_pre = st.text_area("Préparation")
            if st.form_submit_button("💾 Enregistrer"):
                send_action({"action": "add", "titre": m_t, "categorie": m_cat, "ingredients": m_ing, "preparation": m_pre, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    st.header(f"📖 {r['Titre']}")
    
    c_nav1, c_nav2, c_nav3 = st.columns([1.5, 1, 1])
    if c_nav1.button("⬅ Retour", key="nav_ret"): st.session_state.page = "home"; st.rerun()
    if c_nav2.button("✏️ Éditer", key="nav_edit"): st.info("Modifiez dans Google Sheets pour l'instant"); pass
    if c_nav3.button("🗑️ Supprimer", key="nav_del"):
        if send_action({"action": "delete", "titre": r['Titre']}): st.success("Supprimé !"); time.sleep(1); st.session_state.page = "home"; st.rerun()

    st.divider()
    col_left, col_right = st.columns([1, 1.2])
    with col_left:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        
        # --- AJOUT DU SLIDER DE NOTE ET COMMENTAIRES ---
        st.subheader("⭐ Ma Note & Avis")
        curr_note = int(float(r.get('Note', 0))) if r.get('Note') else 0
        curr_comm = str(r.get('Commentaires', ""))
        new_note = st.slider("Note", 0, 5, curr_note, key="slider_note")
        new_comm = st.text_area("Mes commentaires", value=curr_comm, key="area_comm")
        if st.button("💾 Enregistrer l'avis", type="primary"):
            if send_action({"action": "edit", "titre": r['Titre'], "Note": new_note, "Commentaires": new_comm}):
                st.success("Avis mis à jour !"); time.sleep(0.5); st.rerun()

    with col_right:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        for i, ing in enumerate(ings):
            st.checkbox(ing, key=f"chk_{i}")
        if st.button("📥 Envoyer à l'épicerie", type="primary"):
            st.toast("Articles ajoutés !"); time.sleep(0.5); st.session_state.page = "shop"; st.rerun()

    st.divider()
    st.subheader("📝 Préparation")
    st.info(r['Préparation'] if r['Préparation'] else "Aucune étape.")

# --- ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    st.info("Fonctionnalité connectée à votre GSheet Shop.")

# --- AIDE ---
elif st.session_state.page == "help":
    st.title("❓ Aide")
    st.write("1. Ajoutez via URL ou manuel.\n2. Cochez les ingrédients pour l'épicerie.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

