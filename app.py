import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION & STYLE
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
[data-testid="stImage"] img {
    object-fit: cover;
    height: 250px !important;
    width: 100% !important;
    border-radius: 20px;
}
.recipe-title { font-weight: 700; font-size: 1.2rem; margin-top: 10px; min-height: 50px; }
.cat-badge { 
    background: linear-gradient(90deg,#ff9800,#ff5722); 
    color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; 
}
.print-area {
    background-color: white; color: black; padding: 30px;
    border: 2px solid #333; border-radius: 10px;
    font-family: 'Courier New', Courier, monospace;
}
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

if "page" not in st.session_state: st.session_state.page = "home"
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "show_print" not in st.session_state: st.session_state.show_print = False

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Menu")
    if st.button("📚 Bibliothèque", use_container_width=True): 
        st.session_state.page = "home"; st.session_state.show_print = False; st.rerun()
    if st.button("📅 Mon Planning", use_container_width=True): 
        st.session_state.page = "planning"; st.session_state.show_print = False; st.rerun()
    if st.button("➕ Ajouter une recette", use_container_width=True, type="primary"): 
        st.session_state.page = "add"; st.session_state.show_print = False; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): 
        st.session_state.page = "shopping"; st.session_state.show_print = False; st.rerun()
    st.write("---")
    if st.button("❓ Aide & Tutoriel", use_container_width=True): 
        st.session_state.page = "aide"; st.session_state.show_print = False; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): 
        st.cache_data.clear(); st.rerun()

# ======================================================
# PAGE : BIBLIOTHÈQUE
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if df.empty:
        st.warning("⚠️ Aucune recette trouvée.")
    else:
        c1, c2 = st.columns(2)
        search = c1.text_input("🔍 Rechercher")
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
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()

# ======================================================
# PAGE : DÉTAILS (Inclus Planification)
# ======================================================
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    
    if st.session_state.show_print:
        st.markdown(f'<div class="print-area"><h1>{r["Titre"]}</h1><hr><h3>INGRÉDIENTS</h3><p>{str(r["Ingrédients"]).replace("\\n", "<br>")}</p><hr><h3>PRÉPARATION</h3><p>{str(r["Préparation"]).replace("\\n", "<br>")}</p></div>', unsafe_allow_html=True)
        if st.button("Fermer l'aperçu"): st.session_state.show_print = False; st.rerun()

    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

    st.header(f"🍳 {r['Titre']}")
    colA, colB = st.columns([1, 1.2])

    with colA:
        # --- PLANIFICATION ---
        st.subheader("📅 Planifier")
        new_date = st.date_input("Choisir une date pour cuisiner")
        if st.button("Enregistrer au planning", use_container_width=True):
            requests.post(URL_SCRIPT, json={"action": "plan", "titre": r['Titre'], "date_prevue": new_date.strftime("%d/%m/%Y")})
            st.success(f"Prévu pour le {new_date.strftime('%d/%m/%Y')}")
            st.cache_data.clear()

        st.write("---")
        st.subheader("🛒 Ingrédients")
        temp = [it.strip() for i, it in enumerate(str(r['Ingrédients']).split("\n")) if it.strip() and st.checkbox(it.strip(), key=f"ing_{i}")]
        if st.button("Ajouter à l'épicerie", use_container_width=True):
            for item in temp:
                if item not in st.session_state.shopping_list: st.session_state.shopping_list.append(item)
            st.toast("✅ Ajouté !")

    with colB:
        img = str(r['Image']) if "http" in str(r['Image']) else "https://via.placeholder.com/600"
        st.image(img, use_container_width=True)
        if st.button("🖨️ Version imprimable", use_container_width=True): st.session_state.show_print = True; st.rerun()
        st.write("### 📝 Préparation")
        st.write(r['Préparation'])

# ======================================================
# PAGE : PLANNING (NOUVEAU)
# ======================================================
elif st.session_state.page == "planning":
    st.header("📅 Mon Planning de la semaine")
    df = load_data()
    if not df.empty and 'Date_Prevue' in df.columns:
        df_plan = df[df['Date_Prevue'] != ''].copy()
        if df_plan.empty:
            st.info("Aucune recette planifiée pour le moment.")
        else:
            # Tri par date
            df_plan['temp_date'] = pd.to_datetime(df_plan['Date_Prevue'], format='%d/%m/%Y', errors='coerce')
            df_plan = df_plan.sort_values('temp_date')
            
            for _, row in df_plan.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 3, 1])
                    c1.warning(f"🗓️ {row['Date_Prevue']}")
                    c2.subheader(row['Titre'])
                    if c3.button("Ouvrir", key=f"plan_{row['Titre']}"):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()
    else:
        st.info("Le planning est vide.")

# ======================================================
# PAGE : AIDE (Mise à jour)
# ======================================================
elif st.session_state.page == "aide":
    st.header("📖 Guide Complet")
    t1, t2
