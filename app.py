import streamlit as st
import requests
import pandas as pd

# 1. Look & Feel : Fond Blanc et Style Épuré
st.set_page_config(page_title="Mon Livre de Recettes", page_icon="👩‍🍳", layout="wide")

st.markdown("""
    <style>
    /* Fond de la page en blanc */
    .stApp {
        background-color: #FFFFFF;
    }
    /* Cartes de la bibliothèque */
    .recipe-card {
        background-color: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #eee;
        text-align: center;
        margin-bottom: 20px;
    }
    /* Titre de la fiche recette */
    .fiche-titre {
        font-size: 42px;
        font-weight: 800;
        color: #1f2937;
        line-height: 1.2;
    }
    /* Style pour les listes d'ingrédients */
    .ing-item {
        padding: 5px 0px;
        border-bottom: 1px solid #f0f0f0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION ---
URL_CSV_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

if "page" not in st.session_state: st.session_state.page = "home"
if "selected_recipe" not in st.session_state: st.session_state.selected_recipe = None
if "liste_epicerie" not in st.session_state: st.session_state.liste_epicerie = []

# --- MENU LATÉRAL ---
with st.sidebar:
    st.title("👩‍🍳 Menu")
    if st.button("📚 Ma Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("➕ Ajouter une recette", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()
    if st.button("🛒 Ma Liste d'Épicerie", use_container_width=True):
        st.session_state.page = "liste"
        st.rerun()

# --- LOGIQUE DES PAGES ---

# PAGE DÉTAILS (Le beau visuel blanc)
if st.session_state.page == "details" and st.session_state.selected_recipe is not None:
    row = st.session_state.selected_recipe
    st.button("⬅️ Retour à la liste", on_click=lambda: st.session_state.update({"page": "home"}))
    
    col_txt, col_img = st.columns([1.2, 1])
    
    with col_txt:
        st.markdown(f"<div class='fiche-titre'>{row.iloc[1]}</div>", unsafe_allow_html=True)
        st.caption(f"📅 Planifié pour le : {row.iloc[5]}")
        
        st.markdown("### 🛒 Ingrédients")
        # ASTUCE : On sépare le texte par les retours à la ligne pour faire une vraie liste
        items = str(row.iloc[3]).split('\n')
        for item in items:
            if item.strip():
                st.markdown(f"✅ {item.strip()}")
        
        if st.button("🛒 Ajouter à ma liste d'épicerie", type="primary"):
            st.session_state.liste_epicerie.append({"plat": row.iloc[1], "items": row.iloc[3]})
            st.toast("Ajouté à la liste !")

    with col_img:
        img_url = row.iloc[6] if len(row) > 6 else ""
        if pd.notna(img_url) and str(img_url).startswith("http"):
            st.image(img_url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/500x400?text=Image+Recette")

    st.markdown("### 👨‍🍳 Préparation")
    st.write(row.iloc[4])

# PAGE LISTE ÉPICERIE
elif st.session_state.page == "liste":
    st.title("🛒 Ma Liste d'Épicerie")
    if not st.session_state.liste_epicerie:
        st.info("Votre liste est vide.")
    else:
        if st.button("Vider la liste"):
            st.session_state.liste_epicerie = []
            st.rerun()
        for l in st.session_state.liste_epicerie:
            st.checkbox(f"**{l['plat']}** : {l['items']}")

# PAGE AJOUTER
elif st.session_state.page == "ajouter":
    st.title("➕ Nouvelle Recette")
    with st.form("add"):
        t = st.text_input("Nom du plat")
        img = st.text_input("Lien de la photo")
        ing = st.text_area("Ingrédients (un par ligne)")
        prep = st.text_area("Préparation")
        if st.form_submit_button("Sauvegarder"):
            payload = {"titre": t, "ingredients": ing, "preparation": prep, "image": img}
            requests.post(URL_GOOGLE_SCRIPT, json=payload)
            st.success("Enregistré !")

# ACCUEIL
else:
    st.title("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV_SHEETS)
        cols = st.columns(3)
        for index, row in df.iterrows():
            with cols[index % 3]:
                st.markdown(f'<div class="recipe-card">', unsafe_allow_html=True)
                img = row.iloc[6] if len(row) > 6 and pd.notna(row.iloc[6]) else "https://via.placeholder.com/300"
                st.image(img, use_container_width=True)
                st.markdown(f"**{row.iloc[1]}**")
                if st.button("Voir la fiche", key=f"btn_{index}"):
                    st.session_state.selected_recipe = row
                    st.session_state.page = "details"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.error("Connexion au livre...")
