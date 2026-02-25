import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup

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

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS TECHNIQUES
# ======================================================
def send_action(payload):
    with st.spinner("🚀 Action en cours..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear(); time.sleep(1); return True
            st.error(f"Erreur script : {r.text}")
        except Exception as e: st.error(f"Erreur connexion : {e}")
    return False

def scrape_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "Recette Importée"
        elements = soup.find_all(['li', 'p'])
        content_list = []
        for el in elements:
            txt = el.text.strip()
            if 10 < len(txt) < 500: content_list.append(txt)
        return title, "\n".join(dict.fromkeys(content_list))
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
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}

# ======================================================
# 3. SIDEBAR
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning Repas", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Ma Liste", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER / IMPORT / VRAC", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): st.session_state.page = "help"; st.rerun()

# ======================================================
# 4. PAGES
# ======================================================

# --- ACCUEIL ---
if st.session_state.page == "home":
    st.header("📚 Bibliothèque")
    df = load_data()
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("🔍 Rechercher", placeholder="Ex: Poulet")
    cat_f = c2.selectbox("Catégorie", CATEGORIES)
    
    if not df.empty:
        filtered = df.copy()
        if search: filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": filtered = filtered[filtered['Catégorie'] == cat_f]
        
        rows = filtered.reset_index(drop=True)
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><div class="recipe-title">{row["Titre"]}</div></div>', unsafe_allow_html=True)
                        if st.button("Voir la recette", key=f"btn_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    c_back, c_edit, c_del = st.columns([4, 1, 1])
    if c_back.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    if c_edit.button("✏️"): st.session_state.page = "edit"; st.rerun()
    if c_del.button("🗑️"):
        if send_action({"action": "delete", "titre": r['Titre']}): st.session_state.page = "home"; st.rerun()

    st.title(f"🍳 {r['Titre']}")
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        
        # ⭐ SYSTEME D'ÉTOILES ULTRA STABLE
        st.subheader("⭐ Avis & Évaluation")
        comm_brut = str(r.get("Commentaires", ""))
        note_init = 5
        if "Note:" in comm_brut:
            try:
                note_init = int(comm_brut.split("Note:")[1].split("/5")[0].strip())
            except: note_init = 5
        
        note = st.radio("Note :", [1,2,3,4,5], horizontal=True, index=[1,2,3,4,5].index(note_init if note_init in [1,2,3,4,5] else 5), key=f"n_{r['Titre']}")
        comm_texte = comm_brut.split("|",1)[1].strip() if "|" in comm_brut else comm_brut
        txt_comm = st.text_area("Notes :", value=comm_texte, key=f"txt_{r['Titre']}")

        if st.button("💾 Enregistrer la note"):
            if send_action({"action": "update_notes", "titre": r["Titre"], "commentaires": f"Note: {note}/5 | {txt_comm}"}):
                st.success("Note sauvegardée !"); st.rerun()

    with col_r:
        st.subheader("🗓 Planning & Agenda")
        date_plan = st.text_input("Date JJ/MM/AAAA", value=r.get('Date_Prevue', ''))
        ca, cb = st.columns(2)
        if ca.button("📅 Planning Interne"):
            send_action({"action": "update_notes", "titre": r['Titre'], "date_prevue": date_plan}); st.rerun()
        if cb.button("🗓 Google Calendar"):
            send_action({"action": "calendar", "titre": r['Titre'], "date_prevue": date_plan, "ingredients": r['Ingrédients']})

        st.divider()
        st.subheader("🛒 Ingrédients")
        ing_list = [i.strip() for i in str(r['Ingrédients']).split("\n") if i.strip()]
        for i, item in enumerate(ing_list):
            c_i, c_b = st.columns([0.8, 0.2])
            c_i.write(item)
            if c_b.button("➕", key=f"add_sh_{i}"):
                send_action({"action": "add_shop", "article": item}); st.toast("Ajouté !")
        
        st.divider()
        st.subheader("📝 Instructions")
        st.write(r['Préparation'])

# --- AJOUTER / IMPORT & VRAC RÉUNIS ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    t1, t2 = st.tabs(["🪄 Import & Vrac", "📝 Manuel"])
    
    with t1:
        url_in = st.text_input("Lien de la recette (Optionnel pour auto-remplissage)")
        if st.button("🪄 Extraire du Web"):
            title, content = scrape_url(url_in)
            if title:
                st.session_state.temp_title, st.session_state.temp_content = title, content
                st.success("Extraction réussie !")
        
        with st.form("vrac_form"):
            v_t = st.text_input("Titre *", value=st.session_state.get('temp_title', ''))
            v_cat = st.selectbox("Catégorie", CATEGORIES[1:])
            v_c = st.text_area("Bloc Vrac (Copiez-collez tout ici)", value=st.session_state.get('temp_content', ''), height=250)
            if st.form_submit_button("🚀 Enregistrer"):
                if v_t and v_c:
                    payload = {"action": "add", "titre": v_t, "categorie": v_cat, "ingredients": v_c, "preparation": "Tri manuel requis", "date": datetime.now().strftime("%d/%m/%Y")}
                    if send_action(payload): 
                        st.session_state.temp_title = ""; st.session_state.temp_content = ""
                        st.session_state.page = "home"; st.rerun()

    with t2:
        with st.form("manuel_form"):
            m_t = st.text_input("Titre *")
            m_ing = st.text_area("Ingrédients (un par ligne)")
            m_pre = st.text_area("Préparation")
            if st.form_submit_button("💾 Sauver Manuel"):
                if m_t:
                    send_action({"action": "add", "titre": m_t, "ingredients": m_ing, "preparation": m_pre, "date": datetime.now().strftime("%d/%m/%Y")})
                    st.session_state.page = "home"; st.rerun()

# --- ÉDITION ---
elif st.session_state.page == "edit":
    r = st.session_state.recipe_data
    st.header(f"✏️ Modifier : {r['Titre']}")
    with st.form("edit_form"):
        new_t = st.text_input("Titre", value=r['Titre'])
        new_cat = st.selectbox("Catégorie", CATEGORIES[1:], index=CATEGORIES[1:].index(r['Catégorie']) if r['Catégorie'] in CATEGORIES else 0)
        new_ing = st.text_area("Ingrédients", value=r['Ingrédients'], height=200)
        new_pre = st.text_area("Préparation", value=r['Préparation'], height=200)
        new_img = st.text_input("URL Image", value=r['Image'])
        if st.form_submit_button("💾 Mettre à jour"):
            if send_action({"action": "delete", "titre": r['Titre']}):
                payload = {"action": "add", "titre": new_t, "categorie": new_cat, "ingredients": new_ing, "preparation": new_pre, "image": new_img, "date": r['Date']}
                if send_action(payload): st.session_state.page = "home"; st.rerun()

# --- ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste")
    if st.button("🗑 Tout effacer"): send_action({"action": "clear_shop"}); st.rerun()
    try:
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}")
        for idx, row in df_s.iterrows():
            item = row.iloc[0]
            if pd.isna(item) or str(item).lower() in ['nan', 'article']: continue
            ca, cb = st.columns([0.8, 0.2])
            ca.write(f"⬜ {item}")
            if cb.button("❌", key=f"del_{idx}"):
                send_action({"action": "remove_item_shop", "article": item}); st.rerun()
    except: st.info("Liste vide.")

# --- PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ''].copy()
        for _, row in plan.iterrows():
            st.info(f"🗓 **{row['Date_Prevue']}** : {row['Titre']}")

# --- AIDE ---
elif st.session_state.page == "help":
    st.title("❓ Aide")
    st.write("Gestion de recettes v2.0 - Stable")
