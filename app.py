import streamlit as st
import requests
import pandas as pd

# 1. CONFIGURATION & DESIGN ÉPURÉ
st.set_page_config(page_title="Livre de Recettes Numérique", page_icon="👩‍🍳", layout="wide")

st.markdown("""
    <style>
    /* Fond blanc pour toute l'application */
    .stApp {
        background-color: #FFFFFF;
    }
    /* Cartes de la bibliothèque */
    .recipe-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #f0f0f0;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    /* Titre de la fiche recette */
    .fiche-titre {
        font-size: 42px;
        font-weight: 800;
        color: #1f2937;
        margin-bottom: 10px;
    }
    /* Style pour les listes */
    .ingredient-line {
        font-size: 18px;
        padding: 5px 0;
        border-bottom: 1px solid #fafafa;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURATION DES LIENS ---
# Assure-toi que ce lien est bien le lien "Publié sur le Web" au format CSV
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# --- INITIALISATION DE LA MÉMOIRE (SESSION STATE) ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "recipe_data" not in st.session_state:
    st.session_state.recipe_data = None
if "liste_epicerie" not in st.session_state:
    st.session_state.liste_epicerie = []

# --- FONCTIONS DE NAVIGATION ---
def aller_details(data):
    st.session_state.recipe_data = data
    st.session_state.page = "details"

def aller_home():
    st.session_state.page = "home"
    st.session_state.recipe_data = None

# --- MENU LATÉRAL ---
with st.sidebar:
    st.title("👩‍🍳 Menu")
    if st.button("📚 Ma Bibliothèque", use_container_width=True):
        aller_home()
        st.rerun()
    if st.button("➕ Ajouter une recette", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()
    if st.button("🛒 Ma Liste d'Épicerie", use_container_width=True):
        st.session_state.page = "liste"
        st.rerun()

# --- LOGIQUE DES PAGES ---

# 1. PAGE : DÉTAILS DE LA RECETTE
if st.session_state.page == "details" and st.session_state.recipe_data is not None:
    row = st.session_state.recipe_data
    if st.button("⬅️ Retour à la bibliothèque"):
        aller_home()
        st.rerun()
    
    st.divider()
    
    col_txt, col_img = st.columns([1.2, 1])
    
    with col_txt:
        st.markdown(f"<div class='fiche-titre'>{row[1]}</div>", unsafe_allow_html=True)
        st.caption(f"📅 Planifié pour le : {row[5]}")
        
        st.markdown("### 🛒 Ingrédients")
        # On sépare le texte par ligne pour créer une belle liste
        ingredients_bruts = str(row[3])
        if ingredients_bruts and ingredients_bruts != "nan":
            lignes = ingredients_bruts.split('\n')
            for ligne in lignes:
                if ligne.strip():
                    st.markdown(f"✅ {ligne.strip()}")
        
        st.write("")
        if st.button("🛒 Ajouter ces ingrédients à ma liste", type="primary"):
            st.session_state.liste_epicerie.append({"titre": row[1], "items": ingredients_bruts})
            st.toast("Ajouté à la liste d'épicerie !")

    with col_img:
        img_url = row[6] if len(row) > 6 and pd.notna(row[6]) else ""
        if str(img_url).startswith("http"):
            st.image(img_url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/600x450?text=Image+Recette", use_container_width=True)

    st.divider()
    st.markdown("### 👨‍🍳 Préparation")
    st.info(row[4] if pd.notna(row[4]) else "Aucune instruction saisie.")

# 2. PAGE : MA LISTE D'ÉPICERIE
elif st.session_state.page == "liste":
    st.title("🛒 Ma Liste d'Épicerie")
    if not st.session_state.liste_epicerie:
        st.info("Votre liste est vide pour le moment.")
    else:
        if st.button("🗑️ Vider la liste"):
            st.session_state.liste_epicerie = []
            st.rerun()
        
        for idx, lot in enumerate(st.session_state.liste_epicerie):
            with st.expander(f"📍 {lot['titre']}", expanded=True):
                st.write(lot['items'])

# 3. PAGE : AJOUTER UNE RECETTE
elif st.session_state.page == "ajouter":
    st.title("➕ Ajouter une nouvelle recette")
    with st.form("ajout_recette", clear_on_submit=True):
        t = st.text_input("Nom du plat *")
        i = st.text_input("URL de l'image (Lien)")
        d = st.date_input("Date prévue")
        ing = st.text_area("Ingrédients (un par ligne)")
        prep = st.text_area("Préparation")
        
        if st.form_submit_button("Enregistrer"):
            if t:
                payload = {"titre": t, "image": i, "ingredients": ing, "preparation": prep, "date_prevue": str(d)}
                try:
                    requests.post(URL_SCRIPT, json=payload)
                    st.success("Recette enregistrée avec succès !")
                    st.balloons()
                except:
                    st.error("Erreur d'envoi vers Google Sheets.")
            else:
                st.warning("Veuillez donner un nom au plat.")

# 4. PAGE : BIBLIOTHÈQUE (ACCUEIL)
else:
    st.title("📚 Ma Bibliothèque Numérique")
    try:
        # On lit le CSV et on s'assure qu'il est bien chargé
        df = pd.read_csv(URL_CSV)
        
        recherche = st.text_input("🔍 Rechercher une recette...")
        if recherche:
            df = df[df.iloc[:, 1].str.contains(recherche, case=False, na=False)]

        cols = st.columns(3)
        for index, row in df.iterrows():
            with cols[index % 3]:
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                
                # Gestion de l'image
                img = row.iloc[6] if len(row) > 6 and pd.notna(row.iloc[6]) else ""
                if str(img).startswith("http"):
                    st.image(img, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x200?text=Pas+de+photo")
                
                st.markdown(f"### {row.iloc[1]}")
                
                # On utilise une fonction pour passer les données de la ligne proprement
                if st.button("Voir la fiche", key=f"btn_recette_{index}"):
                    aller_details(list(row))
                    st.rerun()
                    
                st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Impossible de charger le livre : {e}")
        st.info("Vérifiez que votre Google Sheets est bien publié au format CSV.")
