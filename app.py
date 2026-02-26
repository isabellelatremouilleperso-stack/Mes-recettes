import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup
import urllib.parse

# --- CONFIGURATION & STYLE ---
st.set_page_config(page_title="Mes Recettes", layout="wide")

st.markdown("""
    <style>
    .recipe-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        margin-bottom: 15px;
    }
    .recipe-img {
        width: 100%;
        height: 150px;
        object-fit: cover;
        border-radius: 8px;
    }
    .recipe-title {
        font-weight: bold;
        text-align: center;
        margin-top: 8px;
        color: #333;
    }
    </style>
""", unsafe_allow_html=True)

# --- FONCTION D'ANALYSE (TON BOUTON GOOGLE) ---
def scrape_url(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        titre = soup.find('h1').text.strip() if soup.find('h1') else "Recette sans titre"
        # Extraction brute du texte pour le tri manuel
        paragraphs = soup.find_all(['p', 'li'])
        contenu = "\n".join([p.text.strip() for p in paragraphs if len(p.text.strip()) > 20])
        return titre, contenu
    except Exception as e:
        return None, str(e)

# --- NAVIGATION ---
if "page" not in st.session_state:
    st.session_state.page = "home"

# --- PAGE ACCUEIL (SANS ÉTOILES) ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data() # Ta fonction de chargement habituelle
    
    if not df.empty:
        # Grille de 3 colonnes
        for i in range(0, len(df), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(df):
                    row = df.iloc[i + j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f"""
                            <div class="recipe-card">
                                <img src="{img}" class="recipe-img">
                                <div class="recipe-title">{row["Titre"]}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button("Voir la recette", key=f"btn_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"
                            st.rerun()

# --- PAGE DÉTAILS (NOTES ET ÉTOILES MODIFIABLES) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.header(f"📖 {r['Titre']}")
    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
        
        st.subheader("⭐ Ma Note & Avis")
        # Récupération des valeurs existantes
        curr_note = int(float(r.get('Note', 0))) if r.get('Note') else 0
        curr_comm = str(r.get('Commentaires', ""))
        
        new_note = st.slider("Note", 0, 5, curr_note, key="slider_det")
        new_comm = st.text_area("Mes notes personnelles :", value=curr_comm, height=100)
        
        if st.button("💾 Enregistrer mon avis", type="primary"):
            # Ici ton appel send_action pour mettre à jour Google Sheets
            st.success("Avis enregistré !")
            st.session_state.recipe_data['Note'] = new_note
            st.session_state.recipe_data['Commentaires'] = new_comm
            st.rerun()

    with col2:
        st.subheader("🛒 Ingrédients")
        st.write(r.get('Ingrédients', "Non renseignés"))
        st.divider()
        st.subheader("📝 Préparation")
        st.write(r.get('Préparation', "Non renseignée"))

# --- PAGE AJOUTER (AVEC BOUTON ANALYSE GOOGLE) ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une Recette")
    tab1, tab2, tab3 = st.tabs(["🌐 Site Web (Auto)", "🎬 Lien Vidéo", "📝 Vrac / Manuel"])

    with tab1:
        st.subheader("Analyse automatique (Bouton Google)")
        url_input = st.text_input("Collez l'URL du site ici", placeholder="https://www.marmiton.org/...")
        
        if st.button("🔍 Analyser le site", type="primary", use_container_width=True):
            if url_input:
                with st.spinner("Analyse du site en cours..."):
                    titre, corps = scrape_url(url_input)
                    if titre:
                        st.session_state.temp_titre = titre
                        st.session_state.temp_contenu = corps
                        st.rerun()
        
        if "temp_titre" in st.session_state:
            st.divider()
            t_final = st.text_input("Titre extrait", value=st.session_state.temp_titre)
            c_final = st.text_area("Contenu (Triez ici !)", value=st.session_state.temp_contenu, height=300)
            if st.button("💾 Enregistrer cet import"):
                # send_action ici...
                del st.session_state.temp_titre
                st.session_state.page = "home"; st.rerun()

    with tab2:
        st.subheader("🎬 Lien Vidéo")
        st.text_input("Lien Insta/TikTok/FB", key="v_url")
        st.text_input("Nom de la recette", key="v_titre")
        if st.button("🚀 Sauvegarder la Vidéo"):
            st.session_state.page = "home"; st.rerun()

    with tab3:
        st.subheader("📝 Saisie libre (Vrac)")
        with st.form("vrac_form"):
            st.text_input("Titre de la recette *")
            st.text_area("Collez votre texte brut ici (Ingrédients, étapes...)", height=250)
            if st.form_submit_button("💾 Enregistrer le vrac"):
                st.session_state.page = "home"; st.rerun()
