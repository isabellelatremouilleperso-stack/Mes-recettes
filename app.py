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

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. LOGIQUE (VENTILATION & SCRAPING)
# ======================================================

def ventiler_vrac(texte_brut):
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
        cols = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires','Note','Video']
        df.columns = cols[:len(df.columns)]
        return df
    except: return pd.DataFrame()

# ======================================================
# 3. NAVIGATION (MENU LATÉRAL)
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"

with st.sidebar:
    st.title("👨‍🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("🛒 Ma Liste d'épicerie", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER RECETTE", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    st.divider()
    if st.button("⭐ Play Store", use_container_width=True): st.session_state.page = "playstore"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): st.session_state.page = "help"; st.rerun()

# ======================================================
# 4. PAGES
# ======================================================

# --- PLAYSTORE (RÉINTÉGRÉ) ---
if st.session_state.page == "playstore":
    st.markdown(f'<center><img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" class="logo-playstore"></center>', unsafe_allow_html=True)
    st.markdown("### Mes Recettes Pro\n**Édition Premium**\n👩‍🍳 Isabelle Latrémouille\n⭐ 4.9 ★ (128 avis)\n📥 1 000+ téléchargements")
    if st.button("📥 Installer l'application", use_container_width=True): st.success("L'application est déjà synchronisée avec votre compte ! 🎉")
    st.divider()
    st.subheader("Aperçus")
    c1, c2, c3 = st.columns(3)
    c1.image("https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg")
    c2.image("https://i.postimg.cc/YCkg460C/shared-image-(5).jpg")
    c3.image("https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- AIDE (RÉINTÉGRÉ) ---
elif st.session_state.page == "help":
    st.title("❓ Aide & Support")
    st.info("Besoin d'aide pour utiliser votre livre de recettes numérique ?")
    st.markdown("""
    - **Importer une recette** : Collez le lien d'un site (Marmiton, CuisineAZ...) dans l'onglet AJOUTER et cliquez sur 'Extraire'.
    - **Ventilation** : L'onglet 2 de l'ajout permet de séparer automatiquement les ingrédients des étapes.
    - **Liste de courses** : Dans la fiche d'une recette, cochez les ingrédients manquants et cliquez sur 'Envoyer à l'épicerie'.
    - **Synchronisation** : Toutes vos recettes sont enregistrées en temps réel dans votre Google Sheets.
    """)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- AJOUTER (AVEC VENTILATION) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    tab1, tab2 = st.tabs(["🔗 1. Import / Vrac", "🪄 2. Détails & Ventilation"])
    
    with tab1:
        url_link = st.text_input("Collez le lien ici")
        if st.button("🪄 Extraire"):
            t, c = scrape_url(url_link)
            if t:
                st.session_state.temp_titre, st.session_state.temp_content = t, c
                st.session_state.temp_source = url_link
                st.success("Extrait avec succès ! Vérifiez l'onglet 2.")
        st.divider()
        vrac_txt = st.text_area("OU Collez votre texte brut ici", value=st.session_state.get('temp_content', ""), height=200)
        if st.button("🧬 Analyser le vrac"):
            st.session_state.temp_content = vrac_txt
            res = ventiler_vrac(vrac_txt)
            st.session_state.update(res)
            st.info("Analyse terminée. Allez à l'onglet 2 pour valider.")

    with tab2:
        with st.form("form_final"):
            f_t = st.text_input("Titre *", value=st.session_state.get('temp_titre', ""))
            f_cat = st.selectbox("Catégorie", CATEGORIES)
            
            c_u1, c_u2 = st.columns(2)
            f_source = c_u1.text_input("🔗 Source (Site)", value=st.session_state.get('temp_source', ""))
            f_video = c_u2.text_input("🎥 Vidéo (YouTube/TikTok)", value="")
            f_img = st.text_input("🖼️ Image (Lien)", value="")
            
            st.divider()
            c1, c2, c3 = st.columns(3)
            f_prepa = c1.text_input("⏳ Prépa", value=st.session_state.get('t_prepa', ""))
            f_cuis = c2.text_input("🔥 Cuisson", value=st.session_state.get('t_cuisson', ""))
            f_port = c3.text_input("🍽 Portions", value=st.session_state.get('port', ""))
            
            f_ing = st.text_area("🛒 Ingrédients", value=st.session_state.get('ing', ""), height=150)
            f_prep = st.text_area("📝 Préparation", value=st.session_state.get('prep', ""), height=150)
            
            if st.form_submit_button("🚀 ENREGISTRER"):
                payload = {
                    "action": "add", "titre": f_t, "categorie": f_cat,
                    "source": f_source, "video": f_video, "image": f_img,
                    "ingredients": f_ing, "preparation": f_prep,
                    "Temps_Prepa": f_prepa, "Temps_Cuisson": f_cuis, "Portions": f_port,
                    "date": datetime.now().strftime("%d/%m/%Y")
                }
                if send_action(payload):
                    st.success("Recette enregistrée !"); time.sleep(1); st.session_state.page = "home"; st.rerun()

# --- BIBLIOTHÈQUE & DÉTAILS ---
elif st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if not df.empty:
        c_sch, c_ct = st.columns([2, 1])
        search = c_sch.text_input("🔍 Rechercher...")
        cat_list = ["Toutes"] + sorted(df['Catégorie'].unique().tolist())
        cat_pick = c_ct.selectbox("Filtre", cat_list)
        mask = df['Titre'].str.contains(search, case=False, na=False)
        if cat_pick != "Toutes": mask = mask & (df['Catégorie'] == cat_pick)
        rows = df[mask]
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(rows):
                    row = rows.iloc[i+j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><div class="recipe-title">{row["Titre"]}</div></div>', unsafe_allow_html=True)
                        if st.button("Voir", key=f"btn_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    st.header(f"📖 {r['Titre']}")
    
    if r.get('Video') and "http" in str(r['Video']):
        st.video(r['Video'])
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        if r.get('Source'): st.link_button("🔗 Source Originale", r['Source'], use_container_width=True)
        st.write(f"⏱ {r.get('Temps_Prepa', '-')} | 🔥 {r.get('Temps_Cuisson', '-')} | 🍽 {r.get('Portions', '-')}")

    with col_r:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        sel = []
        for i, it in enumerate(ings):
            if st.checkbox(it, key=f"ck_{i}"): sel.append(it)
        if st.button("📥 Envoyer à l'épicerie"):
            for it in sel: send_action({"action": "add_shop", "article": it})
            st.toast("Ajouté !"); time.sleep(0.5); st.session_state.page = "shop"; st.rerun()
    st.divider()
    st.subheader("📝 Préparation")
    st.info(r['Préparation'])

# --- ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    try:
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        for idx, row in df_s.iterrows():
            if st.checkbox(str(row.iloc[0]), key=f"s_{idx}"):
                send_action({"action": "remove_shop", "article": str(row.iloc[0])})
                st.rerun()
    except: st.info("Liste vide.")
