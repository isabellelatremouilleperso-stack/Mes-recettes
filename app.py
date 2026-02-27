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
.stApp {
background-color: #0e1117; color: #e0e0e0; }
h1,h2,h3 {
color: #e67e22 !important; }

/* Sidebar */
[data-testid="stSidebar"]
{ background-color: #1e2129; color: white; }
.stButton
button { background-color: #e67e22; color: white; }

/* Inputs */
input,
select, textarea, div[data-baseweb="select"] { color: white
!important; background-color: #1e2129 !important; }

/* Checklist */
.stCheckbox
label p { color: white !important; font-size: 1.1rem !important; font-weight:
500 !important; }

/* Recipe cards */
.recipe-card
{ background-color:#1e2129;border:1px solid
#3d4455;border-radius:12px;padding:10px;height:230px;
display:flex;flex-direction:column; justify-content:space-between;}
.recipe-img
{ width:100%; height:130px; object-fit:cover; border-radius:8px; }
.recipe-title
{ color:white; margin-top:8px; font-size:0.95rem; font-weight:bold;
text-align:center; display:flex; align-items:center; justify-content:center;
height:2.5em; line-height:1.2; }

/* Help boxes */
.help-box {
background-color:#1e2130; padding:15px; border-radius:15px; border-left:5px
solid #e67e22; margin-bottom:20px; }
.help-box
h3 { color:#e67e22; margin-top:0; }

/* Playstore */
.playstore-container
{ display:flex; flex-direction:column; align-items:center;
justify-content:center; text-align:center; width:100%; margin-bottom:20px; }
.logo-rond-centre
{ width:120px !important; height:120px !important; border-radius:50%
!important; object-fit:cover; border:4px solid #e67e22; margin-bottom:15px; }
</style>
""",
unsafe_allow_html=True)

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
        st.markdown(f"""<a href="javascript:window.print()" target="_self" style="text-decoration: none;"><div style="background-color: #e67e22; color: white; height: 38px; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-size: 14px; font-weight: bold; border: 2px solid #d35400;">🖨️ Imprimer</div></a>""", unsafe_allow_html=True)
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
    c_btn.markdown(f"""<a href="{target_url}" target="_blank" style="text-decoration: none;"><div style="background-color: #4285F4; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight
