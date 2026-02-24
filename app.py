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
    /* Design des cartes */
    [data-testid="stImage"] img {
        object-fit: cover;
        height: 250px !important;
        border-radius: 15px;
    }
    .recipe-title { font-weight: 700; font-size: 1.2rem; color: #2c3e50; margin-top: 10px; }
    
    /* Design de la zone d'impression "Jolie" */
    .print-card {
        background-color: white;
        color: #1a1a1a;
        padding: 40px;
        border-radius: 0px;
        border: 1px solid #eee;
        font-family: 'Segoe UI', Roboto, Helvetica, sans-serif;
        line-height: 1.6;
        box-shadow: 0 0 20px rgba(0,0,0,0.05);
        max-width: 800px;
        margin: auto;
    }
    .print-header { border-bottom: 2px solid #e67e22; padding-bottom: 10px; margin-bottom: 20px; text-align: center; }
    .print-section { font-weight: bold; color: #e67e22; text-transform: uppercase; margin-top: 20px; font-size: 0.9rem; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

# --- CONFIG URLs ---
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

# Initialisation persistante de la liste d'épicerie
if "shopping_list" not in st.session_state:
    st.session_state.shopping_list = []
if "page" not in st.session_state:
    st.session_state.page = "home"
if "show_print" not in st.session_state:
    st.session_state.show_print = False

# ======================================================
# BARRE LATÉRALE
# ======================================================
with st.sidebar:
    st.title("🍳 Ma Cuisine")
    if st.button("📚 Ma Bibliothèque", use_container_width=True): 
        st.session_state.page = "home"; st.session_state.show_print = False; st.rerun()
    if st.button("📅 Mon Planning", use_container_width=True): 
        st.session_state.page = "planning"; st.session_state.show_print = False; st.rerun()
    if st.button("🛒 Liste d'Épicerie (" + str(len(st.session_state.shopping_list)) + ")", use_container_width=True): 
        st.session_state.page = "shopping"; st.session_state.show_print = False; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter une recette", use_container_width=True): 
        st.session_state.page = "add"; st.session_state.show_print = False; st.rerun()
    if st.button("❓ Aide", use_container_width=True): 
        st.session_state.page = "aide"; st.session_state.show_print = False; st.rerun()

# ======================================================
# PAGE : BIBLIOTHÈQUE
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if df.empty:
        st.info("Votre bibliothèque est vide. Ajoutez votre première recette !")
    else:
        c1, c2 = st.columns(2)
        search = c1.text_input("🔍 Rechercher...")
        cat_f = c2.selectbox("Catégorie", CATEGORIES)
        
        filtered = df.copy()
        if search: filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": filtered = filtered[filtered['Catégorie'] == cat_f]
        
        grid = st.columns(3)
        for idx, row in filtered.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    img = str(row['Image']) if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                    st.image(img, use_container_width=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Voir la recette", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()

# ======================================================
# PAGE : DÉTAILS & IMPRESSION DESIGN
# ======================================================
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    
    if st.session_state.show_print:
        st.markdown(f"""
        <div class="print-card">
            <div class="print-header">
                <h1 style="margin-bottom:0; color:#e67e22;">{r['Titre']}</h1>
                <p style="color:#7f8c8d; font-style:italic;">Mes Recettes Pro</p>
            </div>
            <div class="print-section">🛒 Ingrédients</div>
            <p style="white-space: pre-wrap;">{r['Ingrédients']}</p>
            <div class="print-section">🍳 Préparation</div>
            <p style="white-space: pre-wrap;">{r['Préparation']}</p>
            {f'<div class="print-section">📝 Notes</div><p>{r["Commentaires"]}</p>' if r['Commentaires'] else ''}
        </div>
        """, unsafe_allow_html=True)
        if st.button("⬅ Quitter l'aperçu et revenir à la fiche"):
            st.session_state.show_print = False; st.rerun()
        st.write("---")

    if not st.session_state.show_print:
        if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
        st.header(r['Titre'])
        
        colA, colB = st.columns([1, 1.2])
        with colA:
            st.subheader("📅 Planifier")
            d_plan = st.date_input("Pour quand ?")
            if st.button("Ajouter au planning"):
                requests.post(URL_SCRIPT, json={"action": "plan", "titre": r['Titre'], "date_prevue": d_plan.strftime("%d/%m/%Y")})
                st.success("C'est noté !")
            
            st.write("---")
            st.subheader("🛒 Ingrédients")
            st.write("Cochez ce qu'il vous manque :")
            ing_list = str(r['Ingrédients']).split("\n")
            to_add = []
            for i, line in enumerate(ing_list):
                if line.strip():
                    if st.checkbox(line.strip(), key=f"chk_{i}"):
                        to_add.append(line.strip())
            
            if st.button("➕ Envoyer à l'épicerie"):
                for item in to_add:
                    if item not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(item)
                st.toast("Liste mise à jour !")

        with colB:
            img = str(r['Image']) if "http" in str(row['Image']) else "https://via.placeholder.com/600"
            st.image(img, use_container_width=True)
            if st.button("🖨️ Préparer une jolie fiche à imprimer", use_container_width=True):
                st.session_state.show_print = True; st.rerun()
            st.write("### 📝 Étapes")
            st.write(r['Préparation'])

# ======================================================
# PAGE : ÉPICERIE (VRAIE LISTE)
# ======================================================
elif st.session_state.page == "shopping":
    st.header("🛒 Ma Liste d'Épicerie")
    if st.button("🗑 Tout effacer"):
        st.session_state.shopping_list = []; st.rerun()
    
    if not st.session_state.shopping_list:
        st.info("Votre liste est vide.")
    else:
        for idx, item in enumerate(st.session_state.shopping_list):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"✅ **{item}**")
            if c2.button("❌", key=f"del_{idx}"):
                st.session_state.shopping_list.pop(idx); st.rerun()

# ======================================================
# AUTRES PAGES (RESTE INCHANGÉ)
# ======================================================
elif st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data()
    if 'Date_Prevue' in df.columns:
        plan = df[df['Date_Prevue'] != ''].copy()
        for _, row in plan.iterrows():
            st.warning(f"{row['Date_Prevue']} : **{row['Titre']}**")

elif st.session_state.page == "aide":
    st.header("❓ Aide")
    st.write("**Impression** : Cliquez sur le bouton 'Préparer une jolie fiche'. Une fois la fiche affichée, utilisez la fonction Imprimer de votre navigateur.")
    st.write("**Épicerie** : Cochez les ingrédients dans une recette, puis cliquez sur 'Envoyer à l'épicerie'.")
