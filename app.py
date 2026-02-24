import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION
# ======================================================

st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

URL_CSV = "TON_URL_CSV"
URL_SCRIPT = "TON_URL_SCRIPT"

CATEGORIES = [
    "Toutes",
    "Poulet", "Bœuf", "Porc", "Poisson", "Pâtes", "Riz",
    "Soupe", "Salade", "Entrée", "Plat Principal",
    "Accompagnement", "Dessert", "Petit-déjeuner", "Autre"
]

# ======================================================
# CACHE
# ======================================================

@st.cache_data(ttl=600)
def load_data():
    return pd.read_csv(URL_CSV).fillna('')

# ======================================================
# SESSION INIT
# ======================================================

for key, value in {
    "page": "home",
    "recipe_data": None,
    "shopping_list": [],
    "checked_items": []
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ======================================================
# SIDEBAR
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

# ======================================================
# HOME
# ======================================================

if st.session_state.page == "home":

    st.header("📚 Ma Bibliothèque")

    df = load_data()

    expected = [
        'Date','Titre','Source','Ingrédients',
        'Préparation','Date_Prevue','Image',
        'Catégorie','Commentaires'
    ]

    if len(df.columns) == 9:
        df.columns = expected
    elif len(df.columns) == 8:
        df.columns = expected[:-1]
        df['Commentaires'] = ""
    else:
        st.error("Structure CSV incorrecte.")
        st.stop()

    df = df[df['Titre'] != ""]

    col1, col2, col3 = st.columns(3)

    with col1:
        search = st.text_input("🔍 Rechercher")
    with col2:
        cat_filter = st.selectbox("Filtrer par catégorie", CATEGORIES)
    with col3:
        sort_option = st.selectbox("Trier par", ["Date ajout", "Date prévue"])

    if search:
        df = df[df['Titre'].str.contains(search, case=False, na=False)]

    if cat_filter != "Toutes":
        df = df[df['Catégorie'] == cat_filter]

    if sort_option == "Date prévue":
        df = df.sort_values("Date_Prevue", ascending=True)
    else:
        df = df.sort_values("Date", ascending=False)

    if df.empty:
        st.info("Aucune recette trouvée.")
    else:
        grid = st.columns(3)
        for idx, row in df.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):

                    img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/200"
                    st.image(img, use_container_width=True)

                    st.markdown(f"**{row['Titre']}**")
                    st.caption(row['Catégorie'])

                    if st.button("Voir", key=f"view_{idx}"):
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

    st.header(r['Titre'])
    st.caption(r['Catégorie'])

    colA, colB = st.columns([1,1.2])

    with colA:
        st.subheader("🛒 Ingrédients")
        for item in str(r['Ingrédients']).split("\n"):
            item = item.strip()
            if item:
                if st.checkbox(item, key=f"{r['Titre']}_{item}"):
                    if item not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(item)

        st.write("---")
        st.subheader("📝 Notes")
        st.info(r.get("Commentaires","Aucune note."))

    with colB:
        st.image(r['Image'], use_container_width=True)
        st.subheader("👨‍🍳 Préparation")
        st.write(r['Préparation'])

    col1, col2 = st.columns(2)

    if col1.button("✏ Modifier"):
        st.session_state.page = "edit"
        st.rerun()

    if col2.button("🗑 Supprimer"):
        try:
            requests.post(URL_SCRIPT, json={
                "action": "delete",
                "titre": r['Titre']
            })
            st.cache_data.clear()
            st.success("Recette supprimée")
            st.session_state.page = "home"
            st.rerun()
        except:
            st.error("Erreur suppression")

# ======================================================
# ADD
# ======================================================

elif st.session_state.page == "add":

    st.header("➕ Nouvelle recette")

    with st.form("add_form"):
        titre = st.text_input("Nom *")
        cat = st.selectbox("Catégorie", CATEGORIES[1:])
        img = st.text_input("Image URL")
        date_p = st.date_input("Date prévue")
        source = st.text_input("Lien source")
        ingr = st.text_area("Ingrédients *")
        prep = st.text_area("Préparation")
        comm = st.text_area("Notes")

        if st.form_submit_button("Enregistrer"):

            data = {
                "action":"add",
                "date":datetime.now().strftime("%d/%m/%Y"),
                "titre":titre,
                "source":source,
                "ingredients":ingr,
                "preparation":prep,
                "date_prevue":date_p.strftime("%d/%m/%Y"),
                "image":img,
                "categorie":cat,
                "commentaires":comm
            }

            try:
                requests.post(URL_SCRIPT,json=data)
                st.cache_data.clear()
                st.success("Ajoutée !")
                st.session_state.page="home"
                st.rerun()
            except:
                st.error("Erreur ajout")

# ======================================================
# EDIT
# ======================================================

elif st.session_state.page == "edit":

    r = st.session_state.recipe_data
    st.header("✏ Modifier recette")

    with st.form("edit_form"):
        titre = st.text_input("Nom", r['Titre'])
        cat = st.selectbox("Catégorie", CATEGORIES[1:], index=CATEGORIES[1:].index(r['Catégorie']))
        ingr = st.text_area("Ingrédients", r['Ingrédients'])
        prep = st.text_area("Préparation", r['Préparation'])
        comm = st.text_area("Notes", r.get("Commentaires",""))

        if st.form_submit_button("Sauvegarder"):

            try:
                requests.post(URL_SCRIPT,json={
                    "action":"update",
                    "titre_original":r['Titre'],
                    "titre":titre,
                    "ingredients":ingr,
                    "preparation":prep,
                    "categorie":cat,
                    "commentaires":comm
                })
                st.cache_data.clear()
                st.success("Modifiée !")
                st.session_state.page="home"
                st.rerun()
            except:
                st.error("Erreur modification")

# ======================================================
# SHOPPING
# ======================================================

elif st.session_state.page == "shopping":

    st.header("🛒 Épicerie")

    if not st.session_state.shopping_list:
        st.info("Liste vide.")
    else:
        for idx,item in enumerate(st.session_state.shopping_list):
            cols=st.columns([0.5,4,1])
            checked=cols[0].checkbox("",key=f"chk_{idx}")
            cols[1].write(item)
            if cols[2].button("❌",key=f"del_{idx}"):
                st.session_state.shopping_list.pop(idx)
                st.rerun()
