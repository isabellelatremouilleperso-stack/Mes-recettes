import streamlit as st
import pandas as pd
import requests
import time
import hashlib
import urllib.parse
import textwrap
from datetime import datetime
from bs4 import BeautifulSoup

# ======================
# CONFIGURATION & LIAISON GOOGLE
# ======================

# 1. Utilisation sécurisée du secret
URL_SCRIPT = st.secrets["Lien_Google"]

# 2. URLs CSV
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/16B4GAT1zILsO_NR73i7oGIiWh2KWeowsXOgRT6b21VY/export?format=csv&gid=1037930000"
URL_CSV_PLAN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=536412190&single=true&output=csv"

# ======================
# CONFIGURATION DES DONNÉES
# ======================
mes_categories = [
    "Toutes", "Accompagnement", "Agneau", "Air Fryer", "Apéro", "Asiatique", 
    "BBQ", "Biscuits", "Boisson", "Boîte à lunch", "Boulangerie", "Buffet", "Buffet chinois", "Bœuf", "Cabane à sucre", 
    "Condiment", "Confiserie", "Crème-glacée", "Dessert", "Entrée", "Épices", 
    "Fondue", "Four à pizza", "Fruits de mer", "Fumoir", "Gâteau", "Goûter", 
    "Indien", "Légumes", "Libanais", "Marinade", "Mexicain", "Muffins", 
    "Ninja Creami", "Ninja Slushie", "Pains", "Pâtes", "Pâtisserie", 
    "Petit-déjeuner", "Pizza", "Plancha", "Plat Principal", "Poisson", 
    "Poke bowl", "Porc", "Poulet", "Poutine", "Riz", "Salade", "Sandwich",  
    "Sauce", "Slow Cooker", "Soupe", "Sport", "Sushi", "Tartare", "Temps des fêtes", 
    "Végétarien", "Vinaigrette", "Autre"
]

# ======================
# FONCTIONS TECHNIQUES (VERSION NETTOYÉE)
# ======================

import streamlit as st
import pandas as pd
import requests
import time
import hashlib
import re  # <--- AJOUTÉ : Indispensable pour le scraping
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse

# ... (tes URLs et catégories restent identiques) ...

def send_action(payload):
    """Envoie les données vers Google Apps Script avec diagnostic."""
    with st.spinner("🚀 Action en cours..."):
        try:
            # On s'assure que l'URL est bien celle du script
            headers = {"Content-Type": "application/json"}
            r = requests.post(URL_SCRIPT, json=payload, headers=headers, timeout=20)
            
            # Diagnostic : On vérifie si "Success" est présent peu importe la casse
            if "success" in r.text.lower():
                st.cache_data.clear() 
                # On ne fait pas de rerun ici, on laisse le bouton appelant le faire
                return True
            else:
                st.error(f"⚠️ Erreur Google : {r.text}")
                return False
        except Exception as e:
            st.error(f"❌ Erreur de connexion : {e}")
            return False

# Modifie ta fonction load_data comme ceci :
@st.cache_data(ttl=3600) # Cache d'une heure par défaut
def load_data(url, force_refresh=False):
    # On n'ajoute le nocache QUE si on force manuellement, sinon on utilise le cache local
    timestamp = int(time.time()) if force_refresh else "stable"
    sep = "&" if "?" in url else "?"
    timestamp_url = f"{url}{sep}v={timestamp}"
    
    try:
        df = pd.read_csv(timestamp_url)
        df = df.fillna('')
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame()

def scrape_url(url):
    import re
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=12)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')

        # 1. Extraction du Titre
        title = "Recette Importée"
        h1_tag = soup.find('h1')
        if h1_tag:
            title = h1_tag.get_text().strip()

        # 2. Nettoyage du bruit (on enlève ce qui n'est pas de la nourriture)
        for junk in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "ins", "button"]):
            junk.extract()

        # 3. Ciblage des conteneurs
        # On cherche les zones qui contiennent "ingredient" ou "recipe-ing"
        ing_container = soup.find(class_=re.compile(r'ingredient|recipe-ing', re.I))
        # On cherche les zones qui contiennent "instruction" ou "step"
        prep_container = soup.find(class_=re.compile(r'instruction|preparation|method|steps|direction', re.I))

        # --- LOGIQUE INGRÉDIENTS ---
        ing_list = []
        # Si on a trouvé un conteneur spécifique, on ne cherche que dedans
        source_ingredients = ing_container if ing_container else soup
        
        # On cherche les <li> (puces) qui sont le standard des ingrédients
        for el in source_ingredients.find_all('li'):
            # separator=" " est vital pour ne pas coller "10" et "grammes" -> "10grammes"
            txt = el.get_text(separator=" ").strip()
            # Nettoyage des espaces doubles
            txt = re.sub(r'\s+', ' ', txt)
            
            # FILTRE : On garde si c'est une ligne de taille raisonnable et pas un lien menu
            if 3 < len(txt) < 150:
                if not any(x in txt.lower() for x in ["connexion", "mon compte", "partager", "imprimer", "newsletter"]):
                    ing_list.append(f"❑ {txt}")

        # --- LOGIQUE PRÉPARATION ---
        prep_list = []
        source_prep = prep_container if prep_container else soup
        
        # On cherche les paragraphes ou les puces d'instructions
        for el in source_prep.find_all(['p', 'li']):
            txt = el.get_text(separator=" ").strip()
            txt = re.sub(r'\s+', ' ', txt)
            
            # On garde les blocs de texte assez longs pour être des étapes
            if len(txt) > 20:
                if not any(x in txt.lower() for x in ["cookies", "droits réservés", "abonnez-vous", "cliquez ici"]):
                    prep_list.append(txt)

        # 4. Finalisation (Suppression des doublons en gardant l'ordre)
        final_ing = "\n".join(list(dict.fromkeys(ing_list)))
        final_prep = "\n\n".join(list(dict.fromkeys(prep_list)))

        return title, final_ing, final_prep

    except Exception as e:
        return "Recette inconnue", "", f"Erreur lors de l'extraction : {e}"
        
import streamlit as st
import hashlib
import time

# ======================
# INITIALISATION ET DESIGN
# ======================

# 1. Configuration de la page (DOIT être la première commande)
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False

# 2. Style CSS (Ta mise en forme)
st.markdown("""
<style>
    .stApp { background-color: #0e1117 !important; }
    [data-testid="stSidebar"] { background-color: #1e2129 !important; }
    h1, h2, h3 { color: #e67e22 !important; }
    .stButton button { 
        background-color: #e67e22 !important; 
        color: white !important; 
        border-radius: 10px; 
        border: none;
        font-weight: bold;
    }
    .logo-container { display: flex; justify-content: center; margin-bottom: 20px; }
    .logo-container img { border-radius: 50%; width: 120px; height: 120px; object-fit: cover; border: 3px solid #e67e22; }
</style>
""", unsafe_allow_html=True)

# ======================
# BARRE LATÉRALE (SIDEBAR)
# ======================
with st.sidebar:
    # Logo et Design
    st.markdown('<div class="logo-container"><img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png"></div>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #e67e22;">Mes Recettes</h3>', unsafe_allow_html=True)

    # --- SECTION SÉCURITÉ (TEST DE RÉALITÉ) ---
    if not st.session_state.get('admin_mode', False):
        pwd_input = st.text_input("🔑 Accès Admin", type="password", key="sidebar_pwd")
        
        if st.button("Se connecter 🔓", use_container_width=True):
            user_code = str(pwd_input).strip()
            input_hash = hashlib.sha256(user_code.encode()).hexdigest().strip()
            
            # Récupération
            target_hash = st.secrets.get("admin_password_hash", "").strip()
            
            if input_hash == target_hash:
                st.session_state.admin_mode = True
                st.rerun()
            else:
                st.error("Accès refusé ❌")
                # ON AFFICHE LES LONGUEURS POUR TROUVER L'ERREUR
                st.info(f"Saisie : {len(input_hash)} car. | Secret : {len(target_hash)} car.")
                if len(target_hash) == 0:
                    st.warning("⚠️ Ton secret 'admin_password_hash' n'est pas trouvé dans Streamlit Cloud.")
    else:
        st.success("✅ Mode Chef Activé")
        if st.button("🔒 Déconnexion", use_container_width=True, key="sidebar_logout_action"):
            st.session_state.admin_mode = False
            st.rerun()

    st.divider()

    # --- NAVIGATION PRINCIPALE ---
    if st.button("📚 Bibliothèque", use_container_width=True, key="nav_sidebar_home"): 
        st.session_state.page = "home"
        st.rerun()
    
    if st.button("📅 Planning", use_container_width=True, key="nav_sidebar_plan"): 
        st.session_state.page = "planning"
        st.rerun()
    
    if st.button("🛒 Ma Liste d'épicerie", use_container_width=True, key="nav_sidebar_shop"): 
        st.session_state.page = "shop"
        st.rerun()

    # --- OPTIONS SUPPLÉMENTAIRES ---
    st.divider()
    
    if st.session_state.get('admin_mode', False):
        if st.button("➕ AJOUTER RECETTE", use_container_width=True, key="nav_sidebar_add"):
            st.session_state.page = "add"
            st.rerun()
    
    if st.button("⭐ Play Store", use_container_width=True, key="nav_sidebar_play"): 
        st.session_state.page = "playstore"
        st.rerun()
        
    if st.button("❓ Aide", use_container_width=True, key="nav_sidebar_help"): 
        st.session_state.page = "help"
        st.rerun()
       
    if st.button("🔄 Actualiser les données", use_container_width=True):
        st.cache_data.clear()
        st.toast("Mise à jour réussie ! 📋")
        time.sleep(0.5)
        st.rerun()

    st.divider()
 
# ======================
# LOGIQUE DES PAGES (CONTENU PRINCIPAL)
# ======================

if st.session_state.page == "home":
    c1, c2 = st.columns([4, 1])
    c1.header("📚 Ma Bibliothèque")
    if c2.button("🔄 Actualiser"):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    
    st.write("Bienvenue dans votre bibliothèque de recettes !")
    # --- NOUVELLE BARRE D'OUTILS (Navigation rapide) ---
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("📅 Voir mon Planning", use_container_width=True):
            st.session_state.page = "planning"
            st.rerun()
    with col_nav2:
        if st.button("📏 Aide-Mémoire & Conversions", use_container_width=True):
            st.session_state.page = "conversion"
            st.rerun()
    
    st.write("") # Petit espace esthétique

    # --- STYLE CSS ---
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
    
    df = load_data(URL_CSV)

    if not df.empty:
        # --- BARRE DE FILTRES ET TRI ---
        col_search, col_cat, col_tri = st.columns([2, 1, 1])
        
        with col_search:
            search = st.text_input("🔍 Rechercher (titre ou ingrédient)...", placeholder="Ex: Poulet, Sauce...")
            
        with col_cat:
    # LISTE MISE À JOUR : + Sandwich
            mes_categories = [
                "Toutes", "Accompagnement", "Agneau", "Air Fryer", "Apéro", "Asiatique", 
                "BBQ", "Biscuits", "Boisson", "Boulangerie", "Buffet", "Buffet chinois", "Bœuf", "Cabane à sucre", "Condiment", 
                "Confiserie", "Crème-glacée", "Dessert", "Entrée", "Épices", "Fondue", 
                "Four à pizza", "Fruits de mer", "Fumoir", "Gâteau", "Goûter", "Indien", 
                "Légumes", "Libanais", "Marinade", "Mexicain", "Muffins", "Ninja Creami", 
                "Ninja Slushie", "Pains", "Pâtes", "Pâtisserie", "Petit-déjeuner", "Pizza", 
                "Plancha", "Plat Principal", "Poisson", "Poke bowl", "Porc", "Poulet", 
                "Poutine", "Riz", "Salade", "Sandwich", "Sauce", "Slow Cooker", "Soupe", "Sport",
                "Sushi", "Tartare", "Temps des fêtes", "Végétarien", "Vinaigrette", "Autre"
            ]
            cat_choisie = st.selectbox("📁 Filtrer par catégorie", mes_categories)

        with col_tri:
            ordre = st.selectbox("🔃 Trier par :", ["A ➡️ Z", "Z ➡️ A", "Les plus récentes"])
        
        # --- LOGIQUE DE FILTRE ---
        mask = (df['Titre'].str.contains(search, case=False, na=False)) | \
               (df['Ingrédients'].str.contains(search, case=False, na=False))
        
        if cat_choisie != "Toutes":
            mask = mask & (df['Catégorie'].str.contains(cat_choisie, case=False, na=False))
        
        rows = df[mask].copy()

        # --- LOGIQUE DE TRI ---
        if ordre == "A ➡️ Z":
            rows = rows.sort_values(by="Titre", ascending=True)
        elif ordre == "Z ➡️ A":
            rows = rows.sort_values(by="Titre", ascending=False)
        elif ordre == "Les plus récentes":
            rows = rows.iloc[::-1] 

        rows = rows.drop_duplicates(subset=['Titre']).reset_index(drop=True)

        # --- FONCTION COULEUR (MISE À JOUR AVEC 49 CATÉGORIES) ---

        def get_cat_color(cat):
            colors = {
                "Accompagnement": "#00A36C",
                "Agneau": "#8B4513",
                "Air Fryer": "#FF4500",
                "Apéro": "#FF4500",
                "Asiatique": "#FF1493",
                "BBQ": "#900C3F",
                "Biscuits": "#D2B48C",
                "Boisson": "#7FFFD4",
                "Boîte à lunch": "#008080",
                "Boulangerie": "#DEB887",
                "Buffet": "#FF8C00",          # Orange vif pour la variété
                "Buffet chinois": "#EE2436",  # Rouge impérial
                "Bœuf": "#C70039",
                "Cabane à sucre": "#D2691E",
                "Condiment": "#DAA520",
                "Confiserie": "#FF69B4",
                "Crème-glacée": "#AFEEEE",
                "Dessert": "#FF33FF",
                "Entrée": "#95A5A6",
                "Épices": "#CD5C5C",
                "Fondue": "#FFD700",
                "Four à pizza": "#E74C3C",
                "Fruits de mer": "#00CED1",
                "Fumoir": "#333333",
                "Gâteau": "#F08080",
                "Goûter": "#D2691E",
                "Indien": "#FF9933",
                "Légumes": "#28B463",
                "Libanais": "#EE2436",
                "Marinade": "#A0522D",
                "Mexicain": "#006341",
                "Muffins": "#BC8F8F",
                "Ninja Creami": "#E0FFFF",
                "Ninja Slushie": "#00BFFF",
                "Pains": "#F5DEB3",
                "Pâtes": "#F1C40F",
                "Pâtisserie": "#EDB9F1",
                "Petit-déjeuner": "#FFD700",
                "Pizza": "#FF6347",
                "Plancha": "#708090",
                "Plat Principal": "#E67E22",
                "Poisson": "#3498DB",
                "Poke bowl": "#20B2AA",
                "Porc": "#FFC0CB",
                "Poulet": "#FF5733",
                "Poutine": "#6F4E37",
                "Riz": "#F5F5DC",
                "Salade": "#7CFC00",
                "Sandwich": "#DAA520",
                "Sauce": "#8B0000",
                "Slow Cooker": "#4B0082",
                "Soupe": "#4682B4",
                "Sport": "#1E90FF",
                "Sushi": "#FF1493",
                "Tartare": "#B22222",
                "Temps des fêtes": "#C41E3A",
                "Temps des fetes": "#C41E3A",
                "Végétarien": "#32CD32",
                "Vinaigrette": "#9ACD32",
                "Autre": "#BDC317"
            }
            # La ligne ci-dessous doit être alignée avec le début de 'colors'
            return colors.get(str(cat).strip(), "#BDC317")
    
        # --- AFFICHAGE DES RÉSULTATS ---
        for i in range(0, len(rows), 2):
            grid_cols = st.columns(2) 
            for j in range(2):
                if i+j < len(rows):
                    row = rows.iloc[i+j]
                    with grid_cols[j]:
                        img_url = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/500x350"
                        
                        raw_cats = str(row['Catégorie']).split(',') if row['Catégorie'] else ["Recette"]
                        badges_html = "".join([f'<span class="category-badge" style="background-color:{get_cat_color(c)}; color:white; padding:2px 8px; border-radius:10px; margin-right:5px; font-size:10px; display:inline-block; margin-bottom:4px;">{c.strip()}</span>' for c in raw_cats if c.strip()])

                        st.markdown(f"""
                            <div class="recipe-card">
                                <div class="recipe-img-container"><img src="{img_url}"></div>
                                <div class="recipe-content">
                                    <div style="margin-bottom:8px;">{badges_html}</div>
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
# --- FIN DU BLOC HOME ---

# --- PAGE DÉTAILS ---
elif st.session_state.page == "details":
    
    # 1. RÉCUPÉRATION ET NETTOYAGE
    r_raw = st.session_state.get('recipe_data', {})
    
    if not r_raw:
        st.error("Aucune donnée trouvée.")
        if st.button("⬅ Retour"):
            st.session_state.page = "home"; st.rerun()
        st.stop()

    if isinstance(r_raw, pd.DataFrame):
        r = r_raw.iloc[0].to_dict()
    elif isinstance(r_raw, list) and len(r_raw) > 0:
        r = r_raw[0]
    else:
        r = r_raw

    current_title = r.get('Titre', 'Recette sans titre')
    is_admin = st.session_state.get('admin_mode', False)

    # --- BARRE DE NAVIGATION ---
    if is_admin:
        c_nav1, c_nav2, c_nav3, c_nav4 = st.columns([1, 1, 1, 1])
        with c_nav1:
            if st.button("⬅ Retour", use_container_width=True, key="btn_ret_adm"): 
                st.session_state.page="home"; st.rerun()
        with c_nav2:
            if st.button("✏️ Éditer", use_container_width=True, key="btn_edit_adm"):
                st.session_state.recipe_to_edit = r.copy()
                st.session_state.page = "edit"; st.rerun()
        with c_nav3:
            if st.button("🖨️ Imprimer", use_container_width=True, key="btn_print_adm"):
                st.session_state.recipe_data = r; st.session_state.page = "print"; st.rerun()
        with c_nav4:
            if st.button("🗑️ Supprimer", use_container_width=True, key="btn_del_adm"):
                if send_action({"action": "delete", "titre": current_title}):
                    st.cache_data.clear(); st.session_state.page = "home"; st.rerun()
    else:
        c_nav_pub1, c_nav_pub2 = st.columns([1, 1])
        with c_nav_pub1:
            if st.button("⬅ Retour", use_container_width=True, key="btn_ret_pub"): 
                st.session_state.page="home"; st.rerun()
        with c_nav_pub2:
            if st.button("🖨️ Imprimer la recette", use_container_width=True, key="btn_print_pub"):
                st.session_state.recipe_data = r; st.session_state.page = "print"; st.rerun()

    st.divider()
    st.header(f"📖 {current_title}")
    
    # --- CORPS DE LA PAGE (IMAGE ET INFOS) ---
    col_g, col_d = st.columns([1, 1.2])
    
    with col_g:
        # 1. Gestion de l'image (Reste seule à gauche pour plus d'impact)
        img_url = r.get('Image', '')
        img_url_str = str(img_url).strip() if img_url else ""
        img_source = img_url_str if img_url_str.startswith("http") else "https://via.placeholder.com/400?text=Pas+d'image"

        try:
            st.image(img_source, use_container_width=True)
        except Exception:
            st.image("https://via.placeholder.com/400?text=Erreur+Image", use_container_width=True)

    # --- TOUT CE QUI SUIT EST DÉSORMAIS RANGÉ DANS LA COLONNE DE DROITE ---
    with col_d:
        # 1. BOUTONS D'INTERACTION RAPIDE (Cuisinée / Favoris)
        c_feat1, c_feat2 = st.columns(2)
        
        with c_feat1:
            import random
            # Liste de messages pour les chefs
            mots_bravo = [
                "Et un michelin de plus ! ⭐", 
                "Gordon Ramsay n'a qu'à bien se tenir ! 👨‍🍳", 
                "C'est meilleur que chez maman ! 🤫", 
                "Appelez les pompiers, c'est du FEU ! 🔥",
                "Miam ! On arrive à quelle heure ? 🏃‍♂️"
            ]

            if 'made_list' not in st.session_state:
                st.session_state.made_list = set()
            
            is_made = current_title in st.session_state.made_list
            label_made = "✅ Testé !" if is_made else "👨‍🍳 Cuisinée ?"
            
            # Action du bouton
            if st.button(label_made, use_container_width=True, key=f"det_made_{current_title}", type="primary" if is_made else "secondary"):
                if is_made:
                    st.session_state.made_list.remove(current_title)
                    st.rerun() # On garde le rerun uniquement pour décocher (enlever le vert)
                else:
                    st.session_state.made_list.add(current_title)
                    
                    # 1. Barre de progression (Effet pro et visuel)
                    barre_succes = st.progress(0)
                    import time
                    for pourcentage in range(100):
                        time.sleep(0.005) 
                        barre_succes.progress(pourcentage + 1)
                    
                    # 2. Message de réussite stylé (Le bandeau vert)
                    st.success(f"Recette validée ! {random.choice(mots_bravo)}")
                    
                    # 3. Notification Toast (Messages variés et punchy)
                    messages_succes = [
                        "Mission accomplie, Chef ! 🎖️",
                        "Miam ! Une pépite de plus au palmarès ! 😋",
                        "Validé par le jury (et ton estomac) ! ✅",
                        "Hop ! C'est dans la boîte ! 🚀",
                        "Tes papilles te disent merci ! 🍴"
                    ]
                    
                    # On choisit un message au hasard dans la liste
                    msg_toast = random.choice(messages_succes)
                    st.toast(msg_toast, icon="✨")
                    
                    # 4. Petite pause pour savourer le succès
                    time.sleep(1.0)
                    
                    # 5. On rafraîchit pour afficher le bouton "Testé"
                    st.rerun()
                    
        with c_feat2:
            if 'fav_list' not in st.session_state:
                st.session_state.fav_list = set()
            
            is_fav = current_title in st.session_state.fav_list
            if st.button("⭐ Préférée" if is_fav else "☆ Favoris", use_container_width=True, key=f"det_fav_{current_title}", type="primary" if is_fav else "secondary"):
                if is_fav:
                    st.session_state.fav_list.remove(current_title)
                else:
                    st.session_state.fav_list.add(current_title)
                    st.toast("Ajouté aux coups de cœur ! 💖")
                st.rerun()

        st.divider()

        # 2. SYSTÈME DE NOTATION (Déplacé ici sur le côté)
        try:
            val_note = r.get('Note', 0)
            note_actuelle = int(float(val_note)) if str(val_note).strip() not in ["", "None", "nan", "-", "0"] else 0
        except: 
            note_actuelle = 0

        st.write(f"**Évaluer cette recette ({note_actuelle} ⭐) :**")
        nouvelle_note = st.select_slider(
            "Note", options=[0, 1, 2, 3, 4, 5], value=note_actuelle, 
            key=f"sl_droit_{current_title}", label_visibility="collapsed"
        )
        
        if nouvelle_note != note_actuelle:
            with st.spinner("Mise à jour..."):
                if send_action({"action": "edit", "old_titre": current_title.strip(), "Note": nouvelle_note}):
                    st.toast("Note enregistrée ! ⭐")
                    st.cache_data.clear(); st.rerun()

        st.write("") 

        # 3. INFORMATIONS GÉNÉRALES
        st.subheader("📋 Informations")
        c_i1, c_i2 = st.columns(2)
        with c_i1:
            st.markdown(f"**🍴 Catégorie :**\n`{r.get('Catégorie', 'Autre')}`")
        with c_i2:
            src_val = r.get('Source', '')
            if src_val and "http" in str(src_val): 
                st.link_button("🌐 Voir la Source", str(src_val), use_container_width=True)
            else: 
                st.markdown("**🌐 Source :**\n*Web*")
        
        # PLANNING OUVERT PAR DÉFAUT (expanded=True)
        with st.expander("📅 **PLANIFIER CETTE RECETTE**", expanded=True):
            u_key = f"plan_{hashlib.md5(current_title.encode()).hexdigest()[:6]}"
            date_p = st.date_input("Choisir une date", key=f"dt_{u_key}")
            if st.button("🗓️ Ajouter au planning", use_container_width=True, key=f"btn_{u_key}"):
                if send_action({"action": "plan", "titre": current_title, "date_prevue": str(date_p)}):
                    st.cache_data.clear(); st.session_state.page = "planning"; st.rerun()

        st.divider()
        
        # 4. MÉTRIQUES LARGES
        m1, m2, m3 = st.columns([1.2, 1.2, 1])
        with m1:
            st.markdown(f"**🕒 Préparation**\n\n{r.get('Temps de préparation', '-')}")
        with m2:
            st.markdown(f"**🔥 Cuisson**\n\n{r.get('Temps de cuisson', '-')}")
        with m3:
            st.markdown(f"**🍽️ Portions**\n\n{r.get('Portions', '-')}")

        st.divider()

        # 4. VIDÉO
        v_link = r.get('Lien vidéo') or r.get('video') or r.get('Vidéo') or ""
        v_link_str = str(v_link).strip()
        if v_link_str.lower().startswith("http"):
            if any(x in v_link_str.lower() for x in ["youtube.com", "youtu.be", "vimeo.com"]):
                with st.expander("🎬 VOIR LE TUTORIEL VIDÉO"):
                    st.video(v_link_str)
            else:
                st.link_button("▶️ Regarder la vidéo", v_link_str, use_container_width=True, type="primary")

    # --- FIN DE LA COLONNE DE DROITE ---
    # --- SECTION INGRÉDIENTS (DEUX COLONNES SOUS LA PHOTO) ---
    st.divider()
    st.subheader("🛒 Ingrédients")
    ings_raw = r.get('Ingrédients', '')
    
    if ings_raw and str(ings_raw).strip() not in ["None", "nan", ""]:
        text_ing = str(ings_raw).replace("❑", "\n").replace(";", "\n")
        ings = [l.strip() for l in text_ing.split("\n") if l.strip()]
        
        sel = []
        col_ing1, col_ing2 = st.columns(2)
        moitie = (len(ings) + 1) // 2
        
        with col_ing1:
            for i in range(moitie):
                # On utilise une clé unique pour chaque checkbox
                if st.checkbox(ings[i], key=f"chk_L_{current_title}_{i}"):
                    sel.append(ings[i])
        with col_ing2:
            for i in range(moitie, len(ings)):
                if st.checkbox(ings[i], key=f"chk_R_{current_title}_{i}"):
                    sel.append(ings[i])
        
        st.write("") 
        
        # --- RÉTABLISSEMENT DU BOUTON ÉPICERIE ---
        if sel:
            if st.button(f"📥 Ajouter ({len(sel)}) au Panier", use_container_width=True, key="btn_add_sel", type="primary"):
                with st.spinner("Envoi à l'épicerie..."):
                    for it in sel:
                        send_action({"action": "add_shop", "article": it})
                st.toast(f"✅ {len(sel)} articles ajoutés !", icon="🛒")
                time.sleep(1); st.rerun()
        else:
            # Message d'info quand rien n'est coché (comme dans ton ancien code)
            st.info("Cochez les ingrédients à acheter pour activer l'ajout au panier.")
    else:
        st.info("Aucun ingrédient pour cette recette.")

    # --- PRÉPARATION (BAS DE PAGE) ---
    st.divider()
    st.subheader("👨‍🍳 Étapes de préparation")
    prep = r.get('Préparation', '')
    if prep:
        st.write(prep)
    else:
        st.warning("Aucune étape enregistrée.")

    # --- NOTES & COMMENTAIRES ---
    st.divider()
    st.markdown("### 📝 Mes Notes & Commentaires")
    notes_texte = r.get('Commentaires', '')
    if notes_texte and str(notes_texte).strip() not in ["None", "nan", ""]:
        st.info(notes_texte)
    else:
        st.write("*Aucune note pour cette recette.*")
        
elif st.session_state.page == "add":
    st.markdown('<h1 style="color: #e67e22;">📥 Ajouter une Nouvelle Recette</h1>', unsafe_allow_html=True)
    
    # --- NAVIGATION ---
    if st.button("⬅ Retour à la Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
        
    # --- SECTION RECHERCHE GOOGLE ---
    st.markdown("""<div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #4285F4; margin-bottom: 20px;"><h4 style="margin:0; color:white;">🔍 Chercher une idée sur Google Canada</h4></div>""", unsafe_allow_html=True)
    
    c_search, c_btn = st.columns([3, 1])
    search_query = c_search.text_input("Que cherchez-vous ?", placeholder="Ex: Pâte à tarte Ricardo", label_visibility="collapsed", max_chars=100)
    
    import urllib.parse
    query_encoded = urllib.parse.quote(search_query + ' recette') if search_query else ""
    target_url = f"https://www.google.ca/search?q={query_encoded}" if search_query else "https://www.google.ca"
    c_btn.markdown(f"""<a href="{target_url}" target="_blank" style="text-decoration: none;"><div style="background-color: #4285F4; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; cursor: pointer;">🌐 Google.ca</div></a>""", unsafe_allow_html=True)
    
    # --- SECTION IMPORTATION ---
    st.markdown("""<div style="background-color: #1e2129; padding: 20px; border-radius: 15px; border: 1px solid #3d4455; margin-top: 10px;"><h3 style="margin-top:0; color:#e67e22;">🌐 Importer depuis le Web</h3>""", unsafe_allow_html=True)
    
    col_url, col_go = st.columns([4, 1])
    
    # On ajoute disabled=True ici pour griser la case de texte
    url_input = col_url.text_input(
        "Collez l'URL ici", 
        placeholder="Désactivé temporairement...", 
        key="url_main", 
        disabled=True
    )
    
    # On ajoute disabled=True ici pour que le bouton ne réagisse plus du tout
    if col_go.button("Bientôt ⏳", use_container_width=True, disabled=True):
        # Ce code est maintenant inaccessible, il ne s'exécutera jamais
        if url_input:
            with st.spinner("Analyse en cours..."):
                t, ing, prep = scrape_url(url_input)
                if t and t.strip() != url_input.strip():
                    st.session_state.scraped_title = t
                    st.session_state.scraped_ingredients = ing
                    st.session_state.scraped_content = prep
                    st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    # --- FORMULAIRE DE SAISIE ---
    with st.container():
        col_t, col_c = st.columns([2, 1])
        titre = col_t.text_input("🏷️ Nom", value=st.session_state.get('scraped_title', ''), placeholder="Nom de la recette")
        
        mes_options = [
            "Accompagnement", "Agneau", "Air Fryer", "Apéro", "Asiatique", 
            "BBQ", "Biscuits", "Boisson", "Boîte à lunch", "Boulangerie", "Buffet", "Buffet chinois","Bœuf", "Cabane à sucre", 
            "Condiment", "Confiserie", "Crème-glacée", "Dessert", "Entrée", 
            "Épices", "Fondue", "Four à pizza", "Fruits de mer", "Fumoir", "Gâteau", 
            "Goûter", "Indien", "Légumes", "Libanais", "Marinade", 
            "Mexicain", "Muffins", "Ninja Creami", "Ninja Slushie", "Pains", 
            "Pâtes", "Pâtisserie", "Petit-déjeuner", "Pizza", "Plancha", 
            "Plat Principal", "Poisson", "Poke bowl", "Porc", "Poulet", 
            "Poutine", "Riz", "Salade", "Sandwich", "Sauce", "Slow Cooker", 
            "Soupe", "Sport", "Sushi", "Tartare", "Temps des fêtes", "Végétarien", 
            "Vinaigrette", "Autre"
        ]
        cat_choisies = col_c.multiselect("📁 Catégories", mes_options)
        
        col_link1, col_link2 = st.columns(2)
        source_url_in = col_link1.text_input("🔗 Lien source", value=url_input if url_input else "", placeholder="https://...")
        video_url_in = col_link2.text_input("🎬 Lien Vidéo", placeholder="URL vidéo...")
        
        st.markdown("#### ⏱️ Paramètres")
        cp1, cp2, cp3 = st.columns(3)
        t_prep = cp1.text_input("🕒 Préparation (min)", placeholder="15", key="p_time")
        t_cuis = cp2.text_input("🔥 Cuisson (min)", placeholder="45", key="c_time")
        port = cp3.text_input("🍽️ Portions", placeholder="4", key="portions")
        
        st.divider()
        
        ci, ce = st.columns(2)
        ingredients_txt = ci.text_area("🍎 Ingrédients", value=st.session_state.get('scraped_ingredients', ''), height=350, key="ing_area")
        instructions_txt = ce.text_area("👨‍🍳 Étapes", value=st.session_state.get('scraped_content', ''), height=350, key="prep_area")
        
        img_url = st.text_input("🖼️ Lien de l'image", placeholder="https://...", key="img_url")
        commentaires = st.text_area("📝 Mes Notes", height=100, key="notes_area")
        
        st.divider()
        
        c_save, c_cancel = st.columns(2)
        if c_save.button("💾 ENREGISTRER MA RECETTE", use_container_width=True):
            if titre and ingredients_txt:
                import datetime
                import re

                # 1. NETTOYAGE DES SYMBOLES MAIS GARDE LES ACCENTS
                # On remplace les caractères spéciaux/graphiques par un saut de ligne, 
                # mais on exclut de la suppression les lettres accentuées françaises.
                # Cela permet de garder "Épaule", "Cuillère", etc.
                text_split = re.sub(r'[^\w\s.,\-()%/°àâäéèêëîïôöùûüçÀÂÄÉÈÊËÎÏÔÖÙÛÜÇ]+', '\n', ingredients_txt)
                
                # 2. NETTOYAGE DES LIGNES VIDES
                # On sépare le texte par ligne, on enlève les espaces inutiles, 
                # et on ne garde que les lignes qui contiennent vraiment du texte.
                lignes = text_split.split('\n')
                ing_propre = "\n".join([l.strip() for l in lignes if l.strip()])

                # --- PAYLOAD ---
                payload = {
                    "action": "add",
                    "date": datetime.date.today().strftime("%d/%m/%Y"),
                    "titre": titre.strip(),
                    "source": source_url_in.strip(),
                    "Ingrédients": ing_propre,  # Texte propre ligne par ligne, sans tirets ajoutés
                    "Préparation": instructions_txt.strip(),
                    "Image": img_url.strip(),
                    "Catégorie": ", ".join(cat_choisies),
                    "Portions": port.strip(),
                    "Temps_Prepa": t_prep.strip(),
                    "Temps_Cuisson": t_cuis.strip(),
                    "Commentaires": commentaires.strip(),
                    "video": video_url_in.strip()
                }
                
                # ... (suite du code d'envoi send_action)
                
                # ... (reste du code d'envoi send_action)
                
                if send_action(payload):
                    st.success("✅ Enregistré !")
                    # Nettoyage des données temporaires
                    for k in ['scraped_title', 'scraped_ingredients', 'scraped_content']:
                        if k in st.session_state: del st.session_state[k]
                    st.cache_data.clear()
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error("❌ Erreur de communication avec Google Sheets.")
            else:
                st.error("🚨 Titre et Ingrédients obligatoires !")

        if c_cancel.button("❌ ANNULER L'AJOUT", use_container_width=True):
            # Nettoyage avant de partir
            for k in ['scraped_title', 'scraped_ingredients', 'scraped_content']:
                if k in st.session_state: del st.session_state[k]
            st.session_state.page = "home"
            st.rerun()
            
elif st.session_state.page == "print":
    if 'recipe_data' not in st.session_state:
        st.error("Aucune donnée trouvée.")
        if st.button("⬅ Retour"):
            st.session_state.page = "home"
            st.rerun()
    else:
        r = st.session_state.recipe_data
        
        # 1. BOUTON DE RETOUR (Streamlit classique)
        if st.button("⬅ Retour aux détails"):
            st.session_state.page = "details"
            st.rerun()

        # 2. PRÉPARATION DES DONNÉES
        ing_raw = str(r.get('Ingrédients','')).split('\n')
        html_ing = "".join([f"<li>{l.strip()}</li>" for l in ing_raw if l.strip()])
        prepa_final = str(r.get('Préparation', '')).replace('\n', '<br>')

        # 3. HTML PUR (Injecté dans un composant isolé)
        # On met tout le CSS et le contenu ensemble ici
        fiche_isolee = f"""
        <div id="print-area" style="background:white; color:black; padding:20px; font-family:Arial, sans-serif;">
            <style>
                @media print {{
                    @page {{ size: A4; margin: 10mm; }}
                    .no-print {{ display: none !important; }}
                    body {{ background: white !important; }}
                }}
                .header-line {{ border-bottom: 3px solid #e67e22; margin-bottom: 10px; }}
                .info-box {{ display: flex; justify-content: space-between; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 5px; color: #444; }}
                h1 {{ margin: 0; font-size: 24px; color: black; }}
                h3 {{ color: #e67e22; border-bottom: 1px solid #ddd; margin-top: 15px; }}
                .ingredients {{ column-count: 2; column-gap: 20px; font-size: 13px; list-style-type: none; padding: 0; }}
            </style>
            
            <button class="no-print" onclick="window.print()" style="width:100%; height:40px; background:#e67e22; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer; margin-bottom:20px;">
                🖨️ LANCER L'IMPRESSION
            </button>

            <div class="header-line"><h1>{r.get('Titre','Recette')}</h1></div>
            <div class="info-box">
                <span>Catégorie : {r.get('Catégorie','-')}</span>
                <span>Portions : {r.get('Portions','-')}</span>
                <span>Temps : {r.get('Temps_Prepa','0')} + {r.get('Temps_Cuisson','0')} min</span>
            </div>
            <h3>🛒 Ingrédients</h3>
            <ul class="ingredients">{html_ing}</ul>
            <h3>👨‍🍳 Préparation</h3>
            <div style="font-size: 13px; line-height: 1.5;">{prepa_final}</div>
        </div>
        """

        # 4. AFFICHAGE DANS L'IFRAME
        import streamlit.components.v1 as components
        components.html(fiche_isolee, height=1000, scrolling=True)
        st.stop()


elif st.session_state.page == "edit":
    # --- PRÉPARATION DES DONNÉES À ÉDITER ---
    r_edit = st.session_state.get('recipe_to_edit', {})

    def clean_edit(x):
        """Nettoie les valeurs pour l'affichage (enlève NaN, les .0, etc.)"""
        val = str(x).strip()
        if val.lower() in ["nan", "none", "", "null", "-", " "]: return ""
        return val.split('.')[0] if '.' in val else val

    # --- TITRE DE LA PAGE ---
    st.markdown('<h1 style="color: #e67e22;">✏️ Modifier la Recette</h1>', unsafe_allow_html=True)
    
    # Bouton de retour
    if st.button("⬅ Annuler et Retour aux détails", use_container_width=True):
        st.session_state.page = "details"
        st.rerun()
    
    st.divider()

    # --- FORMULAIRE D'ÉDITION ---
    with st.form("form_edition_complete"):
        col_t, col_c = st.columns([2, 1])
        titre_edit = col_t.text_input("🏷️ Nom de la recette", value=r_edit.get('Titre', ''))
        
        # --- GESTION DES CATÉGORIES (MISE À JOUR ALPHABÉTIQUE COMPLÈTE) ---
        LISTE_CATS = [
            "Accompagnement", "Agneau", "Air Fryer", "Apéro", "Asiatique", 
            "BBQ", "Biscuits", "Boisson", "Boîte à lunch", "Boulangerie", "Buffet", "Buffet chinois", "Bœuf", "Cabane à sucre", 
            "Condiment", "Confiserie", "Crème-glacée", "Dessert", "Entrée", 
            "Épices", "Fondue", "Four à pizza", "Fruits de mer", "Fumoir", "Gâteau", 
            "Goûter", "Indien", "Légumes", "Libanais", "Marinade", 
            "Mexicain", "Muffins", "Ninja Creami", "Ninja Slushie", "Pains", 
            "Pâtes", "Pâtisserie", "Petit-déjeuner", "Pizza", "Plancha", 
            "Plat Principal", "Poisson", "Poke bowl", "Porc", "Poulet", 
            "Poutine", "Riz", "Salade", "Sandwich", "Sauce", "Slow Cooker", 
            "Soupe", "Sport", "Sushi", "Tartare", "Temps des fêtes", "Végétarien", 
            "Vinaigrette", "Autre"
        ]
        
        # On récupère les catégories actuelles, on nettoie et on fait correspondre
        raw_cats = str(r_edit.get('Catégorie', ''))
        current_cats = [c.strip() for c in raw_cats.split(',') if c.strip()]
        cat_choisies = col_c.multiselect("📁 Catégories", LISTE_CATS, default=[c for c in current_cats if c in LISTE_CATS])
        
        st.markdown("#### ⏱️ Paramètres")
        cp1, cp2, cp3 = st.columns(3)
        
        # On nettoie les temps et portions
        t_p_val = clean_edit(r_edit.get('Temps_Prepa', r_edit.get('Temps de préparation', '')))
        t_c_val = clean_edit(r_edit.get('Temps_Cuisson', r_edit.get('Temps de cuisson', '')))
        p_v_val = clean_edit(r_edit.get('Portions', ''))
        
        t_prep = cp1.text_input("🕒 Préparation (min)", value=t_p_val)
        t_cuis = cp2.text_input("🔥 Cuisson (min)", value=t_c_val)
        port = cp3.text_input("🍽️ Portions", value=p_v_val)
        
        # --- SECTION TEXTE (Ingrédients et Préparation) ---
        ci, ce = st.columns(2)
        ingredients = ci.text_area("🍎 Ingrédients (un par ligne)", value=r_edit.get('Ingrédients', ''), height=300)
        instructions = ce.text_area("👨‍🍳 Étapes de préparation", value=r_edit.get('Préparation', ''), height=300)
        
        # --- SECTION LIENS ET MÉDIAS ---
        img_url = st.text_input("🖼️ Lien de l'image (URL)", value=r_edit.get('Image', ''))
        
        col_v, col_s = st.columns(2)
        video_url = col_v.text_input("📺 Lien Vidéo (TikTok, Instagram, FB)", value=r_edit.get('video', ''))
        source_url = col_s.text_input("🌐 Lien Source (Site web)", value=r_edit.get('Source', ''))
        
        # Champ commentaires
        commentaires = st.text_area("📝 Mes Notes & Astuces", value=r_edit.get('Commentaires', ''), height=100)
        
        st.divider()
        
        # --- BOUTON DE SOUMISSION ---
        submit_btn = st.form_submit_button("💾 ENREGISTRER LES MODIFICATIONS", use_container_width=True)

    # --- LOGIQUE D'ENREGISTREMENT ---
    if submit_btn:
        if titre_edit and ingredients:
            with st.spinner("Mise à jour de la recette..."):
                payload = {
                    "action": "edit", 
                    "old_titre": r_edit.get('Titre'),
                    "titre": titre_edit.strip(), 
                    "Catégorie": ", ".join(cat_choisies),
                    "Ingrédients": ingredients.strip().replace('\n', '  \n'),
                    "Préparation": instructions.strip(),
                    "Image": img_url.strip(),
                    "Temps_Prepa": t_prep.strip(),
                    "Temps_Cuisson": t_cuis.strip(),
                    "Portions": port.strip(),
                    "Commentaires": commentaires.strip(),
                    "video": video_url.strip(),
                    "Source": source_url.strip()
                }
                
                if send_action(payload):
                    st.success("✅ Recette mise à jour avec succès !")
                    st.cache_data.clear() 
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error("❌ Erreur de connexion au serveur lors de la mise à jour.")
        else:
            st.error("🚨 Le titre et les ingrédients sont obligatoires.")

# --- PAGE ÉPICERIE (INTÉGRALE AVEC DESIGN FILIGRANE & GESTION ADMIN) ---
elif st.session_state.page == "shop":
    # 1. DESIGN FINAL : FILIGRANE AJUSTÉ (PLUS PETIT)
    url_header = "https://i.postimg.cc/Y9K56SxC/f1ed1d49-14a2-4bca-90ae-e88d0ba63018.png"

    st.markdown(f"""
        <style>
        /* 1. FILIGRANE RECENTRÉ ET RAPETISSÉ */
        [data-testid="stAppViewContainer"] {{
            background: 
                linear-gradient(rgba(14, 17, 23, 0.8), rgba(14, 17, 23, 0.9)), 
                url("{url_header}");
            background-size: 50%; 
            background-position: center 20%; 
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Transparence des couches Streamlit */
        [data-testid="stHeader"], [data-testid="stMainViewContainer"] {{
            background: transparent;
        }}

        /* 2. CARTES SOMBRES TRANSLUCIDES (Look Pro) */
        .shop-card {{
            background-color: rgba(30, 34, 45, 0.6); 
            padding: 16px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-left: 5px solid #e67e22;
            margin-bottom: 12px;
            color: #ffffff;
            backdrop-filter: blur(8px); 
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        }}

        .neon-title {{
            color: #e67e22;
            font-size: 2.2rem;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(230, 126, 34, 0.4);
        }}
        
        /* Harmonisation du texte Admin sur fond sombre */
        .admin-text {{
            color: #ffffff;
            font-weight: bold;
        }}
        </style>
    """, unsafe_allow_html=True)

    # 2. CONTENEUR ET NAVIGATION
    st.markdown('<div class="keep-container" style="background:transparent;">', unsafe_allow_html=True)
    
    c_titre, c_back = st.columns([0.85, 0.15])
    with c_titre:
        st.markdown('<div class="neon-title">🛒 Liste d\'Épicerie</div>', unsafe_allow_html=True)
    with c_back:
        if st.button("⬅️"):
            st.session_state.page = "home"
            st.rerun()

    st.divider()

    # --- SECTION : AJOUT RAPIDE (Vérifié : tout y est) ---
    if "input_counter" not in st.session_state:
        st.session_state.input_counter = 0

    st.markdown("<h5 style='color:white;'>➕ Ajouter un article</h5>", unsafe_allow_html=True)
    c_input, c_add, c_cancel = st.columns([3, 0.8, 0.8])
    
    new_article = c_input.text_input(
        "Que manque-t-il ?", 
        placeholder="Ex: Lait, Œufs...",
        label_visibility="collapsed", 
        key=f"add_item_{st.session_state.input_counter}"
    )
    
    if c_add.button("➕", use_container_width=True, type="primary"):
        if new_article:
            with st.spinner(""):
                if send_action({"action": "add_shop", "article": new_article.strip()}):
                    st.toast(f"✅ {new_article} ajouté !")
                    st.cache_data.clear()
                    st.session_state.input_counter += 1
                    st.rerun()
        else:
            st.warning("Écrivez un article !")

    if c_cancel.button("✖️", use_container_width=True):
        st.session_state.input_counter += 1
        st.rerun()

    st.divider()

    # --- LOGIQUE D'AFFICHAGE ET GESTION (Vérifié : Admin + Consultation) ---
    try:
        import time
        import json
        is_admin = st.session_state.get('admin_mode', False)
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        
        if not df_s.empty:
            if is_admin:
                # MODE ADMIN : Suppression avec cases à cocher
                with st.form("shop_form", border=False):
                    to_del = []
                    st.markdown("<p style='color:white;'>🛠 <b>Gestion (Cochez pour retirer) :</b></p>", unsafe_allow_html=True)
                    for idx, row in df_s.iterrows():
                        art = str(row.iloc[0]).strip()
                        if art:
                            col_c, col_t = st.columns([0.15, 0.85])
                            # Utilisation de la checkbox Streamlit standard
                            if col_c.checkbox("", key=f"sh_{idx}"):
                                to_del.append(art)
                            col_t.markdown(f"<span style='color:white;'>**{art}**</span>", unsafe_allow_html=True)
                    
                    st.markdown("---")
                    submit_del = st.form_submit_button("🗑 Retirer la sélection", use_container_width=True)
                
                if submit_del:
                    if to_del:
                        if send_action({"action": "remove_shop", "articles": to_del}):
                            st.cache_data.clear()
                            st.rerun()
                    else:
                        st.warning("Cochez des articles.")

                if st.button("🧨 Vider toute la liste", use_container_width=True):
                    if send_action({"action": "clear_shop"}):
                        st.cache_data.clear()
                        st.rerun()
            
            else:
                # MODE CONSULTATION : Look "Carte" moderne
                st.info("📖 Prêt pour le magasin !")
                for idx, row in df_s.iterrows():
                    art = str(row.iloc[0]).strip()
                    if art:
                        st.markdown(f'<div class="shop-card"><b>❑ {art}</b></div>', unsafe_allow_html=True)

            # --- BOUTON COPIER POUR KEEP (Vérifié : Format ligne par ligne) ---
            st.divider()
            items_keep = [str(row.iloc[0]).strip() for idx, row in df_s.iterrows() if str(row.iloc[0]).strip()]
            txt_final = "\\n".join(items_keep)
            js_txt = json.dumps(txt_final)

            st.components.v1.html(f"""
                <button onclick="copyK()" style="width:100%; background:#f1c40f; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer; color:#2c3e50; font-family:sans-serif;">
                    🟡 COPIER TOUT POUR GOOGLE KEEP
                </button>
                <script>
                function copyK() {{
                    const t = {js_txt}.replace(/\\\\n/g, '\\n');
                    const ta = document.createElement("textarea"); ta.value = t;
                    document.body.appendChild(ta); ta.select(); document.execCommand('copy');
                    document.body.removeChild(ta); alert("Liste copiée ! Chaque article sera sur une ligne.");
                }}
                </script>
            """, height=60)

        else:
            st.info("La liste est vide. Tout est sous contrôle ! ✨")

    except Exception as e:
        st.error(f"Erreur de chargement : {e}")

    st.markdown('</div>', unsafe_allow_html=True) # Fermeture du conteneur
# ======================
# PAGE PLANNING
# ======================
elif st.session_state.page == "planning":
    st.markdown('<h1 style="color: #e67e22;">📅 Mon Planning</h1>', unsafe_allow_html=True)
    
    col_nav, col_clear = st.columns([1, 1])
    with col_nav:
        if st.button("⬅ Retour", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
            
    with col_clear:
        if st.session_state.get('admin_mode', False):
            if st.button("🗑️ Vider le planning", use_container_width=True):
                if send_action({"action": "clear_planning"}):
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.button("🔒 Mode Lecture", use_container_width=True, disabled=True)

    st.divider()

    try:
        # 1. CHARGEMENT DES DONNÉES
        df_plan = load_data(URL_CSV_PLAN)
        
        # Secours si vide
        if df_plan.empty or 'Date' not in df_plan.columns:
            df_all = load_data(URL_CSV)
            if 'Date_Prevue' in df_all.columns:
                df_plan = df_all[df_all['Date_Prevue'].astype(str).str.strip() != ""].copy()
                df_plan = df_plan.rename(columns={'Date_Prevue': 'Date'})

        if df_plan.empty:
            st.info("Ton planning est vide.")
        else:
            # 2. NETTOYAGE
            df_plan.columns = df_plan.columns.str.strip()
            df_plan['Date'] = pd.to_datetime(df_plan['Date'], errors='coerce')
            df_plan = df_plan.dropna(subset=['Date', 'Titre']).sort_values(by='Date')

            jours_fr = {"Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"}
            mois_fr = {"January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août", "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"}

            derniere_semaine = -1
            is_admin = st.session_state.get('admin_mode', False)
            
            # --- 3. BOUCLE D'AFFICHAGE (TOUT DOIT ÊTRE DEDANS) ---
            for index, row in df_plan.iterrows():
    
                # --- A. SÉPARATEURS DE SEMAINE ---
                semaine_actuelle = row['Date'].isocalendar()[1]
                if semaine_actuelle != derniere_semaine:
                    st.markdown(f"""
                        <div style="background: linear-gradient(90deg, #2e313d 0%, #1e2129 100%);
                                    padding: 8px 15px; border-radius: 6px; margin: 25px 0 10px 0; 
                                    border-left: 4px solid #95a5a6; display: flex; align-items: center;">
                            <span style="color: #95a5a6; font-size: 0.85rem; font-weight: 800; letter-spacing: 1.5px;">
                                📅 SEMAINE {semaine_actuelle}
                            </span>
                        </div>
                    """, unsafe_allow_html=True)
                    derniere_semaine = semaine_actuelle

                # --- B. FORMATAGE DE LA DATE ---
                try:
                    nom_jour = jours_fr.get(row['Date'].strftime('%A'), "Jour")
                    num_jour = row['Date'].strftime('%d')
                    nom_mois = mois_fr.get(row['Date'].strftime('%B'), "Mois")
                    date_txt = f"{nom_jour} {num_jour} {nom_mois}"
                except:
                    date_txt = "Date inconnue"
        
                # --- C. AFFICHAGE DE LA LIGNE RECETTE ---
                col_txt, col_cal, col_edit, col_del = st.columns([3, 0.5, 0.5, 0.5])
                
                with col_txt:
                    st.markdown(f"""
                        <div style="background-color: #1e2129; padding: 12px; border-radius: 10px; border-left: 4px solid #e67e22; margin-bottom: 5px;">
                            <div style="color: #e67e22; font-size: 0.75rem; font-weight: bold;">{date_txt}</div>
                            <div style="color: white; font-size: 1.05rem; font-weight: 500;">{row['Titre']}</div>
                        </div>
                    """, unsafe_allow_html=True)
        
                with col_cal:
                    if st.button("📖", key=f"view_{index}"):
                        df_all = load_data(URL_CSV) 
                        recipe_full = df_all[df_all['Titre'] == row['Titre']]
                        if not recipe_full.empty:
                            st.session_state.recipe_data = recipe_full.iloc[0].to_dict()
                            st.session_state.page = "details"
                            st.rerun()

                # --- D. BOUTONS ADMIN ---
                with col_edit:
                    if is_admin:
                        if st.button("✏️", key=f"edit_{index}"):
                            st.session_state[f"editing_{index}"] = True
                
                with col_del:
                    if is_admin:
                        if st.button("🗑️", key=f"del_{index}"):
                            date_clean = row['Date'].strftime('%Y-%m-%d')
                            payload = {"action": "remove_plan", "titre": str(row['Titre']).strip(), "date": date_clean}
                            if send_action(payload):
                                st.cache_data.clear()
                                st.rerun()

                # --- E. FORMULAIRE D'ÉDITION ---
                if is_admin and st.session_state.get(f"editing_{index}", False):
                    with st.container():
                        new_date = st.date_input("Nouvelle date", value=row['Date'], key=f"date_input_{index}")
                        c1, c2 = st.columns(2)
                        with c1:
                            if st.button("✅ Confirmer", key=f"confirm_{index}"):
                                payload = {
                                    "action": "update_plan",
                                    "titre": row['Titre'],
                                    "old_date": row['Date'].strftime('%Y-%m-%d'),
                                    "new_date": new_date.strftime('%Y-%m-%d')
                                }
                                if send_action(payload):
                                    st.cache_data.clear()
                                    st.session_state[f"editing_{index}"] = False
                                    st.rerun()
                        with c2:
                            if st.button("❌ Annuler", key=f"cancel_{index}"):
                                st.session_state[f"editing_{index}"] = False
                                st.rerun()

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
    
    # 1. CHARGEMENT DES DONNÉES (Assure-toi que URL_CSV est défini plus haut dans ton code)
    df_raw = load_data(URL_CSV)
    
    # 2. SUPPRESSION DES DOUBLONS (Les deux lignes magiques)
    # On garde la première occurrence de chaque titre
    df = df_raw.drop_duplicates(subset=['Titre'], keep='first')

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


































































































































































































































































































































































































































































































