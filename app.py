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

    /* 5. BOUTONS */
    .logo-playstore {
        width: 100px; height: 100px; border-radius: 50%;
        object-fit: cover; border: 3px solid #e67e22; margin-bottom: 20px;
    }
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

if st.session_state.page == "playstore":
    st.markdown(f'<center><img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" class="logo-playstore"></center>', unsafe_allow_html=True)
    st.markdown("""
    ### Mes Recettes Pro  
    👩‍🍳 Isabelle Latrémouille  
    ⭐ 4.9 ★ (128 avis)  
    📥 1 000+ téléchargements  
    """)
    if st.button("📥 Installer", use_container_width=True):
        st.success("Application installée avec succès ! 🎉")
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.image("https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg")
    c2.image("https://i.postimg.cc/YCkg460C/shared-image-(5).jpg")
    c3.image("https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg")

elif st.session_state.page == "help":
    st.title("❓ Aide & Mode d'emploi")
    st.markdown("""
    1. **Ajouter** : Utilisez l'onglet **Vrac** pour coller un texte complet ou **Manuel**.
    2. **Épicerie** : Cochez les ingrédients dans une recette pour les ajouter au panier.
    3. **Planning** : Saisissez une date dans la fiche d'une recette.
    """)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

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

elif st.session_state.page == "home":
    c1, c2 = st.columns([4, 1])
    c1.header("📚 Ma Bibliothèque")
    if c2.button("🔄 Actualiser"): 
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    df = load_data()
    
    if not df.empty:
        col_search, col_cat = st.columns([2, 1])
        with col_search:
            search = st.text_input("🔍 Rechercher...", placeholder="Ex: Lasagne...")
        with col_cat:
            liste_categories = ["Toutes"] + sorted([str(c) for c in df['Catégorie'].unique() if c])
            cat_choisie = st.selectbox("📁 Catégorie", liste_categories)
        
        # --- FILTRAGE ---
        mask = df['Titre'].str.contains(search, case=False, na=False)
        if cat_choisie != "Toutes":
            mask = mask & (df['Catégorie'] == cat_choisie)
            
        # ICI : Alignement parfait sous le "if cat_choisie"
        rows = filtered.reset_index(drop=True) if 'filtered' in locals() else df[mask].reset_index(drop=True)
        
        # --- AFFICHAGE DE LA GRILLE ---
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><div class="recipe-title">{row["Titre"]}</div></div>', unsafe_allow_html=True)
                        
                       # LE BOUTON DEVIENT VERT GRÂCE AU TYPE PRIMARY
                        if st.button("Voir la recette", key=f"v_{i+j}", use_container_width=True, type="primary"):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"
                            st.rerun()
    else:
        st.warning("Aucune donnée trouvée dans le fichier Excel.")
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    st.markdown('<a href="https://www.google.com/search?q=recettes+de+cuisine" target="_blank" style="text-decoration: none;"><div style="background-color: #4285F4; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px;">🔍 Chercher une idée sur Google</div></a>', unsafe_allow_html=True)

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
                st.success("Extrait ! Allez à l'onglet 2.")

    with tab2:
        with st.form("v_f"):
            v_t = st.text_input("Titre *", value=st.session_state.temp_titre)
            v_cats = st.multiselect("Catégories", CATEGORIES)
            v_txt = st.text_area("Texte (Tri à faire)", value=st.session_state.temp_content, height=250)
            v_src = st.text_input("Source", value=st.session_state.temp_url)
            if st.form_submit_button("🚀 Enregistrer"):
                send_action({"action": "add", "titre": v_t, "categorie": ", ".join(v_cats), "ingredients": v_txt, "preparation": "Import Vrac", "source": v_src, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

    with tab3:
        with st.form("m_f"):
            m_t = st.text_input("Titre *")
            m_ing = st.text_area("Ingrédients")
            m_pre = st.text_area("Préparation")
            if st.form_submit_button("💾 Enregistrer Manuel"):
                send_action({"action": "add", "titre": m_t, "ingredients": m_ing, "preparation": m_pre, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    st.header(f"📖 {r['Titre']}")
    
    if st.button("⬅ Retour à la liste", use_container_width=True): 
        st.session_state.page = "home"; st.rerun()
    
    c1, c2 = st.columns([1, 1.2])
    with c1:
        img_url = r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400"
        st.image(img_url, use_container_width=True)
        if r.get('Source') and "http" in str(r['Source']):
            st.link_button("🌐 Voir le site d'origine", r['Source'], use_container_width=True)
            
    with c2:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        if ings:
            sel = []
            for i, l in enumerate(ings):
                if st.checkbox(l, key=f"chk_{i}"):
                    sel.append(l)
            
            if st.button("📥 Ajouter à l'épicerie", use_container_width=True, type="primary"):
                for it in sel:
                    send_action({"action": "add_shop", "article": it})
                st.toast(f"{len(sel)} articles ajoutés !"); time.sleep(0.5)
                st.session_state.page = "shop"; st.rerun()

    st.divider()
    st.subheader("📝 Préparation")
    st.info(r['Préparation'] if r['Préparation'] else "Aucune étape saisie.")

    # --- NOUVELLE SECTION : GESTION DE LA RECETTE ---
    st.divider()
    st.subheader("⚙️ Gestion")
    
    # On utilise un expander pour que ce soit discret
    with st.expander("Modifier ou Supprimer cette recette"):
        col_ed, col_del = st.columns(2)
        
        # Bouton Éditer (Bleu)
        if col_ed.button("✏️ Éditer", use_container_width=True):
            st.session_state.recipe_data = r
            st.session_state.page = "edit"
            st.rerun()
            
        # Bouton Supprimer (Rouge)
        if col_del.button("🗑️ Supprimer", use_container_width=True):
            if send_action({"action": "delete", "titre": r['Titre']}):
                st.success("Recette supprimée !")
                time.sleep(1)
                st.session_state.page = "home"; st.rerun()
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    try:
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        if not df_s.empty:
            sel_del = [row.iloc[0] for idx, row in df_s.iterrows() if st.checkbox(row.iloc[0], key=f"sh_{idx}")]
            if st.button("🗑 Retirer cochés"):
                for it in sel_del: send_action({"action": "remove_shop", "article": it})
                st.rerun()
            if st.button("🧨 Tout vider"): send_action({"action": "clear_shop"}); st.rerun()
        else: st.info("Liste vide.")
    except: st.error("Erreur de chargement.")
# --- PAGE AJOUTER (Ligne 250 environ) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    
    st.markdown('<a href="https://www.google.com/search?q=recettes+de+cuisine" target="_blank" style="text-decoration: none;"><div style="background-color: #4285F4; color: white; padding: 10px; border-radius: 10px; text-align: center; font-weight: bold; margin-bottom: 20px;">🔍 Chercher une idée sur Google</div></a>', unsafe_allow_html=True)

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
            st.info("Saisie manuelle complète")
            m_t = st.text_input("Titre de la recette *")
            m_cat = st.selectbox("Catégorie", CATEGORIES)
            m_ing = st.text_area("Ingrédients (un par ligne)")
            m_pre = st.text_area("Préparation / Étapes")
            m_img = st.text_input("Lien vers une image (Optionnel)")
            if st.form_submit_button("💾 Enregistrer la recette"):
                if m_t:
                    send_action({
                        "action": "add", 
                        "titre": m_t, 
                        "categorie": m_cat, 
                        "ingredients": m_ing, 
                        "preparation": m_pre, 
                        "image": m_img,
                        "date": datetime.now().strftime("%d/%m/%Y")
                    })
                    st.success("Recette ajoutée !")
                    st.session_state.page = "home"; st.rerun()
                else:
                    st.error("Le titre est obligatoire.")

# --- PAGE DÉTAILS (VISUALISATION) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    st.header(f"📖 {r['Titre']}")
    
    if st.button("⬅ Retour à la bibliothèque"): 
        st.session_state.page = "home"; st.rerun()
    
    c1, c2 = st.columns([1, 1.2])
    with c1:
        img_url = r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400"
        st.image(img_url, use_container_width=True)
        if r.get('Source') and "http" in str(r['Source']):
            st.link_button("🌐 Voir le site d'origine", r['Source'], use_container_width=True)
            
    with c2:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        if ings:
            sel = []
            for i, l in enumerate(ings):
                if st.checkbox(l, key=f"chk_{i}"):
                    sel.append(l)
            
            if st.button("📥 Envoyer à la liste d'épicerie", use_container_width=True, type="primary"):
                for it in sel:
                    send_action({"action": "add_shop", "article": it})
                st.toast(f"{len(sel)} articles ajoutés !"); time.sleep(0.5)
                st.session_state.page = "shop"; st.rerun()
        else:
            st.write("Aucun ingrédient listé.")

    st.divider()
    st.subheader("📝 Préparation")
    st.info(r['Préparation'] if r['Préparation'] else "Aucune étape saisie.")

    # --- ZONE DE GESTION CACHÉE ---
    st.divider()
    with st.expander("🛠️ Options avancées"):
        col_del, col_edit = st.columns(2)
        if col_del.button("🗑️ Supprimer cette recette", use_container_width=True):
            if send_action({"action": "delete", "titre": r['Titre']}):
                st.success("Recette supprimée !"); time.sleep(1)
                st.session_state.page = "home"; st.rerun()
        st.write("Pour modifier le texte, utilisez le fichier Excel directement.")

# --- PAGE ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste d'épicerie")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    try:
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        if not df_s.empty:
            items_to_delete = []
            for idx, row in df_s.iterrows():
                if st.checkbox(str(row.iloc[0]), key=f"sh_{idx}"):
                    items_to_delete.append(str(row.iloc[0]))
            
            st.divider()
            c1, c2 = st.columns(2)
            if c1.button("🗑 Retirer les cochés", use_container_width=True):
                for item in items_to_delete:
                    send_action({"action": "remove_shop", "article": item})
                st.rerun()
            if c2.button("🧨 Tout vider", use_container_width=True):
                send_action({"action": "clear_shop"})
                st.rerun()
        else:
            st.info("Votre liste d'épicerie est vide.")
    except:
        st.error("Erreur lors du chargement de la liste.")

# --- PAGE AIDE (RESTAURÉE) ---
elif st.session_state.page == "help":
    st.title("❓ Aide & Mode d'emploi")
    st.markdown("""
    ### Bienvenue dans votre carnet de recettes !
    
    1. **Bibliothèque** : C'est ici que se trouvent toutes vos recettes. Cliquez sur l'image ou le bouton pour voir le détail.
    2. **Ajouter** : 
        - **Import URL** : Collez un lien (ex: Marmiton) pour extraire le texte.
        - **Tri & Vrac** : Nettoyez le texte extrait ou collez votre propre texte brut ici.
        - **Manuel** : Remplissez les cases une par une.
    3. **Épicerie** : Cochez les ingrédients dans une recette, ils s'ajouteront à votre liste globale.
    4. **Planning** : Pour l'instant, le planning se gère en ajoutant une date dans votre fichier Excel.
    
    **Astuce** : Si une modification ne s'affiche pas, cliquez sur le bouton **🔄 Actualiser** en haut de la bibliothèque.
    """)
    if st.button("⬅ Retour à l'accueil"):
        st.session_state.page = "home"; st.rerun()




