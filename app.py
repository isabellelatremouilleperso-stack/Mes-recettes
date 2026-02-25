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
</style>
""", unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS
# ======================================================
def send_action(payload):
    with st.spinner("🚀 Action..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear(); time.sleep(1); return True
            st.error(f"Erreur : {r.text}")
        except Exception as e: st.error(f"Erreur connexion : {e}")
    return False

def scrape_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "Recette"
        elements = soup.find_all(['li', 'p'])
        content = "\n".join(dict.fromkeys([el.text.strip() for el in elements if 10 < len(el.text.strip()) < 500]))
        return title, content
    except: return None, None

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        return df
    except: return pd.DataFrame()

if "page" not in st.session_state: st.session_state.page = "home"

# ======================================================
# 3. SIDEBAR
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Menu")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Liste", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUT / IMPORT", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): st.session_state.page = "help"; st.rerun()
    
    st.divider()
    st.subheader("🌐 Trouver une idée")
    search_q = st.text_input("Chercher sur Google :", placeholder="ex: Poulet coco")
    if search_q:
        link = f"https://www.google.com/search?q={urllib.parse.quote('recette ' + search_q)}"
        st.link_button("🔍 Lancer la recherche", link, use_container_width=True)

# ======================================================
# 4. PAGES
# ======================================================

# --- ACCUEIL ---
if st.session_state.page == "home":
    st.header("📚 Mes Recettes")
    df = load_data()
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("🔍 Filtrer")
    cat_f = c2.selectbox("Catégorie", CATEGORIES)
    
    if not df.empty:
        filtered = df.copy()
        if search: filtered = filtered[filtered.iloc[:,1].str.contains(search, case=False)]
        if cat_f != "Toutes": filtered = filtered[filtered.iloc[:,7] == cat_f]
        
        rows = filtered.reset_index(drop=True)
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    with cols[j]:
                        img = row.iloc[6] if "http" in str(row.iloc[6]) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><div class="recipe-title">{row.iloc[1]}</div></div>', unsafe_allow_html=True)
                        if st.button("Voir", key=f"v_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = list(st.session_state.recipe_data.values())
    c_back, c_edit, c_del = st.columns([4, 1, 1])
    if c_back.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    if c_edit.button("✏️"): st.session_state.page = "edit"; st.rerun()
    
    st.title(f"🍳 {r[1]}")
    col_l, col_r = st.columns([1, 1.2])
    
    with col_l:
        st.image(r[6] if "http" in str(r[6]) else "https://via.placeholder.com/400")
        st.subheader("⭐ Note")
        comm_brut = str(r[11])
        note_init = 5
        if "Note:" in comm_brut:
            try: note_init = int(comm_brut.split("Note:")[1].split("/5")[0].strip())
            except: pass
        note = st.radio("Note :", [1,2,3,4,5], horizontal=True, index=[1,2,3,4,5].index(note_init if note_init in [1,2,3,4,5] else 5), key="note_rd")
        comm_texte = comm_brut.split("|",1)[1].strip() if "|" in comm_brut else comm_brut
        txt_comm = st.text_area("Notes :", value=comm_texte)
        if st.button("💾 Sauver la note"):
            send_action({"action": "update_notes", "titre": r[1], "commentaires": f"Note: {note}/5 | {txt_comm}"})
            st.rerun()

    with col_r:
        st.subheader("📅 Planning")
        date_p = st.text_input("Date (JJ/MM/AAAA)", value=str(r[5]))
        c_plan, c_goog = st.columns(2)
        if c_plan.button("📅 Planning Interne", use_container_width=True):
            send_action({"action": "update_notes", "titre": r[1], "date_prevue": date_p}); st.rerun()
        
        # BOUTON ORANGE
        if c_goog.button("🗓 Google Calendar", type="primary", use_container_width=True):
            send_action({"action": "calendar", "titre": r[1], "date_prevue": date_p, "ingredients": r[3]})

        st.divider()
        st.subheader("🛒 Ingrédients")
        for i, item in enumerate(str(r[3]).split("\n")):
            if item.strip():
                ci, cb = st.columns([0.8, 0.2])
                ci.write(f"• {item}")
                if cb.button("➕", key=f"sh_{i}"):
                    send_action({"action": "add_shop", "article": item}); st.toast("Ajouté !")

# --- AJOUTER (IMPORT + VRAC RÉUNIS) ---
elif st.session_state.page == "add":
    st.header("➕ Import URL & Vrac")
    url_in = st.text_input("🔗 Lien URL")
    if st.button("🪄 Extraire"):
        t, c = scrape_url(url_in)
        if t:
            st.session_state.temp_t, st.session_state.temp_c = t, c
            st.success("Extraction réussie !")

    st.divider()
    with st.form("f_vrac"):
        v_t = st.text_input("Titre *", value=st.session_state.get('temp_t', ''))
        v_cat = st.selectbox("Catégorie", CATEGORIES[1:])
        v_txt = st.text_area("Vrac (Ingrédients et Étapes)", value=st.session_state.get('temp_c', ''), height=300)
        if st.form_submit_button("🚀 ENREGISTRER"):
            if v_t and v_txt:
                send_action({"action": "add", "titre": v_t, "categorie": v_cat, "ingredients": v_txt, "preparation": "Tri manuel", "date": datetime.now().strftime("%d/%m/%Y")})
                st.session_state.page = "home"; st.rerun()

# --- ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Liste de courses")
    if st.button("🗑 Tout effacer"): send_action({"action": "clear_shop"}); st.rerun()
    try:
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}")
        for idx, row in df_s.iterrows():
            ca, cb = st.columns([0.8, 0.2])
            ca.write(f"⬜ {row.iloc[0]}")
            if cb.button("❌", key=f"d_{idx}"):
                send_action({"action": "remove_item_shop", "article": row.iloc[0]}); st.rerun()
    except: st.write("Vide.")

# --- AIDE ---
elif st.session_state.page == "help":
    st.title("❓ Aide & Utilisation")
    st.info("**Astuce :** Pour les notes, le système enregistre au format `Note: X/5 | Commentaire`. Ne modifiez pas cette structure manuellement pour garder le système stable !")
    st.markdown("""
    1. **Ajouter une recette :** Utilisez l'onglet "Import & Vrac". Vous pouvez coller une URL ou simplement un bloc de texte.
    2. **Planning :** Entrez une date au format JJ/MM/AAAA. Le bouton **Orange** envoie vers votre agenda Google.
    3. **Courses :** Cliquez sur le `+` à côté d'un ingrédient pour l'envoyer dans votre liste.
    4. **Recherche :** Utilisez la barre latérale pour chercher de nouvelles idées sur Google.
    """)
