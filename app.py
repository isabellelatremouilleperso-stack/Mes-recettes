import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup
import urllib.parse

# ======================================================
# CONFIGURATION & DESIGN
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    /* FOND & TITRES */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }

    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background-color: #1e2129;
        color: #ffffff;
    }

    /* LISTE D'ÉPICERIE */
    .stCheckbox label p {
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }

    /* INPUT & TEXTAREA */
    input, select, textarea, div[data-baseweb="select"] {
        color: white !important;
        background-color: #1e2129 !important;
    }
    label, .stMarkdown p { color: white !important; }

    /* CARTES RECETTES */
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

    /* PLAY STORE */
    .playstore-container {
        display: flex; flex-direction: column; align-items: center; text-align: center; margin-bottom: 20px;
    }
    .logo-rond-centre {
        width: 120px !important;
        height: 120px !important;
        border-radius: 50% !important;
        object-fit: cover;
        border: 4px solid #e67e22;
        margin-bottom: 15px;
    }

    /* AIDE */
    .help-box {
        background-color: #1e2130; padding: 20px; border-radius: 15px;
        border-left: 5px solid #e67e22; margin-bottom: 20px;
    }
    .help-box h3 { color: #e67e22; margin-top: 0; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# LIENS & CONSTANTES
# ======================================================
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# FONCTIONS
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
        elements = soup.find_all(['li','p'])
        content = "\n".join(dict.fromkeys([el.text.strip() for el in elements if 10<len(el.text.strip())<500]))
        return title, content
    except: return None,None

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
# SIDEBAR
# ======================================================
with st.sidebar:
    st.image("https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png", width=100)
    st.title("🍳 Mes Recettes")
    if st.button("📚 Bibliothèque"): st.session_state.page="home"; st.rerun()
    if st.button("📅 Planning Repas"): st.session_state.page="planning"; st.rerun()
    if st.button("🛒 Ma Liste d'épicerie"): st.session_state.page="shop"; st.rerun()
    if st.button("➕ Ajouter Recette"): st.session_state.page="add"; st.rerun()
    if st.button("⭐ Play Store"): st.session_state.page="playstore"; st.rerun()
    if st.button("❓ Aide"): st.session_state.page="help"; st.rerun()

# ======================================================
# PAGES
# ======================================================

# --- PAGE BIBLIOTHEQUE ---
if st.session_state.page=="home":
    c1, c2 = st.columns([4,1])
    c1.header("📚 Ma Bibliothèque")
    if c2.button("🔄 Actualiser"): st.cache_data.clear(); st.rerun()
    df = load_data()
    if not df.empty:
        col_search, col_cat = st.columns([2,1])
        with col_search: search = st.text_input("🔍 Rechercher...", placeholder="Ex: Lasagne...")
        with col_cat:
            liste_categories = ["Toutes"] + sorted([str(c) for c in df['Catégorie'].unique() if c])
            cat_choisie = st.selectbox("📁 Catégorie", liste_categories)
        mask = df['Titre'].str.contains(search, case=False, na=False)
        if cat_choisie!="Toutes": mask = mask & (df['Catégorie']==cat_choisie)
        rows = df[mask].reset_index(drop=True)
        for i in range(0,len(rows),3):
            cols = st.columns(3)
            for j in range(3):
                if i+j<len(rows):
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
                            st.session_state.recipe_data=row.to_dict()
                            st.session_state.page="details"
                            st.rerun()
    else: st.warning("Aucune donnée trouvée.")

# --- PAGE DETAILS ---
elif st.session_state.page=="details":
    r = st.session_state.recipe_data
    st.header(f"📖 {r.get('Titre','Sans titre')}")
    col_g, col_d = st.columns([1,1.2])
    with col_g:
        st.image(r.get('Image',"https://via.placeholder.com/400"), use_container_width=True)
        note_act = int(float(r.get('Note',0))) if r.get('Note') else 0
        comm_act = str(r.get('Commentaires',""))
        note_new = st.slider("Note (étoiles)",0,5,note_act)
        comm_new = st.text_area("Commentaires", value=comm_act)
        if st.button("💾 Enregistrer note et avis"):
            send_action({"action":"edit","titre":r['Titre'],"Note":note_new,"Commentaires":comm_new})
            st.session_state.recipe_data['Note']=note_new
            st.session_state.recipe_data['Commentaires']=comm_new
            st.success("Enregistré !")
    with col_d:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r.get('Ingrédients','')).split("\n") if l.strip()]
        sel=[]
        for i,l in enumerate(ings):
            if st.checkbox(l,key=f"chk_det_{i}"): sel.append(l)
        if st.button("📥 Ajouter au Panier"):
            for it in sel: send_action({"action":"add_shop","article":it})
            st.success("Ajouté !")
    st.subheader("📝 Préparation")
    st.write(r.get('Préparation','Aucune étape.'))

# --- PAGE AJOUT ---
elif st.session_state.page=="add":
    st.header("➕ Ajouter une Recette")
    tab1, tab2, tab3 = st.tabs(["🌐 Site Web (Auto)", "🎬 Lien Vidéo", "📝 Vrac / Manuel"])
    # URL
    with tab1:
        google_query = st.text_input("🔎 Rechercher sur Google")
        if google_query:
            query_encoded = urllib.parse.quote(google_query)
            google_url = f"https://www.google.com/search?q={query_encoded}"
            st.markdown(f"[🌍 Rechercher sur Google]({google_url})", unsafe_allow_html=True)
        url_input = st.text_input("Collez l'URL ici")
        if st.button("🔍 Analyser le site"):
            titre, contenu = scrape_url(url_input)
            if titre:
                st.session_state.temp_titre = titre
                st.session_state.temp_contenu = contenu
                st.success("Analyse réussie")
            else: st.error("Aucune donnée trouvée")
        if "temp_titre" in st.session_state:
            t_edit = st.text_input("Titre", st.session_state.temp_titre)
            c_edit = st.text_area("Préparation", st.session_state.temp_contenu, height=250)
            if st.button("💾 Enregistrer URL"):
                send_action({"action":"add","titre":t_edit,"preparation":c_edit,"source":url_input,"date":datetime.now().strftime("%d/%m/%Y")})
                del st.session_state.temp_titre
                st.success("Recette ajoutée !")
    # Vidéo
    with tab2:
        vid_url = st.text_input("Lien vidéo (Insta/TikTok/FB)")
        vid_titre = st.text_input("Nom de la recette")
        if st.button("🚀 Sauvegarder Vidéo"):
            if vid_url and vid_titre:
                send_action({"action":"add","titre":vid_titre,"preparation":f"Vidéo : {vid_url}","source":vid_url,"date":datetime.now().strftime("%d/%m/%Y")})
                st.success("Vidéo enregistrée !")
    # Vrac
    with tab3:
        v_t = st.text_input("Titre")
        v_cat = st.selectbox("Catégorie",CATEGORIES)
        v_txt = st.text_area("Texte / Ingrédients")
        if st.button("💾 Enregistrer Vrac"):
            if v_t:
                send_action({"action":"add","titre":v_t,"catégorie":v_cat,"ingredients":v_txt,"date":datetime.now().strftime("%d/%m/%Y")})
                st.success("Recette ajoutée !")

# --- PAGE EPICERIE ---
elif st.session_state.page=="shop":
    st.header("🛒 Ma Liste d'épicerie")
    if st.button("⬅ Retour"): st.session_state.page="home"; st.rerun()
    try:
        df_shop=pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        if df_shop.empty: st.info("Liste vide")
        else:
            sel=[]
            for idx,row in df_shop.iterrows():
                if st.checkbox(str(row.iloc[0]), key=f"shop_{idx}"): sel.append(str(row.iloc[0]))
            c1,c2=st.columns(2)
            if c1.button("🗑 Retirer sélection"):
                for it in sel: send_action({"action":"remove_shop","article":it})
                st.rerun()
            if c2.button("🧨 Vider liste"):
                send_action({"action":"clear_shop"}); st.rerun()
    except: st.error("Erreur chargement liste")

# --- PAGE PLANNING ---
elif st.session_state.page=="planning":
    st.header("📅 Planning Repas")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'].astype(str).str.strip()!=""].sort_values(by='Date_Prevue')
        for _,row in plan.iterrows():
            with st.expander(f"📌 {row['Date_Prevue']} : {row['Titre']}"):
                if st.button("Voir la fiche", key=f"plan_{row['Titre']}"):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"
                    st.rerun()
    if st.button("⬅ Retour"): st.session_state.page="home"; st.rerun()

# --- PAGE PLAYSTORE ---
elif st.session_state.page=="playstore":
    st.markdown("""
    <div class="playstore-container">
        <img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" class="logo-rond-centre">
        <h1>Mes Recettes Pro</h1>
        <p><b>👩‍🍳 Isabelle Latrémouille</b></p>
        <p>⭐ 4.9 (128 avis) | 📥 1 000+ téléchargements</p>
    </div>
    """, unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    c1.image("https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg", caption="Bibliothèque")
    c2.image("https://i.postimg.cc/YCkg460C/shared-image-(5).jpg", caption="Détails recette")
    c3.image("https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg", caption="Épicerie")
    if st.button("📥 Installer l'application", use_container_width=True): st.success("Installée ! 🎉")

# --- PAGE AIDE ---
elif st.session_state.page=="help":
    st.header("❓ Aide & Astuces")
    if st.button("⬅ Retour"): st.session_state.page="home"; st.rerun()
    st.markdown('<div class="help-box"><h3>📝 Ajouter Recette</h3><p>Onglets URL, Vidéo ou Vrac pour ajouter vos recettes.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="help-box"><h3>📅 Planning Repas</h3><p>Planifiez vos recettes facilement et ouvrez les détails.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="help-box"><h3>🛒 Liste d\'épicerie</h3><p>Cochez les ingrédients pour les envoyer ici. Supprimez ou videz la liste facilement.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="help-box"><h3>🌐 Liens Utiles</h3><p>Google Sheet Recettes : {0}<br>Épicerie : {1}<br>Script : {2}</p></div>'.format(URL_CSV, URL_CSV_SHOP, URL_SCRIPT), unsafe_allow_html=True)
