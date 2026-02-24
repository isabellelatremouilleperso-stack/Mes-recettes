import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 1. CONFIGURATION ET DESIGN
st.set_page_config(page_title="Livre de Recettes", layout="wide")

st.markdown("""
    <style>
    /* Uniformisation des cartes et images */
    [data-testid="stImage"] img {
        object-fit: cover;
        height: 200px !important;
        width: 100% !important;
        border-radius: 10px 10px 0 0;
    }
    .recipe-title {
        height: 70px; 
        overflow: hidden;
        font-weight: bold;
    }
    /* Style pour la barre d'action rapide */
    .stButton button {
        border-radius: 20px;
    }
    .stApp { color: white; }
    </style>
    """, unsafe_allow_html=True)

# Liens
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# 2. MÉMOIRE
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "bought_items" not in st.session_state: st.session_state.bought_items = {}

# 3. BARRE LATÉRALE
with st.sidebar:
    st.title("👩‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", key="side_bib", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("🛒 Ma Liste d'épicerie", key="side_shop", use_container_width=True):
        st.session_state.page = "shopping"
        st.rerun()
    st.write("---")
    st.metric("Articles à acheter", len(st.session_state.shopping_list))

# 4. BARRE D'ACTION SUPÉRIEURE (Quick Access)
col_t1, col_t2 = st.columns([4, 1])
with col_t1:
    st.title("📖 Mon Livre de Recettes")
with col_t2:
    st.write("") # Espacement
    if st.button("➕ Nouvelle Recette", type="primary", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()

st.write("---")

# 5. LOGIQUE DES PAGES
if st.session_state.page == "ajouter":
    st.subheader("🚀 Ajout Rapide")
    with st.form("add_fast"):
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            t = st.text_input("Nom du plat (ex: Lasagnes)")
            d = st.date_input("Date prévue", datetime.now())
            img = st.text_input("Lien de l'image (URL)")
        with col_f2:
            ing = st.text_area("Ingrédients (Collez votre liste ici)", height=150)
        
        pre = st.text_area("Étapes de préparation")
        
        submitted = st.form_submit_button("💾 Enregistrer dans mon livre")
        if submitted:
            if t and ing:
                data = {"titre":t, "date":d.strftime("%d/%m/%Y"), "image":img, "ingredients":ing, "preparation":pre}
                requests.post(URL_SCRIPT, json=data)
                st.success(f"🎉 '{t}' a été ajouté !")
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("Le titre et les ingrédients sont obligatoires.")

elif st.session_state.page == "details" and st.session_state.recipe_data:
    res = st.session_state.recipe_data
    if st.button("⬅️ Retour"):
        st.session_state.page = "home"
        st.rerun()
    st.header(f"🍳 {res['Titre']}")
    # ... (reste du code détails identique) ...
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("🛒 Ingrédients")
        ings = str(res['Ingrédients']).split('\n')
        for i in ings:
            if i.strip():
                if st.checkbox(i.strip(), key=f"det_{i}"):
                    if i.strip() not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(i.strip())
    with col2:
        st.image(str(res['Image']))
        st.info(res['Préparation'])

elif st.session_state.page == "shopping":
    st.title("🛒 Liste d'Épicerie")
    # ... (reste du code shopping identique) ...
    if st.button("🗑️ Vider tout"):
        st.session_state.shopping_list = []
        st.rerun()
    for item in st.session_state.shopping_list:
        st.checkbox(item)

else: # ACCUEIL
    try:
        df = pd.read_csv(URL_CSV).dropna(subset=['Titre'])
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
        
        # Champ de recherche rapide
        search = st.text_input("🔍 Rechercher une recette...", "")
        if search:
            df = df[df['Titre'].str.contains(search, case=False)]

        cols = st.columns(3)
        for idx, row in df.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    img_url = str(row['Image']) if str(row['Image']).startswith("http") else "https://via.placeholder.com/200"
                    st.image(img_url)
                    st.markdown(f'<div class="recipe-title">{row["Titre"]}</div>', unsafe_allow_html=True)
                    st.caption(f"📅 {row['Date']}")
                    if st.button("Voir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    except:
        st.info("Ajoutez votre première recette !")
