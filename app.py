import streamlit as st
import requests
import pandas as pd

# 1. Configuration de la page
st.set_page_config(page_title="Livre de Recettes Numérique", page_icon="👩‍🍳", layout="wide")

# 2. Design (CSS) amélioré
st.markdown("""
    <style>
    .recipe-card {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        text-align: center;
        color: #1f2937;
    }
    .fiche-titre {
        color: #1f2937;
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 5px;
    }
    .section-titre {
        color: #3b82f6;
        border-left: 5px solid #3b82f6;
        padding-left: 10px;
        margin-top: 20px;
    }
    .stButton>button {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION DES LIENS ---
URL_CSV_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# Gestion de la navigation et de la liste
if "page" not in st.session_state: st.session_state.page = "home"
if "selected_recipe" not in st.session_state: st.session_state.selected_recipe = None
if "liste_epicerie" not in st.session_state: st.session_state.liste_epicerie = []

# --- NAVIGATION ---
def aller_a_home():
    st.session_state.page = "home"
    st.session_state.selected_recipe = None

# --- MENU LATÉRAL ---
st.sidebar.title("👩‍🍳 Mon Menu")
if st.sidebar.button("📚 Ma Bibliothèque", use_container_width=True):
    aller_a_home()
    st.rerun()

if st.sidebar.button("➕ Ajouter une recette", use_container_width=True):
    st.session_state.page = "ajouter"
    st.rerun()

if st.sidebar.button("🛒 Ma Liste d'Épicerie", use_container_width=True):
    st.session_state.page = "liste"
    st.rerun()

# --- LOGIQUE D'AFFICHAGE ---

# 1. PAGE : DÉTAILS DE LA RECETTE
if st.session_state.page == "details" and st.session_state.selected_recipe is not None:
    row = st.session_state.selected_recipe
    if st.button("⬅️ Retour"):
        aller_a_home()
        st.rerun()

    col1, col2 = st.columns([1, 1])
    with col1:
        img_url = row.iloc[6] if len(row) > 6 else ""
        if pd.notna(img_url) and str(img_url).startswith("http"):
            st.image(img_url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/500x400?text=Image+non+disponible")
            
    with col2:
        st.markdown(f"<div class='fiche-titre'>{row.iloc[1]}</div>", unsafe_allow_html=True)
        st.caption(f"📅 Planifié : {row.iloc[5]}")
        
        st.markdown("<h3 class='section-titre'>🛒 Ingrédients</h3>", unsafe_allow_html=True)
        ingredients = str(row.iloc[3])
        st.write(ingredients)
        
        if st.button("➕ Ajouter à ma liste d'épicerie"):
            st.session_state.liste_epicerie.append({"plat": row.iloc[1], "items": ingredients})
            st.success("Ingrédients ajoutés !")
            st.toast("🛒 Liste mise à jour !")

    st.markdown("<h3 class='section-titre'>👨‍🍳 Préparation</h3>", unsafe_allow_html=True)
    st.info(row.iloc[4])

# 2. PAGE : MA LISTE D'ÉPICERIE
elif st.session_state.page == "liste":
    st.title("🛒 Ma Liste d'Épicerie")
    if not st.session_state.liste_epicerie:
        st.write("Votre liste est vide pour le moment. Allez dans une recette pour ajouter des ingrédients !")
    else:
        if st.button("🗑️ Tout effacer"):
            st.session_state.liste_epicerie = []
            st.rerun()
            
        for index, lot in enumerate(st.session_state.liste_epicerie):
            with st.expander(f"📍 Pour : {lot['plat']}"):
                st.write(lot['items'])

# 3. PAGE : AJOUTER UNE RECETTE
elif st.session_state.page == "ajouter":
    st.title("📝 Nouvelle Fiche Recette")
    with st.form("add_form", clear_on_submit=True):
        t = st.text_input("Nom du plat *")
        i = st.text_input("URL de l'image")
        d = st.date_input("Date prévue")
        ing = st.text_area("Ingrédients (un par ligne)")
        prep = st.text_area("Étapes de préparation")
        if st.form_submit_button("🚀 Enregistrer"):
            if t:
                payload = {"titre": t, "ingredients": ing, "preparation": prep, "date_prevue": str(d), "image": i}
                requests.post(URL_GOOGLE_SCRIPT, json=payload)
                st.success("Recette enregistrée !")
                st.balloons()

# 4. PAGE : ACCUEIL / BIBLIOTHÈQUE
else:
    st.title("📚 Ma Bibliothèque Numérique")
    try:
        df = pd.read_csv(URL_CSV_SHEETS)
        search = st.text_input("🔍 Rechercher...")
        if search:
            df = df[df.iloc[:, 1].str.contains(search, case=False, na=False)]

        cols = st.columns(3)
        for index, row in df.iterrows():
            with cols[index % 3]:
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                img_url = row.iloc[6] if len(row) > 6 else ""
                if pd.notna(img_url) and str(img_url).startswith("http"):
                    st.image(img_url, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x200?text=Pas+d'image")
                
                st.markdown(f"**{row.iloc[1]}**")
                if st.button("Voir les détails", key=f"btn_home_{index}"):
                    st.session_state.selected_recipe = row
                    st.session_state.page = "details"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error("Synchronisation avec Google Sheets...")
