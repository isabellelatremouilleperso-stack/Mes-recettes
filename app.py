import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

# Style pour forcer les images à avoir la même taille (200px de haut)
st.markdown("""
    <style>
    [data-testid="stImage"] img { 
        object-fit: cover; 
        height: 200px !important; 
        width: 100% !important; 
        border-radius: 10px; 
    }
    .recipe-title { 
        height: 50px; 
        overflow: hidden; 
        font-weight: bold; 
        font-size: 1.1em; 
        margin-top: 5px;
    }
    .cat-badge { 
        background-color: #ffca28; 
        color: #000; 
        padding: 2px 10px; 
        border-radius: 12px; 
        font-size: 0.8em; 
        font-weight: bold; 
    }
    </style>
    """, unsafe_allow_html=True)

# Tes liens
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes", "Poulet", "Bœuf", "Porc", "Poisson", "Pâtes", "Riz", "Soupe", "Salade", "Entrée", "Plat Principal", "Accompagnement", "Dessert", "Petit-déjeuner", "Autre"]

# ======================================================
# CHARGEMENT & CACHE
# ======================================================
@st.cache_data(ttl=600)
def load_data():
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        return df
    except:
        return pd.DataFrame()

# Initialisation
if "page" not in st.session_state: st.session_state.page = "home"
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# ======================================================
# BARRE LATÉRALE
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Mes Recettes PRO")
    if st.button("📚 Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("➕ Ajouter", type="primary", use_container_width=True):
        st.session_state.page = "add"
        st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True):
        st.session_state.page = "shopping"
        st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.write("---")
    if st.button("❓ Aide & Tuto", use_container_width=True):
        st.session_state.page = "aide"
        st.rerun()

# ======================================================
# BIBLIOTHÈQUE (HOME)
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    
    if not df.empty:
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) == 9: df.columns = expected
        elif len(df.columns) == 8:
            df.columns = expected[:-1]
            df['Commentaires'] = ""

        c1, c2 = st.columns(2)
        search = c1.text_input("🔍 Rechercher")
        cat_filter = c2.selectbox("Filtrer", CATEGORIES)
        
        if search: df = df[df['Titre'].str.contains(search, case=False)]
        if cat_filter != "Toutes": df = df[df['Catégorie'] == cat_filter]

        grid = st.columns(3)
        for idx, row in df.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/200"
                    st.image(img, use_container_width=True)
                    if row['Catégorie']:
                        st.markdown(f"<span class='cat-badge'>{row['Catégorie']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()

# ======================================================
# DETAILS
# ======================================================
elif st.session_state.page == "details" and st.session_state.recipe_data:
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): 
        st.session_state.page = "home"
        st.rerun()
    
    st.header(f"🍳 {r['Titre']}")
    colA, colB = st.columns([1, 1.2])
    with colA:
        st.subheader("🛒 Ingrédients")
        for item in str(r['Ingrédients']).split("\n"):
            if item.strip() and st.checkbox(item.strip(), key=f"chk_{item}"):
                if item.strip() not in st.session_state.shopping_list:
                    st.session_state.shopping_list.append(item.strip())
        
        st.write("---")
        st.subheader("📅 Planification")
        st.write(f"Prévu pour le : **{r['Date_Prevue']}**")
        if st.button("📅 Ajouter au Calendrier Google", use_container_width=True):
            try:
                requests.post(URL_SCRIPT, json={"action": "calendar", "titre": r['Titre'], "date_prevue": r['Date_Prevue'], "ingredients": r['Ingrédients']})
                st.success("C'est dans l'agenda !")
            except: st.error("Lien calendrier KO.")

    with colB:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        st.info(f"**Notes :** {r.get('Commentaires', '...')}")
        st.write(f"**Préparation :**\n\n{r['Préparation']}")
    
    st.write("---")
    b1, b2 = st.columns(2)
    if b1.button("✏ Modifier", use_container_width=True): st.session_state.page = "edit"; st.rerun()
    if b2.button("🗑 Supprimer", use_container_width=True):
        requests.post(URL_SCRIPT, json={"action": "delete", "titre": r['Titre']})
        st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# ADD / EDIT
# ======================================================
elif st.session_state.page in ["add", "edit"]:
    is_edit = st.session_state.page == "edit"
    r = st.session_state.recipe_data if is_edit else {}
    st.header("✏ Modifier" if is_edit else "➕ Ajouter")
    with st.form("f"):
        t = st.text_input("Titre", r.get('Titre', ''))
        c = st.selectbox("Catégorie", CATEGORIES[1:])
        i = st.text_input("Image URL", r.get('Image', ''))
        d = st.date_input("Date prévue")
        ing = st.text_area("Ingrédients", r.get('Ingrédients', ''))
        pre = st.text_area("Préparation", r.get('Préparation', ''))
        com = st.text_area("Notes / Commentaires", r.get('Commentaires', ''))
        if st.form_submit_button("Enregistrer"):
            p = {"action": "update" if is_edit else "add", "titre_original": r.get('Titre', ''), "titre": t, "ingredients": ing, "preparation": pre, "categorie": c, "commentaires": com, "image": i, "date": datetime.now().strftime("%d/%m/%Y"), "date_prevue": d.strftime("%d/%m/%Y")}
            requests.post(URL_SCRIPT, json=p)
            st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# SHOPPING
# ======================================================
elif st.session_state.page == "shopping":
    st.header("🛒 Liste d'épicerie")
    if st.button("🚫 Vider"): st.session_state.shopping_list = []; st.rerun()
    for idx, it in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([4,1])
        c1.write(f"- {it}")
        if c2.button("❌", key=f"s_{idx}"): st.session_state.shopping_list.pop(idx); st.rerun()

# ======================================================
# AIDE
# ======================================================
elif st.session_state.page == "aide":
    st.header("📖 Aide")
    st.write("1. **Image** : Utilisez des liens (URL) d'images trouvées sur le web.")
    st.write("2. **Calendrier** : Appuyez sur le bouton dans une recette pour l'ajouter à votre agenda Google.")
    st.write("3. **Notes** : Vos commentaires s'affichent en bleu dans les détails de la recette.")
