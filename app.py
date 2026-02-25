import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup

# ======================================================
# 1. CONFIGURATION & DESIGN
# ======================================================
st.set_page_config(page_title="Mes Recettes", layout="wide", page_icon="🍳")

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
    .stButton>button { border-radius: 8px; font-weight: bold; }
    header {visibility: hidden;} .stDeployButton {display:none;}
</style>
""", unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

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
            if 10 < len(txt) < 500:
                content_list.append(txt)
        return title, "\n".join(dict.fromkeys(content_list))
    except:
        return None, None

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires']
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except:
        return pd.DataFrame()

def send_action(payload):
    with st.spinner("📦 Synchronisation..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear(); time.sleep(1); return True
            st.error(f"Erreur : {r.text}")
        except Exception as e:
            st.error(f"Erreur : {e}")
    return False

if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}

# ======================================================
# 3. BARRE LATÉRALE
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True):
        st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True):
        st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True):
        st.session_state.page = "shop"; st.rerun()
    if st.button("❓ Aide", use_container_width=True):
        st.session_state.page = "help"; st.rerun()
    st.divider()
    if st.button("➕ Ajouter / Import", type="primary", use_container_width=True):
        st.session_state.page = "add"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True):
        st.cache_data.clear(); st.rerun()

# ======================================================
# 4. LOGIQUE DES PAGES
# ======================================================

# --- PAGE AIDE ---
if st.session_state.page == "help":
    st.header("❓ Guide complet")
    st.info("Utilisez l'édition (✏️) pour transformer vos imports 'Vrac' en recettes détaillées.")
    if st.button("Retour"):
        st.session_state.page = "home"; st.rerun()

# --- ACCUEIL ---
elif st.session_state.page == "home":
    st.header("📚 Bibliothèque")
    df = load_data()
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("🔍 Rechercher", placeholder="Ex: Lasagnes")
    cat_f = c2.selectbox("Filtrer", CATEGORIES)
    if not df.empty:
        filtered = df.copy()
        if search:
            filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes":
            filtered = filtered[filtered['Catégorie'].str.contains(cat_f, case=False, na=False)]
        rows = filtered.reset_index(drop=True)
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><div class="recipe-title">{row["Titre"]}</div></div>', unsafe_allow_html=True)
                        if st.button("Ouvrir", key=f"btn_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

# --- DÉTAILS ---
# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    c_back, c_edit, c_del = st.columns([4, 1, 1])
    if c_back.button("⬅ Retour"):
        st.session_state.page = "home"; st.rerun()
    if c_edit.button("✏️"):
        st.session_state.page = "edit"; st.rerun()
    if c_del.button("🗑️"):
        st.session_state.confirm_delete = True

    if st.session_state.get('confirm_delete', False):
        if st.button("✅ Confirmer Suppr."):
            if send_action({"action": "delete", "titre": r['Titre']}):
                st.session_state.page = "home"; st.rerun()
        if st.button("❌ Annuler"):
            st.session_state.confirm_delete = False; st.rerun()

    st.title(f"🍳 {r['Titre']}")
    st.warning(f"🍽️ {r.get('Portions', '?')} pers. | ⏱️ Prép: {r.get('Temps_Prepa', '?')} | 🔥 Cuisson: {r.get('Temps_Cuisson', '?')}")
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        img_url = r.get('Image', '')
        st.image(img_url if "http" in str(img_url) else "https://via.placeholder.com/400")
        
        st.subheader("⭐ Votre avis")
        comm_brut = str(r.get('Commentaires', ''))
        
        # On extrait la note pour l'afficher proprement en texte
        note_actuelle = "Pas encore noté"
        txt_display = comm_brut
        if "Note: " in comm_brut:
            try:
                note_actuelle = comm_brut.split("Note: ")[1].split("|")[0].strip()
                if "| " in comm_brut:
                    txt_display = comm_brut.split("| ")[1]
            except:
                pass

        st.write(f"**Note actuelle :** {note_actuelle}")
        
        # On retire l'argument par défaut qui fait planter
        # On utilise une clé simple sans caractères spéciaux
        new_note = st.feedback("stars", key=f"fb_{hash(r['Titre'])}")
        
        new_comm = st.text_area("Commentaire :", value=txt_display)
        if st.button("💾 Sauver l'avis"):
            val_note = (new_note + 1) if new_note is not None else 0
            format_avis = f"Note: {val_note}/5 | {new_comm}"
            if send_action({"action":"update_notes", "titre": r['Titre'], "commentaires": format_avis}):
                st.rerun()

    with col_r:
        st.subheader("🛒 Ingrédients")
        ing_brut = r.get('Ingrédients', '')
        if ing_brut:
            ing_list = str(ing_brut).split("\n")
            for i, item in enumerate(ing_list):
                if item.strip():
                    st.checkbox(item.strip(), key=f"ing_{hash(item)}_{i}")
        st.divider()
        st.subheader("📝 Préparation")
        st.write(r.get('Préparation', 'Aucune instruction.'))
        # CORRECTION : On utilise default_value au lieu de defaultValue
        new_note = st.feedback("stars", key=f"star_{r['Titre']}", default_value=default_star)
        new_comm = st.text_area("Commentaire :", value=txt_display)
        if st.button("💾 Sauver l'avis"):
            val_note = (new_note + 1) if new_note is not None else 0
            format_avis = f"Note: {val_note}/5 | {new_comm}"
            if send_action({"action":"update_notes", "titre": r['Titre'], "commentaires": format_avis}):
                st.rerun()

    with col_r:
        st.subheader("🛒 Ingrédients")
        ing_brut = r.get('Ingrédients', '')
        if ing_brut:
            ing_list = str(ing_brut).split("\n")
            for i, item in enumerate(ing_list):
                if item.strip() and st.checkbox(item.strip(), key=f"ing_{i}"):
                    pass
        st.divider()
        st.subheader("📝 Préparation")
        st.write(r.get('Préparation', 'Aucune instruction.'))

# --- AJOUTER ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    t1, t2, t3 = st.tabs(["🪄 Import URL", "⚡ Vrac", "📝 Manuel"])
    with t3:
        with st.form("m_form"):
            m_t = st.text_input("Titre *")
            c_m1, c_m2, c_m3 = st.columns(3)
            m_por = c_m1.text_input("Portions")
            m_pre_t = c_m2.text_input("Temps Prép.")
            m_cui_t = c_m3.text_input("Temps Cuisson")
            m_cat = st.selectbox("Catégorie", CATEGORIES[1:])
            m_ing = st.text_area("Ingrédients *")
            m_pre = st.text_area("Préparation")
            if st.form_submit_button("💾 Sauver"):
                payload = {"action": "add", "titre": m_t, "categorie": m_cat, "ingredients": m_ing, "preparation": m_pre, "portions": m_por, "temps_prepa": m_pre_t, "temps_cuisson": m_cui_t, "date": datetime.now().strftime("%d/%m/%Y")}
                if send_action(payload):
                    st.session_state.page = "home"; st.rerun()

# --- ÉDITION ---
elif st.session_state.page == "edit":
    r = st.session_state.recipe_data
    st.header(f"✏️ Modifier : {r.get('Titre', '')}")
    with st.form("edit_form"):
        new_t = st.text_input("Titre", value=r.get('Titre', ''))
        c_e1, c_e2, c_e3 = st.columns(3)
        new_por = c_e1.text_input("Portions", value=r.get('Portions', ''))
        new_pre_t = c_e2.text_input("Temps Prép.", value=r.get('Temps_Prepa', ''))
        new_cui_t = c_e3.text_input("Temps Cuisson", value=r.get('Temps_Cuisson', ''))
        new_cat = st.selectbox("Catégorie", CATEGORIES[1:], index=CATEGORIES[1:].index(r['Catégorie']) if r.get('Catégorie') in CATEGORIES[1:] else 0)
        new_ing = st.text_area("Ingrédients", value=r.get('Ingrédients', ''), height=150)
        new_pre = st.text_area("Préparation", value=r.get('Préparation', ''), height=150)
        new_img = st.text_input("URL Image", value=r.get('Image', ''))
        new_plan = st.text_input("Date Prévue (JJ/MM/AAAA)", value=r.get('Date_Prevue', ''))
        if st.form_submit_button("💾 Enregistrer"):
            if send_action({"action": "delete", "titre": r['Titre']}):
                payload = {"action": "add", "titre": new_t, "categorie": new_cat, "ingredients": new_ing, "preparation": new_pre, "image": new_img, "portions": new_por, "temps_prepa": new_pre_t, "temps_cuisson": new_cui_t, "date_prevue": new_plan, "date": r.get('Date', '')}
                if send_action(payload):
                    st.session_state.page = "home"; st.rerun()

# --- ÉPICERIE & PLANNING ---
elif st.session_state.page == "shop":
    st.header("🛒 Épicerie")
    if st.button("🗑 Tout vider"):
        send_action({"action": "clear_shop"})
    try:
        df_shop = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}")
        for idx, row in df_shop.iterrows():
            item = row.iloc[0]
            if not pd.isna(item):
                ca, cb = st.columns([0.8, 0.2])
                ca.write(f"⬜ {item}")
                if cb.button("❌", key=f"d_{idx}"):
                    send_action({"action": "remove_item_shop", "article": item})
    except:
        st.info("Vide.")

elif st.session_state.page == "planning":
    st.header("📅 Agenda")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ''].copy()
        for _, row in plan.iterrows():
            st.info(f"🗓 {row['Date_Prevue']} - {row['Titre']}")


