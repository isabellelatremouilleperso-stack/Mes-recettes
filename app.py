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
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }
    .recipe-card {
        background-color: #1e2129; border: 1px solid #3d4455;
        border-radius: 12px; padding: 10px; height: 230px; 
        display: flex; flex-direction: column;
    }
    .recipe-img { width: 100%; height: 130px; object-fit: cover; border-radius: 8px; }
    .recipe-title {
        color: white; margin-top: 8px; font-size: 0.9rem; font-weight: bold;
        display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
        overflow: hidden; height: 2.6em; line-height: 1.3;
    }
    header {visibility: hidden;} .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS
# ======================================================
def send_action(payload):
    with st.spinner("🚀 Action..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear(); time.sleep(1); return True
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
        cols = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires']
        if len(df.columns) >= len(cols): df.columns = cols[:len(df.columns)]
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
    if st.button("🛒 Ma Liste", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER RECETTE", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): st.session_state.page = "help"; st.rerun()
    
    st.divider()
    st.subheader("🔍 Trouver sur Google")
    q_google = st.text_input("Recette à chercher :")
    if q_google:
        link = f"https://www.google.com/search?q={urllib.parse.quote('recette ' + q_google)}"
        st.link_button("🌐 Aller sur Google", link, use_container_width=True)

# ======================================================
# 4. PAGES
# ======================================================

# --- ACCUEIL ---
if st.session_state.page == "home":
    st.header("📚 Bibliothèque")
    df = load_data()
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("🔍 Rechercher")
    cat_f = c2.selectbox("Filtrer par catégorie", ["Toutes"] + CATEGORIES)
    
    if not df.empty:
        filtered = df.copy()
        if search: filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": filtered = filtered[filtered['Catégorie'].str.contains(cat_f, case=False)]
        
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
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

# --- AJOUTER RECETTE ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    tab1, tab2, tab3 = st.tabs(["🔗 Import URL", "📝 Vrac", "⌨️ Manuel"])
    
    with tab1:
        url_in = st.text_input("Lien de la recette (ex: Marmiton)")
        if st.button("🪄 Extraire et Sauver"):
            t, c = scrape_url(url_in)
            if t:
                send_action({"action": "add", "titre": t, "ingredients": c, "preparation": "Import URL", "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

    with tab2:
        with st.form("vrac_form"):
            v_t = st.text_input("Titre *")
            v_cats = st.multiselect("Catégories", CATEGORIES)
            v_txt = st.text_area("Bloc texte (ingrédients et étapes)", height=250)
            if st.form_submit_button("🚀 Sauver Vrac"):
                if v_t:
                    send_action({"action": "add", "titre": v_t, "categorie": ", ".join(v_cats), "ingredients": v_txt, "preparation": "Vrac", "date": datetime.now().strftime("%d/%m/%Y")})
                    st.session_state.page = "home"; st.rerun()

    with tab3:
        with st.form("manuel_form"):
            m_t = st.text_input("Titre de la recette *")
            m_cats = st.multiselect("Catégories", CATEGORIES)
            
            c1, c2, c3 = st.columns(3)
            m_por = c1.text_input("Portions", placeholder="ex: 4")
            m_prepa = c2.text_input("Temps Prépa", placeholder="ex: 15 min")
            m_cuis = c3.text_input("Temps Cuisson", placeholder="ex: 30 min")
            
            m_ing = st.text_area("Ingrédients (un par ligne)")
            m_pre = st.text_area("Préparation / Étapes")
            m_img = st.text_input("URL de l'image (optionnel)")
            
            if st.form_submit_button("💾 Sauver Manuel"):
                if m_t:
                    send_action({
                        "action": "add", 
                        "titre": m_t, 
                        "categorie": ", ".join(m_cats), 
                        "ingredients": m_ing, 
                        "preparation": m_pre, 
                        "portions": m_por,
                        "temps_prepa": m_prepa,
                        "temps_cuisson": m_cuis,
                        "image": m_img,
                        "date": datetime.now().strftime("%d/%m/%Y")
                    })
                    st.session_state.page = "home"; st.rerun()

# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    st.title(f"🍳 {r['Titre']}")
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        if r.get('Portions'): st.write(f"👥 **Portions :** {r['Portions']}")
        if r.get('Temps_Prepa'): st.write(f"⏳ **Préparation :** {r['Temps_Prepa']}")
        if r.get('Temps_Cuisson'): st.write(f"🔥 **Cuisson :** {r['Temps_Cuisson']}")
        
    with col_r:
        st.subheader("📅 Planning")
        date_p = st.text_input("Date JJ/MM/AAAA", value=r.get('Date_Prevue', ''))
        c_p1, c_p2 = st.columns(2)
        if c_p1.button("📅 Planning Interne", use_container_width=True):
            send_action({"action": "update_notes", "titre": r['Titre'], "date_prevue": date_p}); st.rerun()
        
        if c_p2.button("🗓 Google Calendar", type="primary", use_container_width=True):
            send_action({"action": "calendar", "titre": r['Titre'], "date_prevue": date_p, "ingredients": r['Ingrédients']})

        st.divider()
        st.write("**Catégories :**", r.get('Catégorie', 'Non classé'))
        st.write("**Ingrédients :**")
        st.write(r['Ingrédients'])
        st.divider()
        st.write("**Préparation :**")
        st.write(r['Préparation'])

# --- AUTRES PAGES ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste")
    # ... (code shop)
elif st.session_state.page == "planning":
    st.header("📅 Planning")
    # ... (code planning)
elif st.session_state.page == "help":
    st.title("❓ Aide")
    st.write("L'onglet Manuel vous permet maintenant de saisir précisément le temps et de choisir plusieurs catégories.")
