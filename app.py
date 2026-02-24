import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION & DESIGN SOMBRE PREMIUM
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    /* Fond noir global */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* Cartes Bibliothèque */
    .recipe-card-box {
        background-color: #1e2129;
        border-radius: 15px;
        border: 1px solid #3d4455;
        margin-bottom: 10px;
        overflow: hidden;
        transition: transform 0.3s;
    }
    .recipe-card-box:hover { transform: scale(1.02); border-color: #e67e22; }
    .recipe-img { width: 100%; height: 200px; object-fit: cover; }
    .recipe-title-text {
        font-weight: 700; font-size: 1.1rem; color: #ffffff;
        padding: 15px; text-align: center; min-height: 60px;
        display: flex; align-items: center; justify-content: center;
    }

    /* Boîtes d'Aide - Grille Sombre */
    .help-box { 
        background-color: #262730; color: #ffffff !important; 
        padding: 20px; border-radius: 12px; border-left: 8px solid #e67e22; 
        margin-bottom: 20px; min-height: 180px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .help-box h3 { color: #e67e22 !important; margin-top: 0; font-size: 1.2rem; }
    .help-box p { font-size: 0.95rem; line-height: 1.4; color: #e0e0e0; }
    
    /* Style des boutons et inputs */
    .stButton>button { border-radius: 8px; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #262730 !important; color: white !important;
    }
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

# Initialisation de l'état
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "page" not in st.session_state: st.session_state.page = "home"

# ======================================================
# BARRE LATÉRALE (SIDEBAR)
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
    st.write("---")
    if st.button("🔄 Actualiser", use_container_width=True):
        st.cache_data.clear(); st.rerun()

# ======================================================
# PAGE : BIBLIOTHÈQUE
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if not df.empty:
        search = st.text_input("🔍 Rechercher une recette...", placeholder="Tapez un nom...")
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
                if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"; st.rerun()
                st.write("###")
    else: st.info("Votre bibliothèque semble vide.")

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
        note = st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"])
        fait = st.checkbox("✅ Recette déjà cuisinée")
        mes_notes = st.text_area("Mes astuces personnelles", value=r.get('Commentaires', ''))
        if st.button("💾 Sauvegarder les notes"):
            requests.post(URL_SCRIPT, json={"action": "update_notes", "titre": r['Titre'], "commentaires": mes_notes})
            st.success("Notes enregistrées !")

        st.write("---")
        st.subheader("📅 Planifier")
        d = st.date_input("Date prévue :", value=datetime.now())
        if st.button("Ajouter au planning"):
            requests.post(URL_SCRIPT, json={"action": "plan", "titre": r['Titre'], "date_prevue": d.strftime("%d/%m/%Y")})
            st.success("Planifié !")

    with c2:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/600", use_container_width=True)
        st.subheader("🛒 Ingrédients")
        for i, line in enumerate(str(r['Ingrédients']).split("\n")):
            if line.strip() and st.checkbox(line.strip(), key=f"ing_{i}"):
                if line.strip() not in st.session_state.shopping_list:
                    st.session_state.shopping_list.append(line.strip())
        st.write("---")
        st.subheader("📝 Préparation")
        st.write(r['Préparation'])

# ======================================================
# PAGE : AJOUTER
# ======================================================
elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    with st.form("form_add"):
        t = st.text_input("Titre de la recette")
        c = st.selectbox("Catégorie", CATEGORIES[1:])
        s = st.text_input("Lien Source (Instagram, TikTok, Blog...)")
        i = st.text_input("URL de l'image")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Préparation (étapes)")
        if st.form_submit_button("💾 Enregistrer la recette"):
            requests.post(URL_SCRIPT, json={"action":"add","titre":t,"source":s,"ingredients":ing,"preparation":pre,"categorie":c,"image":i,"date":datetime.now().strftime("%d/%m/%Y")})
            st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : AIDE (EN BOITES / GRILLE)
# ======================================================
elif st.session_state.page == "aide":
    st.header("❓ Centre d'Aide")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="help-box"><h3>📝 Ajouter</h3><p>Remplissez le formulaire. Pour l\'image, copiez le lien d\'une photo sur le web. N\'oubliez pas la <b>Source</b> pour revoir la vidéo Instagram !</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="help-box"><h3>🛒 Épicerie</h3><p>Cochez les ingrédients manquants dans une recette. Ils s\'ajoutent à votre liste globale accessible via le menu.</p></div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="help-box"><h3>📅 Planning</h3><p>Choisissez une date dans la fiche recette. Elle apparaîtra dans l\'onglet Planning pour organiser votre semaine.</p></div>', unsafe_allow_html=True)
        st.markdown('<div class="help-box"><h3>⭐ Notes</h3><p>Évaluez vos plats et écrivez vos remarques. Cliquez sur <b>Sauvegarder</b> pour ne jamais perdre vos astuces.</p></div>', unsafe_allow_html=True)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# ======================================================
# PLANNING & ÉPICERIE
# ======================================================
elif st.session_state.page == "planning":
    st.header("📅 Mon Planning Cuisine")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ''].copy()
        if plan.empty: st.info("Aucun repas planifié.")
        for _, row in plan.iterrows():
            with st.container(border=True):
                st.write(f"🗓️ **{row['Date_Prevue']}** : {row['Titre']}")
                if st.button("Voir", key=f"plan_{row['Titre']}"):
                    st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

elif st.session_state.page == "shopping":
    st.header("🛒 Ma Liste de Courses")
    if st.button("🗑 Tout vider"): st.session_state.shopping_list = []; st.rerun()
    for idx, item in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([5, 1])
        c1.write(f"✅ {item}")
        if c2.button("❌", key=f"sh_{idx}"): st.session_state.shopping_list.pop(idx); st.rerun()
