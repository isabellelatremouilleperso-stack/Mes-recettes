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
    .source-btn {
        background-color: #3d4455; color: white; text-align: center; 
        padding: 10px; border-radius: 8px; font-weight: bold; 
        margin-bottom: 15px; text-decoration: none; display: block;
    }
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
@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires']
        if len(df.columns) >= len(expected): df.columns = expected[:len(df.columns)]
        return df
    except: return pd.DataFrame()

def send_action(payload):
    with st.spinner("📦 Synchronisation..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.cache_data.clear(); time.sleep(1.5); return True
            st.error(f"Erreur : {r.text}")
        except Exception as e: st.error(f"Erreur : {e}")
    return False

def scrape_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('h1').text.strip() if soup.find('h1') else "Recette Importée"
        # Extraction plus large pour attraper ingrédients ET préparation
        items = [li.text.strip() for li in soup.find_all(['li', 'p']) if 5 < len(li.text.strip()) < 500]
        return title, "\n".join(items)
    except: return None, None

if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}

# ======================================================
# 3. BARRE LATÉRALE
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.divider()
    if st.button("➕ Ajouter / Import", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()

# ======================================================
# 4. LOGIQUE DES PAGES
# ======================================================

# --- ACCUEIL ---
if st.session_state.page == "home":
    st.header("📚 Bibliothèque")
    df = load_data()
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("🔍 Rechercher", placeholder="Ex: Lasagnes")
    cat_f = c2.selectbox("Filtrer", CATEGORIES)
    if not df.empty:
        filtered = df.copy()
        if search: filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": filtered = filtered[filtered['Catégorie'].str.contains(cat_f, case=False, na=False)]
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

# --- DÉTAILS (AVEC ÉTOILES RÉINTÉGRÉES) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    c_back, c_edit, c_del = st.columns([4, 1, 1])
    if c_back.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    if c_edit.button("✏️"): st.session_state.page = "edit"; st.rerun()
    if c_del.button("🗑️"): st.session_state.confirm_delete = True

    if st.session_state.get('confirm_delete', False):
        if st.button("✅ Confirmer Suppr."):
            if send_action({"action": "delete", "titre": r['Titre']}): st.session_state.page = "home"; st.rerun()
        if st.button("❌ Annuler"): st.session_state.confirm_delete = False; st.rerun()

    st.title(f"🍳 {r['Titre']}")
    st.info(f"Portions : {r.get('Portions', '?')} | Prépa : {r.get('Temps_Prepa', '?')} | Cuisson : {r.get('Temps_Cuisson', '?')}")
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        img_url = r.get('Image', '')
        st.image(img_url if "http" in str(img_url) else "https://via.placeholder.com/400")
        if str(r.get('Source', '')).startswith("http"):
            st.markdown(f'<a href="{r["Source"]}" target="_blank" class="source-btn">🔗 Ouvrir le lien </a>', unsafe_allow_html=True)
        
        # --- SECTION AVIS RÉINTÉGRÉE ---
        st.subheader("⭐ Avis & Notes")
        comm_actuel = str(r.get('Commentaires', ''))
        note = st.feedback("stars", key=f"note_{r['Titre']}")
        txt_comm = st.text_area("Notes personnelles :", value=comm_actuel.split(" | ")[1] if " | " in comm_actuel else comm_actuel)
        if st.button("💾 Sauver l'avis"):
            val_note = note + 1 if note is not None else 0
            valeur_finale = f"Note: {val_note}/5 | {txt_comm}"
            if send_action({"action":"update_notes", "titre": r['Titre'], "commentaires": valeur_finale}):
                st.toast("Avis enregistré !"); time.sleep(1); st.rerun()

    with col_r:
        st.subheader("🛒 Ingrédients")
        ing_brut = r.get('Ingrédients', '')
        if ing_brut:
            ing_list = str(ing_brut).split("\n")
            temp_to_add = []
            for i, item in enumerate(ing_list):
                if item.strip() and st.checkbox(item.strip(), key=f"ing_{i}"):
                    temp_to_add.append(item.strip())
            if st.button("➕ Ajouter à l'épicerie"):
                for s in temp_to_add: send_action({"action": "add_shop", "article": s})
                st.toast("Ajouté !")
        st.divider()
        st.subheader("📝 Préparation")
        st.write(r.get('Préparation', 'Aucune instruction.'))

# --- ÉDITION ---
elif st.session_state.page == "edit":
    r = st.session_state.recipe_data
    st.header(f"✏️ Modifier : {r['Titre']}")
    with st.form("edit_form"):
        new_t = st.text_input("Titre", value=r['Titre'])
        new_ing = st.text_area("Ingrédients", value=r['Ingrédients'], height=200)
        new_pre = st.text_area("Préparation", value=r['Préparation'], height=200)
        new_img = st.text_input("URL Image", value=r['Image'])
        if st.form_submit_button("💾 Enregistrer les modifications"):
            if send_action({"action": "delete", "titre": r['Titre']}):
                new_payload = {"action": "add", "titre": new_t, "ingredients": new_ing, "preparation": new_pre, "image": new_img, "date": r['Date']}
                if send_action(new_payload): st.session_state.page = "home"; st.rerun()

# --- AJOUTER / IMPORT (AVEC AIDE GOOGLE RÉTABLIE) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    
    # BOUTON GOOGLE ORANGE BIEN VISIBLE
    st.markdown("""
        <a href="https://www.google.com/search?q=recette" target="_blank" style="text-decoration:none;">
            <div style="background-color:#e67e22; color:white; text-align:center; padding:15px; border-radius:10px; font-weight:bold; margin-bottom:20px; font-size:1.1rem;">
                🔍 Cliquer ici pour chercher sur Google
            </div>
        </a>
    """, unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🪄 Import URL", "⚡ Saisie Vrac", "📝 Manuel"])
    
    with t1:
        url_input = st.text_input("Lien de la recette (Marmiton, etc.)")
        if st.button("🪄 Extraire les informations"):
            title, content = scrape_url(url_input)
            if title:
                st.success(f"✅ Trouvé : {title}")
                st.session_state.temp_title = title
                st.session_state.temp_content = content
                st.info("Passez maintenant à l'onglet 'Saisie Vrac' pour valider.")
            else: st.error("Extraction impossible. Copiez-collez manuellement dans 'Saisie Vrac'.")

    with t2:
        with st.form("vrac_form"):
            v_t = st.text_input("Titre", value=st.session_state.get('temp_title', ''))
            v_c = st.text_area("Tout le contenu collé", value=st.session_state.get('temp_content', ''), height=300)
            v_cat = st.selectbox("Catégorie", CATEGORIES[1:])
            if st.form_submit_button("🚀 Enregistrement Rapide"):
                if v_t and v_c:
                    payload = {"action": "add", "titre": v_t, "categorie": v_cat, "ingredients": v_c, "preparation": "Tri à faire via l'édition", "date": datetime.now().strftime("%d/%m/%Y")}
                    if send_action(payload): st.session_state.page = "home"; st.rerun()

    with t3:
        with st.form("manuel_form"):
            m_t = st.text_input("Titre *")
            m_cat = st.selectbox("Catégorie", CATEGORIES[1:])
            m_ing = st.text_area("Ingrédients *")
            m_pre = st.text_area("Préparation")
            if st.form_submit_button("💾 Sauver Manuel"):
                if m_t and m_ing:
                    payload = {"action": "add", "titre": m_t, "categorie": m_cat, "ingredients": m_ing, "preparation": m_pre, "date": datetime.now().strftime("%d/%m/%Y")}
                    if send_action(payload): st.session_state.page = "home"; st.rerun()

# --- ÉPICERIE & PLANNING (GARDÉS TEL QUEL) ---
elif st.session_state.page == "shop":
    st.header("🛒 Épicerie")
    if st.button("🗑 Tout vider"):
        if send_action({"action": "clear_shop"}): st.rerun()
    try:
        df_shop = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}")
        for idx, row in df_shop.iterrows():
            item = row.iloc[0]
            if pd.isna(item) or str(item).lower() in ['nan', 'article']: continue
            ca, cb = st.columns([0.8, 0.2])
            ca.write(f"⬜ **{item}**")
            if cb.button("❌", key=f"del_{idx}"):
                if send_action({"action": "remove_item_shop", "article": item}): st.rerun()
    except: st.info("Liste vide.")

elif st.session_state.page == "planning":
    st.header("📅 Agenda")
    df = load_data()
    if not df.empty:
        df['Date_Prevue'] = df['Date_Prevue'].astype(str).str.strip()
        plan = df[(df['Date_Prevue'] != '') & (df['Date_Prevue'] != 'nan')].copy()
        if not plan.empty:
            plan['dt_obj'] = pd.to_datetime(plan['Date_Prevue'], format='%d/%m/%Y', errors='coerce')
            plan = plan.sort_values('dt_obj')
            for _, row in plan.iterrows():
                st.markdown(f'<div style="background-color:#1e2129; border-left:5px solid #e67e22; padding:15px; border-radius:10px; margin-bottom:10px;"><span style="color:#e67e22;"><b>🗓 {row["Date_Prevue"]}</b></span><br><span style="font-size:1.2rem; color:white;">{row["Titre"]}</span></div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                if c1.button("📖 Voir", key=f"pv_{row['Titre']}", use_container_width=True):
                    st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
                if c2.button("✅ Terminé", key=f"pd_{row['Titre']}", use_container_width=True):
                    send_action({"action": "update", "titre_original": row['Titre'], "date_prevue": ""}); st.rerun()
        else: st.info("Rien de prévu.")
