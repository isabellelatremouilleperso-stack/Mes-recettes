import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.parse

# ======================
# CONFIGURATION & DESIGN
# ======================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
.stApp { background-color: #0e1117; color: #e0e0e0; }
h1,h2,h3 { color: #e67e22 !important; }

/* Sidebar */
[data-testid="stSidebar"] { background-color: #1e2129; color: white; }
.stButton button { background-color: #e67e22; color: white; }

/* Inputs */
input, select, textarea, div[data-baseweb="select"] { color: white !important; background-color: #1e2129 !important; }

/* Checklist */
.stCheckbox label p { color: white !important; font-size: 1.1rem !important; font-weight: 500 !important; }

/* Recipe cards */
.recipe-card { background-color:#1e2129;border:1px solid #3d4455;border-radius:12px;padding:10px;height:230px; display:flex;flex-direction:column; justify-content:space-between;}
.recipe-img { width:100%; height:130px; object-fit:cover; border-radius:8px; }
.recipe-title { color:white; margin-top:8px; font-size:0.95rem; font-weight:bold; text-align:center; display:flex; align-items:center; justify-content:center; height:2.5em; line-height:1.2; }

/* Help boxes */
.help-box { background-color:#1e2130; padding:15px; border-radius:15px; border-left:5px solid #e67e22; margin-bottom:20px; }
.help-box h3 { color:#e67e22; margin-top:0; }

/* Playstore */
.playstore-container { display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; width:100%; margin-bottom:20px; }
.logo-rond-centre { width:120px !important; height:120px !important; border-radius:50% !important; object-fit:cover; border:4px solid #e67e22; margin-bottom:15px; }
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
        # 1. Lecture du flux CSV
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}")
        
        # 2. Nettoyage basique
        df = df.fillna('')
        
        # 3. On s'assure que les noms de colonnes dans le code correspondent 
        # à ceux de votre tableur (on enlève les espaces pour éviter les bugs)
        df.columns = [c.strip() for c in df.columns]
        
        return df
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        return pd.DataFrame()
        
# --- UTILISATION DE LA FONCTION ---
df = load_data()
st.write("DEBUG: lignes chargées:", len(df))
st.write(df.head(5))

# ======================
# SESSION
# ======================
if "page" not in st.session_state: st.session_state.page="home"

# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.image("https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png", width=100)
    st.title("🍳 Mes Recettes")
    if st.button("📚 Bibliothèque",use_container_width=True,key="side_home"): st.session_state.page="home"; st.rerun()
    if st.button("📅 Planning Repas",use_container_width=True,key="side_plan"): st.session_state.page="planning"; st.rerun()
    if st.button("🛒 Ma Liste d'épicerie",use_container_width=True,key="side_shop"): st.session_state.page="shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER RECETTE",use_container_width=True,key="side_add"): st.session_state.page="add"; st.rerun()
    if st.button("⭐ Play Store",use_container_width=True,key="side_play"): st.session_state.page="playstore"; st.rerun()
    if st.button("❓ Aide",use_container_width=True,key="side_help"): st.session_state.page="help"; st.rerun()

# ======================
# PAGES
# ======================

# --- PAGE ACCUEIL / BIBLIOTHEQUE ---
if st.session_state.page == "home":
    c1,c2 = st.columns([4,1])
    c1.header("📚 Ma Bibliothèque")
    if c2.button("🔄 Actualiser"): st.cache_data.clear(); st.rerun()

    st.divider()
    df = load_data()
    if not df.empty:
        col_search,col_cat = st.columns([2,1])
        with col_search:
            search = st.text_input("🔍 Rechercher...", placeholder="Ex: Lasagne...")
        with col_cat:
            liste_categories = ["Toutes"] + sorted([str(c) for c in df['Catégorie'].unique() if c])
            cat_choisie = st.selectbox("📁 Catégorie", liste_categories)
        
        mask = df['Titre'].str.contains(search, case=False, na=False)
        if cat_choisie != "Toutes":
            mask = mask & (df['Catégorie']==cat_choisie)
        
        rows = df[mask].reset_index(drop=True)
        for i in range(0,len(rows),3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(rows):
                    row = rows.iloc[i+j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f"""
                        <div class="recipe-card">
                            <img src="{img}" class="recipe-img">
                            <div class="recipe-title">{row['Titre']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Voir la recette", key=f"v_{i+j}", use_container_width=True):
                            st.session_state.recipe_data=row.to_dict()
                            st.session_state.page="details"
                            st.rerun()
    else:
        st.warning("Aucune donnée trouvée.")

# --- PAGE DÉTAILS ---
elif st.session_state.page=="details":
    r = st.session_state.recipe_data
    c_nav1,c_nav2,c_nav3 = st.columns([1.5,1,1])
    if c_nav1.button("⬅ Retour"): st.session_state.page="home"; st.rerun()
    if c_nav2.button("✏️ Éditer"): st.session_state.page="add"; st.rerun()
    if c_nav3.button("🗑️ Supprimer"): 
        if send_action({"action":"delete","titre":r['Titre']}):
            st.session_state.page="home"; st.rerun()

    st.divider()
    st.header(f"📖 {r.get('Titre','Sans titre')}")
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
        st.markdown("---")
        st.subheader("📋 Informations")
        st.write(f"**🍴 Catégorie :** {r.get('Catégorie','Non classé')}")
        st.write(f"**👥 Portions :** {r.get('Portions','-')}")
        st.write(f"**⏱ Préparation :** {r.get('Temps_Prepa','-')} min")
        st.write(f"**🔥 Cuisson :** {r.get('Temps_Cuisson','-')} min")
        if r.get('Source') and "http" in str(r.get('Source')):
            st.link_button("🌐 Voir la source", r['Source'], use_container_width=True)
    with col_d:
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
elif st.session_state.page=="add":
    st.header("➕ Ajouter une Recette")
    tab1,tab2,tab3 = st.tabs(["🌐 Site Web (Auto)","🎬 Lien Vidéo","📝 Vrac / Manuel"])
    with tab1:
        url_input = st.text_input("Collez l'URL du site",key="url_auto")
        if st.button("🔍 Analyser le site"):
            titre, contenu = scrape_url(url_input)
            if titre: st.session_state.temp_titre=titre; st.session_state.temp_contenu=contenu; st.rerun()
        if "temp_titre" in st.session_state:
            t_edit = st.text_input("Titre extrait", value=st.session_state.temp_titre)
            c_edit = st.text_area("Contenu extrait", value=st.session_state.temp_contenu,height=250)
            if st.button("💾 Enregistrer import"):
                send_action({"action":"add","titre":t_edit,"preparation":c_edit,"source":url_input,"date":datetime.now().strftime("%d/%m/%Y")})
                del st.session_state.temp_titre; st.session_state.page="home"; st.rerun()
    with tab2:
        s_url = st.text_input("Lien vidéo (Insta/TikTok/FB)",key="vid_url")
        s_t = st.text_input("Nom de la recette",key="vid_titre")
        if st.button("🚀 Sauvegarder Vidéo"):
            if s_url and s_t:
                send_action({"action":"add","titre":s_t,"source":s_url,"preparation":f"Vidéo : {s_url}","date":datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page="home"; st.rerun()
    # Dans l'onglet "Vrac / Manuel"
# --- FIN DE LA PAGE AJOUTER ---
with tab3:
        with st.form("form_vrac"):
            v_t = st.text_input("Titre *")
            v_cat = st.selectbox("Catégorie", CATEGORIES)
            v_date = st.date_input("Planifier pour le (optionnel)", value=None)
            v_txt = st.text_area("Texte brut", height=300)
            submit_vrac = st.form_submit_button("💾 Enregistrer la recette")
            
            if submit_vrac:
                if v_t:
                    payload = {
                        "action": "add",
                        "titre": v_t,
                        "catégorie": v_cat,
                        "ingredients": v_txt,
                        "date": datetime.now().strftime("%d/%m/%Y"),
                        "date_prevue": v_date.strftime("%d/%m/%Y") if v_date else ""
                    }
                    send_action(payload)
                    st.session_state.page = "home"
                    st.rerun()
                else:
                    st.error("Titre obligatoire.")

# --- PAGE ÉPICERIE (BIEN ALIGNÉE À GAUCHE) ---
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

# --- PAGE PLANNING (BIEN ALIGNÉE À GAUCHE) ---
elif st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data()
    if not df.empty:
        # On s'assure que la colonne Date_Prevue existe
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

# --- PAGE PLAYSTORE & AIDE (RESTE DU CODE) ---
elif st.session_state.page == "playstore":
    st.markdown("### 📥 Installer l'application", unsafe_allow_html=True)
    if st.button("Retour à la Bibliothèque"): 
        st.session_state.page = "home"
        st.rerun()

elif st.session_state.page == "help":
    st.header("❓ Aide")
    if st.button("Retour à la Bibliothèque"): 
        st.session_state.page = "home"
        st.rerun()

   
