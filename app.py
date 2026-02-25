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

# LIENS GOOGLE (À vérifier s'ils sont toujours corrects dans ton fichier)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# 2. FONCTIONS TECHNIQUES
# ======================================================
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

def send_action(payload):
    with st.spinner("🚀 Action en cours..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear(); time.sleep(1); return True
            st.error(f"Erreur script : {r.text}")
        except Exception as e: st.error(f"Erreur connexion : {e}")
    return False

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
    if st.button("➕ AJOUTER / IMPORT", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): st.session_state.page = "help"; st.rerun()

# ======================================================
# 4. PAGES
# ======================================================

# --- ACCUEIL ---
if st.session_state.page == "home":
    st.header("📚 Bibliothèque")
    df = load_data()
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("🔍 Rechercher", placeholder="Ex: Lasagnes")
    cat_f = c2.selectbox("Filtrer par catégorie", CATEGORIES)
    
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

# --- DÉTAILS (LE COEUR DU SYSTÈME) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    c_back, c_edit, c_del = st.columns([4, 1, 1])
    if c_back.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    if c_edit.button("✏️ Éditer"): st.session_state.page = "edit"; st.rerun()
    if c_del.button("🗑️ Supprimer"):
        if send_action({"action": "delete", "titre": r['Titre']}): st.session_state.page = "home"; st.rerun()

    st.title(f"🍳 {r['Titre']}")
    st.warning(f"🍴 {r.get('Portions', '?')} pers. | 🕒 Prép: {r.get('Temps_Prepa', '?')} | 🔥 Cuisson: {r.get('Temps_Cuisson', '?')}")

    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        
        # --- ÉTOILES & NOTES (CORRECTION TYPEERROR) ---
        st.subheader("⭐ Avis & Étoiles")
        comm_brut = str(r.get('Commentaires', ''))
        note_init = 0
        if "Note: " in comm_brut:
            try:
                extraits = comm_brut.split("Note: ")[1].split("/5")[0]
                note_init = int(extraits) - 1
            except: note_init = 0
        
        note = st.feedback("stars", key=f"note_{r['Titre']}", initial_value=note_init if 0 <= note_init <= 4 else None)
        comm_texte = comm_brut.split(" | ")[1] if " | " in comm_brut else comm_brut
        txt_comm = st.text_area("Notes personnelles :", value=comm_texte)
        
        if st.button("💾 Enregistrer la note"):
            val_note = (note + 1) if note is not None else 0
            if send_action({"action": "update_notes", "titre": r['Titre'], "commentaires": f"Note: {val_note}/5 | {txt_comm}"}):
                st.toast("Note sauvegardée !"); st.rerun()

    with col_r:
        st.subheader("🗓 Planning & Agenda")
        date_plan = st.text_input("Date (JJ/MM/AAAA)", value=r.get('Date_Prevue', ''))
        ca, cb = st.columns(2)
        if ca.button("📅 Dans mon Planning"):
            send_action({"action": "update_notes", "titre": r['Titre'], "date_prevue": date_plan})
        if cb.button("🗓 Google Calendar"):
            send_action({"action": "calendar", "titre": r['Titre'], "date_prevue": date_plan, "ingredients": r['Ingrédients']})

        st.divider()
        st.subheader("🛒 Ingrédients")
        ing_list = [i.strip() for i in str(r['Ingrédients']).split("\n") if i.strip()]
        to_add = []
        for i, item in enumerate(ing_list):
            if st.checkbox(item, key=f"ck_{i}"): to_add.append(item)
        if st.button(f"➕ Ajouter ({len(to_add)}) à l'épicerie"):
            for s in to_add: send_action({"action": "add_shop", "article": s})
            st.toast("C'est dans la liste !")

        st.divider()
        st.subheader("📝 Instructions")
        st.write(r['Préparation'])

# --- AJOUTER / IMPORT (FUSION TABS) ---
elif st.session_state.page == "add":
    st.header("➕ Nouvelle Recette")
    t1, t2 = st.tabs(["🪄 Import Web", "📝 Manuel"])
    
    with t1:
        url_in = st.text_input("Collez un lien de recette ici")
        if st.button("🪄 Extraire les données"):
            title, content = scrape_url(url_in)
            if title:
                st.session_state.temp_title = title
                st.session_state.temp_content = content
                st.success("Extraction réussie !")
        
        with st.form("import_form"):
            v_t = st.text_input("Titre", value=st.session_state.get('temp_title', ''))
            v_c = st.text_area("Contenu (Ingrédients + Prépa)", value=st.session_state.get('temp_content', ''), height=200)
            if st.form_submit_button("🚀 Enregistrer l'import"):
                if v_t and v_c:
                    payload = {"action": "add", "titre": v_t, "ingredients": v_c, "date": datetime.now().strftime("%d/%m/%Y")}
                    if send_action(payload): st.session_state.page = "home"; st.rerun()

    with t2:
        with st.form("manuel_form"):
            m_t = st.text_input("Nom de la recette *")
            m_cat = st.selectbox("Catégorie", CATEGORIES[1:])
            c1, c2, c3 = st.columns(3)
            m_port = c1.text_input("Portions")
            m_prep = c2.text_input("Temps Prép")
            m_cuis = c3.text_input("Temps Cuisson")
            m_ing = st.text_area("Ingrédients (un par ligne) *")
            m_pre = st.text_area("Préparation / Instructions")
            if st.form_submit_button("💾 SAUVEGARDER"):
                if m_t and m_ing:
                    payload = {"action": "add", "titre": m_t, "categorie": m_cat, "portions": m_port, "temps_prepa": m_prep, "temps_cuisson": m_cuis, "ingredients": m_ing, "preparation": m_pre, "date": datetime.now().strftime("%d/%m/%Y")}
                    if send_action(payload): st.session_state.page = "home"; st.rerun()

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
    st.header("🛒 Ma Liste d'Épicerie")
    if st.button("🗑 Tout effacer"):
        send_action({"action": "clear_shop"}); st.rerun()
    try:
        df_s = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}")
        for idx, row in df_s.iterrows():
            item = row.iloc[0]
            if pd.isna(item) or str(item).lower() in ['nan', 'article']: continue
            ca, cb = st.columns([0.8, 0.2])
            ca.write(f"⬜ {item}")
            if cb.button("❌", key=f"del_{idx}"):
                send_action({"action": "remove_item_shop", "article": item}); st.rerun()
    except: st.info("La liste est vide.")

# --- PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning Repas")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ''].copy()
        for _, row in plan.iterrows():
            st.info(f"🗓 **{row['Date_Prevue']}** : {row['Titre']}")
            if st.button("Voir", key=f"v_{row['Titre']}"):
                st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

# --- AIDE ---
elif st.session_state.page == "help":
    st.title("❓ Aide & Support")
    st.write("**Version 2.0 Premium** | Isabelle Latrémouille")
    st.markdown("""
    - **Import :** Utilisez l'onglet 'Import Web' pour gagner du temps.
    - **Étoiles :** Donnez une note pour retrouver vos recettes préférées.
    - **Synchronisation :** Les données sont sauvées en temps réel sur votre Google Sheet.
    """)
