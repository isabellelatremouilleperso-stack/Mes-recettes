import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION & STYLE (Look Tablette)
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
[data-testid="stImage"] img {
    object-fit: cover;
    height: 250px !important;
    width: 100% !important;
    border-radius: 20px;
}
.recipe-title { font-weight: 700; font-size: 1.2rem; margin-top: 10px; }
.cat-badge { 
    background: linear-gradient(90deg,#ff9800,#ff5722); 
    color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; 
}
.stCheckbox { font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

# --- Remplace par tes vrais liens ---
URL_CSV = "TON_URL_CSV"
URL_SCRIPT = "TON_URL_SCRIPT"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# ======================================================
# CHARGEMENT DES DONNÉES
# ======================================================
@st.cache_data(ttl=600)
def load_data():
    try:
        return pd.read_csv(URL_CSV).fillna('')
    except:
        return pd.DataFrame()

if "page" not in st.session_state: st.session_state.page = "home"
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# ======================================================
# BARRE LATÉRALE
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Menu")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("➕ Ajouter", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page = "shopping"; st.rerun()
    st.write("---")
    st.write(f"🛒 Liste : {len(st.session_state.shopping_list)} articles")

# ======================================================
# PAGE : BIBLIOTHÈQUE
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if not df.empty:
        c1, c2 = st.columns(2)
        search = c1.text_input("🔍 Rechercher")
        cat_f = c2.selectbox("Catégorie", CATEGORIES)

        if search: df = df[df['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": df = df[df['Catégorie'] == cat_f]

        grid = st.columns(3)
        for idx, row in df.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                    st.image(img, use_container_width=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()

# ======================================================
# PAGE : DÉTAILS
# ======================================================
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

    st.header(f"🍳 {r['Titre']}")
    
    colA, colB = st.columns([1, 1.2])

    with colA:
        # --- Étoiles et Statut ---
        note = st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        fait = st.checkbox("✅ J'ai testé cette recette", value=False)
        
        # --- Liens Sociaux ---
        source_url = str(r.get('Source', ''))
        if "instagram.com" in source_url: st.info("📸 Trouvé sur Instagram")
        elif "tiktok.com" in source_url: st.info("🎵 Trouvé sur TikTok")
        elif "facebook.com" in source_url: st.info("💙 Trouvé sur Facebook")
        elif "http" in source_url: st.link_button("🔗 Voir le lien original", source_url)

        st.write("---")
        st.subheader("🛒 Ingrédients")
        temp_items = []
        for i, item in enumerate(str(r['Ingrédients']).split("\n")):
            if item.strip() and st.checkbox(item.strip(), key=f"ing_{i}"):
                temp_items.append(item.strip())
        
        if st.button("➕ Ajouter à l'épicerie", use_container_width=True):
            for it in temp_items:
                if it not in st.session_state.shopping_list: st.session_state.shopping_list.append(it)
            st.toast("Articles ajoutés !")

    with colB:
        img = r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/600"
        st.image(img, use_container_width=True)
        
        # --- Section Impression ---
        with st.expander("🖨️ Préparer pour l'impression"):
            layout_print = f"""RECETTE : {r['Titre']}
Note : {note} {'(TESTÉ ✅)' if fait else ''}
-------------------------------------
INGRÉDIENTS :
{r['Ingrédients']}

PRÉPARATION :
{r['Préparation']}

MES NOTES :
{r.get('Commentaires', 'Aucune')}"""
            st.text_area("Copiez ce texte :", layout_print, height=200)

        st.write("### 📝 Préparation")
        st.write(r['Préparation'])
        if r.get('Commentaires'):
            st.warning(f"**Mes Notes :** {r['Commentaires']}")

    st.write("---")
    if st.button("✏ Modifier la recette", use_container_width=True):
        st.session_state.page = "edit"; st.rerun()

# ======================================================
# PAGE : AJOUTER / MODIFIER
# ======================================================
elif st.session_state.page in ["add", "edit"]:
    is_edit = st.session_state.page == "edit"
    r = st.session_state.recipe_data if is_edit else {}
    st.header("✏ Modifier" if is_edit else "➕ Ajouter")
    
    with st.form("form_add"):
        t = st.text_input("Titre", r.get('Titre',''))
        cat = st.selectbox("Catégorie", CATEGORIES[1:], index=CATEGORIES[1:].index(r.get('Catégorie','Poulet')) if is_edit else 0)
        src = st.text_input("Lien Source (Instagram, TikTok...)", r.get('Source',''))
        img = st.text_input("URL Image", r.get('Image',''))
        ing = st.text_area("Ingrédients (un par ligne)", r.get('Ingrédients',''))
        pre = st.text_area("Préparation", r.get('Préparation',''))
        not_ = st.text_area("Notes & Commentaires", r.get('Commentaires',''))

        if st.form_submit_button("💾 Enregistrer"):
            payload = {
                "action": "update" if is_edit else "add",
                "titre_original": r.get('Titre','') if is_edit else "",
                "titre": t, "source": src, "ingredients": ing, "preparation": pre,
                "categorie": cat, "commentaires": not_, "image": img,
                "date": datetime.now().strftime("%d/%m/%Y")
            }
            requests.post(URL_SCRIPT, json=payload)
            st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : ÉPICERIE
# ======================================================
elif st.session_state.page == "shopping":
    st.header("🛒 Liste d'épicerie")
    if st.button("🚫 Vider"): st.session_state.shopping_list = []; st.rerun()
    for idx, item in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([4,1])
        c1.write(f"• {item}")
        if c2.button("❌", key=f"del_{idx}"):
            st.session_state.shopping_list.pop(idx); st.rerun()
