import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# 1. CONFIGURATION & STYLE
st.set_page_config(page_title="Mes Recettes Pro", layout="wide")
st.markdown("""<style>
    .stApp { background-color: #0d1117; color: #e6edf3; }
    .recipe-card { background: #21262d; border-radius: 15px; padding: 15px; text-align: center; border: 1px solid #30363d; }
    .ps-header { background: linear-gradient(135deg, #1e293b, #0f172a); padding: 30px; border-radius: 20px; text-align: center; }
</style>""", unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

def run_action(payload):
    try:
        r = requests.post(URL_SCRIPT, json=payload, timeout=20)
        if "Success" in r.text: st.cache_data.clear(); return True
    except: return False
    return False

@st.cache_data(ttl=5)
def load_data(url):
    try:
        df = pd.read_csv(f"{url}&nocache={time.time()}").fillna('')
        if "gid=0" in url:
            df.columns = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires','Note','Video'][:len(df.columns)]
        return df
    except: return pd.DataFrame()

# 2. NAVIGATION
if "page" not in st.session_state: st.session_state.page = "home"
with st.sidebar:
    st.title("👨‍🍳 Menu")
    if st.button("📚 Bibliothèque"): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning"): st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Épicerie"): st.session_state.page = "shop"; st.rerun()
    if st.button("➕ AJOUTER", type="primary"): st.session_state.page = "add"; st.rerun()
    if st.button("⭐ Play Store"): st.session_state.page = "playstore"; st.rerun()

# 3. PAGES
if st.session_state.page == "home":
    st.header("📚 Mes Recettes")
    df = load_data(URL_CSV)
    search = st.text_input("🔍 Chercher...")
    if not df.empty:
        filt = df[df['Titre'].str.contains(search, case=False)]
        for i in range(0, len(filt), 3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(filt):
                    r = filt.iloc[i+j]
                    with cols[j]:
                        st.markdown(f'<div class="recipe-card"><b>{r["Titre"]}</b></div>', unsafe_allow_html=True)
                        if st.button("Voir", key=f"v_{i+j}"): st.session_state.recipe_data = r.to_dict(); st.session_state.page = "details"; st.rerun()

elif st.session_state.page == "add":
    st.header("➕ Nouvelle Recette")
    with st.form("add_form"):
        f_t = st.text_input("Titre")
        f_i = st.text_area("Ingrédients")
        f_p = st.text_area("Préparation")
        if st.form_submit_button("🚀 Enregistrer"):
            if run_action({"action":"add","titre":f_t,"ingredients":f_i,"preparation":f_p,"date":datetime.now().strftime("%d/%m/%Y")}):
                st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data(URL_CSV)
    plan = df[df['Date_Prevue'].astype(str).str.strip() != ""]
    for _, row in plan.iterrows(): st.write(f"📌 {row['Date_Prevue']} : {row['Titre']}")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "shop":
    st.header("🛒 Épicerie")
    df_s = load_data(URL_CSV_SHOP)
    for idx, row in df_s.iterrows():
        if st.button(f"🗑️ {row.iloc[0]}", key=f"s_{idx}"):
            if run_action({"action":"delete_shop","article":row.iloc[0]}): st.rerun()
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "playstore":
    st.markdown('<div class="ps-header"><h1>🍳 Mes Recettes Pro</h1><p>⭐ 4.9 | 📥 10k+</p></div>', unsafe_allow_html=True)
    st.image(["https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg", "https://i.postimg.cc/YCkg460C/shared-image-(5).jpg"])
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    st.header(r['Titre'])
    st.write(r['Préparation'])
    if st.button("🗑️ Supprimer"):
        if run_action({"action":"delete","titre":r['Titre']}): st.session_state.page = "home"; st.rerun()
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
