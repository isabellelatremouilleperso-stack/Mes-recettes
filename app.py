import streamlit as st
import requests
import pandas as pd

# ==============================
# CONFIGURATION & DESIGN
# ==============================
st.set_page_config(page_title="Mon Livre de Recettes", page_icon="👩‍🍳", layout="wide")

st.markdown("""
    <style>
    /* Fond de page blanc pur */
    .stApp { background-color: #FFFFFF; }
    
    /* CIBLE UNIQUEMENT LE CONTENU CENTRAL POUR LE TEXTE NOIR */
    /* On évite de toucher à la barre latérale (stSidebar) */
    .main .block-container p, 
    .main .block-container div, 
    .main .block-container span, 
    .main .block-container label, 
    .main .block-container h1, 
    .main .block-container h2, 
    .main .block-container h3 {
        color: #1f2937 !important;
    }

    /* Cartes de la bibliothèque */
    .recipe-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #f0f0f0;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }

    /* Titre de la fiche détaillée */
    .fiche-titre {
        font-size: 42px;
        font-weight: 800;
        color: #1f2937 !important;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# LIENS VERS TES DONNÉES
# ==============================
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# ==============================
# GESTION DE LA MÉMOIRE
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "recipe_data" not in st.session_state:
    st.session_state.recipe_data = None

if "liste_epicerie" not in st.session_state:
    st.session_state.liste_epicerie = []

# ==============================
# MENU LATÉRAL
# ==============================
with st.sidebar:
    st.title("👩‍🍳 Menu")
    
    if st.button("📚 Ma Bibliothèque", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("➕ Ajouter une recette", use_container_width=True):
        st.session_state.page = "ajouter"
        st.rerun()
    if st.button("🛒 Ma Liste d'épicerie", use_container_width=True):
        st.session_state.page = "liste"
        st.rerun()

# ==============================
# PAGE : AJOUTER UNE RECETTE
# ==============================
if st.session_state.page == "ajouter":
    st.title("➕ Nouvelle Recette")
    with st.form("form_add", clear_on_submit=True):
        t = st.text_input("Nom du plat *")
        img = st.text_input("Lien de l'image (URL)")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Préparation")
        
        if st.form_submit_button("🚀 Enregistrer dans mon livre"):
            if t:
                try:
                    requests.post(URL_SCRIPT, json={"titre": t, "image": img, "ingredients": ing, "preparation": pre})
                    st.success("C'est enregistré ! 🎉")
                    st.balloons()
                except: st.error("Erreur de sauvegarde.")
            else: st.warning("Le nom du plat est obligatoire.")

# ==============================
# PAGE : DÉTAILS D'UNE RECETTE
# ==============================
elif st.session_state.page == "details":
    if st.session_state.recipe_data is not None:
        row = st.session_state.recipe_data
        if st.button("⬅️ Retour à la bibliothèque"):
            st.session_state.page = "home"
            st.rerun()

        st.markdown(f"<div class='fiche-titre'>{row['Titre']}</div>", unsafe_allow_html=True)
        
        col_txt, col_img = st.columns([1, 1])
        with col_txt:
            st.markdown("### 🛒 Ingrédients")
            items = str(row["Ingrédients"]).split("\n")
            for item in items:
                if item.strip(): st.write(f"✅ {item.strip()}")
            
            if st.button("🛒 Ajouter à ma liste", type="primary"):
                st.session_state.liste_epicerie.append({"t": row['Titre'], "i": row['Ingrédients']})
                st.toast("Ajouté !")

        with col_img:
            if str(row["Image"]).startswith("http"):
                st.image(row["Image"], use_container_width=True)
            else:
                st.image("https://via.placeholder.com/500x400?text=Pas+d'image")

        st.divider()
        st.markdown("### 👨‍🍳 Préparation")
        st.info(row["Préparation"] if pd.notna(row["Préparation"]) else "Aucune instruction.")
    else:
        st.session_state.page = "home"
        st.rerun()

# ==============================
# PAGE : LISTE D'ÉPICERIE
# ==============================
elif st.session_state.page == "liste":
    st.title("🛒 Ma Liste d'Épicerie")
    if not st.session_state.liste_epicerie:
        st.info("Ta liste est vide.")
    else:
        if st.button("🗑️ Vider la liste"):
            st.session_state.liste_epicerie = []
            st.rerun()
        for item in st.session_state.liste_epicerie:
            with st.expander(f"📍 {item['t']}"):
                st.write(item["i"])

# ==============================
# PAGE : ACCUEIL (BIBLIOTHÈQUE)
# ==============================
else:
    st.title("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV)
        df.columns = ['Horodatage', 'Titre', 'Source', 'Ingrédients', 'Préparation', 'Date', 'Image']
        
        cols = st.columns(3)
        for index, row in df.iterrows():
            with cols[index % 3]:
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                img = row["Image"] if str(row["Image"]).startswith("http") else "https://via.placeholder.com/300"
                st.image(img, use_container_width=True)
                st.write(f"**{row['Titre']}**")
                
                if st.button("Voir la fiche", key=f"btn_{index}"):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Erreur de connexion : {e}")
