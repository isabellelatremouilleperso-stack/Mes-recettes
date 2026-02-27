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

st.markdown("""
<style>
/* --- DESIGN ÉCRAN (Dark Mode par défaut) --- */
.only-print { display: none !important; }

@media print {
    /* 1. ON CACHE LE SURFLU */
    .no-print, [data-testid="stSidebar"], [data-testid="stHeader"], 
    .stButton, button, header, footer, [data-testid="stDecoration"] {
        display: none !important;
        height: 0px !important;
    }

    /* 2. FORCE LE FOND BLANC ET TEXTE NOIR */
    html, body, .stApp, .main, .block-container {
        background-color: white !important;
        color: black !important;
    }

    /* 3. UTILISE TOUTE LA LARGEUR DE LA PAGE */
    .main .block-container {
        max-width: 100% !important;
        width: 100% !important;
        padding: 0.5cm !important;
        margin: 0 !important;
    }

    /* 4. REND LE TEXTE ET LES LISTES VISIBLES */
    .only-print {
        display: block !important;
        visibility: visible !important;
        color: black !important;
        font-size: 12pt !important;
    }

    /* Force absolument tout le texte en noir (pour contrer le mode sombre) */
    h1, h2, h3, h4, p, span, li, div {
        color: black !important;
    }

    /* 5. AJUSTE LES IMAGES POUR LE PAPIER */
    img {
        max-width: 8cm !important;
        border-radius: 10px !important;
    }
}
</style>
""", unsafe_allow_html=True)

# --- SECTION STYLE (Correction de l'erreur 76) ---
st.markdown("""
<style>
<style>
/* --- DESIGN ÉCRAN --- */
.only-print { display: none !important; }

@media print {
    /* Cache tout ce qui gène */
    .no-print, [data-testid="stSidebar"], [data-testid="stHeader"], .stButton, button {
        display: none !important;
    }

    /* Force l'apparition de la liste pour le papier */
    .only-print {
        display: block !important;
        visibility: visible !important;
        color: black !important;
        font-size: 14pt !important;
    }

    /* Force le fond blanc pour économiser l'encre */
    .stApp {
        background-color: white !important;
        color: black !important;
    }
}
</style>
    /* 4. ON UTILISE TOUTE LA LARGEUR (Supprime le décalage de la sidebar) */
    .main .block-container {
        max-width: 100% !important;
        width: 100% !important;
        padding: 0.5cm !important;
        margin: 0 !important;
    }

    /* 5. ON REND LES IMAGES PLUS NETTES */
    img {
        max-width: 10cm !important;
        border-radius: 10px !important;
        margin-bottom: 10px !important;
    }
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
    # On utilise le même style CSS que dans le Play Store pour le logo
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" 
             style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid #e67e22; object-fit: cover;">
    </div>
    """, unsafe_allow_html=True)
    
    st.title("🍳 Mes Recettes")
    if st.button("📚 Bibliothèque",use_container_width=True,key="side_home"): st.session_state.page="home"; st.rerun()
    if st.button("📅 Planning Repas",use_container_width=True,key="side_plan"): st.session_state.page="planning"; st.rerun()
    if st.button("🛒 Ma Liste d'épicerie",use_container_width=True,key="side_shop"): st.session_state.page="shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER RECETTE",use_container_width=True,key="side_add"): st.session_state.page="add"; st.rerun()
    if st.button("⭐ Play Store",use_container_width=True,key="side_play"): st.session_state.page="playstore"; st.rerun()
    if st.button("❓ Aide",use_container_width=True,key="side_help"): st.session_state.page="help"; st.rerun()

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
    
    # CSS AVANCÉ POUR UN LOOK PRO ET ÉPURÉ
    st.markdown("""
        <style>
        /* On crée une carte qui ressemble à celles de ta tablette */
        .recipe-card {
            background-color: #1e1e1e;
            border-radius: 12px;
            border: 1px solid #333;
            margin-bottom: 25px;
            overflow: hidden; /* Pour que l'image ne dépasse pas des coins arrondis */
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            height: 480px; /* On fixe une hauteur totale pour que tout soit aligné */
        }
        
        /* L'IMAGE : Elle prend tout l'espace et se cadre toute seule */
        .recipe-img-container {
            width: 100%;
            height: 320px; /* Hauteur de l'image */
            overflow: hidden;
        }
        
        .recipe-img-container img {
            width: 100%;
            height: 100%;
            object-fit: cover; /* MAGIE : cadre l'image parfaitement sans déformer */
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
            height: 50px; /* Pour que les titres longs ne décalent pas tout */
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
        # Barre de recherche plus fine
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
            colors = {"Poulet": "#FF5733", "Bœuf": "#C70039", "Dessert": "#FF33FF",
                      "Légumes": "#28B463", "Poisson": "#3498DB", "Pâtes": "#F1C40F"}
            return colors.get(cat, "#e67e22")

        rows = df[mask].reset_index(drop=True)
        
        # AFFICHAGE EN 2 COLONNES (PLUS GRAND ET PLUS BEAU)
        for i in range(0, len(rows), 2):
            grid_cols = st.columns(2) 
            for j in range(2):
                if i+j < len(rows):
                    row = rows.iloc[i+j]
                    with grid_cols[j]:
                        img_url = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/500x350"
                        cat_label = row['Catégorie'] if row['Catégorie'] else "Recette"
                        
                        # Création de la carte HTML
                        st.markdown(f"""
                        <div class="recipe-card">
                            <div class="recipe-img-container">
                                <img src="{img_url}">
                            </div>
                            <div class="recipe-content">
                                <span class="category-badge" style="background-color:{get_cat_color(cat_label)}; color:white;">
                                    {cat_label}
                                </span>
                                <div class="recipe-title-text">{row['Titre']}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Le bouton est juste en dessous de la carte
                        if st.button("📖 Ouvrir la recette", key=f"v_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"
                            st.rerun()
    else:
        st.warning("Aucune donnée trouvée.")
# --- PAGE DÉTAILS (CONSULTATION) ---
elif st.session_state.page=="details":
    r = st.session_state.recipe_data

    # --- BARRE D'OUTILS : RETOUR, ÉDITER, IMPRIMER, SUPPRIMER ---
    # On utilise 4 colonnes pour bien aligner les boutons en haut
    c_nav1, c_nav2, c_nav3, c_nav4 = st.columns([1, 1, 1, 1])
    
    with c_nav1:
        if st.button("⬅ Retour", use_container_width=True): 
            st.session_state.page="home"; st.rerun()
    
    with c_nav2:
        if st.button("✏️ Éditer", use_container_width=True): 
            st.session_state.page="add"; st.rerun()
    
    with c_nav3:
        # On utilise un composant "link_button" natif de Streamlit si disponible, 
        # ou un lien HTML stylé très simple.
        st.markdown(f"""
            <a href="javascript:window.print()" target="_self" style="text-decoration: none;">
                <div style="
                    background-color: #e67e22;
                    color: white;
                    height: 38px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: bold;
                    border: 2px solid #d35400;
                ">
                    🖨️ Imprimer
                </div>
            </a>
        """, unsafe_allow_html=True)
            
    with c_nav4:
        if st.button("🗑️ Supprimer", use_container_width=True): 
            if send_action({"action":"delete","titre":r['Titre']}):
                st.session_state.page="home"; st.rerun()

    st.divider()
    
    # --- TITRE DE LA RECETTE ---
    st.header(f"📖 {r.get('Titre','Sans titre')}")
    
    # ... (Le reste du code pour l'affichage des colonnes gauche/droite reste le même)
    col_g, col_d = st.columns([1, 1.2])
    # ... etc
    col_g,col_d = st.columns([1,1.2])
    with col_g:
        img_url = r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400"
        st.image(img_url,use_container_width=True)
        st.markdown("### ⭐ Ma Note & Avis")
        note_actuelle = int(float(r.get('Note',0))) if r.get('Note') else 0
        comm_actuel = str(r.get('Commentaires',""))
        nouvelle_note = st.slider("Note",0,5,note_actuelle,key="val_note")
        nouveau_comm = st.text_area("Commentaires / astuces",value=comm_actuel,height=100,key="val_comm")
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
        raw_ings = str(r.get('Ingrédients',''))
        ings = [l.strip() for l in raw_ings.split("\n") if l.strip()]

        if ings:
            # --- CE QUE TU VOIS SUR TA TABLETTE ---
            st.markdown('<div class="no-print">', unsafe_allow_html=True)
            for i, l in enumerate(ings):
                st.checkbox(l, key=f"chk_print_final_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

            # --- CE QUI SORT SUR TON PAPIER (On force le noir ici aussi) ---
            st.markdown('<div class="only-print" style="color: black !important;">', unsafe_allow_html=True)
            for l in ings:
                # Utilisation d'un texte simple avec une puce
                st.write(f"• {l}")
            st.markdown('</div>', unsafe_allow_html=True)
# --- PAGE : AJOUTER UNE RECETTE (ÉPURÉE) ---
elif st.session_state.page == "add":
    st.markdown('<h1 style="color: #e67e22;">📥 Ajouter une Nouvelle Recette</h1>', unsafe_allow_html=True)
    
    # --- NAVIGATION SIMPLE ---
    if st.button("⬅ Retour à la Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()

    st.write("")
    # --- BARRE DE RECHERCHE GOOGLE.CA (FIXÉE) ---
    st.markdown("""
        <div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; border-left: 5px solid #4285F4; margin-bottom: 20px;">
            <h4 style="margin:0; color:white;">🔍 Chercher une idée sur Google Canada</h4>
        </div>
    """, unsafe_allow_html=True)
    
    c_search, c_btn = st.columns([3, 1])
    search_query = c_search.text_input("Que cherchez-vous ?", placeholder="Ex: Pâte à tarte Ricardo", label_visibility="collapsed")
    
    import urllib.parse
    query_encoded = urllib.parse.quote(search_query + ' recette') if search_query else ""
    target_url = f"https://www.google.ca/search?q={query_encoded}" if search_query else "https://www.google.ca"
    
    c_btn.markdown(f"""
        <a href="{target_url}" target="_blank" style="text-decoration: none;">
            <div style="background-color: #4285F4; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; cursor: pointer;">
                🌐 Aller sur Google.ca
            </div>
        </a>
    """, unsafe_allow_html=True)

    # --- SECTION IMPORTATION ---
    st.markdown("""
        <div style="background-color: #1e2129; padding: 20px; border-radius: 15px; border: 1px solid #3d4455; margin-top: 10px;">
            <h3 style="margin-top:0; color:#e67e22;">🌐 Importer depuis le Web</h3>
    """, unsafe_allow_html=True)
    
    col_url, col_go = st.columns([4, 1])
    url_input = col_url.text_input("Collez l'URL ici", placeholder="https://www.ricardocuisine.com/...")
    
    if col_go.button("Extraire ✨", use_container_width=True):
        if url_input:
            t, c = scrape_url(url_input)
            if t:
                st.session_state.scraped_title = t
                st.session_state.scraped_content = c
                st.success("Extraction réussie !")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # --- FORMULAIRE (STRUCTURE ORIGINALE CONSERVÉE) ---
    with st.container():
        # Ligne 1 : Titre et Catégories (Passage en MULTISELECT)
        col_t, col_c = st.columns([2, 1])
        titre = col_t.text_input("🏷️ Nom de la recette", 
                                 value=st.session_state.get('scraped_title', ''),
                                 placeholder="Ex: Lasagne de maman")
        
        # Ici on peut maintenant choisir plusieurs catégories
        cat_choisies = col_c.multiselect("📁 Catégories", CATEGORIES, default=["Autre"])

        # Ligne 2 : Paramètres de cuisson
        st.markdown("#### ⏱️ Paramètres de cuisson")
        cp1, cp2, cp3 = st.columns(3)
        t_prep = cp1.text_input("🕒 Préparation (min)", placeholder="15")
        t_cuis = cp2.text_input("🔥 Cuisson (min)", placeholder="45")
        port = cp3.text_input("🍽️ Portions", placeholder="4")

        st.divider()

        # Ligne 3 : Ingrédients & Étapes (Côte à côte)
        ci, ce = st.columns(2)
        with ci:
            st.markdown("### 🍎 Ingrédients")
            ingredients = st.text_area("Un ingrédient par ligne", height=300, placeholder="2 tasses de farine...")
        with ce:
            st.markdown("### 👨‍🍳 Étapes de préparation")
            val_p = st.session_state.get('scraped_content', '')
            instructions = st.text_area("Décrivez les étapes", value=val_p, height=300)

        # Ligne 4 : Image
        st.markdown("#### 🖼️ Visuel")
        img_url = st.text_input("Lien de l'image (URL)", placeholder="https://...")

        # --- SECTION : COMMENTAIRES / NOTES ---
        st.markdown("#### 📝 Mes Notes & Astuces")
        commentaires = st.text_area("Ajoutez vos conseils (ex: Moins de sucre, temps de repos...)", 
                                    height=100,
                                    placeholder="Ce champ m'aide à ajuster la recette la prochaine fois...")

        st.divider()

        # --- BOUTON SAUVEGARDE ---
        if st.button("💾 ENREGISTRER DANS MA BIBLIOTHÈQUE", use_container_width=True):
            if titre and ingredients:
                # On transforme la liste des catégories en texte pour la sauvegarde
                cat_finales = ", ".join(cat_choisies)
                
                payload = {
                    "action": "add",
                    "titre": titre,
                    "Catégorie": cat_finales,
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
                    st.success(f"✅ '{titre}' ajouté avec succès !")
                    if 'scraped_title' in st.session_state: del st.session_state.scraped_title
                    if 'scraped_content' in st.session_state: del st.session_state.scraped_content
                    time.sleep(1)
                    st.session_state.page = "home"
                    st.rerun()
            else:
                st.error("Le titre et les ingrédients sont obligatoires !")
# --- PAGE ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    if st.button("⬅ Retour"): 
        st.session_state.page = "home"
        st.rerun()
    try:
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        if not df_s.empty:
            to_del = []
            for idx, row in df_s.iterrows():
                if st.checkbox(str(row.iloc[0]), key=f"sh_{idx}"): 
                    to_del.append(str(row.iloc[0]))
            
            c1, c2 = st.columns(2)
            if c1.button("🗑 Retirer"):
                for it in to_del: 
                    send_action({"action": "remove_shop", "article": it})
                st.rerun()
            if c2.button("🧨 Vider"): 
                send_action({"action": "clear_shop"})
                st.rerun()
        else: 
            st.info("Liste vide.")
    except: 
        st.error("Erreur de chargement de l'épicerie.")

# --- PAGE PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data()
    if not df.empty:
        if 'Date_Prevue' in df.columns:
            plan = df[df['Date_Prevue'].astype(str).str.strip() != ""].sort_values(by='Date_Prevue')
            for _, row in plan.iterrows():
                with st.expander(f"📌 {row['Date_Prevue']} : {row['Titre']}"):
                    if st.button("Voir la fiche", key=f"p_{row['Titre']}"):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
        else:
            st.warning("Aucun repas planifié pour le moment.")
    if st.button("⬅ Retour"): 
        st.session_state.page = "home"
        st.rerun()

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
# --- PAGE AIDE (RESTAURÉE) ---
elif st.session_state.page=="help":
    st.header("❓ Aide & Astuces")
    ca,cb=st.columns(2)
    with ca:
        st.markdown("""
        <div class="help-box">
            <h3>📝 Ajouter Recette</h3>
            <p>🌐 Site Web, 🎬 Vidéo ou 📝 Vrac/manuel pour ajouter vos recettes.</p>
        </div>
        """,unsafe_allow_html=True)
        st.markdown("""
        <div class="help-box">
            <h3>🔍 Rechercher</h3>
            <p>Recherchez par titre ou filtre par catégorie dans la bibliothèque.</p>
        </div>
        """,unsafe_allow_html=True)
    with cb:
        st.markdown("""
        <div class="help-box">
            <h3>🛒 Liste d'Épicerie</h3>
            <p>Cochez les ingrédients pour les ajouter. Retirer ou vider la liste à tout moment.</p>
        </div>
        """,unsafe_allow_html=True)
        st.markdown("""
        <div class="help-box">
            <h3>📅 Planning</h3>
            <p>Planifiez vos repas et accédez directement aux fiches des recettes.</p>
        </div>
        """,unsafe_allow_html=True)
    st.divider()
    if st.button("⬅ Retour à la Bibliothèque",use_container_width=True):
        st.session_state.page="home"; st.rerun()






















































