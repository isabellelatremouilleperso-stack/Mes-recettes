import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ======================================================
# CONFIGURATION & STYLE (Correction contraste)
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    [data-testid="stImage"] img { object-fit: cover; height: 250px !important; border-radius: 15px; }
    .recipe-title { font-weight: 700; font-size: 1.2rem; color: #2c3e50; margin-top: 10px; }
    
    /* Zone d'impression */
    .print-card {
        background-color: white; color: black; padding: 40px; border: 2px solid #eee;
        font-family: 'serif'; line-height: 1.6; max-width: 800px; margin: auto;
    }
    
    /* BOITES D'AIDE - Correction du texte invisible */
    .help-box { 
        background-color: #ffffff; 
        color: #1a1a1a !important; /* Force le texte en noir */
        padding: 20px; 
        border-radius: 10px; 
        border-left: 8px solid #e67e22; 
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .help-box h3 { color: #e67e22 !important; margin-top: 0; }
    .help-box p, .help-box li { color: #1a1a1a !important; }

    /* Planning fiches */
    .plan-card {
        background-color: #fff3e0;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ffcc80;
        margin-bottom: 10px;
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

# Session State
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "page" not in st.session_state: st.session_state.page = "home"
if "show_print" not in st.session_state: st.session_state.show_print = False

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Ma Cuisine Pro")
    if st.button("📚 Bibliothèque", use_container_width=True): 
        st.session_state.page = "home"; st.session_state.show_print = False; st.rerun()
    if st.button("📅 Mon Planning", use_container_width=True): 
        st.session_state.page = "planning"; st.session_state.show_print = False; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): 
        st.session_state.page = "shopping"; st.session_state.show_print = False; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter une recette", use_container_width=True, type="primary"): 
        st.session_state.page = "add"; st.rerun()
    if st.button("❓ Aide & Tutoriel", use_container_width=True): 
        st.session_state.page = "aide"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()

# ======================================================
# PAGE : DÉTAILS
# ======================================================
if st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.session_state.show_print:
        st.markdown(f'<div class="print-card"><h1>{r["Titre"]}</h1><hr><h3>INGRÉDIENTS</h3><p>{r["Ingrédients"]}</p><h3>PRÉPARATION</h3><p>{r["Préparation"]}</p></div>', unsafe_allow_html=True)
        if st.button("Fermer l'impression"): st.session_state.show_print = False; st.rerun()
    else:
        if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
        colA, colB = st.columns([1, 1.2])
        with colA:
            st.subheader("📅 Planifier")
            d_plan = st.date_input("Date prévue", value=datetime.now())
            if st.button("Enregistrer la date", use_container_width=True):
                requests.post(URL_SCRIPT, json={"action": "plan", "titre": r['Titre'], "date_prevue": d_plan.strftime("%d/%m/%Y")})
                st.success(f"Planifié !")
                st.cache_data.clear()
            st.write("---")
            st.subheader("🛒 Épicerie")
            to_add = [l.strip() for i, l in enumerate(str(r['Ingrédients']).split("\n")) if l.strip() and st.checkbox(l.strip(), key=f"ing_{i}")]
            if st.button("➕ Ajouter à la liste"):
                for item in to_add:
                    if item not in st.session_state.shopping_list: st.session_state.shopping_list.append(item)
                st.toast("Liste mise à jour !")
        with colB:
            st.header(r['Titre'])
            st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/600", use_container_width=True)
            if st.button("🖨️ Version imprimable", use_container_width=True): st.session_state.show_print = True; st.rerun()
            st.write("### 📝 Étapes")
            st.write(r['Préparation'])

# ======================================================
# PAGE : PLANNING (Visuel)
# ======================================================
elif st.session_state.page == "planning":
    st.header("📅 Planning des repas")
    df = load_data()
    if not df.empty and 'Date_Prevue' in df.columns:
        plan = df[df['Date_Prevue'] != ''].copy()
        if plan.empty: st.info("Aucun repas planifié.")
        else:
            # On trie les dates pour que le plus proche soit en haut
            plan['sort_date'] = pd.to_datetime(plan['Date_Prevue'], format='%d/%m/%Y', errors='coerce')
            plan = plan.sort_values('sort_date')
            
            for _, row in plan.iterrows():
                with st.container():
                    st.markdown(f"""<div class="plan-card">
                        <span style="font-size:1.2rem;">🗓️ <b>{row['Date_Prevue']}</b></span> — <b>{row['Titre']}</b>
                    </div>""", unsafe_allow_html=True)
                    if st.button("Voir la recette", key=f"plan_btn_{row['Titre']}"):
                        st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
    else: st.info("Le planning est vide.")

# ======================================================
# PAGE : AIDE (Correction visuelle)
# ======================================================
elif st.session_state.page == "aide":
    st.header("❓ Aide & Tutoriel")
    
    st.markdown("""
    <div class="help-box">
        <h3>🚀 Ajouter une recette</h3>
        <p>1. Cliquez sur le bouton <b>Ajouter</b> dans le menu.<br>
        2. <b>Source</b> : Collez ici le lien Instagram, TikTok ou le site web.<br>
        3. <b>Image</b> : Trouvez une photo sur Google, faites un clic-droit et choisissez 'Copier l'adresse de l'image'.</p>
    </div>
    <div class="help-box">
        <h3>🛒 Liste d'Épicerie</h3>
        <p>Dans la fiche d'une recette, cochez les ingrédients qu'il vous manque. Cliquez sur le bouton <b>Ajouter</b>. Votre liste globale est disponible dans l'onglet 'Épicerie'.</p>
    </div>
    <div class="help-box">
        <h3>📅 Planning</h3>
        <p>Sélectionnez une date via le calendrier dans la fiche recette et validez. La recette apparaîtra dans votre onglet 'Planning'.</p>
    </div>
    <div class="help-box">
        <h3>🖨️ Impression</h3>
        <p>Cliquez sur 'Version imprimable' pour une fiche épurée. Utilisez ensuite la fonction 'Imprimer' de votre navigateur.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅ Retour à la bibliothèque"): st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : AJOUTER (Avec Source)
# ======================================================
elif st.session_state.page == "add":
    st.header("➕ Nouvelle recette")
    with st.form("add_form"):
        t = st.text_input("Nom du plat")
        c = st.selectbox("Catégorie", CATEGORIES[1:])
        s = st.text_input("Source (Instagram, TikTok...)")
        i = st.text_input("Lien de l'image (URL)")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Étapes de préparation")
        if st.form_submit_button("Sauvegarder"):
            requests.post(URL_SCRIPT, json={"action":"add","titre":t,"source":s,"ingredients":ing,"preparation":pre,"categorie":c,"image":i,"date":datetime.now().strftime("%d/%m/%Y")})
            st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# HOME & SHOPPING
# ======================================================
elif st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if df.empty: st.info("Aucune recette ici.")
    else:
        grid = st.columns(3)
        for idx, row in df.iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    st.image(row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400", use_container_width=True)
                    st.markdown(f"**{row['Titre']}**")
                    if st.button("Ouvrir", key=f"h_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()

elif st.session_state.page == "shopping":
    st.header("🛒 Ma Liste de Courses")
    if st.button("Effacer tout"): st.session_state.shopping_list = []; st.rerun()
    for idx, item in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([5, 1])
        c1.write(f"• **{item}**")
        if c2.button("❌", key=f"s_{idx}"): st.session_state.shopping_list.pop(idx); st.rerun()
