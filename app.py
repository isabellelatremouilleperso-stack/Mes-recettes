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
    [data-testid="stImage"] img { object-fit: cover; height: 250px !important; border-radius: 15px; }
    .help-box { 
        background-color: #ffffff; color: #1a1a1a !important; 
        padding: 20px; border-radius: 10px; border-left: 8px solid #e67e22; 
        margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .help-box h3 { color: #e67e22 !important; margin-top: 0; }
    .help-box p { color: #1a1a1a !important; }
</style>
""", unsafe_allow_html=True)

# --- LIENS ---
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
if "show_print" not in st.session_state: st.session_state.show_print = False

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True): 
        st.session_state.page = "home"; st.session_state.show_print = False; st.rerun()
    if st.button("📅 Planning", use_container_width=True): 
        st.session_state.page = "planning"; st.session_state.show_print = False; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): 
        st.session_state.page = "shopping"; st.session_state.show_print = False; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter une recette", use_container_width=True, type="primary"): 
        st.session_state.page = "add"; st.rerun()
    if st.button("❓ Aide & Tutoriel", use_container_width=True): 
        st.session_state.page = "aide"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True):
        st.cache_data.clear(); st.rerun()

# ======================================================
# PAGE : BIBLIOTHÈQUE (HOME)
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if df.empty:
        st.warning("Aucune recette trouvée. Vérifiez votre fichier Google Sheets.")
    else:
        search = st.text_input("🔍 Rechercher une recette")
        filtered = df[df['Titre'].str.contains(search, case=False)]
        
        grid = st.columns(3)
        for idx, row in filtered.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                    st.image(img, use_container_width=True)
                    st.markdown(f"**{row['Titre']}**")
                    if st.button("Ouvrir", key=f"h_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()

# ======================================================
# PAGE : DÉTAILS (Étoiles, Notes, Planning)
# ======================================================
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    colA, colB = st.columns([1, 1.2])
    with colA:
        st.subheader("⭐ Évaluation")
        st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"])
        st.checkbox("✅ Recette testée")
        notes = st.text_area("📝 Mes notes", value=r.get('Commentaires', ''))
        if st.button("💾 Sauvegarder les notes"):
            requests.post(URL_SCRIPT, json={"action": "update_notes", "titre": r['Titre'], "commentaires": notes})
            st.success("Enregistré !")

        st.write("---")
        st.subheader("📅 Planifier")
        d_plan = st.date_input("Date", value=datetime.now())
        if st.button("Ajouter au planning"):
            requests.post(URL_SCRIPT, json={"action": "plan", "titre": r['Titre'], "date_prevue": d_plan.strftime("%d/%m/%Y")})
            st.success("Planifié !")

    with colB:
        st.header(r['Titre'])
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/600")
        
        st.subheader("🛒 Ingrédients")
        to_add = [l.strip() for l in str(r['Ingrédients']).split("\n") if l.strip() and st.checkbox(l.strip())]
        if st.button("➕ Ajouter à l'épicerie"):
            st.session_state.shopping_list.extend([x for x in to_add if x not in st.session_state.shopping_list])
            st.toast("Ajouté !")

        st.subheader("📝 Préparation")
        st.write(r['Préparation'])

# ======================================================
# PAGE : AJOUTER (CORRIGÉE AVEC BOUTON)
# ======================================================
elif st.session_state.page == "add":
    st.header("➕ Nouvelle recette")
    with st.form("form_ajout"):
        t = st.text_input("Titre")
        c = st.selectbox("Catégorie", CATEGORIES[1:])
        s = st.text_input("Source (Instagram...)")
        i = st.text_input("URL Image")
        ing = st.text_area("Ingrédients")
        pre = st.text_area("Préparation")
        # LE BOUTON MANQUANT ÉTAIT ICI :
        submitted = st.form_submit_button("💾 Sauvegarder la recette")
        if submitted:
            requests.post(URL_SCRIPT, json={"action":"add","titre":t,"source":s,"ingredients":ing,"preparation":pre,"categorie":c,"image":i,"date":datetime.now().strftime("%d/%m/%Y")})
            st.cache_data.clear()
            st.session_state.page = "home"
            st.rerun()

# ======================================================
# PAGE : AIDE (BOITES BLANCHES)
# ======================================================
elif st.session_state.page == "aide":
    st.header("❓ Aide & Tutoriel")
    st.markdown("""
    <div class="help-box">
        <h3>🚀 Ajouter une recette</h3>
        <p>Utilisez le bouton <b>Ajouter</b>. Pour l'image, copiez l'adresse d'une image sur Google Images.</p>
    </div>
    <div class="help-box">
        <h3>⭐ Évaluation & Notes</h3>
        <p>Sur chaque fiche, vous pouvez donner des étoiles et écrire vos astuces (ex: "Cuire 5 min de moins"). Cliquez sur <b>Sauvegarder</b> pour ne pas les perdre.</p>
    </div>
    <div class="help-box">
        <h3>🛒 Épicerie</h3>
        <p>Cochez les ingrédients manquants dans une recette et envoyez-les vers votre liste de courses.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : PLANNING & ÉPICERIE
# ======================================================
elif st.session_state.page == "planning":
    st.header("📅 Planning")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != '']
        for _, row in plan.iterrows():
            st.info(f"🗓️ {row['Date_Prevue']} : **{row['Titre']}**")
    else: st.write("Planning vide.")

elif st.session_state.page == "shopping":
    st.header("🛒 Épicerie")
    if st.button("Vider"): st.session_state.shopping_list = []; st.rerun()
    for idx, item in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([5, 1])
        c1.write(f"• {item}")
        if c2.button("❌", key=f"s_{idx}"): st.session_state.shopping_list.pop(idx); st.rerun()
