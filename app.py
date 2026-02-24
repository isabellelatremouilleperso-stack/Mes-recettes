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
    
    /* BOITES D'AIDE - Texte forcé en noir */
    .help-box { 
        background-color: #ffffff; color: #1a1a1a !important; 
        padding: 20px; border-radius: 10px; border-left: 8px solid #e67e22; 
        margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .help-box h3 { color: #e67e22 !important; margin-top: 0; }
    .help-box p { color: #1a1a1a !important; }

    /* Fiche Impression */
    .print-card {
        background-color: white; color: black; padding: 40px; border: 2px solid #eee;
        font-family: 'serif'; line-height: 1.6; max-width: 800px; margin: auto;
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

# ======================================================
# PAGE : DÉTAILS (Étoiles, Notes, Case Fait)
# ======================================================
if st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.session_state.show_print:
        st.markdown(f'<div class="print-card"><h1>{r["Titre"]}</h1><hr><h3>INGRÉDIENTS</h3><p>{r["Ingrédients"]}</p><h3>PRÉPARATION</h3><p>{r["Préparation"]}</p></div>', unsafe_allow_html=True)
        if st.button("❌ Quitter l'aperçu"): st.session_state.show_print = False; st.rerun()
    else:
        if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
        
        st.header(r['Titre'])
        colA, colB = st.columns([1, 1.2])
        
        with colA:
            # --- ÉVALUATION ---
            st.subheader("⭐ Évaluation")
            note_etoile = st.select_slider("Ma note", options=["⭐","⭐⭐","⭐⭐⭐","⭐⭐⭐⭐","⭐⭐⭐⭐⭐"], value="⭐⭐⭐⭐⭐")
            fait = st.checkbox("✅ Recette déjà testée", value=False)
            mes_notes = st.text_area("📝 Mes commentaires personnels", value=r.get('Commentaires', ''), placeholder="Ex: Ajouter plus de sel, diminuer le temps de cuisson...")
            
            if st.button("💾 Sauvegarder mes notes/note"):
                requests.post(URL_SCRIPT, json={"action": "update_notes", "titre": r['Titre'], "commentaires": mes_notes})
                st.success("Notes enregistrées !")
                st.cache_data.clear()

            st.write("---")
            st.subheader("📅 Planning")
            d_plan = st.date_input("Pour quand ?", value=datetime.now())
            if st.button("Ajouter au planning"):
                requests.post(URL_SCRIPT, json={"action": "plan", "titre": r['Titre'], "date_prevue": d_plan.strftime("%d/%m/%Y")})
                st.success("Planning mis à jour !")
                st.cache_data.clear()

        with colB:
            st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/600", use_container_width=True)
            if st.button("🖨️ Préparer pour l'impression", use_container_width=True): st.session_state.show_print = True; st.rerun()
            
            st.write("### 🛒 Ingrédients")
            to_add = [l.strip() for i, l in enumerate(str(r['Ingrédients']).split("\n")) if l.strip() and st.checkbox(l.strip(), key=f"ing_{i}")]
            if st.button("➕ Envoyer à l'épicerie"):
                for item in to_add:
                    if item not in st.session_state.shopping_list: st.session_state.shopping_list.append(item)
                st.toast("C'est dans la liste !")
            
            st.write("### 📝 Préparation")
            st.write(r['Préparation'])

# ======================================================
# PAGE : AIDE (BOITES)
# ======================================================
elif st.session_state.page == "aide":
    st.header("❓ Aide & Tutoriel")
    st.markdown("""
    <div class="help-box">
        <h3>⭐ Noter une recette</h3>
        <p>Utilisez le curseur d'étoiles et la case à cocher pour vous souvenir des recettes que vous avez aimées. N'oubliez pas de cliquer sur <b>'Sauvegarder mes notes'</b>.</p>
    </div>
    <div class="help-box">
        <h3>🚀 Ajouter avec Source</h3>
        <p>Dans le formulaire d'ajout, collez le lien Instagram ou TikTok dans la case <b>Source</b> pour ne jamais perdre la vidéo d'origine.</p>
    </div>
    <div class="help-box">
        <h3>🛒 Liste d'Épicerie</h3>
        <p>Cochez les ingrédients manquants dans une recette. Ils s'ajouteront à votre liste globale dans l'onglet 'Épicerie' du menu.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : PLANNING
# ======================================================
elif st.session_state.page == "planning":
    st.header("📅 Mon Planning")
    df = load_data()
    if not df.empty and 'Date_Prevue' in df.columns:
        plan = df[df['Date_Prevue'] != ''].copy()
        for _, row in plan.iterrows():
            with st.container(border=True):
                st.write(f"🗓️ **{row['Date_Prevue']}** — {row['Titre']}")
                if st.button("Ouvrir", key=f"p_{row['Titre']}"):
                    st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
    else: st.info("Planning vide.")

# ======================================================
# PAGE : AJOUTER
# ======================================================
elif st.session_state.page == "add":
    st.header("➕ Nouvelle recette")
    with st.form("add_form"):
        t = st.text_input("Titre")
        c = st.selectbox("Catégorie", CATEGORIES[1:])
