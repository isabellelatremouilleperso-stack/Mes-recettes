import streamlit as st
import requests
import pandas as pd

# 1. STYLE ÉPURÉ
st.set_page_config(page_title="Livre de Recettes", page_icon="👩‍🍳", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .recipe-card {
        background-color: #ffffff; border-radius: 15px; padding: 20px;
        border: 1px solid #f0f0f0; text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.03); margin-bottom: 20px;
    }
    .fiche-titre { font-size: 42px; font-weight: 800; color: #1f2937; }
    </style>
    """, unsafe_allow_html=True)

# --- LIENS (À VÉRIFIER) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

# --- MÉMOIRE ---
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = None
if "liste_epicerie" not in st.session_state: st.session_state.liste_epicerie = []

# --- MENU ---
with st.sidebar:
    st.title("👩‍🍳 Menu")
    if st.button("📚 Bibliothèque"): st.session_state.page = "home"; st.rerun()
    if st.button("➕ Ajouter"): st.session_state.page = "ajouter"; st.rerun()
    if st.button("🛒 Épicerie"): st.session_state.page = "liste"; st.rerun()

# --- PAGES ---

# 1. PAGE AJOUTER (Placée en haut pour être prioritaire)
if st.session_state.page == "ajouter":
    st.title("➕ Nouvelle Recette")
    with st.form("form_add", clear_on_submit=True):
        t = st.text_input("Nom du plat")
        i = st.text_input("Lien image")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Préparation")
        if st.form_submit_button("🚀 Enregistrer"):
            if t:
                requests.post(URL_SCRIPT, json={"titre":t, "image":i, "ingredients":ing, "preparation":pre})
                st.success("Enregistré ! Retourne à la bibliothèque.")
                st.balloons()

# 2. PAGE DÉTAILS
elif st.session_state.page == "details":
    if st.session_state.recipe_data is not None:
        row = st.session_state.recipe_data
        st.button("⬅️ Retour", on_click=lambda: st.session_state.update({"page": "home"}))
        st.markdown(f"<div class='fiche-titre'>{row[1]}</div>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### 🛒 Ingrédients")
            for l in str(row[3]).split('\n'):
                if l.strip(): st.write(f"✅ {l.strip()}")
            if st.button("➕ Ajouter à l'épicerie"):
                st.session_state.liste_epicerie.append({"t": row[1], "i": row[3]})
                st.toast("Ajouté !")
        with col2:
            if str(row[6]).startswith("http"): st.image(row[6], use_container_width=True)
        st.markdown("### 👨‍🍳 Préparation")
        st.info(row[4])
    else:
        st.session_state.page = "home"
        st.rerun()

# 3. PAGE ÉPICERIE
elif st.session_state.page == "liste":
    st.title("🛒 Ma Liste")
    if not st.session_state.liste_epicerie: st.info("Vide")
    else:
        for item in st.session_state.liste_epicerie:
            with st.expander(f"📍 {item['t']}"): st.write(item['i'])
        if st.button("Vider"): st.session_state.liste_epicerie = []; st.rerun()

# 4. PAGE ACCUEIL
else:
    st.title("📚 Bibliothèque")
    try:
        df = pd.read_csv(URL_CSV)
        cols = st.columns(3)
        for index, row in df.iterrows():
            with cols[index % 3]:
                st.markdown('<div class="recipe-card">', unsafe_allow_html=True)
                img = row.iloc[6] if len(row) > 6 and str(row.iloc[6]).startswith("http") else "https://via.placeholder.com/200"
                st.image(img, use_container_width=True)
                st.write(f"**{row.iloc[1]}**")
                if st.button("Voir la fiche", key=f"btn_{index}"):
                    st.session_state.recipe_data = list(row)
                    st.session_state.page = "details"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error("⚠️ Problème de connexion au Google Sheets.")
        st.info("Vérifiez que le fichier est bien 'Publié sur le Web' en format CSV.")
