import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

# Style pour les images uniformes et les badges
st.markdown("""
    <style>
    [data-testid="stImage"] img { 
        object-fit: cover; 
        height: 250px !important; 
        width: 100% !important; 
        border-radius: 15px; 
    }
    .recipe-title { 
        height: 50px; 
        overflow: hidden; 
        font-weight: bold; 
        font-size: 1.2em; 
        margin-top: 5px;
    }
    .cat-badge { 
        background-color: #ffca28; 
        color: #000; 
        padding: 2px 12px; 
        border-radius: 12px; 
        font-size: 0.85em; 
        font-weight: bold; 
    }
    </style>
    """, unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes", "Poulet", "Bœuf", "Porc", "Poisson", "Pâtes", "Riz", "Soupe", "Salade", "Entrée", "Plat Principal", "Accompagnement", "Dessert", "Petit-déjeuner", "Autre"]

@st.cache_data(ttl=600)
def load_data():
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        return df
    except:
        return pd.DataFrame()

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

# ======================================================
# BIBLIOTHÈQUE (HOME)
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if not df.empty:
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) == 9: df.columns = expected
        elif len(df.columns) == 8: df.columns = expected[:-1]; df['Commentaires'] = ""

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
                    if row['Catégorie']: st.markdown(f"<span class='cat-badge'>{row['Catégorie']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()

# ======================================================
# DETAILS (AVEC CALENDRIER INTERACTIF)
# ======================================================
elif st.session_state.page == "details" and st.session_state.recipe_data:
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.header(f"🍳 {r['Titre']}")
    colA, colB = st.columns([1, 1.2])
    with colA:
        st.subheader("🛒 Ingrédients")
        temp_items = []
        for item in str(r['Ingrédients']).split("\n"):
            clean_item = item.strip()
            if clean_item and st.checkbox(clean_item, key=f"chk_{clean_item}"):
                temp_items.append(clean_item)
        
        if st.button("➕ Ajouter à l'épicerie", use_container_width=True):
            if temp_items:
                for it in temp_items:
                    if it not in st.session_state.shopping_list: st.session_state.shopping_list.append(it)
                st.toast(f"✅ {len(temp_items)} articles ajoutés !")
            else: st.warning("Cochez des ingrédients.")
        
        st.write("---")
        
        # --- NOUVEAU : CALENDRIER DE CHOIX ---
        st.subheader("📅 Planifier ce repas")
        
        # On essaie de lire la date existante ou on prend aujourd'hui
        try:
            current_date = datetime.strptime(r['Date_Prevue'], "%d/%m/%Y")
        except:
            current_date = datetime.now()
            
        chosen_date = st.date_input("Choisir une date", value=current_date)
        
        if st.button("📅 Envoyer vers Google Agenda", use_container_width=True, type="primary"):
            try:
                formatted_date = chosen_date.strftime("%d/%m/%Y")
                requests.post(URL_SCRIPT, json={
                    "action": "calendar", 
                    "titre": r['Titre'], 
                    "date_prevue": formatted_date, 
                    "ingredients": r['Ingrédients']
                })
                st.success(f"Programmé pour le {formatted_date} !")
            except: st.error("Erreur de synchronisation.")

    with colB:
        st.image(r['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        st.info(f"**Notes :** {r.get('Commentaires', '...')}")
        st.write(f"**Préparation :**\n\n{r['Préparation']}")
    
    st.write("---")
    b1, b2 = st.columns(2)
    if b1.button("✏ Modifier", use_container_width=True): st.session_state.page = "edit"; st.rerun()
    if b2.button("🗑 Supprimer", use_container_width=True):
        requests.post(URL_SCRIPT, json={"action": "delete", "titre": r['Titre']})
        st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# ADD / EDIT / SHOPPING / AIDE (Reste identique)
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
        com = st.text_area("Notes", r.get('Commentaires', ''))
        if st.form_submit_button("Enregistrer"):
            p = {"action": "update" if is_edit else "add", "titre_original": r.get('Titre', ''), "titre": t, "ingredients": ing, "preparation": pre, "categorie": c, "commentaires": com, "image": i, "date": datetime.now().strftime("%d/%m/%Y"), "date_prevue": d.strftime("%d/%m/%Y")}
            requests.post(URL_SCRIPT, json=p)
            st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "shopping":
    st.header("🛒 Liste d'épicerie")
    if st.button("🚫 Vider"): st.session_state.shopping_list = []; st.rerun()
    for idx, it in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([4,1]); c1.write(f"- {it}")
        if c2.button("❌", key=f"s_{idx}"): st.session_state.shopping_list.pop(idx); st.rerun()

elif st.session_state.page == "aide":
    st.header("📖 Aide")
    st.write("- **Planification** : Sélectionnez une date dans le calendrier pour l'ajouter à votre agenda mobile.")
