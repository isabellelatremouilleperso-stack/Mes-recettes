import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION (Garde tes liens ici)
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes", "Poulet", "Bœuf", "Porc", "Poisson", "Pâtes", "Riz", "Soupe", "Salade", "Entrée", "Plat Principal", "Accompagnement", "Dessert", "Petit-déjeuner", "Autre"]

# ======================================================
# CHARGEMENT DES DONNÉES
# ======================================================
@st.cache_data(ttl=600)
def load_data():
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        return df
    except:
        return pd.DataFrame()

# ======================================================
# INITIALISATION DES VARIABLES (Évite les AttributeError)
# ======================================================
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "checked_items" not in st.session_state: st.session_state.checked_items = []

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
# PAGE : BIBLIOTHÈQUE
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    
    if not df.empty:
        # Normalisation des colonnes
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) == 9: df.columns = expected
        elif len(df.columns) == 8:
            df.columns = expected[:-1]
            df['Commentaires'] = ""

        c1, c2 = st.columns(2)
        search = c1.text_input("🔍 Rechercher par titre")
        cat_filter = c2.selectbox("Filtrer par catégorie", CATEGORIES)
        
        if search: df = df[df['Titre'].str.contains(search, case=False)]
        if cat_filter != "Toutes": df = df[df['Catégorie'] == cat_filter]

        grid = st.columns(3)
        for idx, row in df.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/200"
                    st.image(img, use_container_width=True)
                    st.markdown(f"**{row['Titre']}**")
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()
    else:
        st.warning("Impossible de charger les données. Vérifiez votre URL_CSV.")

# ======================================================
# PAGE : DÉTAILS DE LA RECETTE
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
            item_clean = item.strip()
            if item_clean:
                if st.checkbox(item_clean, key=f"chk_{item_clean}"):
                    if item_clean not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(item_clean)
        
        st.write("---")
        st.subheader("📅 Calendrier")
        st.write(f"Date prévue : {r['Date_Prevue']}")
        if st.button("📅 Mettre à mon agenda Google", use_container_width=True):
            try:
                requests.post(URL_SCRIPT, json={"action": "calendar", "titre": r['Titre'], "date_prevue": r['Date_Prevue'], "ingredients": r['Ingrédients']})
                st.success("Ajouté à l'agenda !")
            except: st.error("Erreur de connexion au calendrier.")

    with colB:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        st.info(f"**Mes Notes :** {r.get('Commentaires', 'Aucune note.')}")
        st.write(f"**Préparation :**\n\n{r['Préparation']}")
    
    st.write("---")
    b1, b2 = st.columns(2)
    if b1.button("✏ Modifier la recette", use_container_width=True):
        st.session_state.page = "edit"
        st.rerun()
    if b2.button("🗑 Supprimer la recette", use_container_width=True):
        requests.post(URL_SCRIPT, json={"action": "delete", "titre": r['Titre']})
        st.cache_data.clear()
        st.session_state.page = "home"
        st.rerun()

# ======================================================
# PAGES : AJOUTER / MODIFIER
# ======================================================
elif st.session_state.page in ["add", "edit"]:
    is_edit = st.session_state.page == "edit"
    r = st.session_state.recipe_data if is_edit else {}
    st.header("✏ Modifier" if is_edit else "➕ Ajouter une recette")
    
    with st.form("recipe_form"):
        titre = st.text_input("Nom de la recette", r.get('Titre', ''))
        cat = st.selectbox("Catégorie", CATEGORIES[1:], index=0)
        img_url = st.text_input("URL de l'image", r.get('Image', ''))
        date_p = st.date_input("Date prévue")
        ingr = st.text_area("Ingrédients (un par ligne)", r.get('Ingrédients', ''))
        prep = st.text_area("Instructions de préparation", r.get('Préparation', ''))
        comm = st.text_area("Vos commentaires / notes", r.get('Commentaires', ''))
        
        if st.form_submit_button("💾 Enregistrer"):
            payload = {
                "action": "update" if is_edit else "add",
                "titre_original": r.get('Titre', '') if is_edit else "",
                "titre": titre,
                "ingredients": ingr,
                "preparation": prep,
                "categorie": cat,
                "commentaires": comm,
                "image": img_url,
                "date": datetime.now().strftime("%d/%m/%Y"),
                "date_prevue": date_p.strftime("%d/%m/%Y")
            }
            requests.post(URL_SCRIPT, json=payload)
            st.cache_data.clear()
            st.session_state.page = "home"
            st.rerun()

# ======================================================
# PAGE : ÉPICERIE
# ======================================================
elif st.session_state.page == "shopping":
    st.header("🛒 Ma Liste d'Épicerie")
    if st.button("🚫 Tout vider"):
        st.session_state.shopping_list = []
        st.rerun()
    
    for idx, it in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([4,1])
        c1.write(f"- {it}")
        if c2.button("❌", key=f"del_sh_{idx}"):
            st.session_state.shopping_list.pop(idx)
            st.rerun()

# ======================================================
# PAGE : AIDE
# ======================================================
elif st.session_state.page == "aide":
    st.header("📖 Aide & Tutoriel")
    st.markdown("""
    - **Bibliothèque** : Visualisez toutes vos recettes. Utilisez la recherche pour filtrer rapidement.
    - **Ajouter** : Remplissez le formulaire. L'image doit être un lien internet (URL).
    - **Épicerie** : Dans une recette, cochez les ingrédients manquants pour les ajouter ici.
    - **Agenda** : Cliquez sur le bouton calendrier dans une recette pour l'ajouter à votre Google Calendar.
    """)
