import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION & DESIGN ÉLÉGANT
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    [data-testid="stImage"] img {
        object-fit: cover;
        height: 250px !important;
        border-radius: 15px;
    }
    .recipe-title { font-weight: 700; font-size: 1.2rem; color: #2c3e50; margin-top: 10px; }
    
    /* Design de la zone d'impression "Fiche Pro" */
    .print-card {
        background-color: white;
        color: #1a1a1a;
        padding: 40px;
        border: 2px solid #eee;
        font-family: 'serif';
        line-height: 1.6;
        max-width: 800px;
        margin: auto;
    }
    .print-header { border-bottom: 3px solid #e67e22; padding-bottom: 10px; margin-bottom: 20px; text-align: center; }
    .print-section { font-weight: bold; color: #e67e22; text-transform: uppercase; margin-top: 25px; border-bottom: 1px solid #eee; }
</style>
""", unsafe_allow_html=True)

# --- CONFIG URLs (Tes liens) ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except:
        return pd.DataFrame()

# Initialisation des variables de session
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "page" not in st.session_state: st.session_state.page = "home"
if "show_print" not in st.session_state: st.session_state.show_print = False

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True): 
        st.session_state.page = "home"; st.session_state.show_print = False; st.rerun()
    if st.button("📅 Mon Planning", use_container_width=True): 
        st.session_state.page = "planning"; st.session_state.show_print = False; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): 
        st.session_state.page = "shopping"; st.session_state.show_print = False; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter", use_container_width=True): 
        st.session_state.page = "add"; st.rerun()
    if st.button("❓ Aide & Tuto", use_container_width=True): 
        st.session_state.page = "aide"; st.rerun()

# ======================================================
# PAGE : BIBLIOTHÈQUE
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if df.empty:
        st.info("Aucune recette trouvée.")
    else:
        c1, c2 = st.columns(2)
        search = c1.text_input("🔍 Rechercher")
        cat_f = c2.selectbox("Catégorie", CATEGORIES)
        filtered = df[df['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": filtered = filtered[filtered['Catégorie'] == cat_f]
        
        grid = st.columns(3)
        for idx, row in filtered.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    img = str(row['Image']) if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                    st.image(img, use_container_width=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()

# ======================================================
# PAGE : DÉTAILS & IMPRESSION
# ======================================================
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    
    if st.session_state.show_print:
        st.markdown(f"""
        <div class="print-card">
            <div class="print-header"><h1>{r['Titre']}</h1></div>
            <div class="print-section">🛒 INGRÉDIENTS</div>
            <p style="white-space: pre-wrap;">{r['Ingrédients']}</p>
            <div class="print-section">🍳 PRÉPARATION</div>
            <p style="white-space: pre-wrap;">{r['Préparation']}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("❌ Quitter l'aperçu"): st.session_state.show_print = False; st.rerun()
        st.write("---")

    if not st.session_state.show_print:
        if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
        st.header(r['Titre'])
        
        colA, colB = st.columns([1, 1.2])
        with colA:
            st.subheader("📅 Planifier")
            d_plan = st.date_input("Pour quand ?")
            if st.button("Enregistrer au planning"):
                requests.post(URL_SCRIPT, json={"action": "plan", "titre": r['Titre'], "date_prevue": d_plan.strftime("%d/%m/%Y")})
                st.success("C'est noté !")
            
            st.write("---")
            st.subheader("🛒 Ingrédients")
            st.write("Cochez ce qu'il vous manque :")
            to_add = []
            for i, line in enumerate(str(r['Ingrédients']).split("\n")):
                if line.strip() and st.checkbox(line.strip(), key=f"chk_{i}"):
                    to_add.append(line.strip())
            
            if st.button("➕ Ajouter à l'épicerie", use_container_width=True):
                for item in to_add:
                    if item not in st.session_state.shopping_list: st.session_state.shopping_list.append(item)
                st.toast("Liste mise à jour !")

        with colB:
            # CORRECTION DU BUG ICI : on utilise r['Image'] au lieu de row['Image']
            img_url = str(r['Image']) if "http" in str(r['Image']) else "https://via.placeholder.com/600"
            st.image(img_url, use_container_width=True)
            if st.button("🖨️ Préparer pour l'impression", use_container_width=True):
                st.session_state.show_print = True; st.rerun()
            st.write("### 📝 Étapes")
            st.write(r['Préparation'])

# ======================================================
# PAGE : ÉPICERIE
# ======================================================
elif st.session_state.page == "shopping":
    st.header("🛒 Ma Liste d'Épicerie")
    if st.button("🗑 Tout effacer"): st.session_state.shopping_list = []; st.rerun()
    
    if not st.session_state.shopping_list:
        st.info("Votre liste est vide.")
    else:
        for idx, item in enumerate(st.session_state.shopping_list):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"✅ **{item}**")
            if c2.button("❌", key=f"del_{idx}"):
                st.session_state.shopping_list.pop(idx); st.rerun()

# ======================================================
# PAGE : AIDE (Mise à jour complète)
# ======================================================
elif st.session_state.page == "aide":
    st.header("❓ Aide & Tutoriel")
    t1, t2, t3 = st.tabs(["🛒 Épicerie", "🖨️ Impression", "📅 Planning"])
    with t1:
        st.write("Dans une recette, cochez les ingrédients manquants et cliquez sur 'Ajouter'. Retrouvez-les ici pour faire vos courses.")
    with t2:
        st.write("Le bouton 'Préparer pour l'impression' crée une fiche propre. Utilisez ensuite le menu de votre navigateur pour 'Imprimer' ou 'Enregistrer en PDF'.")
    with t3:
        st.write("Choisissez une date dans la fiche recette pour l'ajouter à votre calendrier de cuisine.")
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : PLANNING
# ======================================================
elif st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data()
    if not df.empty and 'Date_Prevue' in df.columns:
        plan = df[df['Date_Prevue'] != ''].copy()
        for _, row in plan.iterrows():
            st.warning(f"🗓️ {row['Date_Prevue']} : **{row['Titre']}**")
    else:
        st.info("Planning vide.")

# ======================================================
# PAGE : AJOUTER
# ======================================================
elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    with st.form("add_form"):
        t = st.text_input("Titre")
        c = st.selectbox("Catégorie", CATEGORIES[1:])
        ing = st.text_area("Ingrédients")
        pre = st.text_area("Préparation")
        img = st.text_input("URL Image")
        if st.form_submit_button("Enregistrer"):
            requests.post(URL_SCRIPT, json={"action":"add","titre":t,"ingredients":ing,"preparation":pre,"categorie":c,"image":img,"date":datetime.now().strftime("%d/%m/%Y")})
            st.cache_data.clear(); st.session_state.page = "home"; st.rerun()
