import streamlit as st
import requests
import pandas as pd

# 1. CONFIGURATION ET STYLE BLANC ÉPURÉ
st.set_page_config(page_title="Mon Livre de Recettes", page_icon="👩‍🍳", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .recipe-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #f0f0f0;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    .fiche-titre { font-size: 42px; font-weight: 800; color: #1f2937; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LIENS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# --- MÉMOIRE DE L'APPLI ---
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "liste_epicerie" not in st.session_state: st.session_state.liste_epicerie = []

# --- NAVIGATION ---
def aller_home():
    st.session_state.page = "home"
    st.session_state.recipe_data = None

# --- MENU LATÉRAL ---
with st.sidebar:
    st.title("👩‍🍳 Menu")
    if st.button("📚 Ma Bibliothèque", use_container_width=True): aller_home(); st.rerun()
    if st.button("➕ Ajouter une recette", use_container_width=True): st.session_state.page = "ajouter"; st.rerun()
    if st.button("🛒 Ma Liste d'Épicerie", use_container_width=True): st.session_state.page = "liste"; st.rerun()

# --- PAGES ---

# 1. PAGE DÉTAILS (CORRIGÉE)
if st.session_state.page == "details" and st.session_state.recipe_data is not None:
    row = st.session_state.recipe_data
    if st.button("⬅️ Retour à la bibliothèque"): aller_home(); st.rerun()
    
    st.divider()
    col_txt, col_img = st.columns([1.2, 1])
    
    with col_txt:
        st.markdown(f"<div class='fiche-titre'>{row[1]}</div>", unsafe_allow_html=True)
        st.caption(f"📅 Planifié pour le : {row[5]}")
        
        st.markdown("### 🛒 Ingrédients")
        # On affiche chaque ligne d'ingrédient proprement
        lignes = str(row[3]).split('\n')
        for l in lignes:
            if l.strip(): st.markdown(f"✅ {l.strip()}")
        
        if st.button("🛒 Ajouter à ma liste d'épicerie", type="primary"):
            st.session_state.liste_epicerie.append({"titre": row[1], "items": row[3]})
            st.toast("Ajouté !")

    with col_img:
        img_url = row[6] if len(row) > 6 and pd.notna(row[6]) else ""
        if str(img_url).startswith("http"):
            st.image(img_url, use_container_width=True)
        else:
            st.image("https://via.placeholder.com/600x450?text=Image+Recette")

    st.divider()
    st.markdown("### 👨‍🍳 Préparation")
    st.write(row[4] if pd.notna(row[4]) else "Aucune instruction.")

# 2. PAGE BIBLIOTHÈQUE
elif st.session_state.page == "home":
    st.title("📚 Ma Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV)
        cols = st.columns(3)
        for index, row in df.iterrows():
            with cols[index % 3]:
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                img = row.iloc[6] if len(row) > 6 and pd.notna(row.iloc[6]) else ""
                st.image(img if str(img).startswith("http") else "https://via.placeholder.com/300", use_container_width=True)
                st.markdown(f"**{row.iloc[1]}**")
                if st.button("Voir la fiche", key=f"btn_{index}"):
                    # ON SAUVEGARDE TOUTES LES DONNÉES AVANT DE CHANGER
                    st.session_state.recipe_data = list(row)
                    st.session_state.page = "details"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    except:
        st.error("Connexion au livre...")

# 3. PAGE ÉPICERIE
elif st.session_state.page == "liste":
    st.title("🛒 Ma Liste d'Épicerie")
    if not st.session_state.liste_epicerie:
        st.info("Liste vide.")
    else:
        if st.button("Vider"): st.session_state.liste_epicerie = []; st.rerun()
        for lot in st.session_state.liste_epicerie:
            with st.expander(f"📍 {lot['titre']}"): st.write(lot['items'])

# 4. PAGE AJOUTER
elif st.session_state.page == "ajouter":
    st.title("➕ Ajouter")
    with st.form("add"):
        t = st.text_input("Plat")
        i = st.text_input("Lien image")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Préparation")
        if st.form_submit_button("Enregistrer"):
            requests.post(URL_SCRIPT, json={"titre":t, "image":i, "ingredients":ing, "preparation":pre})
            st.success("Enregistré !")
