import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse

# --- INITIALISATION DU SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "home"

# ======================
# CONFIGURATION & DESIGN
# ======================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

if st.session_state.page != "print":
    st.markdown("""
    <style>

    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1,h2,h3 { color: #e67e22 !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #1e2129; color: white; }
    .stButton button { background-color: #e67e22; color: white; }

    /* Inputs */
    input, select, textarea, div[data-baseweb="select"] { 
        color: white !important; 
        background-color: #1e2129 !important; 
    }

    /* Checklist */
    .stCheckbox label p { 
        color: white !important; 
        font-size: 1.1rem !important; 
        font-weight: 500 !important; 
    }

    /* Recipe cards */
    .recipe-card { 
        background-color:#1e2129; 
        border:1px solid #3d4455; 
        border-radius:12px; 
        padding:10px; 
        height:230px; 
        display:flex; 
        flex-direction:column; 
        justify-content:space-between;
    }

    .recipe-img { 
        width:100%; 
        height:130px; 
        object-fit:cover; 
        border-radius:8px; 
    }

    .recipe-title { 
        color:white; 
        margin-top:8px; 
        font-size:0.95rem; 
        font-weight:bold; 
        text-align:center; 
        display:flex; 
        align-items:center; 
        justify-content:center; 
        height:2.5em; 
        line-height:1.2; 
    }

    /* Help boxes */
    .help-box { 
        background-color:#1e2130; 
        padding:15px; 
        border-radius:15px; 
        border-left:5px solid #e67e22; 
        margin-bottom:20px; 
    }

    .help-box h3 { 
        color:#e67e22; 
        margin-top:0; 
    }

    </style>
    """, unsafe_allow_html=True)

# ======================
# CONSTANTES
# ======================
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================
# FONCTIONS
# ======================
def send_action(payload):
    with st.spinner("🚀 Action..."):
        try:
            r = requests.post(URL_SCRIPT,json=payload,timeout=20)
            if "Success" in r.text:
                st.cache_data.clear()
                time.sleep(0.5)
                return True
        except:
            pass
    return False

def scrape_url(url):
    try:
        headers={'User-Agent':'Mozilla/5.0'}
        res = requests.get(url,headers=headers,timeout=10)
        res.encoding=res.apparent_encoding
        soup=BeautifulSoup(res.text,'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "Recette Importée"
        elements = soup.find_all(['li','p'])
        content = "\n".join(dict.fromkeys([el.text.strip() for el in elements if 10<len(el.text.strip())<500]))
        return title, content
    except:
        return None,None

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}")
        df = df.fillna('')
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" 
             style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid #e67e22; object-fit: cover;">
    </div>
    """, unsafe_allow_html=True)
    
    st.title("🍳 Mes Recettes")
    if st.button("📚 Bibliothèque",use_container_width=True,key="side_home"):
        st.session_state.page="home"; st.rerun()
    if st.button("📅 Planning Repas",use_container_width=True,key="side_plan"):
        st.session_state.page="planning"; st.rerun()
    if st.button("🛒 Ma Liste d'épicerie",use_container_width=True,key="side_shop"):
        st.session_state.page="shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER RECETTE",use_container_width=True,key="side_add"):
        st.session_state.page="add"; st.rerun()
    if st.button("⭐ Play Store",use_container_width=True,key="side_play"):
        st.session_state.page="playstore"; st.rerun()
    if st.button("❓ Aide",use_container_width=True,key="side_help"):
        st.session_state.page="help"; st.rerun()
# ======================
# LOGIQUE DES PAGES
# ======================

# --- PAGE ACCUEIL ---
if st.session_state.page == "home":
    c1, c2 = st.columns([4, 1])
    c1.header("📚 Ma Bibliothèque")
    if c2.button("🔄 Actualiser"):
        st.cache_data.clear()
        st.rerun()
    st.divider()
    st.markdown("""
        <style>
        .recipe-card {
            background-color: #1e1e1e;
            border-radius: 12px;
            border: 1px solid #333;
            margin-bottom: 25px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            height: 480px;
        }
        .recipe-img-container {
            width: 100%;
            height: 320px;
            overflow: hidden;
        }
        .recipe-img-container img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .recipe-content {
            padding: 15px;
            text-align: center;
        }
        .recipe-title-text {
            color: #e0e0e0;
            font-size: 1.3rem;
            font-weight: 600;
            margin: 10px 0;
            line-height: 1.2;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .category-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    df = load_data()
    if not df.empty:
        col_search, col_cat = st.columns([2, 1])
        with col_search:
            search = st.text_input("🔍 Rechercher une recette...", placeholder="Ex: Sauce spaghetti...")
        with col_cat:
            liste_categories = ["Toutes"] + sorted([str(c) for c in df['Catégorie'].unique() if c])
            cat_choisie = st.selectbox("📁 Filtrer par catégorie", liste_categories)
        
        mask = df['Titre'].str.contains(search, case=False, na=False)
        if cat_choisie != "Toutes":
            mask = mask & (df['Catégorie'] == cat_choisie)
        
        def get_cat_color(cat):
            colors = {"Poulet": "#FF5733", "Bœuf": "#C70039", "Dessert": "#FF33FF", "Légumes": "#28B463", "Poisson": "#3498DB", "Pâtes": "#F1C40F"}
            return colors.get(cat, "#e67e22")

        rows = df[mask].reset_index(drop=True)
        for i in range(0, len(rows), 2):
            grid_cols = st.columns(2) 
            for j in range(2):
                if i+j < len(rows):
                    row = rows.iloc[i+j]
                    with grid_cols[j]:
                        img_url = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/500x350"
                        cat_label = row['Catégorie'] if row['Catégorie'] else "Recette"
                        st.markdown(f"""
                            <div class="recipe-card">
                                <div class="recipe-img-container"><img src="{img_url}"></div>
                                <div class="recipe-content">
                                    <span class="category-badge" style="background-color:{get_cat_color(cat_label)}; color:white;">{cat_label}</span>
                                    <div class="recipe-title-text">{row['Titre']}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("📖 Ouvrir la recette", key=f"v_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"
                            st.rerun()
    else:
        st.warning("Aucune donnée trouvée.")

# --- PAGE DÉTAILS ---
elif st.session_state.page=="details":
    r = st.session_state.recipe_data
    c_nav1, c_nav2, c_nav3, c_nav4 = st.columns([1, 1, 1, 1])
    with c_nav1:
        if st.button("⬅ Retour", use_container_width=True): st.session_state.page="home"; st.rerun()
    with c_nav2:
        if st.button("✏️ Éditer", use_container_width=True): st.session_state.page="add"; st.rerun()
    with c_nav3:
        if st.button("🖨️ Version imprimable", use_container_width=True):
            st.session_state.page = "print"
            st.rerun()
    with c_nav4:
        if st.button("🗑️ Supprimer", use_container_width=True): 
            if send_action({"action":"delete","titre":r['Titre']}): st.session_state.page="home"; st.rerun()

    st.divider()
    st.header(f"📖 {r.get('Titre','Sans titre')}")
    col_g, col_d = st.columns([1, 1.2])
    with col_g:
        img_url = r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400"
        st.image(img_url,use_container_width=True)
        st.markdown("### ⭐ Ma Note & Avis")
        note_actuelle = int(float(r.get('Note',0))) if r.get('Note') else 0
        nouvelle_note = st.slider("Note",0,5,note_actuelle,key="val_note")
        nouveau_comm = st.text_area("Commentaires / astuces",value=str(r.get('Commentaires',"")),height=100,key="val_comm")
        if st.button("💾 Enregistrer ma note",use_container_width=True):
            if send_action({"action":"edit","titre":r['Titre'],"Note":nouvelle_note,"Commentaires":nouveau_comm}):
                st.success("Note enregistrée !"); st.session_state.recipe_data['Note']=nouvelle_note; st.session_state.recipe_data['Commentaires']=nouveau_comm; st.rerun()
    with col_d:
        st.subheader("📋 Informations")
        st.write(f"**🍴 Catégorie :** {r.get('Catégorie','Non classé')}")
        st.write(f"**👥 Portions :** {r.get('Portions','-')}")
        st.write(f"**⏱ Préparation :** {r.get('Temps_Prepa','-')} min")
        st.write(f"**🔥 Cuisson :** {r.get('Temps_Cuisson','-')} min")
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r.get('Ingrédients','')).split("\n") if l.strip()]
        sel=[]
        for i,l in enumerate(ings):
            if st.checkbox(l,key=f"chk_det_final_{i}"): sel.append(l)
        if st.button("📥 Ajouter au Panier",use_container_width=True):
            for it in sel: send_action({"action":"add_shop","article":it})
            st.toast("Ajouté !"); st.session_state.page="shop"; st.rerun()
    st.divider()
    st.subheader("📝 Préparation")
    st.write(r.get('Préparation','Aucune étape.'))

# --- PAGE AJOUTER ---
elif st.session_state.page == "add":
    st.markdown('<h1 style="color: #e67e22;">📥 Ajouter une Nouvelle Recette</h1>', unsafe_allow_html=True)
    if st.button("⬅ Retour à la Bibliothèque", use_container_width=True):
        st.session_state.page = "home"; st.rerun()
        
    st.markdown("""<div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #4285F4; margin-bottom: 20px;"><h4 style="margin:0; color:white;">🔍 Chercher une idée sur Google Canada</h4></div>""", unsafe_allow_html=True)
    
    c_search, c_btn = st.columns([3, 1])
    search_query = c_search.text_input("Que cherchez-vous ?", placeholder="Ex: Pâte à tarte Ricardo", label_visibility="collapsed")
    query_encoded = urllib.parse.quote(search_query + ' recette') if search_query else ""
    target_url = f"https://www.google.ca/search?q={query_encoded}" if search_query else "https://www.google.ca"
    
    # Correction de la ligne coupée ici :
    c_btn.markdown(f"""<a href="{target_url}" target="_blank" style="text-decoration: none;"><div style="background-color: #4285F4; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; cursor: pointer;">🌐 Aller sur Google.ca</div></a>""", unsafe_allow_html=True)
    
    st.markdown("""<div style="background-color: #1e2129; padding: 20px; border-radius: 15px; border: 1px solid #3d4455; margin-top: 10px;"><h3 style="margin-top:0; color:#e67e22;">&#127760; Importer depuis le Web</h3>""", unsafe_allow_html=True)
    
    col_url, col_go = st.columns([4, 1])
    url_input = col_url.text_input("Collez l'URL ici", placeholder="https://www.ricardocuisine.com/...")
    
    if col_go.button("Extraire &#10024;", use_container_width=True):
        if url_input:
            t, c = scrape_url(url_input)
            if t:
                st.session_state.scraped_title = t
                st.session_state.scraped_content = c
                st.success("Extraction réussie !"); st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.divider()
    
    with st.container():
        col_t, col_c = st.columns([2, 1])
        titre = col_t.text_input("🏷️ Nom de la recette", value=st.session_state.get('scraped_title', ''), placeholder="Ex: Lasagne de maman")
        cat_choisies = col_c.multiselect("📁 Catégories", CATEGORIES, default=["Autre"])
        
        st.markdown("#### ⏱️ Paramètres de cuisson")
        cp1, cp2, cp3 = st.columns(3)
        t_prep = cp1.text_input("🕒 Préparation (min)", placeholder="15")
        t_cuis = cp2.text_input("🔥 Cuisson (min)", placeholder="45")
        port = cp3.text_input("🍽️ Portions", placeholder="4")
        
        st.divider()
        
        ci, ce = st.columns(2)
        ingredients = ci.text_area("🍎 Ingrédients", height=300, placeholder="2 tasses de farine...")
        val_p = st.session_state.get('scraped_content', '')
        instructions = ce.text_area("👨‍🍳 Étapes de préparation", value=val_p, height=300)
        
        img_url = st.text_input("🖼️ Lien de l'image (URL)", placeholder="https://...")
        commentaires = st.text_area("📝 Mes Notes & Astuces", height=100, placeholder="Ce champ m'aide à ajuster...")
        
        st.divider()
        
        if st.button("💾 ENREGISTRER DANS MA BIBLIOTHÈQUE", use_container_width=True):
            if titre and ingredients:
                payload = {
                    "action": "add", 
                    "titre": titre, 
                    "Catégorie": ", ".join(cat_choisies), 
                    "Ingrédients": ingredients, 
                    "Préparation": instructions, 
                    "Image": img_url, 
                    "Temps_Prepa": t_prep, 
                    "Temps_Cuisson": t_cuis, 
                    "Portions": port, 
                    "Note": 0, 
                    "Commentaires": commentaires
                }
                if send_action(payload):
                    st.success(f"✅ '{titre}' ajouté !"); time.sleep(1)
                    if 'scraped_title' in st.session_state: del st.session_state.scraped_title
                    if 'scraped_content' in st.session_state: del st.session_state.scraped_content
                    st.session_state.page = "home"; st.rerun()
            else:
                st.error("Le titre et les ingrédients sont obligatoires !")
# --- PAGE ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    if st.button("⬅ Retour"):
        st.session_state.page = "home"; st.rerun()
    try:
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        if not df_s.empty:
            to_del = []
            for idx, row in df_s.iterrows():
                # Utilisation de ton style de checklist
                if st.checkbox(str(row.iloc[0]), key=f"sh_{idx}"):
                    to_del.append(str(row.iloc[0]))
            
            st.divider()
            c1, c2 = st.columns(2)
            if c1.button("🗑 Retirer les articles sélectionnés", use_container_width=True):
                for it in to_del:
                    send_action({"action": "remove_shop", "article": it})
                st.rerun()
            if c2.button("🧨 Vider toute la liste", use_container_width=True):
                send_action({"action": "clear_shop"})
                st.rerun()
        else:
            st.info("Votre liste est vide pour le moment.")
    except:
        st.error("Erreur de chargement de la liste.")

# --- PAGE PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning de la semaine")
    if st.button("⬅ Retour"):
        st.session_state.page = "home"; st.rerun()
    st.divider()
    df = load_data()
    if not df.empty and 'Date_Prevue' in df.columns:
        # On filtre les recettes qui ont une date prévue
        plan = df[df['Date_Prevue'].astype(str).str.strip() != ""].sort_values(by='Date_Prevue')
        if not plan.empty:
            for _, row in plan.iterrows():
                with st.expander(f"📌 {row['Date_Prevue']} : {row['Titre']}"):
                    st.write(f"**Catégorie :** {row['Catégorie']}")
                    if st.button("Voir la fiche complète", key=f"p_btn_{row['Titre']}"):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
        else:
            st.info("Aucun repas planifié pour le moment.")
    else:
        st.warning("La colonne de planning est introuvable ou vide.")

# ==========================================
# --- PAGE FICHE PRODUIT PLAY STORE (STYLE RÉEL) ---
# ==========================================
elif st.session_state.page == "playstore":
    # CSS pour le style Dark Store
    st.markdown("""
        <style>
        .play-title { font-size: 2.2rem; font-weight: 600; color: white; margin-bottom: 0px; }
        .play-dev { color: #01875f; font-weight: 500; font-size: 1.1rem; margin-bottom: 20px; }
        .play-stats { display: flex; justify-content: flex-start; gap: 40px; border-top: 1px solid #3c4043; border-bottom: 1px solid #3c4043; padding: 15px 0; margin-bottom: 25px; }
        .stat-box { text-align: center; }
        .stat-val { font-size: 1.1rem; font-weight: bold; color: white; display: block; }
        .stat-label { font-size: 0.8rem; color: #bdc1c6; }
        .screenshot-img { border-radius: 10px; border: 1px solid #3c4043; margin-right: 10px; }
        </style>
    """, unsafe_allow_html=True)

    # --- EN-TÊTE (Logo à droite) ---
    col_info, col_logo = st.columns([2, 1])
    
    with col_info:
        st.markdown('<div class="play-title">Mes Recettes Pro</div>', unsafe_allow_html=True)
        st.markdown('<div class="play-dev">VosSoins Inc.</div>', unsafe_allow_html=True)
        
        # Barre de statistiques officielle
        st.markdown("""
        <div class="play-stats">
            <div class="stat-box"><span class="stat-val">4,9 ⭐</span><span class="stat-label">1,44 k avis</span></div>
            <div class="stat-box"><span class="stat-val">100 k+</span><span class="stat-label">Téléchargements</span></div>
            <div class="stat-box"><span class="stat-val">E</span><span class="stat-label">Tout le monde</span></div>
        </div>
        """, unsafe_allow_html=True)

    with col_logo:
        # Ton logo rond
        st.markdown("""
        <div style="display: flex; justify-content: flex-end;">
            <img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" 
                 style="width: 130px; height: 130px; border-radius: 20%; border: 1px solid #3c4043; object-fit: cover;">
        </div>
        """, unsafe_allow_html=True)

    # --- BOUTON INSTALLER ET EXPLOSION ---
    placeholder_action = st.empty()
    
    if placeholder_action.button("Installer", key="play_install"):
        with placeholder_action:
            # Ton image de bombe fournie
            st.image("https://i.postimg.cc/HnxJDBjf/cartoon-hand-bomb-vector-template-(2).jpg", width=250)
            time.sleep(2.5)
        placeholder_action.empty()
        st.markdown("<h3 style='color:#01875f;'>✓ Installé</h3>", unsafe_allow_html=True)

    st.write("✨ Cette appli est proposée pour tous vos appareils")
    
    # --- GALERIE DE PHOTOS (Tes liens fournis) ---
    st.write("")
    col_pic1, col_pic2, col_pic3 = st.columns(3)
    with col_pic1:
        st.image("https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg", use_container_width=True)
    with col_pic2:
        st.image("https://i.postimg.cc/YCkg460C/shared-image-(5).jpg", use_container_width=True)
    with col_pic3:
        st.image("https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg", use_container_width=True)

    st.divider()

    # --- À PROPOS (Texte authentique) ---
    st.markdown("### À propos de cette appli →", unsafe_allow_html=True)
    st.write("""
    **Mes Recettes Pro** combine un gestionnaire de recettes, une liste de courses et un planificateur de repas en une seule application intuitive.
    Ajoutez facilement des recettes depuis n'importe quel site web.
    """)
    
    st.markdown('<span style="background:#3c4043; padding:5px 15px; border-radius:15px; font-size:0.9rem;">Productivité</span>', unsafe_allow_html=True)

    st.divider()

    # --- RETOUR ---
    if st.button("⬅ Retour", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
        
# --- PAGE IMPRIMABLE ---
elif st.session_state.page == "print":
    r = st.session_state.recipe_data

    # 1. STYLE CSS (Propre et efficace)
    st.markdown("""
        <style>
        .stApp { background-color: white !important; color: black !important; }
        [data-testid="stHeader"], [data-testid="stSidebar"], footer, .stButton { display: none !important; }
        
        .paper-sheet {
            background-color: white;
            color: black;
            font-family: 'Segoe UI', sans-serif;
            max-width: 850px;
            margin: 0 auto;
            padding: 20px;
        }

        .print-box {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 25px;
        }

        h1 { color: black !important; border-bottom: 3px solid #e67e22; padding-bottom: 10px; }
        h3 { color: #e67e22 !important; margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 5px; }

        @media print {
            .no-print { display: none !important; }
            .print-box { border: 1px solid #ccc; background-color: white !important; }
            .page-break { page-break-before: always; }
            * { color: black !important; }
        }
        </style>
    """, unsafe_allow_html=True)

    # 2. BARRE D'INSTRUCTIONS (no-print)
    st.markdown("""
        <div style="background-color: #fff3cd; padding: 15px; border: 1px solid #ffeeba; border-radius: 10px; color: #856404; margin-bottom: 20px;" class="no-print">
            <strong>💡 Prêt pour l'impression :</strong> Utilisez <b>CTRL+P</b> ou le menu <b>Imprimer</b> de votre navigateur.
        </div>
    """, unsafe_allow_html=True)

    if st.button("⬅ Retourner à la recette", use_container_width=True):
        st.session_state.page = "details"
        st.rerun()

    # 3. LOGIQUE DE DÉCOUPAGE (Indispensable pour ta sauce spaghetti)
    texte_complet = str(r.get('Ingrédients', ''))
    import re
    # On sépare si on trouve le mot "Préparation" dans le champ ingrédients
    split_match = re.search(r'(?i)Préparation|Preparation', texte_complet)
    
    if split_match:
        ingredients_txt = texte_complet[:split_match.start()].strip()
        prepa_txt = texte_complet[split_match.start():].strip()
    else:
        ingredients_txt = texte_complet
        prepa_txt = r.get('Préparation', '')

    # Préparation des lignes d'ingrédients
    lignes_ing = [l.strip() for l in ingredients_txt.split('\n') if l.strip()]
    html_ingredients = ""
    for l in lignes_ing:
        if l.endswith(':'): # C'est un titre (ex: Liquides :)
            html_ingredients += f"<p style='margin: 8px 0 3px 0;'><b>{l}</b></p>"
        else: # C'est un ingrédient
            html_ingredients += f"<p style='margin: 3px 0;'>☐ {l}</p>"

    # 4. RENDU FINAL (Tout dans un seul f-string pour éviter les bugs d'affichage)
    st.markdown(f"""
        <div class="paper-sheet">
            <h1>{r.get('Titre', 'Recette')}</h1>
            
            <div style="display: flex; justify-content: space-between; margin-bottom: 20px; font-weight: bold;">
                <span>Catégorie : {r.get('Catégorie', '-')}</span>
                <span>Portions : {r.get('Portions', '-')}</span>
                <span>Temps : {r.get('Temps_Prepa', '0')} + {r.get('Temps_Cuisson', '0')} min</span>
            </div>

            <div class="print-box">
                <h3>🛒 Ingrédients</h3>
                {html_ingredients}
            </div>

            <div class="print-box page-break">
                <h3>👨‍🍳 Préparation</h3>
                <div style="white-space: pre-wrap; line-height: 1.6;">{prepa_txt}</div>
            </div>

            <p style="text-align: center; font-size: 0.8em; color: #666; margin-top: 30px;">
                Fiche générée par Mes Recettes Pro
            </p>
        </div>
    """, unsafe_allow_html=True)
# --- PAGE AIDE ---
elif st.session_state.page=="help":
    st.header("❓ Aide & Astuces")
    ca, cb = st.columns(2)
    ca.markdown('<div class="help-box"><h3>📝 Ajouter Recette</h3><p>Importez via URL (Ricardo, etc.) ou entrez vos propres créations manuellement.</p></div>', unsafe_allow_html=True)
    ca.markdown('<div class="help-box"><h3>🔍 Recherche</h3><p>Utilisez la barre de recherche et les filtres par catégorie pour retrouver vos plats.</p></div>', unsafe_allow_html=True)
    cb.markdown('<div class="help-box"><h3>🛒 Liste d\'Épicerie</h3><p>Cochez les ingrédients dans une recette pour les envoyer ici. Pratique pour les courses !</p></div>', unsafe_allow_html=True)
    cb.markdown('<div class="help-box"><h3>📅 Planning</h3><p>Visualisez vos repas de la semaine directement depuis votre calendrier Google Sheets.</p></div>', unsafe_allow_html=True)
    st.divider()
    if st.button("⬅ Retour à la Bibliothèque", use_container_width=True):
        st.session_state.page="home"; st.rerun()




















