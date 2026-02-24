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

# Tes liens de connexion
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes", "Poulet", "Bœuf", "Porc", "Poisson", "Pâtes", "Riz", "Soupe", "Salade", "Entrée", "Plat Principal", "Accompagnement", "Dessert", "Petit-déjeuner", "Autre"]

# ======================================================
# GESTION DES DONNÉES
# ======================================================
@st.cache_data(ttl=600)
def load_data():
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        return df
    except:
        return pd.DataFrame()

if "page" not in st.session_state: st.session_state.page = "home"
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None

# ======================================================
# BARRE LATÉRALE
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Mes Recettes PRO")
    if st.button("📚 Bibliothèque", use_container_width=True):
        st.session_state.page = "home"; st.rerun()
    if st.button("➕ Ajouter une recette", type="primary", use_container_width=True):
        st.session_state.page = "add"; st.rerun()
    if st.button("🛒 Ma Liste d'Épicerie", use_container_width=True):
        st.session_state.page = "shopping"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.write("---")
    if st.button("❓ Aide & Tuto", use_container_width=True):
        st.session_state.page = "aide"; st.rerun()

# ======================================================
# PAGE : BIBLIOTHÈQUE
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if not df.empty:
        # On s'assure que les colonnes sont bien nommées
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= 8: df.columns = expected[:len(df.columns)]

        c1, c2 = st.columns(2)
        search = c1.text_input("🔍 Rechercher une recette")
        cat_filter = c2.selectbox("Filtrer par catégorie", CATEGORIES)
        
        if search: df = df[df['Titre'].str.contains(search, case=False)]
        if cat_filter != "Toutes": df = df[df['Catégorie'] == cat_filter]

        grid = st.columns(3)
        for idx, row in df.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    img_url = str(row['Image']) if "http" in str(row['Image']) else "https://via.placeholder.com/200"
                    st.image(img_url, use_container_width=True)
                    if row['Catégorie']: st.markdown(f"<span class='cat-badge'>{row['Catégorie']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()

# ======================================================
# PAGE : DÉTAILS (VERSION FINALE OPTIMISÉE)
# ======================================================
elif st.session_state.page == "details" and st.session_state.recipe_data:
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.header(f"🍳 {r.get('Titre', 'Recette')}")
    colA, colB = st.columns([1, 1.2])

    with colA:
        st.subheader("🛒 Ingrédients")
        temp_items = []
        liste_ing = str(r.get('Ingrédients','')).split("\n")
        for i, item in enumerate(liste_ing):
            clean_item = item.strip()
            if clean_item and st.checkbox(clean_item, key=f"chk_{r.get('Titre')}_{i}"):
                temp_items.append(clean_item)
        
        if st.button("➕ Ajouter à l'épicerie", use_container_width=True):
            if temp_items:
                for it in temp_items:
                    if it not in st.session_state.shopping_list: st.session_state.shopping_list.append(it)
                st.toast(f"✅ {len(temp_items)} articles ajoutés !")
            else: st.warning("Cochez des ingrédients d'abord.")
        
        st.write("---")
        st.subheader("📅 Planifier ce repas")
        try:
            current_date = datetime.strptime(str(r.get('Date_Prevue','')), "%d/%m/%Y")
        except:
            current_date = datetime.now()
            
        chosen_date = st.date_input("Choisir une date", value=current_date)
        
        if st.button("📅 Envoyer vers Google Agenda", use_container_width=True, type="primary"):
            try:
                formatted_date = chosen_date.strftime("%d/%m/%Y")
                requests.post(URL_SCRIPT, json={
                    "action": "calendar", "titre": r['Titre'], 
                    "date_prevue": formatted_date, "ingredients": r['Ingrédients']
                })
                st.success(f"Programmé pour le {formatted_date} !")
            except: st.error("Erreur de synchronisation.")

    with colB:
        img_detail = str(r.get('Image','')) if "http" in str(r.get('Image','')) else "https://via.placeholder.com/400"
        st.image(img_detail, use_container_width=True)
        st.info(f"**Notes :** {r.get('Commentaires', 'Aucune note.')}")
        st.write(f"**Préparation :**\n\n{r.get('Préparation','')}")
        
        # --- NOUVEAU : BOUTON PARTAGE / IMPRESSION ---
        st.write("---")
        with st.expander("📋 Partager ou Imprimer la recette"):
            texte_partage = f"RECETTE : {r['Titre']}\n\nINGRÉDIENTS :\n{r['Ingrédients']}\n\nPRÉPARATION :\n{r['Préparation']}"
            st.text_area("Texte prêt à copier :", texte_partage, height=150)
            st.caption("Astuce : Copiez ce texte pour l'envoyer par email ou l'imprimer.")

    st.write("---")
    b1, b2 = st.columns(2)
    if b1.button("✏ Modifier", use_container_width=True): st.session_state.page = "edit"; st.rerun()
    if b2.button("🗑 Supprimer", use_container_width=True):
        requests.post(URL_SCRIPT, json={"action": "delete", "titre": r['Titre']})
        st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : AJOUTER / MODIFIER
# ======================================================
elif st.session_state.page in ["add", "edit"]:
    is_edit = st.session_state.page == "edit"
    r = st.session_state.recipe_data if is_edit else {}
    st.header("✏ Modifier la recette" if is_edit else "➕ Ajouter une recette")
    
    with st.form("recipe_form"):
        t = st.text_input("Titre", r.get('Titre', ''))
        c = st.selectbox("Catégorie", CATEGORIES[1:])
        img = st.text_input("URL de l'image", r.get('Image', ''))
        d_prev = st.date_input("Date prévue")
        ingr = st.text_area("Ingrédients (un par ligne)", r.get('Ingrédients', ''))
        prep = st.text_area("Préparation", r.get('Préparation', ''))
        comm = st.text_area("Notes personnelles", r.get('Commentaires', ''))
        
        if st.form_submit_button("💾 Enregistrer"):
            payload = {
                "action": "update" if is_edit else "add",
                "titre_original": r.get('Titre', '') if is_edit else "",
                "titre": t, "ingredients": ingr, "preparation": prep,
                "categorie": c, "commentaires": comm, "image": img,
                "date": datetime.now().strftime("%d/%m/%Y"),
                "date_prevue": d_prev.strftime("%d/%m/%Y")
            }
            requests.post(URL_SCRIPT, json=payload)
            st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : ÉPICERIE
# ======================================================
elif st.session_state.page == "shopping":
    st.header("🛒 Ma Liste d'Épicerie")
    if st.button("🚫 Tout vider"): st.session_state.shopping_list = []; st.rerun()
    
    if not st.session_state.shopping_list:
        st.info("Votre liste est vide. Allez dans une recette pour ajouter des ingrédients !")
    else:
        for idx, it in enumerate(st.session_state.shopping_list):
            c1, c2 = st.columns([4,1])
            c1.write(f"- {it}")
            if c2.button("❌", key=f"del_sh_{idx}"):
                st.session_state.shopping_list.pop(idx); st.rerun()

# ======================================================
# PAGE : AIDE
# ======================================================
elif st.session_state.page == "aide":
    st.header("📖 Guide d'utilisation")
    st.markdown("""
    1.  **Calendrier** : Choisissez une date directement dans la fiche recette pour l'ajouter à votre Agenda Google.
    2.  **Partage** : Utilisez le bloc 'Partager' en bas d'une recette pour copier le texte proprement.
    3.  **Images** : Pour de meilleurs résultats, utilisez des liens d'images trouvées sur Google Images.
    """)
