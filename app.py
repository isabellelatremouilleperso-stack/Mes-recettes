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
    /* FOND ET TITRES */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }

    /* LISTE D'ÉPICERIE */
    .stCheckbox label p {
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }

    /* SAISIE ET RECHERCHE */
    input, select, textarea, div[data-baseweb="select"] {
        color: white !important;
        background-color: #1e2129 !important;
    }
    label, .stMarkdown p { color: white !important; }

    /* CARTES DE RECETTES */
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

    /* BOUTONS & AIDE */
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

# ======================================================
# 2. LIENS
# ======================================================
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 3. FONCTIONS
# ======================================================
def send_action(payload):
    with st.spinner("🚀 Action..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear()
                time.sleep(0.5)
                return True
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
# 4. SIDEBAR
# ======================================================
with st.sidebar:
    st.image("https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png", width=100)
    st.title("🍳 Mes Recettes")

    if st.button("📚 Bibliothèque"): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning Repas"): st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Ma Liste d'épicerie"): st.session_state.page = "shop"; st.rerun()
    if st.button("➕ Ajouter Recette"): st.session_state.page = "add"; st.rerun()
    if st.button("⭐ Play Store"): st.session_state.page = "playstore"; st.rerun()
    if st.button("❓ Aide"): st.session_state.page = "help"; st.rerun()

# ======================================================
# 5. PAGES
# ======================================================

# --- PAGE ACCUEIL ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if not df.empty:
        search = st.text_input("🔍 Rechercher...")
        cat_choisie = st.selectbox("📁 Catégorie", ["Toutes"] + sorted(df['Catégorie'].unique()))
        mask = df['Titre'].str.contains(search, case=False, na=False)
        if cat_choisie != "Toutes": mask = mask & (df['Catégorie'] == cat_choisie)
        rows = df[mask].reset_index(drop=True)

        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i+j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f"""
                        <div class="recipe-card">
                            <img src="{img}" class="recipe-img">
                            <div class="recipe-title">{row['Titre']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Voir la recette", key=f"v_{i+j}"):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"
                            st.rerun()
    else:
        st.warning("Aucune donnée trouvée.")

# --- PAGE DETAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    st.header(f"📖 {r.get('Titre','Sans titre')}")
    col1, col2 = st.columns([1,1.2])
    with col1:
        st.image(r.get('Image',"https://via.placeholder.com/400"), use_container_width=True)
        note_actuelle = int(float(r.get('Note',0))) if r.get('Note') else 0
        comm_actuel = str(r.get('Commentaires',""))
        nouvelle_note = st.slider("Note (étoiles)",0,5,note_actuelle)
        nouveau_comm = st.text_area("Commentaires", value=comm_actuel)
        if st.button("💾 Enregistrer note et avis"):
            send_action({"action":"edit","titre":r['Titre'],"Note":nouvelle_note,"Commentaires":nouveau_comm})
            st.session_state.recipe_data['Note']=nouvelle_note
            st.session_state.recipe_data['Commentaires']=nouveau_comm
            st.success("Enregistré !")
    with col2:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r.get('Ingrédients','')).split("\n") if l.strip()]
        sel = []
        for i,l in enumerate(ings):
            if st.checkbox(l, key=f"chk_{i}"): sel.append(l)
        if st.button("📥 Ajouter au Panier"):
            for it in sel: send_action({"action":"add_shop","article":it})
            st.success("Ajouté !")
    st.subheader("📝 Préparation")
    st.write(r.get('Préparation','Aucune étape.'))

# --- PAGE AJOUT ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    v_t = st.text_input("Titre")
    v_cat = st.selectbox("Catégorie",CATEGORIES)
    v_txt = st.text_area("Texte / ingrédients")
    if st.button("💾 Enregistrer"):
        if v_t:
            send_action({"action":"add","titre":v_t,"catégorie":v_cat,"ingredients":v_txt,"date":datetime.now().strftime("%d/%m/%Y")})
            st.success("Recette ajoutée !")
            st.session_state.page="home"
            st.rerun()
        else:
            st.error("Titre obligatoire.")

# --- PAGE EPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Liste d'épicerie")
    if st.button("⬅ Retour"): st.session_state.page="home"; st.rerun()
    try:
        df_shop = pd.read_csv(URL_CSV_SHOP)
        if df_shop.empty: st.info("Liste vide")
        else:
            for i,row in df_shop.iterrows():
                st.checkbox(f"{row['Article']}")
    except:
        st.error("Erreur chargement liste.")
    new_item = st.text_input("Nouvel article")
    if st.button("Ajouter article"):
        if new_item:
            requests.post(URL_SCRIPT,json={"action":"add_shop","article":new_item})
            st.success("Article ajouté !")
            st.rerun()

# --- PAGE PLAY STORE ---
elif st.session_state.page == "playstore":
    st.header("📱 Mes Recettes Pro")
    st.subheader("🍳 Isabelle Latrémouille")
    st.markdown("🏆 Choix de l'éditeur")
    st.markdown("⭐ 4.9 (2 847 avis)")
    st.markdown("📥 10 000+ téléchargements")
    st.button("Installer")
    st.markdown("---")
    st.subheader("📌 Description")
    st.write("Application complète de gestion de recettes avec :\n✔ Planification\n✔ Liste d'épicerie\n✔ Notes et étoiles\n✔ Synchronisation Google Sheets\n✔ Interface sombre professionnelle")
    st.markdown("---")
    st.subheader("🔒 Sécurité")
    st.success("✔ Aucune donnée vendue")
    st.success("✔ Synchronisation sécurisée via Google Script")

# --- PAGE AIDE ---
elif st.session_state.page == "help":
    st.header("📘 Centre d'aide")
    if st.button("⬅ Retour"): st.session_state.page="home"; st.rerun()
    st.markdown("## 🔹 Ajouter une recette")
    st.write("- Onglet Ajouter > remplir titre, ingrédients, instructions > Enregistrer")
    st.markdown("## 🔹 Modifier une recette")
    st.write("- Bibliothèque > sélectionner > modifier > Enregistrer")
    st.markdown("## 🔹 Planifier repas")
    st.write("- Planning > sélectionner date > choisir recette")
    st.markdown("## 🔹 Liste d'épicerie")
    st.write("- Les recettes planifiées ajoutent automatiquement les ingrédients. Vous pouvez ajouter manuellement")
    st.markdown("## 🔹 Synchronisation")
    st.info(f"Recettes : {URL_CSV}\nÉpicerie : {URL_CSV_SHOP}\nScript : {URL_SCRIPT}")
    st.markdown("## 🔹 Problèmes fréquents")
    st.write("❌ Recettes non affichées → vérifier Google Sheet publié en CSV\n❌ Impossible d'ajouter un article → vérifier script Google WebApp\n❌ App vide → rafraîchir")
    st.markdown("---")
    st.markdown("Version 2.0 Premium")
