import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# CONFIG (Garde tes URLs ici)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# CONFIG (Garde tes URLs ici)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes", "Poulet", "Bœuf", "Porc", "Poisson", "Pâtes", "Riz", "Soupe", "Salade", "Entrée", "Plat Principal", "Accompagnement", "Dessert", "Petit-déjeuner", "Autre"]

@st.cache_data(ttl=600)
def load_data():
    try: return pd.read_csv(URL_CSV).fillna('')
    except: return pd.DataFrame()

if "page" not in st.session_state: st.session_state.page = "home"
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("👨‍🍳 Mes Recettes PRO")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("➕ Ajouter", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page = "shopping"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.write("---")
    if st.button("❓ Aide & Tuto", use_container_width=True): st.session_state.page = "aide"; st.rerun()

# --- LOGIQUE DES PAGES ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if not df.empty:
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        df.columns = expected if len(df.columns) == 9 else expected[:-1] + ['Commentaires']
        
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
                    st.markdown(f"**{row['Titre']}**")
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()

elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.header(f"🍳 {r['Titre']}")
    colA, colB = st.columns([1,1.2])
    with colA:
        st.subheader("🛒 Ingrédients")
        for item in str(r['Ingrédients']).split("\n"):
            if item.strip() and st.checkbox(item.strip(), key=f"chk_{item}"):
                if item.strip() not in st.session_state.shopping_list: st.session_state.shopping_list.append(item.strip())
        
        st.write("---")
        # --- BOUTON CALENDRIER ---
        st.subheader("📅 Planification")
        st.write(f"Prévu pour le : **{r['Date_Prevue']}**")
        if st.button("📅 Ajouter à mon Agenda Google", use_container_width=True):
            try:
                requests.post(URL_SCRIPT, json={"action": "calendar", "titre": r['Titre'], "date_prevue": r['Date_Prevue'], "ingredients": r['Ingrédients']})
                st.success("Ajouté à l'agenda !")
            except: st.error("Erreur de connexion.")

    with colB:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        st.info(f"**Note :** {r.get('Commentaires', 'Aucune note.')}")
        st.write(f"**Préparation :**\n\n{r['Préparation']}")
    
    st.write("---")
    b1, b2 = st.columns(2)
    if b1.button("✏ Modifier", use_container_width=True): st.session_state.page = "edit"; st.rerun()
    if b2.button("🗑 Supprimer", use_container_width=True):
        requests.post(URL_SCRIPT, json={"action": "delete", "titre": r['Titre']})
        st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# --- (Les pages Add/Edit/Shopping restent identiques à la version précédente) ---"

CATEGORIES = ["Toutes", "Poulet", "Bœuf", "Porc", "Poisson", "Pâtes", "Riz", "Soupe", "Salade", "Entrée", "Plat Principal", "Accompagnement", "Dessert", "Petit-déjeuner", "Autre"]

@st.cache_data(ttl=600)
def load_data():
    try: return pd.read_csv(URL_CSV).fillna('')
    except: return pd.DataFrame()

if "page" not in st.session_state: st.session_state.page = "home"
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("👨‍🍳 Mes Recettes PRO")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("➕ Ajouter", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page = "shopping"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()
    st.write("---")
    if st.button("❓ Aide & Tuto", use_container_width=True): st.session_state.page = "aide"; st.rerun()

# --- LOGIQUE DES PAGES ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if not df.empty:
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        df.columns = expected if len(df.columns) == 9 else expected[:-1] + ['Commentaires']
        
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
                    st.markdown(f"**{row['Titre']}**")
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"
                        st.rerun()

elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.header(f"🍳 {r['Titre']}")
    colA, colB = st.columns([1,1.2])
    with colA:
        st.subheader("🛒 Ingrédients")
        for item in str(r['Ingrédients']).split("\n"):
            if item.strip() and st.checkbox(item.strip(), key=f"chk_{item}"):
                if item.strip() not in st.session_state.shopping_list: st.session_state.shopping_list.append(item.strip())
        
        st.write("---")
        # --- BOUTON CALENDRIER ---
        st.subheader("📅 Planification")
        st.write(f"Prévu pour le : **{r['Date_Prevue']}**")
        if st.button("📅 Ajouter à mon Agenda Google", use_container_width=True):
            try:
                requests.post(URL_SCRIPT, json={"action": "calendar", "titre": r['Titre'], "date_prevue": r['Date_Prevue'], "ingredients": r['Ingrédients']})
                st.success("Ajouté à l'agenda !")
            except: st.error("Erreur de connexion.")

    with colB:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        st.info(f"**Note :** {r.get('Commentaires', 'Aucune note.')}")
        st.write(f"**Préparation :**\n\n{r['Préparation']}")
    
    st.write("---")
    b1, b2 = st.columns(2)
    if b1.button("✏ Modifier", use_container_width=True): st.session_state.page = "edit"; st.rerun()
    if b2.button("🗑 Supprimer", use_container_width=True):
        requests.post(URL_SCRIPT, json={"action": "delete", "titre": r['Titre']})
        st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# --- (Les pages Add/Edit/Shopping restent identiques à la version précédente) ---
