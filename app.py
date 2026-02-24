import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION & DESIGN PREMIUM
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    /* Global */
    .stApp { background-color: #f4f7f6; }
    
    /* Cartes Bibliothèque */
    .recipe-card {
        background-color: white;
        border-radius: 15px;
        padding: 0px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 1px solid #e0e0e0;
    }
    .recipe-img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        border-radius: 15px 15px 0 0;
    }
    .recipe-content {
        padding: 15px;
        text-align: center;
    }
    .recipe-title-text {
        font-weight: 800;
        font-size: 1.1rem;
        color: #2c3e50;
        margin-bottom: 10px;
        min-height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Boîtes d'Aide */
    .help-box { 
        background-color: #ffffff; color: #1a1a1a !important; 
        padding: 25px; border-radius: 12px; border-left: 10px solid #e67e22; 
        margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .help-box h3 { color: #e67e22 !important; font-weight: 700; margin-bottom: 10px; }
    .help-box p { color: #333 !important; font-size: 1rem; line-height: 1.5; }
</style>
""", unsafe_allow_html=True)

# --- LIENS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

def load_data():
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= len(expected): df.columns = expected[:len(df.columns)]
        return df
    except: return pd.DataFrame()

# Session States
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
    if st.button("➕ Ajouter une recette", use_container_width=True, type="primary"): 
        st.session_state.page = "add"; st.rerun()
    if st.button("❓ Aide & Tutoriel", use_container_width=True): 
        st.session_state.page = "aide"; st.rerun()
    st.write("---")
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()

# ======================================================
# PAGE : BIBLIOTHÈQUE (GRILLE MODERNE)
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    
    if df.empty:
        st.info("Recherche de vos recettes en cours...")
    else:
        search = st.text_input("🔍 Rechercher une recette", placeholder="Ex: Poulet, Pâtes...")
        filtered = df[df['Titre'].str.contains(search, case=False)]
        
        st.write("##")
        cols = st.columns(3)
        for idx, row in filtered.reset_index(drop=True).iterrows():
            with cols[idx % 3]:
                # Affichage de la carte
                img_url = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                st.markdown(f"""
                <div class="recipe-card">
                    <img src="{img_url}" class="recipe-img">
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<div class='recipe-title-text'>{row['Titre']}</div>", unsafe_allow_html=True)
                if st.button("Voir la recette", key=f"btn_{idx}", use_container_width=True):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"; st.rerun()
                st.write("###")

# ======================================================
# PAGE : DÉTAILS
# ======================================================
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.header(f"🍳 {r['Titre']}")
    col1, col2 = st.columns([1, 1.2])
    
    with col1:
        st.subheader("⭐ Avis & Notes")
        st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"])
        st.checkbox("✅ Recette faite", value=False)
        notes = st.text_area("Mes commentaires", value=r.get('Commentaires', ''), height=100)
        if st.button("💾 Sauvegarder les notes"):
            requests.post(URL_SCRIPT, json={"action": "update_notes", "titre": r['Titre'], "commentaires": notes})
            st.success("Enregistré !")

        st.write("---")
        st.subheader("📅 Planning")
        d_plan = st.date_input("Planifier pour le :", value=datetime.now())
        if st.button("Mettre au planning"):
            requests.post(URL_SCRIPT, json={"action": "plan", "titre": r['Titre'], "date_prevue": d_plan.strftime("%d/%m/%Y")})
            st.success("Planning mis à jour !")

    with col2:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/600", use_container_width=True)
        st.subheader("🛒 Ingrédients")
        ing_list = str(r['Ingrédients']).split("\n")
        selection = []
        for i, line in enumerate(ing_list):
            if line.strip() and st.checkbox(line.strip(), key=f"ing_{i}"):
                selection.append(line.strip())
        
        if st.button("➕ Ajouter à l'épicerie", use_container_width=True):
            st.session_state.shopping_list.extend([x for x in selection if x not in st.session_state.shopping_list])
            st.toast("Liste mise à jour !")

        st.write("---")
        st.subheader("📝 Étapes de préparation")
        st.write(r['Préparation'])

# ======================================================
# PAGE : AIDE (BOITES BLANCHES TEXTE NOIR)
# ======================================================
elif st.session_state.page == "aide":
    st.header("❓ Aide & Tutoriel")
    
    st.markdown("""
    <div class="help-box">
        <h3>🚀 Bibliothèque & Design</h3>
        <p>Vos recettes sont présentées sous forme de fiches visuelles. Cliquez sur <b>Voir la recette</b> pour ouvrir le détail, noter le plat ou planifier votre repas.</p>
    </div>
    <div class="help-box">
        <h3>🛒 Liste d'Épicerie</h3>
        <p>Dans chaque recette, cochez les ingrédients qu'il vous manque et cliquez sur <b>Ajouter à l'épicerie</b>. Le menu à gauche affiche le nombre d'articles dans votre panier.</p>
    </div>
    <div class="help-box">
        <h3>⭐ Notes & Évaluation</h3>
        <p>Vous pouvez noter vos plats et écrire vos propres astuces. N'oubliez pas de cliquer sur <b>Sauvegarder les notes</b> pour que vos commentaires soient enregistrés dans votre fichier Google.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : AJOUTER
#
