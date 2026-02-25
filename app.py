import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup
import urllib.parse

# ======================================================
# 1. CONFIGURATION & DESIGN (COMPLET + PLACES PHOTOS)
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
    .app-header { display: flex; align-items: center; gap: 20px; margin-bottom: 20px; }
    .playstore-img { border-radius: 15px; border: 2px solid #3d4455; width: 100%; }
    header {visibility: hidden;} .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS (IMPORT URL, ACTIONS, LOAD)
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

# --- PLAY STORE (AVEC PLACES PHOTOS) ---
if st.session_state.page == "playstore":
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/8100/8100851.png", width=100)
    st.markdown("### Mes Recettes Pro\n**Isabelle Latrémouille**\n⭐ 4.9 ★ | 📥 1 000+")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("📥 Installer", use_container_width=True):
        st.success("Application installée ! 🎉")

    st.subheader("📸 Aperçus de l'écran")
    col_img1, col_img2, col_img3 = st.columns(3)
    with col_img1:
        st.image("https://via.placeholder.com/300x600/1e2129/e67e22?text=Bibliothèque+Recettes", caption="Ma Bibliothèque", use_container_width=True)
    with col_img2:
        st.image("https://via.placeholder.com/300x600/1e2129/e67e22?text=Planning+Hebdo", caption="Mon Planning", use_container_width=True)
    with col_img3:
        st.image("https://via.placeholder.com/300x600/1e2129/e67e22?text=Liste+Courses", caption="Ma Liste d'épicerie", use_container_width=True)
    
    st.divider()
    st.subheader("📝 À propos")
    st.write("L'outil ultime pour organiser vos repas, noter vos créations et synchroniser vos courses.")

# --- PLANNING (CORRIGÉ : DÉTECTION LARGE) ---
elif st.session_state.page == "planning":
    st.header("📅 Planning Repas")
    df = load_data()
    if not df.empty:
        # On nettoie et on vérifie si la colonne Date_Prevue a du contenu
        plan = df[df['Date_Prevue'].astype(str).str.strip() != ""]
        if not plan.empty:
            for _, row in plan.iterrows():
                with st.expander(f"📌 {row['Date_Prevue']} : {row['Titre']}"):
                    st.write(f"**Catégorie:** {row['Catégorie']}")
                    if st.button("Voir Fiche", key=f"plan_{row['Titre']}"):
                        st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
        else:
            st.info("Le planning est vide. Ajoutez une date dans les détails d'une recette pour la voir ici.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- BIBLIOTHÈQUE ---
elif st.session_state.page == "home":
    c1, c2 = st.columns([4, 1])
    c1.header("📚 Bibliothèque")
    if c2.button("🔄 Sync"): st.cache_data.clear(); st.rerun()
    df = load_data()
    search = st.text_input("🔍 Rechercher...")
    if not df.empty:
        filtered = df[df['Titre'].str.contains(search, case=False)] if search else df
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

# --- AJOUTER RECETTE (TOUS LES MODES) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter")
    t1, t2, t3 = st.tabs(["🔗 URL", "📝 Vrac", "⌨️ Manuel"])
    with t1:
        u = st.text_input("Lien")
        if st.button("🪄 Importer"):
            tit, con = scrape_url(u)
            if tit: send_action({"action": "add", "titre": tit, "ingredients": con, "preparation": "Import URL", "date": datetime.now().strftime("%d/%m/%Y")}); st.session_state.page = "home"; st.rerun()
    with t2:
        with st.form("v_f"):
            vt = st.text_input("Titre *"); vc = st.multiselect("Cats", CATEGORIES)
            c1, c2, c3 = st.columns(3)
            vp, vpre, vcui = c1.text_input("Portions"), c2.text_input("Prépa"), c3.text_input("Cuisson")
            vtxt = st.text_area("Ingrédients & Étapes")
            if st.form_submit_button("🚀 Sauver"):
                send_action({"action": "add", "titre": vt, "categorie": ", ".join(vc), "ingredients": vtxt, "portions": vp, "temps_prepa": vpre, "temps_cuisson": vcui, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()
    with t3:
        with st.form("m_f"):
            mt = st.text_input("Titre *"); mc = st.multiselect("Cats", CATEGORIES)
            c1, c2, c3 = st.columns(3)
            mp, mpre, mcui = c1.text_input("Portions"), c2.text_input("Prépa"), c3.text_input("Cuisson")
            mi, mpr, mim = st.text_area("Ingrédients"), st.text_area("Étapes"), st.text_input("URL Image")
            if st.form_submit_button("💾 Sauver"):
                send_action({"action": "add", "titre": mt, "categorie": ", ".join(mc), "ingredients": mi, "preparation": mpr, "portions": mp, "temps_prepa": mpre, "temps_cuisson": mcui, "image": mim, "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

# --- DÉTAILS (NOTES, ÉTOILES, COMMENTAIRES) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    st.title(f"🍳 {r['Titre']}")
    try: nv = int(float(r.get('Note', 0)))
    except: nv = 0
    st.write("⭐" * nv + "☆" * (5 - nv))
    c1, c2 = st.columns([1, 1.2])
    with c1:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        new_n = st.selectbox("Ma Note", [1,2,3,4,5], index=(nv-1 if 1<=nv<=5 else 4))
        new_c = st.text_area("Commentaires", value=r.get('Commentaires', ''))
        new_d = st.text_input("Date Planning (JJ/MM/AAAA)", value=r.get('Date_Prevue', ''))
        if st.button("💾 Enregistrer"):
            send_action({"action": "update_notes", "titre": r['Titre'], "date_prevue": new_d, "commentaires": new_c, "note": new_n})
            st.rerun()
    with c2:
        st.subheader("🛒 Ingrédients"); ings = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip()]
        sel = []
        for i, l in enumerate(ings):
            if st.checkbox(l, key=f"d_{i}"): sel.append(l)
        if st.button("📥 Ajouter à l'épicerie"):
            for x in sel: send_action({"action": "add_shop", "article": x})
            st.success("Ajouté !")
        st.divider(); st.subheader("📝 Étapes"); st.write(r['Préparation'])
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# --- ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Épicerie")
    try:
        ds = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}").fillna('')
        to_d = []
        for ix, rw in ds.iterrows():
            if st.checkbox(rw.iloc[0], key=f"s_{ix}"): to_d.append(rw.iloc[0])
        if st.button("🗑 Retirer"):
            for it in to_d: send_action({"action": "remove_shop", "article": it})
            st.rerun()
    except: st.info("Vide.")

# --- AIDE (RESTAURÉE) ---
elif st.session_state.page == "help":
    st.title("❓ Aide")
    st.write("1. **Sync** : Bouton 🔄 pour charger les nouveautés du Sheets.")
    st.write("2. **Planning** : Mettez une date dans la fiche recette.")
    st.write("3. **Épicerie** : Cochez pour ajouter ou retirer.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
