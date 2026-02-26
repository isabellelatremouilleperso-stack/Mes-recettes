import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup
import re
import json
import urllib.parse

# ======================================================
# 1. CONFIGURATION & DESIGN ORIGINAL
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

# Tes URLs
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS DE LOGIQUE (EXTENSIONS)
# ======================================================

def ventiler_vrac(texte_brut):
    """Analyse le texte pour extraire les champs spécifiques"""
    data = {"ing": "", "prep": "", "t_prepa": "", "t_cuisson": "", "port": ""}
    lignes = texte_brut.split('\n')
    mode = None
    for l in lignes:
        l_low = l.lower().strip()
        if not l_low: continue
        time_match = re.search(r'(\d+\s*(min|h|heure))', l_low)
        if "prep" in l_low and time_match: data["t_prepa"] = time_match.group(1)
        elif "cuisson" in l_low and time_match: data["t_cuisson"] = time_match.group(1)
        port_match = re.search(r'(\d+)\s*(pers|port|conv)', l_low)
        if port_match: data["port"] = port_match.group(1)
        if any(x in l_low for x in ["ingrédient", "ingredien", "liste"]): mode = "ing"; continue
        if any(x in l_low for x in ["préparation", "etapes", "instruction", "recette :"]): mode = "prep"; continue
        if mode == "ing": data["ing"] += l + "\n"
        elif mode == "prep": data["prep"] += l + "\n"
        else: data["ing"] += l + "\n"
    return data

def scrape_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        json_data = soup.find('script', type='application/ld+json')
        if json_data:
            try:
                d = json.loads(json_data.string)
                recipe = d if not isinstance(d, list) else next((i for i in d if i.get('@type') == 'Recipe'), None)
                if recipe:
                    title = recipe.get('name', '')
                    ing = "\n".join(recipe.get('recipeIngredient', []))
                    steps = recipe.get('recipeInstructions', [])
                    prep = "\n".join([s.get('text', str(s)) for s in steps]) if isinstance(steps, list) else str(steps)
                    return title, f"INGRÉDIENTS :\n{ing}\n\nPRÉPARATION :\n{prep}"
            except: pass
        title = soup.find('h1').text.strip() if soup.find('h1') else "Recette Importée"
        elements = soup.find_all(['li', 'p'])
        content = "\n".join(dict.fromkeys([el.text.strip() for el in elements if 10 < len(el.text.strip()) < 500]))
        return title, content
    except: return None, None

def send_action(payload):
    with st.spinner("🚀 Action en cours..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear(); return True
        except: pass
    return False

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        cols = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires','Note']
        df.columns = cols[:len(df.columns)]
        return df
    except: return pd.DataFrame()

# Initialisation session
if "page" not in st.session_state: st.session_state.page = "home"

# ======================================================
# 3. SIDEBAR (NAVIGATION)
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

# --- BIBLIOTHÈQUE ---
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

# --- AJOUTER (AVEC VENTILATION INTELLIGENTE) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    st.markdown('<a href="https://www.google.com/search?q=recettes+de+cuisine" target="_blank" style="text-decoration: none;"><div style="background-color: #4285F4; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px;">🔍 Chercher une idée sur Google</div></a>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔗 1. Import & Vrac", "🪄 2. Ventilation"])
    
    if 'temp_titre' not in st.session_state: st.session_state.temp_titre = ""
    if 'temp_content' not in st.session_state: st.session_state.temp_content = ""

    with tab1:
        url_link = st.text_input("Collez le lien ici")
        if st.button("🪄 Extraire"):
            t, c = scrape_url(url_link)
            if t:
                st.session_state.temp_titre, st.session_state.temp_content = t, c
                st.success("Extrait ! Passez à l'onglet 2.")
        st.divider()
        vrac_txt = st.text_area("OU Collez votre texte brut ici", value=st.session_state.temp_content, height=200)
        if st.button("🧬 Analyser le vrac"):
            st.session_state.temp_content = vrac_txt
            res = ventiler_vrac(vrac_txt)
            st.session_state.update(res)
            st.info("Données analysées. Vérifiez l'onglet 2.")

    # --- REMPLACE UNIQUEMENT LA PARTIE "TAB2" DANS TON CODE OU REPRENDS CE BLOC ---

    with tab2:
        with st.form("form_final"):
            f_t = st.text_input("Titre de la recette *", value=st.session_state.get('temp_titre', ""))
            f_cat = st.selectbox("Catégorie", CATEGORIES)
            
            # --- AJOUT DES URLS ---
            f_source = st.text_input("🔗 Lien de la source (Site web)", value=url_link if 'url_link' in locals() else "")
            f_video = st.text_input("🎥 Lien de la vidéo (YouTube, TikTok...)", value="")
            
            st.divider()
            
            c1, c2, c3 = st.columns(3)
            f_prepa = c1.text_input("⏳ Temps Prépa", value=st.session_state.get('t_prepa', ""))
            f_cuis = c2.text_input("🔥 Temps Cuisson", value=st.session_state.get('t_cuisson', ""))
            f_port = c3.text_input("🍽 Portions", value=st.session_state.get('port', ""))
            
            f_ing = st.text_area("🛒 Ingrédients (Isolés par l'analyse)", value=st.session_state.get('ing', ""), height=150)
            f_prep = st.text_area("📝 Étapes de préparation", value=st.session_state.get('prep', ""), height=200)
            
            f_img = st.text_input("🖼️ Lien de l'image (URL)", value="")
            
            if st.form_submit_button("🚀 ENREGISTRER TOUT DANS LE CLOUD"):
                # On prépare toutes les données pour ton Google Script
                payload = {
                    "action": "add",
                    "titre": f_t,
                    "categorie": f_cat,
                    "source": f_source,      # RÉINTÉGRÉ
                    "video": f_video,        # RÉINTÉGRÉ
                    "ingredients": f_ing,
                    "preparation": f_prep,
                    "Temps_Prepa": f_prepa,
                    "Temps_Cuisson": f_cuis,
                    "Portions": f_port,
                    "image": f_img,
                    "date": datetime.now().strftime("%d/%m/%Y")
                }
                
                if send_action(payload):
                    st.success("✅ Recette complète enregistrée !")
                    time.sleep(1)
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error("❌ Erreur lors de l'envoi. Vérifie ta connexion.")

# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    st.header(f"📖 {r['Titre']}")
    c_nav1, c_nav2, c_nav3 = st.columns([1.5, 1, 1])
    if c_nav1.button("⬅ Retour", key="nav_ret"): st.session_state.page = "home"; st.rerun()
    if c_nav3.button("🗑️ Supprimer", key="nav_del"):
        if send_action({"action": "delete", "titre": r['Titre']}):
            st.success("Supprimé !"); time.sleep(1); st.session_state.page = "home"; st.rerun()

    st.divider()
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        st.subheader("⭐ Note & Avis")
        n_note = st.slider("Note", 0, 5, int(float(r.get('Note',0))) if r.get('Note') else 0)
        n_comm = st.text_area("Commentaires", value=str(r.get('Commentaires', "")))
        if st.button("💾 Sauver l'avis"):
            if send_action({"action": "edit", "titre": r['Titre'], "Note": n_note, "Commentaires": n_comm}): st.toast("Avis mis à jour !")

    with col_r:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        sel_items = []
        for i, it in enumerate(ings):
            if st.checkbox(it, key=f"c_{i}"): sel_items.append(it)
        if st.button("📥 Ajouter à l'épicerie", type="primary"):
            for it in sel_items: send_action({"action": "add_shop", "article": it})
            st.toast("Ajouté !"); time.sleep(0.5); st.session_state.page = "shop"; st.rerun()

    st.divider()
    st.subheader("📝 Préparation")
    st.info(r['Préparation'] if r['Préparation'] else "Aucune étape.")

# --- ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    try:
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        if not df_s.empty:
            to_del = []
            for idx, row in df_s.iterrows():
                if st.checkbox(str(row.iloc[0]), key=f"sh_{idx}"): to_del.append(str(row.iloc[0]))
            c1, c2 = st.columns(2)
            if c1.button("🗑 Retirer cochés"):
                for it in to_del: send_action({"action": "remove_shop", "article": it})
                st.rerun()
            if c2.button("🧨 Tout vider"):
                send_action({"action": "clear_shop"}); st.rerun()
        else: st.info("Liste vide.")
    except: st.error("Erreur chargement.")

# --- AIDE ---
elif st.session_state.page == "help":
    st.title("❓ Aide")
    st.markdown("1. **Ajouter** : Collez une URL ou du texte brut, puis utilisez l'onglet Ventilation pour distribuer automatiquement les ingrédients et la préparation.\n2. **Épicerie** : Cochez dans la recette pour envoyer au panier.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

