import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION & STYLE (RETOUR AU BEAU DESIGN)
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    /* Cartes de la bibliothèque */
    [data-testid="stImage"] img { 
        object-fit: cover; 
        height: 220px !important; 
        width: 100% !important;
        border-radius: 15px 15px 0 0; 
    }
    .recipe-card {
        background-color: #ffffff;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        padding: 0px;
        margin-bottom: 20px;
        transition: transform 0.2s;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .recipe-title { 
        font-weight: 700; 
        font-size: 1.1rem; 
        color: #2c3e50; 
        padding: 15px;
        text-align: center;
        min-height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Boîtes d'aide */
    .help-box { 
        background-color: #ffffff; color: #1a1a1a !important; 
        padding: 20px; border-radius: 10px; border-left: 8px solid #e67e22; 
        margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .help-box h3 { color: #e67e22 !important; margin-top: 0; }
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
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except:
        return pd.DataFrame()

# Initialisation
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "page" not in st.session_state: st.session_state.page = "home"

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True): 
        st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): 
        st.session_state.page = "planning"; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): 
        st.session_state.page = "shopping"; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter une recette", use_container_width=True, type="primary"): 
        st.session_state.page = "add"; st.rerun()
    if st.button("❓ Aide & Tutoriel", use_container_width=True): 
        st.session_state.page = "aide"; st.rerun()

# ======================================================
# PAGE : BIBLIOTHÈQUE (RETOUR AU DESIGN ÉLÉGANT)
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    
    if df.empty:
        st.info("Chargement de vos recettes...")
        st.rerun()
    else:
        search = st.text_input("🔍 Rechercher une recette...", label_visibility="collapsed")
        filtered = df[df['Titre'].str.contains(search, case=False)]
        
        st.write("##")
        grid = st.columns(3)
        for idx, row in filtered.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                # On crée une "carte" visuelle
                with st.container():
                    img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                    st.image(img, use_container_width=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Voir la recette", key=f"h_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()
                st.write("---")

# ======================================================
# PAGE : DÉTAILS (Étoiles, Notes, Planning)
# ======================================================
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour à la liste"): st.session_state.page = "home"; st.rerun()
    
    st.header(f"🍳 {r['Titre']}")
    colA, colB = st.columns([1, 1.3])
    
    with colA:
        st.subheader("⭐ Évaluation")
        st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"])
        st.checkbox("✅ Déjà cuisiné")
        notes = st.text_area("📝 Mes astuces / commentaires", value=r.get('Commentaires', ''), height=150)
        if st.button("💾 Enregistrer mes notes"):
            requests.post(URL_SCRIPT, json={"action": "update_notes", "titre": r['Titre'], "commentaires": notes})
            st.success("Notes sauvegardées !")

        st.write("---")
        st.subheader("📅 Planifier")
        d_plan = st.date_input("Choisir une date", value=datetime.now())
        if st.button("Ajouter au planning"):
            requests.post(URL_SCRIPT, json={"action": "plan", "titre": r['Titre'], "date_prevue": d_plan.strftime("%d/%m/%Y")})
            st.success(f"Prévu pour le {d_plan.strftime('%d/%m/%Y')} !")

    with colB:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/600", use_container_width=True)
        
        st.subheader("🛒 Ingrédients")
        st.info("Cochez pour ajouter à votre liste d'épicerie :")
        ing_lines = str(r['Ingrédients']).split("\n")
        to_add = []
        for i, line in enumerate(ing_lines):
            if line.strip() and st.checkbox(line.strip(), key=f"ing_{i}"):
                to_add.append(line.strip())
        
        if st.button("➕ Ajouter la sélection à l'épicerie", use_container_width=True):
            st.session_state.shopping_list.extend([x for x in to_add if x not in st.session_state.shopping_list])
            st.toast("Liste mise à jour !")

        st.write("---")
        st.subheader("📝 Préparation")
        st.write(r['Préparation'])

# ======================================================
# PAGE : AJOUTER (AVEC BOUTON SUBMIT)
# ======================================================
elif st.session_state.page == "add":
    st.header("➕ Ajouter une nouvelle pépite")
    with st.form("form_ajout"):
        t = st.text_input("Titre de la recette")
        c = st.selectbox("Catégorie", CATEGORIES[1:])
        s = st.text_input("Source (Instagram, TikTok, Blog...)")
        i = st.text_input("URL de l'image (Lien)")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Étapes de préparation")
        
        submitted = st.form_submit_button("💾 Enregistrer dans ma bibliothèque")
        if submitted:
            requests.post(URL_SCRIPT, json={"action":"add","titre":t,"source":s,"ingredients":ing,"preparation":pre,"categorie":c,"image":i,"date":datetime.now().strftime("%d/%m/%Y")})
            st.cache_data.clear()
            st.session_state.page = "home"
            st.rerun()

# ======================================================
# PAGE : AIDE (BOITES)
# ======================================================
elif st.session_state.page == "aide":
    st.header("❓ Aide & Tutoriel")
    st.markdown("""
    <div class="help-box">
        <h3>🚀 Ajouter une recette</h3>
        <p>Utilisez le formulaire <b>Ajouter</b>. N'oubliez pas de mettre le lien <b>Source</b> (Instagram/TikTok) pour retrouver la vidéo plus tard !</p>
    </div>
    <div class="help-box">
        <h3>⭐ Évaluation & Notes</h3>
        <p>Notez vos recettes et écrivez vos changements dans la zone <b>Notes</b>. Cliquez bien sur le bouton de sauvegarde pour mettre à jour votre fichier Google.</p>
    </div>
    <div class="help-box">
        <h3>📅 Planning</h3>
        <p>Le planning vous permet de prévoir vos repas. Les recettes planifiées s'affichent dans l'onglet <b>Mon Planning</b>.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# ======================================================
# PLANNING & SHOPPING
# ======================================================
elif st.session_state.page == "planning":
    st.header("📅 Mon Planning")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ''].copy()
        for _, row in plan.iterrows():
            st.success(f"🗓️ **{row['Date_Prevue']}** : {row['Titre']}")
    else: st.info("Rien de prévu pour le moment.")

elif st.session_state.page == "shopping":
    st.header("🛒 Liste d'Épicerie")
    if st.button("🗑 Vider la liste"): st.session_state.shopping_list = []; st.rerun()
    for idx, item in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([5, 1])
        c1.write(f"✅ **{item}**")
        if c2.button("❌", key=f"s_{idx}"): st.session_state.shopping_list.pop(idx); st.rerun()
