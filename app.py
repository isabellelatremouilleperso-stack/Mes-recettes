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

    /* 2. LISTE D'ÉPICERIE (Tes commandes étaient ici !) */
    .stCheckbox label p {
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    .stCheckbox [data-testid="stWidgetLabel"] {
        color: white !important;
    }

    /* 3. SAISIE ET RECHERCHE (Pour téléphone) */
    input, select, textarea, div[data-baseweb="select"] {
        color: white !important;
        background-color: #1e2129 !important;
    }
    label, .stMarkdown p { color: white !important; }
    ::placeholder { color: #888888 !important; opacity: 1 !important; }

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

    /* 5. BOUTONS DE NAVIGATION COLORÉS */
    div.stButton > button { border-radius: 10px; font-weight: bold; height: 3em; }
    [data-testid="column"]:nth-of-type(1) button { background-color: #2e7d32 !important; color: white !important; }
    [data-testid="column"]:nth-of-type(2) button { background-color: #1565c0 !important; color: white !important; }
    [data-testid="column"]:nth-of-type(3) button { background-color: #e67e22 !important; color: white !important; }
    [data-testid="column"]:nth-of-type(4) button { background-color: #c0392b !important; color: white !important; }
    [data-testid="column"]:nth-of-type(5) button { background-color: #7b1fa2 !important; color: white !important; }
    .logo-playstore {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #e67e22;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS DE GESTION (SCRAPER, ACTIONS, LOAD)
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

# --- PAGE PLAY STORE ---
if st.session_state.page == "playstore":
    # Cette ligne va utiliser le style que tu viens de créer à la ligne 58
    st.markdown(f'<center><img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" class="logo-playstore"></center>', unsafe_allow_html=True)
    st.image("https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png", width=100)
    st.markdown("""
    ### Mes Recettes Pro  
    👩‍🍳 Isabelle Latrémouille  
    ⭐ 4.9 ★ (128 avis)  
    📥 1 000+ téléchargements  
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("")
    
    col1, col2 = st.columns([1,3])
    with col1:
        if st.button("📥 Installer", use_container_width=True):
            st.success("Application installée avec succès ! 🎉")
            
    st.divider()
    st.subheader("📸 Aperçu")
    
    c1, c2, c3 = st.columns(3)
    # Prépare tes chemins d'images ici pour ce soir
    c1.image("https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg")
    c2.image("https://i.postimg.cc/YCkg460C/shared-image-(5).jpg")
    c3.image("https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg")
    
    st.divider()
    st.subheader("📝 À propos de cette application")
    st.write("""
    Mes Recettes Pro est une application complète de gestion culinaire.
    ✔ Gestion des recettes  
    ✔ Système de notes ⭐  
    ✔ Planning intégré 📅  
    ✔ Liste d'épicerie intelligente 🛒  
    ✔ Synchronisation Google  
    Une solution parfaite pour organiser vos repas comme un chef !
    """)
    
    st.divider()
    st.subheader("ℹ️ Informations")
    st.write("""
    Version : 2.0 Premium  
    Mise à jour : Février 2026  
    Catégorie : Cuisine  
    Compatibilité : Android / Tablette  
    Développeur : Isabelle Latrémouille  
    """)

# --- PAGE AIDE (TON TEXTE ORIGINAL RESTAURÉ) ---
elif st.session_state.page == "help":
    st.title("❓ Aide & Mode d'emploi")
    st.markdown("""
    1. **Ajouter** : Utilisez l'onglet **Vrac** pour coller un texte complet rapidement, ou **Manuel** pour remplir chaque champ.
    2. **Épicerie** : Dans une recette, cochez les ingrédients manquants et cliquez sur le bouton bleu. Dans la page Épicerie, cochez ce que vous avez acheté pour le retirer de la liste.
    3. **Planning** : Saisissez une date dans la fiche d'une recette pour qu'elle apparaisse dans votre calendrier.
    4. **Actualiser** : Si vous avez modifié le fichier Excel directement, utilisez le bouton 🔄 en haut de la bibliothèque.
    """)
    if st.button("⬅ Retour"):
        st.session_state.page = "home"
        st.rerun()

# --- PLANNING (CORRIGÉ POUR ÉVITER LE VIDE) ---
elif st.session_state.page == "planning":
    st.header("📅 Planning des Repas")
    df = load_data()
    if not df.empty:
        # Filtre les lignes où la colonne Date_Prevue n'est pas vide
        plan = df[df['Date_Prevue'].astype(str).str.strip() != ""].sort_values(by='Date_Prevue')
        if not plan.empty:
            for _, row in plan.iterrows():
                with st.expander(f"📌 {row['Date_Prevue']} : {row['Titre']}"):
                    if st.button("Voir la fiche complète", key=f"p_{row['Titre']}"):
                        st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
        else:
            st.info("Aucun repas planifié pour le moment. Ajoutez une date dans la fiche d'une recette.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- MODULE BIBLIOTHÈQUE (RECHERCHE + FILTRE CATÉGORIE) ---
elif st.session_state.page == "home":
    c1, c2 = st.columns([4, 1])
    c1.header("📚 Ma Bibliothèque")
    if c2.button("🔄 Actualiser"): 
        st.cache_data.clear()
        st.rerun()
   # --- NAVIGATION STYLE APPLI MOBILE ---
    st.markdown("""
        <style>
        div.stButton > button {
            border-radius: 10px;
            font-weight: bold;
            height: 3em;
        }
        /* Couleur spécifique pour chaque bouton par leur ordre */
        .stColumn:nth-child(1) button { background-color: #2e7d32; color: white; border: none; } /* Vert */
        .stColumn:nth-child(2) button { background-color: #1565c0; color: white; border: none; } /* Bleu */
        .stColumn:nth-child(3) button { background-color: #e67e22; color: white; border: none; } /* Orange */
        .stColumn:nth-child(4) button { background-color: #546e7a; color: white; border: none; } /* Gris-bleu */
        </style>
    """, unsafe_allow_html=True)

 
        
    st.divider()
    df = load_data()
    
    if not df.empty:
        # --- ZONE DE FILTRES ---
        col_search, col_cat = st.columns([2, 1])
        
        with col_search:
            search = st.text_input("🔍 Rechercher par nom...", placeholder="Ex: Lasagne, Poulet...")
            
        with col_cat:
            # On récupère la liste unique des catégories + une option "Toutes"
            liste_categories = ["Toutes"] + sorted([str(c) for c in df['Catégorie'].unique() if c])
            cat_choisie = st.selectbox("📁 Catégorie", liste_categories)
        
        # --- LOGIQUE DE FILTRAGE COMBINÉE ---
        # 1. Filtre par texte (Nom)
        mask = df['Titre'].str.contains(search, case=False, na=False)
        
        # 2. Filtre par catégorie (si différent de "Toutes")
        if cat_choisie != "Toutes":
            mask = mask & (df['Catégorie'] == cat_choisie)
            
        filtered = df[mask]
        # ------------------------------------
        
        st.write(f"*{len(filtered)} recette(s) trouvée(s)*")
        
        rows = filtered.reset_index(drop=True)
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><div class="recipe-title">{row["Titre"]}</div></div>', unsafe_allow_html=True)
                        if st.button("Voir", key=f"btn_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"
                            st.rerun()
    else:
        st.warning("Aucune donnée trouvée dans le fichier Excel.")

# --- AJOUTER RECETTE (IMPORT URL + VRAC + MANUEL) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    tab1, tab2, tab3 = st.tabs(["🔗 Import URL", "📝 Vrac", "⌨️ Manuel"])
    
    with tab1:
        url_link = st.text_input("Collez le lien du site (Marmiton, Ricardo, etc.)")
        if st.button("🪄 Extraire et Importer"):
            t, c = scrape_url(url_link)
            if t: 
                # On ajoute "source": url_link pour que le bouton "Recette originale" fonctionne
                send_action({
                    "action": "add", 
                    "titre": t, 
                    "ingredients": c, 
                    "preparation": "Import automatique", 
                    "source": url_link, 
                    "date": datetime.now().strftime("%d/%m/%Y")
                })
                st.success(f"✅ {t} ajouté avec sa source !")
                time.sleep(1)
                st.session_state.page = "home"; st.rerun()
                
    with tab2:
        with st.form("v_f"):
            v_t = st.text_input("Titre *")
            v_cats = st.multiselect("Catégories", CATEGORIES)
            c1, c2, c3 = st.columns(3)
            v_por, v_pre, v_cui = c1.text_input("Portions"), c2.text_input("Temps Prépa"), c3.text_input("Temps Cuisson")
            v_txt = st.text_area("Texte de la recette", height=250)
            # --- NOUVEAU CHAMP SOURCE EN VRAC ---
            v_source = st.text_input("Lien du site d'origine (URL)")
            
            if st.form_submit_button("🚀 Enregistrer en Vrac"):
                send_action({"action": "add", "titre": v_t, "categorie": ", ".join(v_cats), "ingredients": v_txt, "preparation": "Import Vrac", "portions": v_por, "temps_prepa": v_pre, "temps_cuisson": v_cui, "source": v_source, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()
                
    with tab3:
        with st.form("m_f"):
            m_t = st.text_input("Titre *")
            m_cats = st.multiselect("Catégories", CATEGORIES)
            c1, c2, c3 = st.columns(3)
            m_por, m_pre, m_cui = c1.text_input("Portions"), c2.text_input("Préparation"), c3.text_input("Cuisson")
            m_ing, m_prepa = st.text_area("Ingrédients"), st.text_area("Étapes")
            # --- LES DEUX LIENS IMPORTANTS ---
            m_img = st.text_input("Lien Image (Lien direct .jpg)")
            m_source = st.text_input("Lien du site d'origine (URL)")
            
            if st.form_submit_button("💾 Enregistrer"):
                send_action({"action": "add", "titre": m_t, "categorie": ", ".join(m_cats), "ingredients": m_ing, "preparation": m_prepa, "portions": m_por, "temps_prepa": m_pre, "temps_cuisson": m_cui, "image": m_img, "source": m_source, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

# --- DÉTAILS (VERSION BEAUTIFUL) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.title(f"🍳 {r['Titre']}")
    
    # Système de note stylisé
    try: nv = int(float(r.get('Note', 0)))
    except: nv = 0
    st.markdown(f"<h3 style='color: #f1c40f;'>{'⭐' * nv}{'☆' * (5 - nv)}</h3>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1.2])
    with c1:
        # Image avec coins arrondis (géré par le CSS global)
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        
        # --- LIEN SOURCE STYLE "BADGE" ---
        if r.get('Source') and "http" in str(r['Source']):
            st.markdown(f"""
                <div style="background-color: #262730; padding: 10px; border-radius: 10px; border-left: 5px solid #e67e22; margin-top: 10px;">
                    <a href="{r['Source']}" target="_blank" style="text-decoration: none; color: #e67e22; font-weight: bold;">
                        📖 Voir la recette originale →
                    </a>
                </div>
            """, unsafe_allow_html=True)
        # ---------------------------------

        st.divider()
        st.subheader("⚙️ Paramètres")
        new_note = st.selectbox("Ma Note", [1,2,3,4,5], index=(nv-1 if 1<=nv<=5 else 4))
        new_comm = st.text_area("Mes Commentaires", value=r.get('Commentaires', ''), placeholder="Ajoutez vos notes personnelles ici...")
        new_plan = st.text_input("📅 Planifier (JJ/MM/AAAA)", value=r.get('Date_Prevue', ''))
        
        if st.button("💾 Sauvegarder les modifications", use_container_width=True):
            send_action({"action": "update_notes", "titre": r['Titre'], "date_prevue": new_plan, "commentaires": new_comm, "note": new_note})
            st.success("Modifications enregistrées !")
            time.sleep(1)
            st.rerun()
            
    with c2:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        
        # Petit container pour les ingrédients
        with st.container():
            sel = []
            for i, l in enumerate(ings):
                if st.checkbox(f"**{l}**", key=f"det_{i}"): 
                    sel.append(l)
            
            if st.button("📥 Ajouter la sélection au panier", use_container_width=True, type="primary"):
                if sel:
                    for x in sel: send_action({"action": "add_shop", "article": x})
                    st.toast(f"{len(sel)} articles ajoutés !", icon="🛒")
                else:
                    st.warning("Veuillez cocher des ingrédients.")
        
        st.divider()
        st.subheader("📝 Préparation")
        st.info(r['Préparation'])
# --- ÉPICERIE (VERSION ÉPURÉE SANS BOUTON RETOUR) ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
        
    try:
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        if not df_s.empty:
            selection_delete = []
            for idx, row in df_s.iterrows():
                # On affiche chaque article avec sa case à cocher
                if st.checkbox(row.iloc[0], key=f"s_{idx}"): 
                    selection_delete.append(row.iloc[0])
            
            st.divider()
            c1, c2 = st.columns(2)
            if c1.button("🗑 Retirer cochés", use_container_width=True):
                for it in selection_delete: 
                    send_action({"action": "remove_shop", "article": it})
                st.rerun()
            if c2.button("🧨 Tout vider", use_container_width=True):
                send_action({"action": "clear_shop"})
                st.rerun()
        else: 
            st.info("Votre liste est vide.")
            
    except: 
        st.info("Impossible de charger la liste.")

# --- AIDE (RESTAURÉE À L'IDENTIQUE) ---
elif st.session_state.page == "help":
    st.title("❓ Aide & Mode d'emploi")
    st.markdown("""
    1. **Ajouter** : Utilisez l'onglet **Vrac** pour coller un texte complet rapidement, ou **Manuel** pour remplir chaque champ.
    2. **Épicerie** : Dans une recette, cochez les ingrédients manquants et cliquez sur le bouton bleu. Dans la page Épicerie, cochez ce que vous avez acheté pour le retirer de la liste.
    3. **Planning** : Saisissez une date dans la fiche d'une recette pour qu'elle apparaisse dans votre calendrier.
    4. **Actualiser** : Si vous avez modifié le fichier Excel directement, utilisez le bouton 🔄 en haut de la bibliothèque.
    """)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()


























