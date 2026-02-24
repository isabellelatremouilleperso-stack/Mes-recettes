import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION & STYLE (Optimisé Tablette)
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
.stCheckbox { font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# CONNEXION GOOGLE SHEETS (TES LIENS)
# ======================================================
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# ======================================================
# GESTION DES DONNÉES
# ======================================================
@st.cache_data(ttl=60) # Rafraîchissement toutes les minutes
def load_data():
    try:
        # Lecture du CSV
        df = pd.read_csv(URL_CSV).fillna('')
        
        # Sécurité : Si les colonnes ne sont pas nommées correctement dans le CSV
        # on force les noms pour que le code fonctionne
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except Exception as e:
        st.error(f"Erreur de lecture : {e}")
        return pd.DataFrame()

if "page" not in st.session_state: st.session_state.page = "home"
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None

# ======================================================
# BARRE LATÉRALE
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Menu")
    if st.button("📚 Bibliothèque", use_container_width=True): 
        st.session_state.page = "home"
        st.rerun()
    if st.button("➕ Ajouter", use_container_width=True): 
        st.session_state.page = "add"
        st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): 
        st.session_state.page = "shopping"
        st.rerun()
    st.write("---")
    if st.button("🔄 Actualiser", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# ======================================================
# PAGE : BIBLIOTHÈQUE
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    
    if df.empty:
        st.warning("⚠️ La bibliothèque est vide ou le lien CSV est mort.")
    else:
        c1, c2 = st.columns(2)
        search = c1.text_input("🔍 Rechercher")
        cat_f = c2.selectbox("Catégorie", CATEGORIES)

        filtered_df = df.copy()
        if search: 
            filtered_df = filtered_df[filtered_df['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": 
            filtered_df = filtered_df[filtered_df['Catégorie'] == cat_f]

        grid = st.columns(3)
        for idx, row in filtered_df.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    img_url = str(row['Image']) if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                    st.image(img_url, use_container_width=True)
                    if row['Catégorie']:
                        st.markdown(f"<span class='cat-badge'>{row['Catégorie']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()

# ======================================================
# PAGE : DÉTAILS
# ======================================================
elif st.session_state.page == "details" and st.session_state.recipe_data:
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): 
        st.session_state.page = "home"
        st.rerun()

    st.header(f"🍳 {r['Titre']}")
    
    colA, colB = st.columns([1, 1.2])

    with colA:
        # --- Étoiles et Statut ---
        st.subheader("⭐ Évaluation")
        note = st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
        fait = st.checkbox("✅ J'ai testé cette recette", value=False)
        
        # --- Liens Sociaux ---
        source_url = str(r.get('Source', ''))
        if "instagram.com" in source_url: st.info("📸 Source : Instagram")
        elif "tiktok.com" in source_url: st.info("🎵 Source : TikTok")
        elif "facebook.com" in source_url: st.info("💙 Source : Facebook")
        elif "http" in source_url: st.link_button("🔗 Voir l'original", source_url)

        st.write("---")
        st.subheader("🛒 Ingrédients")
        temp_items = []
        for i, item in enumerate(str(r['Ingrédients']).split("\n")):
            clean_it = item.strip()
            if clean_it and st.checkbox(clean_it, key=f"ing_{i}"):
                temp_items.append(clean_it)
        
        if st.button("➕ Ajouter à l'épicerie", use_container_width=True):
            if temp_items:
                for it in temp_items:
                    if it not in st.session_state.shopping_list: st.session_state.shopping_list.append(it)
                st.toast("✅ Ajouté à la liste !")
            else:
                st.warning("Cochez des ingrédients.")

    with colB:
        img_detail = str(r['Image']) if "http" in str(r['Image']) else "https://via.placeholder.com/600"
        st.image(img_detail, use_container_width=True)
        
        # --- Section Impression ---
        with st.expander("🖨️ Préparer pour l'impression"):
            layout_print = f"RECETTE : {r['Titre']}\nNote : {note}\n{'-'*30}\nINGRÉDIENTS :\n{r['Ingrédients']}\n\nPRÉPARATION :\n{r['Préparation']}\n\nNOTES :\n{r.get('Commentaires', '')}"
            st.text_area("Texte à copier :", layout_print, height=150)

        st.write("### 📝 Préparation")
        st.write(r['Préparation'])
        if r.get('Commentaires'):
            st.warning(f"**Notes :** {r['Commentaires']}")

    st.write("---")
    b1, b2 = st.columns(2)
    if b1.button("✏ Modifier", use_container_width=True):
        st.session_state.page = "edit"; st.rerun()
    if b2.button("🗑 Supprimer", use_container_width=True):
        requests.post(URL_SCRIPT, json={"action": "delete", "titre": r['Titre']})
        st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : AJOUTER / MODIFIER
# ======================================================
elif st.session_state.page in ["add", "edit"]:
    is_edit = st.session_state.page == "edit"
    r = st.session_state.recipe_data if is_edit else {}
    st.header("✏ Modifier" if is_edit else "➕ Ajouter")
    
    with st.form("form_recipe"):
        t = st.text_input("Titre", r.get('Titre',''))
        cat = st.selectbox("Catégorie", CATEGORIES[1:], index=0)
        src = st.text_input("Lien (Insta, TikTok...)", r.get('Source',''))
        img = st.text_input("URL Image", r.get('Image',''))
        ing = st.text_area("Ingrédients", r.get('Ingrédients',''))
        pre = st.text_area("Préparation", r.get('Préparation',''))
        com = st.text_area("Notes", r.get('Commentaires',''))

        if st.form_submit_button("💾 Enregistrer"):
            p = {
                "action": "update" if is_edit else "add",
                "titre_original": r.get('Titre','') if is_edit else "",
                "titre": t, "source": src, "ingredients": ing, "preparation": pre,
                "categorie": cat, "commentaires": com, "image": img,
                "date": datetime.now().strftime("%d/%m/%Y")
            }
            requests.post(URL_SCRIPT, json=p)
            st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : ÉPICERIE
# ======================================================
elif st.session_state.page == "shopping":
    st.header("🛒 Liste d'épicerie")
    if st.button("🚫 Tout vider"): 
        st.session_state.shopping_list = []
        st.rerun()
    
    if not st.session_state.shopping_list:
        st.info("Votre liste est vide.")
    else:
        for idx, item in enumerate(st.session_state.shopping_list):
            c1, c2 = st.columns([4,1])
            c1.write(f"• {item}")
            if c2.button("❌", key=f"del_{idx}"):
                st.session_state.shopping_list.pop(idx)
                st.rerun()
