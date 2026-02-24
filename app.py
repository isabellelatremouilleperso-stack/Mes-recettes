import streamlit as st
import requests
import pandas as pd

# 1. Config & Style
st.set_page_config(page_title="Livre de Recettes", page_icon="👩‍🍳", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .recipe-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #eeeeee;
        text-align: center;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
    }
    .fiche-titre { font-size: 38px; font-weight: 800; color: #1f2937; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIG ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# --- INITIALISATION DE LA MÉMOIRE ---
if "page" not in st.session_state:
    st.session_state.page = "home"
if "recipe_data" not in st.session_state:
    st.session_state.recipe_data = None
if "liste_epicerie" not in st.session_state:
    st.session_state.liste_epicerie = []

# --- FONCTIONS DE NAVIGATION ---
def aller_details(row):
    st.session_state.recipe_data = row
    st.session_state.page = "details"

def aller_home():
    st.session_state.page = "home"
    st.session_state.recipe_data = None

# --- MENU LATÉRAL ---
with st.sidebar:
    st.title("👨‍🍳 Menu")
    if st.button("📚 Bibliothèque", use_container_width=True): aller_home()
    if st.button("➕ Ajouter", use_container_width=True): st.session_state.page = "ajouter"
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page = "liste"

# --- PAGES ---

# 1. PAGE DÉTAILS
if st.session_state.page == "details" and st.session_state.recipe_data is not None:
    row = st.session_state.recipe_data
    if st.button("⬅️ Retour"): aller_home()
    
    st.divider()
    col_txt, col_img = st.columns([1.2, 1])
    
    with col_txt:
        st.markdown(f"<div class='fiche-titre'>{row[1]}</div>", unsafe_allow_html=True)
        st.caption(f"📅 Prévue le : {row[5]}")
        st.markdown("### 🛒 Ingrédients")
        
        # Nettoyage et affichage aéré
        items = str(row[3]).split('\n')
        for item in items:
            if item.strip(): st.markdown(f"✅ {item.strip()}")
            
        if st.button("➕ Ajouter à l'épicerie", type="primary"):
            st.session_state.liste_epicerie.append({"nom": row[1], "ing": row[3]})
            st.toast("Ajouté !")

    with col_img:
        # Gestion sécurisée de l'image
        img_url = row[6] if len(row) > 6 and pd.notna(row[6]) else ""
        if str(img_url).startswith("http"):
            st.image(img_url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/500x400?text=Image+indisponible")

    st.markdown("### 👨‍🍳 Préparation")
    st.info(row[4])

# 2. PAGE BIBLIOTHÈQUE
elif st.session_state.page == "home":
    st.title("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV)
        # On s'assure que les colonnes sont bien lues
        cols = st.columns(3)
        for index, row in df.iterrows():
            with cols[index % 3]:
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                img = row.iloc[6] if len(row) > 6 and pd.notna(row.iloc[6]) else ""
                if str(img).startswith("http"):
                    st.image(img, use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/300x200?text=Pas+de+photo")
                
                st.markdown(f"**{row.iloc[1]}**")
                # Correction majeure : on passe les valeurs de la ligne, pas l'objet complexe
                if st.button("Voir la fiche", key=f"btn_{index}"):
                    aller_details(row.values)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.error("Chargement du livre...")

# 3. PAGE ÉPICERIE
elif st.session_state.page == "liste":
    st.title("🛒 Ma Liste d'Épicerie")
    if not st.session_state.liste_epicerie:
        st.write("Votre liste est vide.")
    else:
        if st.button("Vider la liste"):
            st.session_state.liste_epicerie = []
            st.rerun()
        for item in st.session_state.liste_epicerie:
            with st.expander(f"📍 {item['nom']}"):
                st.write(item['ing'])

# 4. PAGE AJOUTER
elif st.session_state.page == "ajouter":
    st.title("➕ Nouvelle Recette")
    with st.form("add_form"):
        t = st.text_input("Titre")
        img = st.text_input("Lien image")
        ing = st.text_area("Ingrédients")
        prep = st.text_area("Préparation")
        if st.form_submit_button("Enregistrer"):
            requests.post(URL_SCRIPT, json={"titre":t, "image":img, "ingredients":ing, "preparation":prep})
            st.success("Enregistré !")
