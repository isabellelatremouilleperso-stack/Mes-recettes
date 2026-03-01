import streamlit as st
import pandas as pd
import requests
import time
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse

# ======================
# CONFIGURATION & LIAISON GOOGLE
# ======================

# 1. Utilisation sécurisée du secret
URL_SCRIPT = st.secrets["Lien_Google"]

# 2. URLs CSV
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_CSV_PLAN = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=536412190&single=true&output=csv"

# ======================
# FONCTIONS TECHNIQUES (VERSION NETTOYÉE)
# ======================

def send_action(payload):
    """Envoie les données vers Google Apps Script avec diagnostic."""
    with st.spinner("🚀 Action en cours..."):
        try:
            headers = {"Content-Type": "application/json"}
            r = requests.post(URL_SCRIPT, json=payload, headers=headers, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear() 
                time.sleep(0.5)
                return True
            else:
                st.error(f"⚠️ Erreur Google : {r.text}")
                return False
        except Exception as e:
            st.error(f"❌ Erreur de connexion : {e}")
            return False

@st.cache_data(ttl=300) 
def load_data(url):
    try:
        timestamp_url = f"{url}&nocache={int(time.time())}"
        df = pd.read_csv(timestamp_url)
        df.columns = [c.strip() for c in df.columns] 
        df = df.fillna("")
        if not df.empty and 'Titre' in df.columns:
            df['Titre'] = df['Titre'].astype(str).str.strip()
            df = df.drop_duplicates(subset=['Titre'], keep='first')
        return df
    except Exception as e:
        st.error(f"Erreur chargement : {e}")
        return pd.DataFrame()

def scrape_url(url):
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

        # 2. Nettoyage agressif du bruit
        for junk in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "ins"]):
            junk.extract()

        # 3. Ciblage intelligent (priorité aux classes culinaires communes)
        # On cherche des conteneurs qui ont souvent les mots clés "ingredients" ou "recipe"
        ing_container = soup.find(class_=re.compile(r'ingredient|ingredients|recipe-ing', re.I))
        prep_container = soup.find(class_=re.compile(r'instruction|preparation|method|steps', re.I))

        # --- LOGIQUE INGRÉDIENTS ---
        if ing_container:
            items = ing_container.find_all('li')
        else:
            items = soup.find_all('li')
            
        ing_list = []
        for el in items:
            txt = el.get_text().strip()
            # On filtre pour garder les lignes qui ressemblent à des ingrédients (courtes mais informatives)
            if 3 < len(txt) < 150 and not any(x in txt.lower() for x in ["partager", "imprimer", "connexion"]):
                ing_list.append(f"❑ {txt}")

        # --- LOGIQUE PRÉPARATION ---
        if prep_container:
            steps = prep_container.find_all(['p', 'li'])
        else:
            steps = soup.find_all('p')

        prep_list = []
        for el in steps:
            txt = el.get_text().strip()
            # On garde les paragraphes assez longs pour être des instructions
            if len(txt) > 20 and not any(x in txt.lower() for x in ["cookies", "droits réservés", "abonnez-vous"]):
                prep_list.append(txt)

        # Nettoyage des doublons et suppression des lignes vides
        final_ing = "\n".join([i for i in list(dict.fromkeys(ing_list)) if i.strip()])
        final_prep = "\n\n".join([p for p in list(dict.fromkeys(prep_list)) if p.strip()])

        return title, final_ing, final_prep

    except Exception as e:
        # Retourne des chaînes vides au lieu de None pour éviter les erreurs de concaténation plus tard
        return "Recette inconnue", "", f"Erreur lors de l'extraction : {e}"
# ======================
# INITIALISATION ET DESIGN
# ======================

if 'page' not in st.session_state:
    st.session_state.page = "home"

st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

# Style CSS combiné et optimisé
st.markdown("""
<style>
    .stApp, header, [data-testid="stHeader"] { background-color: #0e1117 !important; }
    [data-testid="stSidebar"], [data-testid="stSidebarContent"] { background-color: #1e2129 !important; }
    h1, h2, h3 { color: #e67e22 !important; }
    .stButton button { background-color: #e67e22 !important; color: white !important; border-radius: 10px; border:none; }
    input, select, textarea, div[data-baseweb="select"] { color: white !important; background-color: #1e2129 !important; }
    .logo-container { display: flex; justify-content: center; margin-bottom: 10px; }
    .logo-container img { border-radius: 50%; width: 120px; height: 120px; object-fit: cover; border: 3px solid #e67e22; }
    [data-testid="stSidebarCollapsedControl"] svg { fill: #e67e22 !important; }
</style>
""", unsafe_allow_html=True)

# ======================
# SÉCURITÉ ADMIN
# ======================
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = (st.query_params.get("admin") == "oui")

# --- 5. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    # Logo et Titre
    st.markdown('<div class="logo-container"><img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png"></div>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #e67e22; margin-top: -10px;">Mes Recettes</h3>', unsafe_allow_html=True)
    
    # --- LE BOUTON ACTUALISER EST ICI ---
    if st.button("🔄 Actualiser la Bibliothèque", use_container_width=True, key="btn_refresh_side"):
        st.cache_data.clear()
        st.toast("Mise à jour réussie ! 📋")
        time.sleep(0.5)
        st.rerun()
    
    st.divider()

    # Section Sécurité Admin
    if not st.session_state.admin_mode:
        pwd = st.text_input("🔑 Accès Admin", type="password")
        if st.button("Se connecter 🔓", use_container_width=True):
            clean_pwd = pwd.strip()
            input_hash = hashlib.sha256(clean_pwd.encode()).hexdigest()
            target_hash = "81907797768e18f2d5743c7b3967d79b9423c8e427b372f69466e31b63604f7a"
            if clean_pwd == "142203" or input_hash == target_hash:
                st.session_state.admin_mode = True
                st.rerun()
            else:
                st.error("Code incorrect ❌")
    else:
        st.success("✅ Mode Chef Activé")
        if st.button("🔒 Déconnexion", use_container_width=True):
            st.session_state.admin_mode = False
            st.rerun()

    st.divider()
    
    # Navigation
    if st.button("📚 Bibliothèque", use_container_width=True, key="nav_home"): 
        st.session_state.page="home"; st.rerun()
    if st.button("📅 Planning Repas", use_container_width=True, key="nav_plan"): 
        st.session_state.page="planning"; st.rerun()
    if st.button("🛒 Ma Liste d'épicerie", use_container_width=True, key="nav_shop"): 
        st.session_state.page="shop"; st.rerun()
    
    st.divider()
    if st.session_state.admin_mode:
        if st.button("➕ AJOUTER RECETTE", use_container_width=True, key="nav_add"):
            st.session_state.page="add"; st.rerun()
    
    if st.button("⭐ Play Store", use_container_width=True, key="nav_play"): 
        st.session_state.page="playstore"; st.rerun()
    if st.button("❓ Aide", use_container_width=True, key="nav_help"): 
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
            liste_categories = ["Toutes"] + sorted([str(c) for c in df['Catégorie'].unique() if c])
            cat_choisie = st.selectbox("📁 Filtrer par catégorie", liste_categories)

        with col_tri:
            ordre = st.selectbox("🔃 Trier par :", ["A ➡️ Z", "Z ➡️ A", "Les plus récentes"])
        
        # --- LOGIQUE DE FILTRE ---
        mask = (df['Titre'].str.contains(search, case=False, na=False)) | \
               (df['Ingrédients'].str.contains(search, case=False, na=False))
        
        if cat_choisie != "Toutes":
            mask = mask & (df['Catégorie'] == cat_choisie)
        
        # On crée la base de travail filtrée
        rows = df[mask].copy()

        # --- LOGIQUE DE TRI (CORRIGÉE) ---
        if ordre == "A ➡️ Z":
            rows = rows.sort_values(by="Titre", ascending=True)
        elif ordre == "Z ➡️ A":
            rows = rows.sort_values(by="Titre", ascending=False)
        elif ordre == "Les plus récentes":
            # On inverse l'ordre original du dataframe filtré
            rows = rows.iloc[::-1] 


        # IMPORTANT : On réinitialise l'index UNE SEULE FOIS ici pour valider le tri
        rows = rows.reset_index(drop=True)

        # --- SÉCURITÉ ANTI-DOUBLONS (Post-filtrage) ---
        # On supprime les doublons sur le titre au cas où le filtre en aurait généré
        rows = rows.drop_duplicates(subset=['Titre'], keep='first').reset_index(drop=True)

        # --- FONCTION COULEUR ---
        def get_cat_color(cat):
            colors = {
                "Poulet": "#FF5733", "Bœuf": "#C70039", "Porc": "#FFC0CB", 
                "Agneau": "#8B4513", "Poisson": "#3498DB", "Fruits de mer": "#00CED1",
                "Pâtes": "#F1C40F", "Riz": "#F5F5DC", "Légumes": "#28B463", 
                "Soupe": "#4682B4", "Salade": "#7CFC00", "Entrée": "#95A5A6",
                "Plat Principal": "#E67E22", "Dessert": "#FF33FF", "Petit-déjeuner": "#FFD700",
                "Goûter": "#D2691E", "Apéro": "#FF4500", "Sauce": "#8B0000", 
                "Boisson": "#7FFFD4", "Autre": "#BDC317",
                "Air Fryer": "#FF4500", "Boulangerie": "#DEB887", "Condiment": "#DAA520",
                "Épices": "#CD5C5C", "Fumoir": "#333333", "Indien": "#FF9933",
                "Libanais": "#EE2436", "Mexicain": "#006341", "Pains": "#F5DEB3",
                "Pizza": "#FF6347", "Plancha": "#708090", "Poutine": "#6F4E37",
                "Slow Cooker": "#4B0082", "Sushi": "#FF1493", "Tartare": "#B22222",
                "Végétarien": "#32CD32"
            }
            return colors.get(cat, "#e67e22")

        # --- NETTOYAGE ANTI-DOUBLONS ---
        rows = rows.drop_duplicates(subset=['Titre'])
        rows = rows.reset_index(drop=True)

        # --- AFFICHAGE DES RÉSULTATS ---
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
    # 1. RÉCUPÉRATION ET CHARGEMENT FRAIS
    current_title = st.session_state.recipe_data.get('Titre')
    
    try:
        df_fresh = pd.read_csv(f"{URL_CSV}&nocache={time.time()}")
        fresh_recipe = df_fresh[df_fresh['Titre'] == current_title]
        if not fresh_recipe.empty:
            r = fresh_recipe.iloc[0].to_dict()
            st.session_state.recipe_data = r
        else:
            r = st.session_state.recipe_data
    except:
        r = st.session_state.recipe_data

    # --- BARRE DE NAVIGATION ---
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
            if send_action({"action": "delete", "titre": current_title}):
                st.cache_data.clear()
                st.session_state.page = "home"; st.rerun()

    st.divider()
    st.header(f"📖 {r.get('Titre','Sans titre')}")

    # --- CORPS DE LA PAGE ---
    col_g, col_d = st.columns([1, 1.2])

    with col_g:
        # VISUEL
        img_url = r.get('Image', '')
        st.image(img_url if "http" in str(img_url) else "https://via.placeholder.com/400?text=Pas+d'image", use_container_width=True)
            
        # NOTATION INTERACTIVE (Slider de sauvegarde)
        try:
            val_note = r.get('Note', r.get('note', 0))
            note_actuelle = int(float(val_note)) if str(val_note).strip() not in ["", "None", "nan", "-"] else 0
        except:
            note_actuelle = 0

        st.write("**Évaluer cette recette :**")
        nouvelle_note = st.select_slider("Glissez pour noter", options=[0, 1, 2, 3, 4, 5], value=note_actuelle, key=f"slider_{current_title}")
        
        if nouvelle_note != note_actuelle:
            with st.spinner("Mise à jour de la note..."):
                payload_n = r.copy()
                payload_n.update({"action": "edit", "Note": nouvelle_note, "note": nouvelle_note})
                if send_action(payload_n):
                    st.toast("Note enregistrée ! ⭐")
                    st.session_state.recipe_data['Note'] = nouvelle_note
                    st.rerun()

        if note_actuelle > 0:
            st.markdown(f"### {'⭐' * note_actuelle}")

        st.divider()
        st.markdown("### 📝 Mes Notes")
        notes_texte = r.get('Commentaires', '')
        if notes_texte and str(notes_texte).strip() not in ["None", "nan", ""]:
            st.info(notes_texte)
        else:
            st.write("*Aucune note.*")

    with col_d:
        # 1. INFORMATIONS & MÉTRIQUES
        st.subheader("📋 Informations")

        # Fonction de nettoyage locale pour éviter les erreurs de variables non définies
        def clean_metrique(valeur):
            v_str = str(valeur).strip().lower()
            if v_str in ["nan", "none", "", "0", "0.0", "null", "-"]:
                return "-"
            # On garde seulement le chiffre entier (ex: 20.0 -> 20)
            return str(valeur).split('.')[0]

        # Calcul des valeurs propres
        p_final = clean_metrique(r.get('Temps de préparation'))
        c_final = clean_metrique(r.get('Temps de cuisson'))
        port_final = clean_metrique(r.get('Portions'))

        # Affichage des métriques
        m1, m2, m3 = st.columns(3)
        m1.metric("🕒 Prépa", f"{p_final} min" if p_final != "-" else "-")
        m2.metric("🔥 Cuisson", f"{c_final} min" if c_final != "-" else "-")
        m3.metric("🍽️ Portions", port_final)

        # 2. SUPPORT VIDÉO (SI EXISTE)
        r_vals = list(r.values())
        v_link = r_vals[13] if len(r_vals) > 13 else r.get('video', '')
        if v_link and "http" in str(v_link):
            st.divider()
            if "youtube" in str(v_link) or "youtu.be" in str(v_link):
                st.video(str(v_link))
            else:
                st.link_button("📺 Voir la vidéo", str(v_link), use_container_width=True)

        st.divider()

        # 3. INGRÉDIENTS
        st.subheader("🛒 Ingrédients")
        ings_raw = r.get('Ingrédients', '')
        if ings_raw and str(ings_raw).strip() not in ["None", "nan", ""]:
            text_ing = str(ings_raw).replace("❑", "\n").replace(";", "\n")
            ings = [l.strip() for l in text_ing.split("\n") if l.strip()]
            for i, line in enumerate(ings):
                st.checkbox(line, key=f"chk_{current_title}_{i}")
        else:
            st.info("Aucun ingrédient.")
        
        st.divider()

        # 4. PLANNING
        st.subheader("📅 Planifier")
        date_p = st.date_input("Date", key="date_det")
        if st.button("🗓️ Ajouter au planning", use_container_width=True):
            if send_action({"action": "plan", "titre": current_title, "date_prevue": str(date_p)}):
                st.success("Ajouté !")

    # --- PRÉPARATION (BAS DE PAGE) ---
    st.divider()
    st.subheader("👨‍🍳 Étapes de préparation")
    prep = r.get('Préparation', '')
    if prep:
        st.write(prep)
    else:
        st.warning("Aucune étape enregistrée.")

# --- FIN DU BLOC DETAILS ---
elif st.session_state.page == "add":
    st.markdown('<h1 style="color: #e67e22;">📥 Ajouter une Nouvelle Recette</h1>', unsafe_allow_html=True)
    
    if st.button("⬅ Retour à la Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
        
    # --- SECTION RECHERCHE GOOGLE CANADA ---
    st.markdown("""<div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #4285F4; margin-bottom: 20px;"><h4 style="margin:0; color:white;">🔍 Chercher une idée sur Google Canada</h4></div>""", unsafe_allow_html=True)
    
    c_search, c_btn = st.columns([3, 1])
    search_query = c_search.text_input("Que cherchez-vous ?", placeholder="Ex: Pâte à tarte Ricardo", label_visibility="collapsed", max_chars=100)
    
    query_encoded = urllib.parse.quote(search_query + ' recette') if search_query else ""
    target_url = f"https://www.google.ca/search?q={query_encoded}" if search_query else "https://www.google.ca"
    
    c_btn.markdown(f"""<a href="{target_url}" target="_blank" style="text-decoration: none;"><div style="background-color: #4285F4; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; cursor: pointer;">🌐 Aller sur Google.ca</div></a>""", unsafe_allow_html=True)
    
    # --- SECTION IMPORTATION WEB / SCRAPING ---
    st.markdown("""<div style="background-color: #1e2129; padding: 20px; border-radius: 15px; border: 1px solid #3d4455; margin-top: 10px;"><h3 style="margin-top:0; color:#e67e22;">🌐 Importer depuis le Web</h3>""", unsafe_allow_html=True)
    
    col_url, col_go = st.columns([4, 1])
    url_input = col_url.text_input("Collez l'URL ici", placeholder="https://www.ricardocuisine.com/...", key="url_main")
    
    if col_go.button("Extraire ✨", use_container_width=True):
        if url_input:
            with st.spinner("Analyse et tri de la recette..."):
                t, ing, prep = scrape_url(url_input)
                if t:
                    st.session_state.scraped_title = t
                    st.session_state.scraped_ingredients = ing
                    st.session_state.scraped_content = prep
                    st.success("Extraction réussie ! ✨")
                    st.rerun()
                else:
                    st.warning("⚠️ Ce site bloque l'accès automatique. Copiez le texte manuellement.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()
    
    # --- FORMULAIRE PRINCIPAL ---
    with st.container():
        col_t, col_c = st.columns([2, 1])
        
        titre_val = st.session_state.get('scraped_title', '')
        ing_val = st.session_state.get('scraped_ingredients', '')
        prep_val = st.session_state.get('scraped_content', '')

        titre = col_t.text_input("🏷️ Nom de la recette", value=titre_val, placeholder="Ex: Lasagne de maman", max_chars=150)
        cat_choisies = col_c.multiselect("📁 Catégories", CATEGORIES, default=["Autre"])
        
        col_link1, col_link2 = st.columns(2)
        source_url = col_link1.text_input("🔗 Lien source (Site Web)", value=url_input if url_input else "", placeholder="https://...")
        video_url = col_link2.text_input("🎬 Lien Vidéo (TikTok, Instagram, FB)", placeholder="URL de la vidéo...")
        
        st.markdown("#### ⏱️ Paramètres de cuisson")
        cp1, cp2, cp3 = st.columns(3)
        t_prep = cp1.text_input("🕒 Préparation (min)", placeholder="15", key="p_time")
        t_cuis = cp2.text_input("🔥 Cuisson (min)", placeholder="45", key="c_time")
        port = cp3.text_input("🍽️ Portions", placeholder="4", key="portions")
        
        st.divider()
        
        ci, ce = st.columns(2)
        # Utilisation de st.text_area avec les valeurs scrapées
        ingredients = ci.text_area("🍎 Ingrédients (un par ligne)", value=ing_val, height=350, placeholder="2 tasses de farine...", key="ing_area")
        instructions = ce.text_area("👨‍🍳 Étapes de préparation", value=prep_val, height=350, key="prep_area")
        
        img_url = st.text_input("🖼️ Lien de l'image (URL)", placeholder="https://...", key="img_url")
        commentaires = st.text_area("📝 Mes Notes & Astuces", height=100, key="notes_area")
        
        st.divider()
        
# --- BOUTONS FINAUX ---
    c_save, c_cancel = st.columns(2)
    
    with c_save:
        if st.button("💾 ENREGISTRER MA RECETTE", use_container_width=True, key="save_vfinal"):
            if titre and ingredients:
                import datetime
                payload = {
                    "action": "add",
                    "date": datetime.date.today().strftime("%d/%m/%Y"),
                    "titre": titre.strip(),
                    "source": source_url.strip(),
                    "Ingrédients": ingredients.strip().replace('\n', '  \n'),
                    "Préparation": instructions.strip(),
                    "Image": img_url.strip(),
                    "Catégorie": ", ".join(cat_choisies),
                    "Portions": port.strip(),
                    "Temps_Prepa": t_prep.strip(),
                    "Temps_Cuisson": t_cuis.strip(),
                    "Commentaires": commentaires.strip(),
                    "video": video_url.strip()
                }
                
                if send_action(payload):
                    st.success("✅ Enregistré !")
                    st.cache_data.clear()
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error("❌ Erreur de connexion au serveur.")
            else:
                st.error("🚨 Le titre et les ingrédients sont obligatoires !")

    with c_cancel:
        if st.button("❌ ANNULER L'AJOUT", use_container_width=True, key="cancel_vfinal"):
            st.session_state.page = "home"
            st.rerun()
                
 # --- PAGE ÉDITION (DÉDIÉE) ---
elif st.session_state.page == "edit":
    r_edit = st.session_state.get('recipe_to_edit', {})

    # Fonction de nettoyage améliorée
    def clean_val(x):
        val = str(x).strip().lower()
        # On attrape tous les cas "vides"
        if val in ["nan", "none", "", "null", "0", "0.0", "-"]: 
            return "-"
        
        # On nettoie le texte : on enlève le .0 si c'est un nombre entier
        # Exemple : "20.0" devient "20"
        return str(x).split('.')[0]

    # --- APPLICATION AUX MÉTRIQUES ---
    p_final = clean_val(r.get('Temps de préparation', '-'))
    c_final = clean_val(r.get('Temps de cuisson', '-'))
    port_final = clean_val(r.get('Portions', '-'))

    st.markdown('<h1 style="color: #e67e22;">✏️ Modifier la Recette</h1>', unsafe_allow_html=True)
    
    if st.button("⬅ Annuler et Retour", use_container_width=True):
        st.session_state.page = "details"
        st.rerun()
    
    st.divider()
    
    with st.container():
        col_t, col_c = st.columns([2, 1])
        titre_edit = col_t.text_input("🏷️ Nom de la recette", value=clean_val(r_edit.get('Titre', '')), key="edit_titre")
        
        # Sécurité Catégories
        raw_cats = clean_val(r_edit.get('Catégorie', 'Autre'))
        current_cats = [c.strip() for c in raw_cats.split(',') if c.strip()]
        valid_cats = [c for c in current_cats if c in CATEGORIES]
        cat_choisies = col_c.multiselect("📁 Catégories", CATEGORIES, default=valid_cats if valid_cats else ["Autre"])
        
        st.markdown("#### ⏱️ Paramètres de cuisson")
        cp1, cp2, cp3 = st.columns(3)
        t_prep = cp1.text_input("🕒 Préparation (min)", value=clean_val(r_edit.get('Temps_Prepa', '')), key="edit_prep")
        t_cuis = cp2.text_input("🔥 Cuisson (min)", value=clean_val(r_edit.get('Temps_Cuisson', '')), key="edit_cuis")
        port = cp3.text_input("🍽️ Portions", value=clean_val(r_edit.get('Portions', '')), key="edit_port")
        
        st.divider()
        
        ci, ce = st.columns(2)
        ingredients = ci.text_area("🍎 Ingrédients", height=300, value=clean_val(r_edit.get('Ingrédients', '')), key="edit_ing")
        instructions = ce.text_area("👨‍🍳 Étapes de préparation", height=300, value=clean_val(r_edit.get('Préparation', '')), key="edit_ins")
        
        img_url = st.text_input("🖼️ Lien de l'image (URL)", value=clean_val(r_edit.get('Image', '')), key="edit_img")

        # Vidéo (Nouveau champ)
        r_list_vals = list(r_edit.values())
        old_v = r_list_vals[13] if len(r_list_vals) > 13 else ""
        video_url = st.text_input("📺 Lien Vidéo (YouTube, TikTok, FB)", value=clean_val(old_v), key="edit_vid")
        
        commentaires = st.text_area("📝 Mes Notes & Astuces", height=100, value=clean_val(r_edit.get('Commentaires', '')), key="edit_comm")
        
        st.divider()
        
        if st.button("💾 ENREGISTRER LES MODIFICATIONS", use_container_width=True, key="edit_submit_btn"):
            if titre_edit.strip() != "" and ingredients.strip() != "":
                
                payload = {
                    "action": "edit", 
                    "titre": titre_edit, 
                    "old_titre": clean_val(r_edit.get('Titre', titre_edit)),
                    "Catégorie": ", ".join(cat_choisies), 
                    "Ingrédients": ingredients, 
                    "Préparation": instructions, 
                    "Image": img_url, 
                    "Temps_Prepa": clean_val(t_prep), 
                    "Temps_Cuisson": clean_val(t_cuis), 
                    "Portions": clean_val(port), 
                    "Note": clean_val(r_edit.get('Note', 0)), 
                    "Commentaires": commentaires,
                    "video": video_url 
                }
                
                with st.spinner("Enregistrement en cours..."):
                    # Utilisation de la fonction send_action que tu as déjà définie
                    if send_action(payload):
                        st.success("✅ Recette mise à jour !")
                        st.cache_data.clear()
                        if 'recipe_to_edit' in st.session_state: del st.session_state.recipe_to_edit
                        st.session_state.page = "home"
                        st.rerun()
                    else:
                        st.error("❌ Erreur lors de l'envoi à Google.")
            else:
                st.error("⚠️ Le titre et les ingrédients sont obligatoires !")
# --- PAGE ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    
    if st.button("⬅ Retour"):
        st.session_state.page = "home"
        st.rerun()

    try:
        # On force la lecture sans cache avec un timestamp
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        
        if not df_s.empty:
            # On utilise un formulaire Streamlit pour éviter que la page ne saute à chaque clic
            with st.form("shop_form"):
                to_del = []
                st.write("Cochez les articles à retirer de la liste :")
                
                # On affiche les articles
                for idx, row in df_s.iterrows():
                    article_nom = str(row.iloc[0]).strip()
                    if article_nom: # On ignore les lignes vides
                        # Si coché, on ajoute à la liste to_del
                        if st.checkbox(article_nom, key=f"sh_{idx}"):
                            to_del.append(article_nom)
                
                st.divider()
                
                # Le bouton de validation du formulaire
                submit_del = st.form_submit_button("🗑 Retirer les articles sélectionnés", use_container_width=True)
                
            # Bouton "Vider tout" hors du formulaire pour plus de sécurité
            if st.button("🧨 Vider toute la liste", use_container_width=True):
                if send_action({"action": "clear_shop"}):
                    st.cache_data.clear()
                    st.success("Liste vidée !")
                    st.rerun()

            # Logique de suppression suite au clic sur le bouton du formulaire
            if submit_del:
                if to_del:
                    with st.spinner("Mise à jour..."):
                        # ENVOI UNIQUE à Google Apps Script
                        if send_action({"action": "remove_shop", "articles": to_del}):
                            st.cache_data.clear()
                            st.toast(f"Retiré : {len(to_del)} article(s)")
                            st.rerun()
                else:
                    st.warning("Veuillez cocher au moins un article.")
                    
        else:
            st.info("Votre liste est vide pour le moment.")
            
    except Exception as e:
        st.error(f"Erreur de chargement : {e}")
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
        if st.session_state.admin_mode:
            if st.button("🗑️ Vider le planning", use_container_width=True):
                if send_action({"action": "clear_planning"}):
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.button("🔒 Mode Lecture", use_container_width=True, disabled=True)

    st.divider()

    try:
        # CHARGEMENT : On essaie le fichier Planning, sinon la Bibliothèque
        df_plan = load_data(URL_CSV_PLAN)
        
        # Si le fichier planning est vide, on regarde dans la bibliothèque (version 5:48)
        if df_plan.empty or 'Date' not in df_plan.columns:
            df_all = load_data(URL_CSV)
            if 'Date_Prevue' in df_all.columns:
                df_plan = df_all[df_all['Date_Prevue'].astype(str).str.strip() != ""].copy()
                df_plan = df_plan.rename(columns={'Date_Prevue': 'Date'})

        if df_plan.empty:
            st.info("Ton planning est vide.")
        else:
            df_plan.columns = df_plan.columns.str.strip()
            df_plan['Date'] = pd.to_datetime(df_plan['Date'], errors='coerce')
            df_plan = df_plan.dropna(subset=['Date', 'Titre']).sort_values(by='Date')

            # --- TRADUCTION & AFFICHAGE ---
            jours_fr = {"Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi", "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi", "Sunday": "Dimanche"}
            mois_fr = {"January": "Janvier", "February": "Février", "March": "Mars", "April": "Avril", "May": "Mai", "June": "Juin", "July": "Juillet", "August": "Août", "September": "Septembre", "October": "Octobre", "November": "Novembre", "December": "Décembre"}

            derniere_semaine = -1
            for index, row in df_plan.iterrows():
                semaine_actuelle = row['Date'].isocalendar()[1]
                
                if semaine_actuelle != derniere_semaine:
                    st.markdown(f"""<div style="background-color: #2e313d; padding: 5px 15px; border-radius: 8px; margin: 20px 0 10px 0; border-left: 3px solid #95a5a6;">
                                    <span style="color: #95a5a6; font-size: 0.8rem; font-weight: bold; letter-spacing: 1px;">SEMAINE {semaine_actuelle}</span>
                                 </div>""", unsafe_allow_html=True)
                    derniere_semaine = semaine_actuelle

                date_txt = f"{jours_fr.get(row['Date'].strftime('%A'))} {row['Date'].strftime('%d')} {mois_fr.get(row['Date'].strftime('%B'))}"
                
                col_txt, col_cal, col_del = st.columns([3, 0.6, 0.6])
                with col_txt:
                    st.markdown(f"""<div style="background-color: #1e2129; padding: 12px; border-radius: 10px; border-left: 4px solid #e67e22; margin-bottom: 5px;">
                                    <div style="color: #e67e22; font-size: 0.75rem; font-weight: bold;">{date_txt}</div>
                                    <div style="color: white; font-size: 1.05rem; font-weight: 500;">{row['Titre']}</div>
                                 </div>""", unsafe_allow_html=True)
                
                with col_cal:
                    if st.button("📖", key=f"view_{index}"):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()

                with col_del:
                    if st.session_state.admin_mode:
                        if st.button("🗑️", key=f"del_{index}"):
                            if send_action({"action": "remove_plan", "titre": row['Titre'], "date": str(row['Date'].date())}):
                                st.cache_data.clear()
                                st.rerun()
    except Exception as e:
        st.error(f"Oups ! Erreur d'affichage : {e}")
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





































































































































































































































































