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
    .recipe-title { font-weight: 700; font-size: 1.2rem; color: #2c3e50; margin-top: 10px; }
    .print-card {
        background-color: white; color: black; padding: 40px; border: 2px solid #eee;
        font-family: 'serif'; line-height: 1.6; max-width: 800px; margin: auto;
    }
    .print-header { border-bottom: 3px solid #e67e22; padding-bottom: 10px; margin-bottom: 20px; text-align: center; }
    .print-section { font-weight: bold; color: #e67e22; text-transform: uppercase; margin-top: 25px; border-bottom: 1px solid #eee; }
    .help-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #e67e22; margin-bottom: 20px; }
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
    st.title("🍳 Menu Principal")
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
        st.markdown(f'<div class="print-card"><div class="print-header"><h1>{r["Titre"]}</h1></div><div class="print-section">🛒 INGRÉDIENTS</div><p style="white-space: pre-wrap;">{r["Ingrédients"]}</p><div class="print-section">🍳 PRÉPARATION</div><p style="white-space: pre-wrap;">{r["Préparation"]}</p></div>', unsafe_allow_html=True)
        if st.button("❌ Quitter l'impression"): st.session_state.show_print = False; st.rerun()
    else:
        if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
        st.header(r['Titre'])
        colA, colB = st.columns([1, 1.2])
        with colA:
            st.subheader("📅 Planifier")
            d_plan = st.date_input("Choisir une date", value=datetime.now())
            if st.button("Valider la date"):
                requests.post(URL_SCRIPT, json={"action": "plan", "titre": r['Titre'], "date_prevue": d_plan.strftime("%d/%m/%Y")})
                st.success(f"Prévu pour le {d_plan.strftime('%d/%m/%Y')}")
                st.cache_data.clear()
            st.write("---")
            st.subheader("🛒 Ingrédients")
            to_add = [line.strip() for i, line in enumerate(str(r['Ingrédients']).split("\n")) if line.strip() and st.checkbox(line.strip(), key=f"c_{i}")]
            if st.button("➕ Ajouter à l'épicerie"):
                for item in to_add:
                    if item not in st.session_state.shopping_list: st.session_state.shopping_list.append(item)
                st.toast("Liste mise à jour !")
        with colB:
            img_url = str(r['Image']) if "http" in str(r['Image']) else "https://via.placeholder.com/600"
            st.image(img_url, use_container_width=True)
            if st.button("🖨️ Préparer pour l'impression", use_container_width=True): st.session_state.show_print = True; st.rerun()
            st.write("### 📝 Étapes")
            st.write(r['Préparation'])

# ======================================================
# PAGE : PLANNING
# ======================================================
elif st.session_state.page == "planning":
    st.header("📅 Mon Planning Cuisine")
    df = load_data()
    if not df.empty and 'Date_Prevue' in df.columns:
        plan = df[df['Date_Prevue'] != ''].copy()
        if plan.empty: st.info("Rien de prévu au calendrier.")
        else:
            for _, row in plan.iterrows():
                with st.expander(f"🗓️ {row['Date_Prevue']} - {row['Titre']}", expanded=True):
                    st.write(f"**Catégorie :** {row['Catégorie']}")
                    if st.button("Voir la fiche", key=f"p_{row['Titre']}"):
                        st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
    else: st.info("Planning vide.")

# ======================================================
# PAGE : AIDE (EN BOITES)
# ======================================================
elif st.session_state.page == "aide":
    st.header("❓ Aide & Tutoriel")
    with st.container():
        st.markdown('<div class="help-box"><h3>🚀 Ajouter une recette</h3>Collez le lien Instagram ou TikTok dans la case <b>Source</b>. Pour l\'image, faites un clic-droit sur une photo sur internet et choisissez "Copier l\'adresse de l\'image".</div>', unsafe_allow_html=True)
        st.markdown('<div class="help-box"><h3>🛒 Liste d\'Épicerie</h3>Cochez les ingrédients manquants dans une recette et cliquez sur "Ajouter". Votre liste se remplit toute seule dans l\'onglet Épicerie.</div>', unsafe_allow_html=True)
        st.markdown('<div class="help-box"><h3>📅 Planning</h3>Sélectionnez une date directement sur la fiche d\'une recette. Elle apparaîtra automatiquement dans votre calendrier de cuisine.</div>', unsafe_allow_html=True)
        st.markdown('<div class="help-box"><h3>🖨️ Impression</h3>Cliquez sur "Préparer pour l\'impression" pour voir une fiche propre, puis utilisez la fonction imprimer de votre tablette ou PC.</div>', unsafe_allow_html=True)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : AJOUTER (AVEC SOURCE/INSTA)
# ======================================================
elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    with st.form("add_form"):
        t = st.text_input("Titre de la recette")
        c = st.selectbox("Catégorie", CATEGORIES[1:])
        s = st.text_input("Lien Source (Instagram, TikTok, Blog...)")
        i = st.text_input("URL de l'image")
        ing = st.text_area("Ingrédients (un par ligne)")
        pre = st.text_area("Préparation")
        if st.form_submit_button("Sauvegarder"):
            requests.post(URL_SCRIPT, json={"action":"add","titre":t,"source":s,"ingredients":ing,"preparation":pre,"categorie":c,"image":i,"date":datetime.now().strftime("%d/%m/%Y")})
            st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# PAGE : HOME & ÉPICERIE (Inchangés mais vérifiés)
# ======================================================
elif st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if df.empty: st.info("Bibliothèque vide.")
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
    st.header("🛒 Épicerie")
    if st.button("Vider tout"): st.session_state.shopping_list = []; st.rerun()
    for idx, item in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([5, 1])
        c1.write(f"• {item}")
        if c2.button("❌", key=f"s_{idx}"): st.session_state.shopping_list.pop(idx); st.rerun()
