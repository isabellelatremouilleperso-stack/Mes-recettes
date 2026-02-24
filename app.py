import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION & DESIGN MODE SOMBRE
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    /* Force le fond sombre sur toute l'application */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Cartes de la Bibliothèque - Design Épuré */
    .recipe-card-box {
        background-color: #1e2129;
        border-radius: 15px;
        border: 1px solid #3d4455;
        margin-bottom: 10px;
        overflow: hidden;
    }
    .recipe-img {
        width: 100%;
        height: 180px;
        object-fit: cover;
    }
    .recipe-title-text {
        font-weight: 700;
        font-size: 1.1rem;
        color: #ffffff;
        padding: 12px;
        text-align: center;
        min-height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Boîtes d'Aide - Fond gris foncé, texte blanc */
    .help-box { 
        background-color: #262730; 
        color: #ffffff !important; 
        padding: 20px; 
        border-radius: 12px; 
        border-left: 8px solid #e67e22; 
        margin-bottom: 20px; 
    }
    .help-box h3 { color: #e67e22 !important; margin-top: 0; }
    
    /* Inputs du formulaire */
    input, textarea { background-color: #262730 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- CONFIG URLs ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

@st.cache_data(ttl=30)
def load_data():
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= len(expected): df.columns = expected[:len(df.columns)]
        return df
    except: return pd.DataFrame()

# Initialisation de la navigation
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "page" not in st.session_state: st.session_state.page = "home"

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True): 
        st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): 
        st.session_state.page = "planning"; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): 
        st.session_state.page = "shopping"; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter", use_container_width=True, type="primary"): 
        st.session_state.page = "add"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): 
        st.session_state.page = "aide"; st.rerun()

# ======================================================
# PAGE : BIBLIOTHÈQUE (HOME)
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    
    if not df.empty:
        search = st.text_input("🔍 Rechercher", placeholder="Ex: Poulet, Gâteau...")
        filtered = df[df['Titre'].str.contains(search, case=False)]
        
        cols = st.columns(3)
        for idx, row in filtered.reset_index(drop=True).iterrows():
            with cols[idx % 3]:
                img_url = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                st.markdown(f"""
                <div class="recipe-card-box">
                    <img src="{img_url}" class="recipe-img">
                    <div class="recipe-title-text">{row['Titre']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Voir la recette", key=f"btn_{idx}", use_container_width=True):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"; st.rerun()
                st.write("###")
    else:
        st.info("Aucune recette trouvée.")

# ======================================================
# PAGE : DÉTAILS
# ======================================================
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.header(f"🍳 {r['Titre']}")
    c1, c2 = st.columns([1, 1.2])
    
    with c1:
        st.subheader("⭐ Avis & Notes")
        st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"])
        st.checkbox("✅ Recette déjà faite")
        mes_notes = st.text_area("Notes personnelles", value=r.get('Commentaires', ''))
        if st.button("💾 Sauvegarder"):
            requests.post(URL_SCRIPT, json={"action": "update_notes", "titre": r['Titre'], "commentaires": mes_notes})
            st.success("Notes enregistrées !")

        st.write("---")
        st.subheader("📅 Planning")
        d = st.date_input("Pour quand ?", value=datetime.now())
        if st.button("Planifier"):
            requests.post(URL_SCRIPT, json={"action": "plan", "titre": r['Titre'], "date_prevue": d.strftime("%d/%m/%Y")})
            st.success("Ajouté au calendrier !")

    with c2:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/600", use_container_width=True)
        st.subheader("🛒 Épicerie")
        for i, line in enumerate(str(r['Ingrédients']).split("\n")):
            if line.strip() and st.checkbox(line.strip(), key=f"i_{i}"):
                if line.strip() not in st.session_state.shopping_list:
                    st.session_state.shopping_list.append(line.strip())
        st.write("### 📝 Préparation")
        st.write(
