import streamlit as st
import requests
import pandas as pd

# 1. Config de la page
st.set_page_config(page_title="Livre de Recettes Numérique", page_icon="👩‍🍳", layout="wide")

# 2. Design (CSS) pour les cartes et la fiche
st.markdown("""
    <style>
    .recipe-card {
        background-color: white;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        text-align: center;
        color: black;
    }
    .fiche-titre {
        color: #1f2937;
        font-size: 35px;
        font-weight: 800;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION ---
URL_CSV_SHEETS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_GOOGLE_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# Gestion de la navigation
if "page" not in st.session_state:
    st.session_state.page = "bibliotheque"
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None

# --- MENU LATÉRAL ---
st.sidebar.title("👨‍🍳 Menu")
if st.sidebar.button("📚 Ma Bibliothèque", use_container_width=True):
    st.session_state.page = "bibliotheque"
    st.session_state.selected_recipe = None
    st.rerun()

if st.sidebar.button("➕ Ajouter une recette", use_container_width=True):
    st.session_state.page = "ajouter"
    st.rerun()

# --- LOGIQUE DES PAGES ---

# 1. PAGE : FORMULAIRE D'AJOUT
if st.session_state.page == "ajouter":
    st.title("📝 Ajouter une nouvelle recette")
    with st.form("form_new_recipe", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t = st.text_input("Nom du plat *")
            s = st.text_input("Source (Lien)")
            i = st.text_input("Lien de l'image (URL)")
        with col2:
            d = st.date_input("Planifier pour le")
            ing = st.text_area("Ingrédients")
        prep = st.text_area("Préparation")
        
        if st.form_submit_button("🚀 Enregistrer dans mon livre"):
            if t:
                payload = {"titre": t, "source": s, "ingredients": ing, "preparation": prep, "date_prevue": str(d), "image": i}
                requests.post(URL_GOOGLE_SCRIPT, json=payload)
                st.success("C'est envoyé ! La recette apparaîtra dans quelques minutes.")
                st.balloons()
            else:
                st.error("Le nom du plat est obligatoire.")

# 2. PAGE : DÉTAILS D'UNE RECETTE
elif st.session_state.page == "details" and st.session_state.selected_recipe is not None:
    row = st.session_state.selected_recipe
    if st.button("⬅️ Retour à la liste"):
        st.session_state.page = "bibliotheque"
        st.rerun()
    
    st.divider()
    col_img, col_txt = st.columns([1, 1])
    with col_img:
        img_url = row.iloc[6] if len(row) > 6 else ""
        if pd.notna(img_url) and str(img_url).startswith("http"):
            st.image(img_url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/500x400?text=Image+non+disponible")
    with col_txt:
        st.markdown(f"<div class='fiche-titre'>{row.iloc[1]}</div>", unsafe_allow_html=True)
        st.info(f"📅 Prévue pour le : {row.iloc[5]}")
        st.subheader("🛒 Ingrédients")
        st.write(row.iloc[3])
    
    st.divider()
    st.subheader("👨‍🍳 Préparation")
    st.write(row.iloc[4])

# 3. PAGE : BIBLIOTHÈQUE (ACCUEIL)
else:
    st.title("📚 Ma Bibliothèque Numérique")
    try:
        df = pd.read_csv(URL_CSV_SHEETS)
        search = st.text_input("🔍 Rechercher une recette...")
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
                if st.button("Voir les détails", key=f"recette_{index}"):
                    st.session_state.selected_recipe = row
                    st.session_state.page = "details"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error("Connexion au livre en cours... (Vérifiez votre publication Google Sheets)")
