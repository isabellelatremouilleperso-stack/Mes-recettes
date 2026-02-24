import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION & STYLE
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
.recipe-title { font-weight: 700; font-size: 1.2rem; margin-top: 10px; min-height: 50px; }
.cat-badge { 
    background: linear-gradient(90deg,#ff9800,#ff5722); 
    color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; 
}
</style>
""", unsafe_allow_html=True)

# --- URL CONFIG ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# ======================================================
# DATA LOAD
# ======================================================
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except:
        return pd.DataFrame()

if "page" not in st.session_state: st.session_state.page = "home"
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Menu")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("➕ Ajouter", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page = "shopping"; st.rerun()
    st.write("---")
    if st.button("❓ Aide & Tuto", use_container_width=True): st.session_state.page = "aide"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()

# ======================================================
# HOME
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if df.empty:
        st.warning("⚠️ Aucune recette trouvée.")
    else:
        c1, c2 = st.columns(2)
        search = c1.text_input("🔍 Rechercher")
        cat_f = c2.selectbox("Catégorie", CATEGORIES)

        filtered = df.copy()
        if search: filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": filtered = filtered[filtered['Catégorie'] == cat_f]

        grid = st.columns(3)
        for idx, row in filtered.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    img = str(row['Image']) if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                    st.image(img, use_container_width=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()

# ======================================================
# DETAILS
# ======================================================
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

    st.header(f"🍳 {r['Titre']}")
    colA, colB = st.columns([1, 1.2])

    with colA:
        note = st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        source_url = str(r.get('Source', ''))
        if "http" in source_url: st.link_button("🔗 Voir l'original", source_url)

        st.subheader("🛒 Ingrédients")
        temp = []
        for i, it in enumerate(str(r['Ingrédients']).split("\n")):
            if it.strip() and st.checkbox(it.strip(), key=f"i_{i}"): temp.append(it.strip())
        
        if st.button("➕ Ajouter à l'épicerie", use_container_width=True):
            for item in temp:
                if item not in st.session_state.shopping_list: st.session_state.shopping_list.append(item)
            st.toast("✅ Ajouté !")

    with colB:
        img = str(r['Image']) if "http" in str(r['Image']) else "https://via.placeholder.com/600"
        st.image(img, use_container_width=True)
        with st.expander("🖨️ Version Texte (Imprimer)"):
            st.text_area("Copier :", f"RECETTE : {r['Titre']}\n\n{r['Ingrédients']}\n\n{r['Préparation']}", height=150)
        st.write("### 📝 Préparation")
        st.write(r['Préparation'])

# ======================================================
# AJOUTER / MODIFIER
# ======================================================
elif st.session_state.page in ["add", "edit"]:
    st.header("➕ Nouvelle Recette")
    with st.form("add_form"):
        t = st.text_input("Titre")
        c = st.selectbox("Catégorie", CATEGORIES[1:])
        s = st.text_input("Lien Source")
        i = st.text_input("URL Image")
        ing = st.text_area("Ingrédients")
        pre = st.text_area("Préparation")
        if st.form_submit_button("💾 Sauvegarder"):
            requests.post(URL_SCRIPT, json={"action":"add","titre":t,"source":s,"ingredients":ing,"preparation":pre,"categorie":c,"image":i,"date":datetime.now().strftime("%d/%m/%Y")})
            st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# ÉPICERIE
# ======================================================
elif st.session_state.page == "shopping":
    st.header("🛒 Mon Épicerie")
    if st.button("Vider tout"): st.session_state.shopping_list = []; st.rerun()
    for idx, item in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([4,1])
        c1.write(f"• {item}")
        if c2.button("❌", key=f"d_{idx}"): st.session_state.shopping_list.pop(idx); st.rerun()

# ======================================================
# PAGE AIDE (RÉINTÉGRÉE)
# ======================================================
elif st.session_state.page == "aide":
    st.header("❓ Aide & Tutoriel")
    
    with st.container(border=True):
        st.subheader("🚀 Guide de démarrage rapide")
        st.write("""
        1. **Ajouter une recette** : Cliquez sur le bouton **Ajouter** dans le menu. Remplissez le titre, les ingrédients et surtout collez un lien d'image.
        2. **Gérer l'épicerie** : Dans une recette, cochez les ingrédients que vous n'avez pas, puis cliquez sur 'Ajouter à l'épicerie'.
        3. **Synchroniser** : Si vous modifiez votre Google Sheet à la main, cliquez sur **Actualiser** dans l'application.
        """)
        
    st.info("💡 **Astuce Tablette** : Pour imprimer, ouvrez la section 'Version Texte' dans une recette, copiez le contenu, et utilisez la fonction de partage de votre appareil.")

    if st.button("⬅ Retour à la bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
