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
    /* 1. FOND ET TITRES */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }

    /* 2. LISTE D'ÉPICERIE */
    .stCheckbox label p {
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }

    /* 3. SAISIE ET RECHERCHE */
    input, select, textarea, div[data-baseweb="select"] {
        color: white !important;
        background-color: #1e2129 !important;
    }
    label, .stMarkdown p { color: white !important; }

    /* 4. CARTES DE RECETTES */
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

    /* 5. BOUTONS & AIDE */
    .logo-playstore {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; border: 3px solid #e67e22; margin-bottom: 20px;
    }
    .help-box {
        background-color: #1e2130; padding: 20px; border-radius: 15px;
        border-left: 5px solid #e67e22; margin-bottom: 20px;
    }
    .help-box h3 { color: #e67e22; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

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

def scrape_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "Recette Importée"
        elements = soup.find_all(['li', 'p'])
        content = "\n".join(dict.fromkeys([el.text.strip() for el in elements if 10 < len(el.text.strip()) < 500]))
        return title, content
    except: return None, None

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
# 3. SIDEBAR (Version Originale Restaurée)
# ======================================================
with st.sidebar:
    # On utilise la méthode directe qui fonctionnait au début
    st.image("https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png", width=100)
    
    st.title("🍳 Mes Recettes")

    # NAVIGATION (Vérifie bien qu'il n'y a pas de doublons en dessous !)
    if st.button("📚 Bibliothèque", use_container_width=True, key="side_home"): 
        st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning Repas", use_container_width=True, key="side_plan"): 
        st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Ma Liste d'épicerie", use_container_width=True, key="side_shop"): 
        st.session_state.page = "shop"; st.rerun()
    
    st.divider()
    
    if st.button("➕ AJOUTER RECETTE", type="primary", use_container_width=True, key="side_add"): 
        st.session_state.page = "add"; st.rerun()
    if st.button("⭐ Play Store", use_container_width=True, key="side_play"): 
        st.session_state.page = "playstore"; st.rerun()
    if st.button("❓ Aide", use_container_width=True, key="side_help"): 
        st.session_state.page = "help"; st.rerun()
# ======================================================
# 4. PAGES
# ======================================================

# --- PAGE ACCUEIL ---
if st.session_state.page == "home":
    c1, c2 = st.columns([4, 1])
    c1.header("📚 Ma Bibliothèque")
    if c2.button("🔄 Actualiser"): 
        st.cache_data.clear(); st.rerun()
    
    st.divider()
    df = load_data()
    
    if not df.empty:
        col_search, col_cat = st.columns([2, 1])
        with col_search:
            search = st.text_input("🔍 Rechercher...", placeholder="Ex: Lasagne...")
        with col_cat:
            liste_categories = ["Toutes"] + sorted([str(c) for c in df['Catégorie'].unique() if c])
            cat_choisie = st.selectbox("📁 Catégorie", liste_categories)
        
        mask = df['Titre'].str.contains(search, case=False, na=False)
        if cat_choisie != "Toutes":
            mask = mask & (df['Catégorie'] == cat_choisie)
            
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
    else:
        st.warning("Aucune donnée trouvée.")

# --- PAGE DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    st.header(f"📖 {r['Titre']}")
    
    c_nav1, c_nav2, c_nav3 = st.columns([1.5, 1, 1])
    if c_nav1.button("⬅ Retour", key="det_back"): st.session_state.page = "home"; st.rerun()
    if c_nav2.button("✏️ Éditer", key="det_edit"): st.session_state.page = "edit"; st.rerun()
    if c_nav3.button("🗑️", key="det_del"): st.session_state.confirm_delete = True

    if st.session_state.get('confirm_delete', False):
        st.error("⚠️ Supprimer ?")
        conf1, conf2 = st.columns(2)
        if conf1.button("✅ OUI", key="c_yes"):
            if send_action({"action": "delete", "titre": r['Titre']}):
                st.session_state.confirm_delete = False; st.session_state.page = "home"; st.rerun()
        if conf2.button("❌ NON", key="c_no"): st.session_state.confirm_delete = False; st.rerun()

    st.divider()
    c1, c2 = st.columns([1, 1.2])
    with c1:
        img_url = r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400"
        st.image(img_url, use_container_width=True)
        if r.get('Source') and "http" in str(r['Source']):
            st.link_button("🌐 Voir la source", r['Source'], use_container_width=True)
    with c2:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        sel = []
        for i, l in enumerate(ings):
            if st.checkbox(l, key=f"chk_{i}"): sel.append(l)
        if st.button("📥 Panier", type="primary"):
            for it in sel: send_action({"action": "add_shop", "article": it})
            st.toast("Ajouté !"); time.sleep(0.5); st.session_state.page = "shop"; st.rerun()

    st.divider()
    st.subheader("📝 Préparation")
    st.info(r['Préparation'] if r['Préparation'] else "Aucune étape.")

# --- PAGE AJOUTER (Version avec URL, Vidéo et Vrac) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    
    # On utilise 3 onglets pour que tu aies toutes les options sous la main
    tab1, tab2, tab3 = st.tabs(["🌐 Site Web (Auto)", "🎬 Lien Vidéo", "📝 Vrac / Manuel"])

    # --- 1. L'IMPORTATION URL ---
    with tab1:
        st.subheader("Extraire depuis un site")
        web_url = st.text_input("Collez l'URL ici", key="web_url_input")
        if st.button("🔍 Analyser le site"):
            if web_url:
                with st.spinner("Analyse..."):
                    titre, contenu = scrape_url(web_url)
                    if titre:
                        # Tri intelligent automatique mais modifiable
                        lignes = contenu.split('\n')
                        tri = [l.strip() for l in lignes if 10 < len(l.strip()) < 350]
                        st.session_state.temp_titre = titre
                        st.session_state.temp_contenu = "\n".join(tri)
        
        if "temp_titre" in st.session_state:
            t_edit = st.text_input("Titre extrait", value=st.session_state.temp_titre)
            c_edit = st.text_area("Contenu extrait (Triez ici !)", value=st.session_state.temp_contenu, height=250)
            if st.button("💾 Enregistrer cet import"):
                send_action({"action": "add", "titre": t_edit, "preparation": c_edit, "source": web_url, "date": datetime.now().strftime("%d/%m/%Y")})
                del st.session_state.temp_titre
                st.session_state.page = "home"; st.rerun()

    # --- 2. L'IMPORTATION VIDÉO ---
    with tab2:
        st.subheader("Lien Vidéo")
        s_url = st.text_input("Lien Insta/TikTok/FB", key="vid_url")
        s_t = st.text_input("Nom de la recette", key="vid_titre")
        if st.button("🚀 Sauvegarder Vidéo"):
            send_action({"action": "add", "titre": s_t, "source": s_url, "preparation": f"Vidéo : {s_url}", "date": datetime.now().strftime("%d/%m/%Y")})
            st.session_state.page = "home"; st.rerun()

    # --- 3. L'OPTION VRAC / MANUEL (Celle que tu voulais garder) ---
    with tab3:
        st.subheader("Saisie libre (Vrac)")
        st.info("Collez votre texte ici, triez-le comme vous voulez, puis enregistrez.")
        
        # On utilise un formulaire pour le vrac/manuel
        with st.form("form_vrac"):
            v_t = st.text_input("Titre de la recette *")
            v_cat = st.selectbox("Catégorie", CATEGORIES)
            v_txt = st.text_area("Collez votre texte brut ou vos ingrédients ici", height=300, 
                                 help="Vous pouvez copier-coller un bloc de texte et supprimer ce qui ne sert à rien.")
            
            submit_vrac = st.form_submit_button("💾 Enregistrer la recette")
            
            if submit_vrac:
                if v_t:
                    send_action({
                        "action": "add", 
                        "titre": v_t, 
                        "catégorie": v_cat,
                        "ingredients": v_txt, # Dans le vrac, on met tout dans ingrédients pour que tu puisses trier après
                        "date": datetime.now().strftime("%d/%m/%Y")
                    })
                    st.session_state.page = "home"; st.rerun()
                else:
                    st.error("Le titre est obligatoire.")
# --- PAGE ÉPICERIE ---
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
            if c1.button("🗑 Retirer"):
                for it in to_del: send_action({"action": "remove_shop", "article": it})
                st.rerun()
            if c2.button("🧨 Vider"): send_action({"action": "clear_shop"}); st.rerun()
        else: st.info("Liste vide.")
    except: st.error("Erreur.")

# --- PAGE PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'].astype(str).str.strip() != ""].sort_values(by='Date_Prevue')
        for _, row in plan.iterrows():
            with st.expander(f"📌 {row['Date_Prevue']} : {row['Titre']}"):
                if st.button("Voir la fiche", key=f"p_{row['Titre']}"):
                    st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE PLAY STORE
# ======================================================
elif st.session_state.page == "playstore":

    # 1. STYLE POUR LE CENTRAGE ET LE LOGO ROND
    st.markdown("""
    <style>
    .playstore-container {
        display: flex;
        flex-direction: column;
        align-items: center; /* Centre horizontalement */
        justify-content: center;
        text-align: center;
        width: 100%;
        margin-bottom: 20px;
    }
    .logo-rond-centre {
        width: 120px !important;
        height: 120px !important;
        border-radius: 50% !important; /* Rend l'image ronde */
        object-fit: cover;
        border: 4px solid #e67e22; /* Bordure orange */
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 2. AFFICHAGE DU LOGO ET INFOS AU MILIEU
    st.markdown(f"""
    <div class="playstore-container">
        <img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" class="logo-rond-centre">
        <h1 style="margin:0; color:#e67e22;">Mes Recettes Pro</h1>
        <p style="font-size: 1.2rem; margin: 5px 0;"><b>👩‍🍳 Isabelle Latrémouille</b></p>
        <p style="margin:0;">⭐ 4.9 ★ (128 avis) | 📥 1 000+ téléchargements</p>
    </div>
    """, unsafe_allow_html=True)

    # 3. LE BOUTON INSTALLER (Large)
    if st.button("📥 Installer l'application", use_container_width=True, type="primary"):
        st.success("Application installée avec succès ! 🎉")

    st.divider()

    # --- LE RESTE DE TA PAGE (Aperçu, À propos...) ---
    st.subheader("📸 Aperçu")
    c1, c2, c3 = st.columns(3)
    # Ici, remplace par tes vraies images si tu en as
    c1.image("https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg", caption="Ma Bibliothèque")
    c2.image("https://i.postimg.cc/YCkg460C/shared-image-(5).jpg", caption="Détails de Recette")
    c3.image("https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg", caption="Liste d'Épicerie")

    st.divider()
    # ... suite du code (À propos et Infos) ...
    
    # Description et Infos Techniques
    col_desc, col_tech = st.columns(2)
    
    with col_desc:
        st.subheader("📝 À propos")
        st.write("""
        **Mes Recettes Pro** est votre compagnon culinaire ultime.
        * ✔ Gestion intuitive des recettes
        * ✔ Système de notes ⭐
        * ✔ Planning hebdomadaire 📅
        * ✔ Liste d'épicerie intelligente 🛒
        * ✔ Synchronisation Cloud
        """)
        
    with col_tech:
        st.subheader("ℹ️ Informations")
        st.write("""
        **Version** : 2.0 Premium  
        **Mise à jour** : Février 2026  
        **Catégorie** : Cuisine  
        **Développeur** : Isabelle Latrémouille
        """)

    st.divider()
    if st.button("⬅ Retour à la Bibliothèque", use_container_width=True, key="back_from_play"):
        st.session_state.page = "home"
        st.rerun()
# --- PAGE AIDE ---
elif st.session_state.page == "help":
    st.header("❓ Aide & Astuces")
    ca, cb = st.columns(2)
    with ca:
        st.markdown('<div class="help-box"><h3>📝 Ajouter</h3><p>Utilisez l\'onglet <b>Réseaux Sociaux</b> pour Instagram/TikTok.</p></div>', unsafe_allow_html=True)
    with cb:
        st.markdown('<div class="help-box"><h3>🛒 Épicerie</h3><p>Cochez les ingrédients dans une recette pour les envoyer ici.</p></div>', unsafe_allow_html=True)
    
    if st.button("⬅ Retour", use_container_width=True, key="btn_retour_aide"): 
        st.session_state.page = "home"; st.rerun()















