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
# SYSTÈME DE SÉCURITÉ
# ======================
# Vérifie si l'URL contient ?admin=oui
url_admin = st.query_params.get("admin") == "oui"

if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = url_admin

with st.sidebar:
    st.divider()
    if not st.session_state.admin_mode:
        # Champ de mot de passe discret pour toi
        pwd = st.text_input("🔑 Accès Admin", type="password", help="Tape ton code pour modifier")
        if pwd == "142203":  # <--- CHOISIS TON MOT DE PASSE ICI
            st.session_state.admin_mode = True
            st.rerun()
    else:
        st.success("✅ Mode Chef Activé")
        if st.button("🔒 Déconnexion"):
            st.session_state.admin_mode = False
            st.rerun()

# ======================
# CONSTANTES
# ======================
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"

# Voici l'URL générée avec ton GID 536412190
URL_CSV_PLAN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=536412190&single=true&output=csv"

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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Récupération du titre
        title = soup.find('h1').text.strip() if soup.find('h1') else "Recette Importée"
        
        # Récupération plus large des éléments de texte
        # On augmente la limite à 2000 caractères pour ne pas couper les longues instructions
        elements = soup.find_all(['li', 'p', 'span']) 
        raw_list = [el.text.strip() for el in elements if 5 < len(el.text.strip()) < 2000]
        
        # Nettoyage des doublons tout en gardant l'ordre
        content = "\n".join(list(dict.fromkeys(raw_list)))
        
        return title, content
    except Exception as e:
        print(f"Erreur scrap: {e}")
        return None, None

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
    # --- CODE POUR LE LOGO ROND ---
    st.markdown("""
        <style>
        .logo-container {
            display: flex;
            justify-content: center;
            margin-bottom: 10px;
        }
        .logo-container img {
            border-radius: 50%; /* Le cercle parfait */
            width: 120px;       /* Largeur fixe */
            height: 120px;      /* Hauteur identique pour éviter l'ovale */
            object-fit: cover;  /* Empêche de déformer l'image */
            border: 3px solid #e67e22; /* Ton liseré orange */
            padding: 2px;
        }
        </style>
        <div class="logo-container">
            <img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png">
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<h3 style="text-align: center; color: #e67e22; margin-top: -10px;">Mes Recettes</h3>', unsafe_allow_html=True)
    st.divider()
    
    # ... la suite de tes boutons (Actualiser, etc.)
    
    if st.button("🔄 Actualiser les données", use_container_width=True):
        st.cache_data.clear()
        st.toast("Mise à jour réussie ! 📋")
        time.sleep(0.5)
        st.rerun()

    st.divider()

    # SECTION NAVIGATION
    if st.button("📚 Bibliothèque", use_container_width=True, key="side_home"):
        st.session_state.page="home"; st.rerun()
        
    if st.button("📅 Planning Repas", use_container_width=True, key="side_plan"):
        st.session_state.page="planning"; st.rerun()
        
    if st.button("🛒 Ma Liste d'épicerie", use_container_width=True, key="side_shop"):
        st.session_state.page="shop"; st.rerun()

    if st.button("⚖️ Aide-Mémoire", use_container_width=True, key="side_conv"):
        st.session_state.page="conversion"; st.rerun()
    
    st.divider()
    
    # SECTION ADMIN (Bouton Ajouter)
    if st.session_state.admin_mode:
        if st.button("➕ AJOUTER RECETTE", use_container_width=True, key="side_add"):
            if 'recipe_to_edit' in st.session_state:
                del st.session_state.recipe_to_edit
            st.session_state.page="add"; st.rerun()
    else:
        st.info("📖 Mode Consultation")

    # BOUTONS DU BAS
    if st.button("⭐ Play Store", use_container_width=True, key="side_play"):
        st.session_state.page="playstore"; st.rerun()

    if st.button("❓ Aide", use_container_width=True, key="side_help"):
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

    # --- NOUVELLE BARRE D'OUTILS (Navigation rapide) ---
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("📅 Voir mon Planning", use_container_width=True):
            st.session_state.page = "planning"
            st.rerun()
    with col_nav2:
        # Voici ton bouton Aide-Mémoire facile à retrouver
        if st.button("📏 Aide-Mémoire & Conversions", use_container_width=True):
            st.session_state.page = "conversion"
            st.rerun()
    
    st.write("") # Petit espace esthétique

    # --- STYLE CSS (Inchangé) ---
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
        /* ... la suite de ton CSS reste identique ... */
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
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    
    # BARRE DE NAVIGATION
    c_nav1, c_nav2, c_nav3, c_nav4 = st.columns([1, 1, 1, 1])
    with c_nav1:
        if st.button("⬅ Retour", use_container_width=True): 
            st.session_state.page="home"; st.rerun()
    with c_nav2:
        if st.button("✏️ Éditer", use_container_width=True):
            st.session_state.recipe_to_edit = r.copy()
            st.session_state.page = "edit"; st.rerun()
    with c_nav3:
        if st.button("🖨️ Imprimer", use_container_width=True):
            st.session_state.page = "print"; st.rerun()
    with c_nav4:
        if st.button("🗑️ Supprimer", use_container_width=True):
            if send_action({"action": "delete", "titre": r['Titre']}):
                st.cache_data.clear()
                st.toast(f"Recette '{r['Titre']}' supprimée ! 🗑️")
                st.session_state.page = "home"; st.rerun()

    st.divider()

    # --- EN-TÊTE ---
    st.header(f"📖 {r.get('Titre','Sans titre')}")

    # --- CORPS DE LA PAGE ---
    col_g, col_d = st.columns([1, 1.2])
    
    with col_g:
        # IMAGE
        img_url = r.get('Image', '')
        if "http" in str(img_url):
            st.image(img_url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/400?text=Pas+d'image", use_container_width=True)
            
        # SYSTÈME D'ÉTOILES INTERACTIF
        st.write("**Évaluer cette recette :**")
        nouveau_choix = st.feedback("stars", key=f"star_det_{r['Titre']}")
        if nouveau_choix is not None:
            note_finale = nouveau_choix + 1
            if send_action({"action": "edit", "titre": r['Titre'], "Note": note_finale}):
                st.toast(f"Note enregistrée : {note_finale} ⭐")
                st.cache_data.clear()
        
        st.divider()

        # INFOS (Portions et Temps sous l'image)
        t1, t2, t3 = st.columns(3)
        t1.metric("🕒 Prépa", f"{r.get('Temps_Prepa', r.get('temps_prepa', '-'))}m")
        t2.metric("🔥 Cuisson", f"{r.get('Temps_Cuisson', r.get('temps_cuisson', '-'))}m")
        t3.metric("🍽️ Portions", r.get('Portions', r.get('portions', '-')))
            
        # SECTION NOTES
        st.markdown("### 📝 Mes Notes")
        notes = r.get('Commentaires', '')
        if notes:
            st.info(notes)
        else:
            st.write("*Aucune note pour le moment.*")

    with col_d:
        st.subheader("📋 Informations")
        st.write(f"**🍴 Catégorie :** {r.get('Catégorie', 'Autre')}")
        
        source = r.get('Source', r.get('source', ''))
        if "http" in str(source):
            st.link_button("🌐 Voir la source originale", str(source), use_container_width=True)

        st.divider()
        
        # SECTION PLANNING
        st.subheader("📅 Planifier ce repas")
        date_plan = st.date_input("Choisir une date", value=datetime.now(), key="plan_date_det")
        if st.button("🗓️ Ajouter au planning & Google", use_container_width=True):
            res1 = send_action({"action": "plan", "titre": r['Titre'], "date": str(date_plan)})
            res2 = send_action({
                "action": "calendar", 
                "titre": r['Titre'], 
                "date_prevue": date_plan.strftime("%d/%m/%Y"),
                "ingredients": r.get('Ingrédients', '')
            })
            if res1 and res2:
                st.success("✅ Ajouté partout !")
                st.cache_data.clear()

        st.divider()

        # SECTION INGRÉDIENTS
        st.subheader("🛒 Ingrédients")
        ings_raw = r.get('Ingrédients', '')
        ings = [l.strip() for l in str(ings_raw).split("\n") if l.strip()]
        selected_ings = []
        for i, line in enumerate(ings):
            if st.checkbox(line, key=f"chk_det_{i}"):
                selected_ings.append(line)
        
        if st.button("📥 Ajouter la sélection au Panier", use_container_width=True):
            for item in selected_ings:
                send_action({"action": "add_shop", "article": item})
            st.toast("Ingrédients envoyés !")

    st.divider()

    # --- SECTION PRÉPARATION ---
    st.subheader("👨‍🍳 Étapes de préparation")
    prep = r.get('Préparation', r.get('preparation', ''))
    if prep:
        st.write(prep)
    else:
        st.warning("Aucune étape de préparation enregistrée.")

# --- FIN DE LA PAGE DÉTAILS ---

elif st.session_state.page == "add":
    # Ton code pour la page d'ajout continue ici...
elif st.session_state.page == "add":
    st.markdown('<h1 style="color: #e67e22;">📥 Ajouter une Nouvelle Recette</h1>', unsafe_allow_html=True)
    if st.button("⬅ Retour à la Bibliothèque", use_container_width=True):
        st.session_state.page = "home"; st.rerun()
        
    st.markdown("""<div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #4285F4; margin-bottom: 20px;"><h4 style="margin:0; color:white;">🔍 Chercher une idée sur Google Canada</h4></div>""", unsafe_allow_html=True)
    
    c_search, c_btn = st.columns([3, 1])
    search_query = c_search.text_input("Que cherchez-vous ?", placeholder="Ex: Pâte à tarte Ricardo", label_visibility="collapsed")
    query_encoded = urllib.parse.quote(search_query + ' recette') if search_query else ""
    target_url = f"https://www.google.ca/search?q={query_encoded}" if search_query else "https://www.google.ca"
    
    c_btn.markdown(f"""<a href="{target_url}" target="_blank" style="text-decoration: none;"><div style="background-color: #4285F4; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; cursor: pointer;">🌐 Aller sur Google.ca</div></a>""", unsafe_allow_html=True)
    
    st.markdown("""<div style="background-color: #1e2129; padding: 20px; border-radius: 15px; border: 1px solid #3d4455; margin-top: 10px;"><h3 style="margin-top:0; color:#e67e22;">🌐 Importer depuis le Web</h3>""", unsafe_allow_html=True)
    
    col_url, col_go = st.columns([4, 1])
    url_input = col_url.text_input("Collez l'URL ici", placeholder="https://www.ricardocuisine.com/...", key="url_main")
    
    if col_go.button("Extraire ✨", use_container_width=True):
        if url_input:
            with st.spinner("Analyse du site en cours..."):
                t, c = scrape_url(url_input)
                if t:
                    st.session_state.scraped_title = t
                    st.session_state.scraped_content = c
                    st.success("Extraction réussie ! ✨")
                    st.rerun()
                else:
                    st.warning("⚠️ Ce site bloque l'accès automatique. Copiez le texte manuellement.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    with st.container():
        col_t, col_c = st.columns([2, 1])
        # On utilise une variable intermédiaire pour plus de sûreté
        titre_val = st.session_state.get('scraped_title', '')
        titre = col_t.text_input("🏷️ Nom de la recette", value=titre_val, placeholder="Ex: Lasagne de maman")
        
        cat_choisies = col_c.multiselect("📁 Catégories", CATEGORIES, default=["Autre"])
        
        # SOURCE : On s'assure que si l'URL est extraite, elle va ici
        source_url = st.text_input("🔗 Lien source", value=url_input if url_input else "", placeholder="https://...")
        
        st.markdown("#### ⏱️ Paramètres de cuisson")
        cp1, cp2, cp3 = st.columns(3)
        t_prep = cp1.text_input("🕒 Préparation (min)", placeholder="15", key="p_time")
        t_cuis = cp2.text_input("🔥 Cuisson (min)", placeholder="45", key="c_time")
        port = cp3.text_input("🍽️ Portions", placeholder="4", key="portions")
        
        st.divider()
        
        ci, ce = st.columns(2)
        # On s'assure que les ingrédients ne sont pas écrasés par l'extraction si on a déjà écrit
        ingredients = ci.text_area("🍎 Ingrédients", height=300, placeholder="2 tasses de farine...", key="ing_area")
        
        # ÉTAPES : On force la valeur extraite si elle existe
        prep_val = st.session_state.get('scraped_content', '')
        instructions = ce.text_area("👨‍🍳 Étapes de préparation", value=prep_val, height=300, key="prep_area")
        
        img_url = st.text_input("🖼️ Lien de l'image (URL)", placeholder="https://...", key="img_url")
        commentaires = st.text_area("📝 Mes Notes & Astuces", height=100, key="notes_area")
        
        st.divider()
        
        if st.button("💾 ENREGISTRER DANS MA BIBLIOTHÈQUE", use_container_width=True):
            if titre and ingredients:
                import datetime
                # On prépare l'envoi
                payload = {
                    "action": "add",
                    "date": datetime.date.today().strftime("%d/%m/%Y"),
                    "titre": titre,
                    "source": source_url,
                    "ingredients": ingredients,
                    "preparation": instructions,
                    "image": img_url,
                    "categorie": ", ".join(cat_choisies),
                    "portions": port,
                    "temps_prepa": t_prep,
                    "temps_cuisson": t_cuis,
                    "commentaires": commentaires
                }

                if send_action(payload):
                    st.success(f"✅ '{titre}' a été ajoutée !")
                    st.cache_data.clear()
                    # On vide proprement les états d'extraction
                    for key in ['scraped_title', 'scraped_content']:
                        if key in st.session_state:
                            st.session_state[key] = ""
                    time.sleep(1)
                    st.session_state.page = "home"
                    st.rerun()
            else:
                st.error("🚨 Le titre et les ingrédients sont obligatoires !")
# --- PAGE ÉDITION (DÉDIÉE) ---
elif st.session_state.page == "edit":
    r_edit = st.session_state.get('recipe_to_edit', {})
    
    st.markdown('<h1 style="color: #e67e22;">✏️ Modifier la Recette</h1>', unsafe_allow_html=True)
    
    if st.button("⬅ Annuler et Retour", use_container_width=True):
        st.session_state.page = "details"
        st.rerun()
    
    st.divider()
    
    with st.container():
        col_t, col_c = st.columns([2, 1])
        titre_edit = col_t.text_input("🏷️ Nom de la recette", value=r_edit.get('Titre', ''))
        
        # Sécurité pour le multiselect (évite le crash StreamlitAPIException)
        raw_cats = str(r_edit.get('Catégorie', 'Autre'))
        current_cats = [c.strip() for c in raw_cats.split(',') if c.strip()]
        valid_cats = [c for c in current_cats if c in CATEGORIES]
        if not valid_cats: valid_cats = ["Autre"]
        
        cat_choisies = col_c.multiselect("📁 Catégories", CATEGORIES, default=valid_cats)
        
        st.markdown("#### ⏱️ Paramètres de cuisson")
        cp1, cp2, cp3 = st.columns(3)
        t_prep = cp1.text_input("🕒 Préparation (min)", value=str(r_edit.get('Temps_Prepa', '')))
        t_cuis = cp2.text_input("🔥 Cuisson (min)", value=str(r_edit.get('Temps_Cuisson', '')))
        port = cp3.text_input("🍽️ Portions", value=str(r_edit.get('Portions', '')))
        
        st.divider()
        
        ci, ce = st.columns(2)
        ingredients = ci.text_area("🍎 Ingrédients", height=300, value=r_edit.get('Ingrédients', ''))
        instructions = ce.text_area("👨‍🍳 Étapes de préparation", height=300, value=r_edit.get('Préparation', ''))
        
        img_url = st.text_input("🖼️ Lien de l'image (URL)", value=r_edit.get('Image', ''))
        commentaires = st.text_area("📝 Mes Notes & Astuces", height=100, value=r_edit.get('Commentaires', ''))
        
        st.divider()
        
        if st.button("💾 ENREGISTRER LES MODIFICATIONS", use_container_width=True):
            if titre_edit and ingredients:
                payload = {
                    "action": "edit", 
                    "titre": titre_edit, 
                    "Catégorie": ", ".join(cat_choisies), 
                    "Ingrédients": ingredients, 
                    "Préparation": instructions, 
                    "Image": img_url, 
                    "Temps_Prepa": t_prep, 
                    "Temps_Cuisson": t_cuis, 
                    "Portions": port, 
                    "Note": r_edit.get('Note', 0), 
                    "Commentaires": commentaires
                }
                if send_action(payload):
                    st.success("✅ Recette mise à jour !")
                    st.cache_data.clear()
                    # On nettoie et on retourne à l'accueil
                    if 'recipe_to_edit' in st.session_state: del st.session_state.recipe_to_edit
                    st.session_state.page = "home"
                    st.rerun()
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

# ======================
# PAGE PLANNING
# ======================
elif st.session_state.page == "planning":
    st.markdown('<h1 style="color: #e67e22;">📅 Mon Planning</h1>', unsafe_allow_html=True)
    
    # --- BARRE D'ACTIONS (Retour et Tout vider) ---
    col_nav, col_clear = st.columns([1, 1])
    with col_nav:
        if st.button("⬅ Retour", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
            
    with col_clear:
        # On vérifie si on est admin pour afficher le bouton de vidage
        if st.session_state.admin_mode:
            if st.button("🗑️ Vider le planning", use_container_width=True, help="Efface uniquement la liste dans Google Sheets"):
                with st.spinner("Nettoyage..."):
                    if send_action({"action": "clear_planning"}):
                        st.cache_data.clear()
                        import time
                        time.sleep(1)
                        st.rerun()
        else:
            # Bouton grisé pour les visiteurs
            st.button("🗑️ Vider (Admin uniquement)", use_container_width=True, disabled=True)

    st.divider()

    try:
        df_plan = pd.read_csv(URL_CSV_PLAN)
        
        if df_plan.empty or len(df_plan) == 0:
            st.info("Ton planning est vide.")
        else:
            # --- NETTOYAGE ET TRI ---
            df_plan['Date'] = pd.to_datetime(df_plan['Date'], errors='coerce')
            df_plan = df_plan.dropna(subset=['Date', 'Titre'])
            df_plan = df_plan.sort_values(by='Date')

            # --- TRADUCTION ---
            jours_fr = {"Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"}
            mois_fr = {"January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août", "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"}

            # --- AFFICHAGE AVEC SÉPARATEUR DE SEMAINE ---
            derniere_semaine = -1
            
            for index, row in df_plan.iterrows():
                semaine_actuelle = row['Date'].isocalendar()[1]
                
                if semaine_actuelle != derniere_semaine:
                    st.markdown(f"""
                        <div style="background-color: #2e313d; padding: 5px 15px; border-radius: 8px; margin: 20px 0 10px 0; border-left: 3px solid #95a5a6;">
                            <span style="color: #95a5a6; font-size: 0.8rem; font-weight: bold; letter-spacing: 1px;">SÉLECTION SEMAINE {semaine_actuelle}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    derniere_semaine = semaine_actuelle

                # --- CARTE DE RECETTE ---
                jour_eng = row['Date'].strftime('%A')
                mois_eng = row['Date'].strftime('%B')
                date_txt = f"{jours_fr.get(jour_eng, jour_eng)} {row['Date'].strftime('%d')} {mois_fr.get(mois_eng, mois_eng)}"
                
                col_txt, col_btn = st.columns([4, 1])
                
                with col_txt:
                    st.markdown(f"""
                    <div style="background-color: #1e2129; padding: 12px; border-radius: 10px; border-left: 4px solid #e67e22; margin-bottom: 5px;">
                        <div style="color: #e67e22; font-size: 0.75rem; font-weight: bold; text-transform: uppercase;">{date_txt}</div>
                        <div style="color: white; font-size: 1.05rem; margin-top: 2px; font-weight: 500;">{row['Titre']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    st.write("") 
                    # Sécurité : Seul l'admin peut supprimer une ligne du planning
                    if st.session_state.admin_mode:
                        if st.button("🗑️", key=f"btn_plan_{index}_{semaine_actuelle}"):
                            with st.spinner():
                                if send_action({"action": "remove_plan", "titre": row['Titre'], "date": str(row['Date'].date())}):
                                    st.cache_data.clear()
                                    import time
                                    time.sleep(1.2)
                                    st.rerun()
                    else:
                        # Icône de cadenas pour les visiteurs
                        st.button("🔒", key=f"lock_{index}", disabled=True)

    except Exception as e:
        st.error(f"Erreur d'affichage du planning : {e}")

# --- PAGE CONVERSION / AIDE-MÉMOIRE ---
elif st.session_state.page == "conversion":
    # Titre stylisé pour le haut de la page
    st.markdown('<h1 style="color: #e67e22;">⚖️ Aide-Mémoire Culinaire</h1>', unsafe_allow_html=True)
    st.write("Convertissez vos mesures et traduisez les termes QC/FR en un clin d'œil.")
    
    if st.button("⬅ Retour à l'accueil"):
        st.session_state.page = "home"
        st.rerun()

    st.divider()

    # Création des onglets pour une navigation fluide sur mobile
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Four", "💧 Liquides", "⚖️ Poids", "📖 Lexique"])

    with tab1:
        st.subheader("Températures du four")
        c1, c2 = st.columns(2)
        with c1:
            temp_in = st.number_input("Valeur", value=350, step=5, key="temp_val")
        with c2:
            mode_temp = st.selectbox("Conversion", ["°F ➔ °C", "°C ➔ °F"], key="temp_mode")
        
        if "°F ➔ °C" in mode_temp:
            res = (temp_in - 32) * 5/9
            st.success(f"🔥 **{temp_in}°F** vaut environ **{round(res)}°C**")
        else:
            res = (temp_in * 9/5) + 32
            st.success(f"🔥 **{temp_in}°C** vaut environ **{round(res)}°F**")

    with tab2:
        st.subheader("Volumes (Liquides)")
        v_val = st.number_input("Quantité", value=1.0, step=0.25, key="vol_val")
        v_unit = st.selectbox("De", ["Tasse(s)", "Cuillère à soupe (table)", "Cuillère à thé (café)", "Once (oz)"])
        
        if "Tasse" in v_unit: st.info(f"💧 = **{int(v_val * 250)} ml**")
        elif "soupe" in v_unit: st.info(f"💧 = **{int(v_val * 15)} ml**")
        elif "thé" in v_unit: st.info(f"💧 = **{int(v_val * 5)} ml**")
        else: st.info(f"💧 = **{int(v_val * 30)} ml**")

    with tab3:
        st.subheader("Masses (Poids)")
        p_val = st.number_input("Valeur", value=1.0, step=0.1, key="poids_val")
        p_unit = st.selectbox("Conversion", ["Livres (lb) ➔ Grammes", "Onces (oz) ➔ Grammes", "Grammes ➔ Onces (oz)"])
        
        if "Livres" in p_unit:
            st.warning(f"⚖️ **{p_val} lb** = **{round(p_val * 454)} g**")
        elif "Onces" in p_unit:
            st.warning(f"⚖️ **{p_val} oz** = **{round(p_val * 28.35)} g**")
        else:
            st.warning(f"⚖️ **{p_val} g** = **{round(p_val / 28.35, 2)} oz**")

    with tab4:
        st.subheader("Dictionnaire Québec ⬌ France")
        search = st.text_input("🔍 Chercher un terme...", "").lower()
        lexique = {
            "Poudre à pâte": "Levure chimique", "Soda à pâte": "Bicarbonate de soude",
            "Crème sure": "Crème aigre", "Sucre à glacer": "Sucre glace",
            "Farine tout usage": "Farine T55", "Mijoteuse": "Crock pot / Slow cooker",
            "Papier parchemin": "Papier sulfurisé", "Fécule de maïs": "Maïzena",
            "Échalote française": "Échalote", "Lait évaporé": "Lait concentré non sucré"
        }
        for qc, fr in lexique.items():
            if search in qc.lower() or search in fr.lower():
                st.markdown(f"**{qc}** ➔ *{fr}*")
                                    
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
        
import streamlit as st
import textwrap  # Assure-toi que c'est en haut du fichier


# --- PAGES ---
if st.session_state.page == "home":
    st.write("Bienvenue sur Mes Recettes Pro")

elif st.session_state.page == "details":
    st.write("Détails de la recette")

# --- PAGE IMPRIMABLE FINALE (ZÉRO BOITE NOIRE) ---
elif st.session_state.page == "print":
    if 'recipe_data' not in st.session_state:
        st.error("Aucune donnée de recette trouvée.")
        if st.button("⬅ Retour"): 
            st.session_state.page = "home"
            st.rerun()
    else:
        r = st.session_state.recipe_data
        
        # 1. NAVIGATION
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅ Retour aux détails", use_container_width=True):
                st.session_state.page = "details"
                st.rerun()
        with col2:
            import streamlit.components.v1 as components
            components.html('<button onclick="window.parent.print()" style="width:100%; height:40px; background:#e67e22; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">🖨️ LANCER L\'IMPRESSION</button>', height=50)

        # 2. CSS DE FORCE
        st.markdown("""
<style>
@media print {
    [data-testid="stHeader"], [data-testid="stSidebar"], footer, .stButton, button, iframe { display: none !important; }
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stCanvas"], .main {
        background-color: white !important;
        color: black !important;
    }
    [data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; }
    .print-sheet { margin-top: -60px !important; }
    .page-break { page-break-before: always; margin-top: 20px; }
    p, div, li { page-break-inside: avoid; }
}
.print-sheet { background: white !important; color: black !important; padding: 20px; font-family: sans-serif; }
.header-line { border-bottom: 3px solid #e67e22; margin-bottom: 10px; }
.info-box { display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 15px; font-size: 14px; border-bottom: 1px solid #eee; padding-bottom: 5px; }
h1 { color: black !important; margin: 0 !important; font-size: 30px; }
h3 { color: #e67e22 !important; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

        # 3. TRAITEMENT DES DONNÉES
        ing_raw = str(r.get('Ingrédients','')).split('\n')
        html_ing = "".join([f"<div style='margin-bottom:3px;'>• {l.strip()}</div>" for l in ing_raw if l.strip()])
        prepa_final = str(r.get('Préparation', '')).replace('\n', '<br>')
        
        # Logique de saut de page
        nb_ingredients = len([l for l in ing_raw if l.strip()])
        class_saut_page = "page-break" if nb_ingredients > 15 else ""

        # 4. RENDU FINAL (SANS AUCUNE INDENTATION DANS LE TEXTE)
        # TRÈS IMPORTANT : Ne rajoute pas d'espaces au début des lignes ci-dessous !
        fiche_html = f"""
<div class="print-sheet">
<div class="header-line"><h1>{r.get('Titre','Recette')}</h1></div>
<div class="info-box">
<span>Catégorie : {r.get('Catégorie','-')}</span>
<span>Portions : {r.get('Portions','-')}</span>
<span>Temps : {r.get('Temps_Prepa','0')} + {r.get('Temps_Cuisson','0')} min</span>
</div>
<div style="margin-bottom: 15px;">
<h3>🛒 Ingrédients</h3>
<div style="column-count: 2; column-gap: 30px; font-size: 13px;">{html_ing}</div>
</div>
<div class="{class_saut_page}">
<h3>👨‍🍳 Préparation</h3>
<div style="line-height: 1.5; text-align: justify; font-size: 13px;">{prepa_final}</div>
</div>
<div style="text-align:center; color:#888; font-size:11px; margin-top:30px; border-top:1px solid #eee; padding-top:10px;">Généré par Mes Recettes Pro</div>
</div>
"""
        st.markdown(fiche_html, unsafe_allow_html=True)
# --- PAGE AIDE ---
elif st.session_state.page=="help":
    st.markdown('<h1 style="color: #e67e22;">❓ Centre d\'aide</h1>', unsafe_allow_html=True)
    
    # --- 1. BARRE DE STATUTS RAPIDE ---
    st.info("💡 **Astuce :** Pour une meilleure expérience sur mobile, ajoutez cette page à votre écran d'accueil via le menu de votre navigateur.")

    # --- 2. LES FONCTIONNALITÉS CLÉS (Grille de cartes) ---
    st.subheader("🚀 Guide de démarrage")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color:#1e2130; padding:20px; border-radius:15px; border-left:5px solid #4285F4; height:200px;">
            <h4 style="color:#4285F4; margin-top:0;">📥 Importer une recette</h4>
            <p style="font-size:0.9rem;">Copiez l'adresse URL d'un site (ex: Ricardo, Marmiton) et collez-la dans la section <b>Ajouter</b>. 
            L'intelligence artificielle extraira le titre et les étapes pour vous !</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("") # Espace
        st.markdown("""
        <div style="background-color:#1e2130; padding:20px; border-radius:15px; border-left:5px solid #28B463; height:200px;">
            <h4 style="color:#28B463; margin-top:0;">🛒 Liste de courses</h4>
            <p style="font-size:0.9rem;">Dans la fiche d'une recette, cochez les ingrédients manquants et cliquez sur <b>Ajouter au panier</b>. 
            Ils apparaîtront instantanément dans votre liste d'épicerie.</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background-color:#1e2130; padding:20px; border-radius:15px; border-left:5px solid #e67e22; height:200px;">
            <h4 style="color:#e67e22; margin-top:0;">📝 Gérer vos favoris</h4>
            <p style="font-size:0.9rem;">Utilisez la barre de recherche en haut de la <b>Bibliothèque</b> pour filtrer par nom ou par catégorie. 
            Vous pouvez aussi noter vos recettes de 1 à 5 étoiles.</p>
        </div>
        """, unsafe_allow_html=True)
        st.write("") # Espace
        st.markdown("""
        <div style="background-color:#1e2130; padding:20px; border-radius:15px; border-left:5px solid #FF33FF; height:200px;">
            <h4 style="color:#FF33FF; margin-top:0;">📅 Planning</h4>
            <p style="font-size:0.9rem;">Le planning se synchronise avec votre Google Sheets. Vous y retrouverez les dates prévues pour vos prochains repas 
            pour ne plus jamais manquer d'inspiration.</p>
        </div>
        """, unsafe_allow_html=True)

    # --- 3. FOIRE AUX QUESTIONS (Expander) ---
    st.divider()
    st.subheader("🤔 Questions fréquentes")
    
    with st.expander("Comment modifier une recette existante ?"):
        st.write("Allez dans la bibliothèque, ouvrez la recette de votre choix, puis cliquez sur le bouton ✏️ **Éditer** en haut de la page.")

    with st.expander("L'image de ma recette ne s'affiche pas ?"):
        st.write("Assurez-vous que le lien (URL) se termine par .jpg, .png ou .webp. Si vous utilisez Google Images, faites un clic droit sur l'image et choisissez 'Copier l'adresse de l'image'.")

    with st.expander("Comment supprimer un article de la liste d'épicerie ?"):
        st.write("Dans la page **Ma Liste**, cochez les articles que vous avez achetés, puis cliquez sur le bouton rouge **Retirer les articles sélectionnés**.")

    # --- 4. BOUTON RETOUR ---
    st.write("")
    if st.button("⬅ Retour à la Bibliothèque", use_container_width=True):
        st.session_state.page="home"
        st.rerun()








































































































