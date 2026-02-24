import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from io import BytesIO

# ======================================================
# CONFIG & CSS (Ton style tablette optimisé)
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
.recipe-title { font-weight: 700; font-size: 1.1rem; margin-top: 10px; min-height: 48px; }
.cat-badge { 
    background: linear-gradient(90deg,#ff9800,#ff5722); 
    color: white; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; 
}
</style>
""", unsafe_allow_html=True)

# --- N'oublie pas de remettre tes vraies URLs ici ---
URL_CSV = "TON_URL_CSV"
URL_SCRIPT = "TON_URL_SCRIPT"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# ======================================================
# PDF GENERATOR (Inclus la note maintenant)
# ======================================================
def generate_recipe_pdf(recipe, rating):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle('T', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor("#E65100"))
    normal_style = styles['Normal']
    
    elements = [
        Paragraph(recipe['Titre'], title_style),
        Paragraph(f"Note : {'⭐' * rating}", normal_style),
        Spacer(1, 12),
        Paragraph("Ingrédients", styles['Heading2'])
    ]
    
    for item in str(recipe['Ingrédients']).split("\n"):
        if item.strip(): elements.append(Paragraph(f"• {item.strip()}", normal_style))
        
    elements.append(Spacer(1, 12))
    elements.append(Paragraph("Préparation", styles['Heading2']))
    elements.append(Paragraph(recipe['Préparation'].replace("\n", "<br/>"), normal_style))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

# ======================================================
# DATA & SESSION
# ======================================================
@st.cache_data(ttl=600)
def load_data():
    try:
        return pd.read_csv(URL_CSV).fillna('')
    except:
        return pd.DataFrame()

if "page" not in st.session_state: st.session_state.page = "home"
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Menu")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("➕ Ajouter", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page = "shopping"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()

# ======================================================
# HOME (Ma Bibliothèque)
# ======================================================
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if not df.empty:
        # Renommage colonnes pour sécurité
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= 9: df.columns = expected[:len(df.columns)]

        c1, c2 = st.columns(2)
        search = c1.text_input("🔍 Rechercher")
        cat_f = c2.selectbox("Catégorie", CATEGORIES)

        if search: df = df[df['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": df = df[df['Catégorie'] == cat_f]

        grid = st.columns(3)
        for idx, row in df.reset_index(drop=True).iterrows():
            with grid[idx % 3]:
                with st.container(border=True):
                    img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                    st.image(img, use_container_width=True)
                    st.markdown(f"<div class='recipe-title'>{row['Titre']}</div>", unsafe_allow_html=True)
                    if st.button("Ouvrir", key=f"btn_{idx}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()

# ======================================================
# DETAILS
# ======================================================
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()

    st.header(f"🍳 {r['Titre']}")
    
    colA, colB = st.columns([1, 1.2])

    with colA:
        # Étoiles & Lien Social
        note = st.select_slider("Ma note", options=[1,2,3,4,5], value=5)
        source_url = str(r.get('Source', ''))
        if "instagram" in source_url.lower(): st.info("📸 Recette via Instagram")
        elif "tiktok" in source_url.lower(): st.info("🎵 Recette via TikTok")
        elif "http" in source_url.lower(): st.link_button("🔗 Voir la source originale", source_url)

        st.subheader("🛒 Ingrédients")
        temp_items = []
        for i, item in enumerate(str(r['Ingrédients']).split("\n")):
            if item.strip() and st.checkbox(item.strip(), key=f"chk_{i}"):
                temp_items.append(item.strip())
        
        if st.button("➕ Ajouter à l'épicerie", use_container_width=True):
            for it in temp_items:
                if it not in st.session_state.shopping_list: st.session_state.shopping_list.append(it)
            st.toast("C'est dans la liste !")

        st.write("---")
        # PDF GENERATOR
        pdf_file = generate_recipe_pdf(r, note)
        st.download_button("🖨 Télécharger en PDF", pdf_file, f"{r['Titre']}.pdf", "application/pdf", use_container_width=True)

    with colB:
        img = r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/600"
        st.image(img, use_container_width=True)
        st.write("### 📝 Préparation")
        st.write(r['Préparation'])
        if r.get('Commentaires'):
            st.warning(f"**Notes :** {r['Commentaires']}")

# ======================================================
# ADD (Avec le champ SOURCE pour les liens)
# ======================================================
elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    with st.form("form_add"):
        titre = st.text_input("Titre")
        categorie = st.selectbox("Catégorie", CATEGORIES[1:])
        source = st.text_input("Lien (Instagram, TikTok, Blog...)")
        image = st.text_input("URL Image")
        ingredients = st.text_area("Ingrédients (un par ligne)")
        preparation = st.text_area("Préparation")
        commentaires = st.text_area("Notes / Commentaires")

        if st.form_submit_button("Enregistrer"):
            payload = {
                "action": "add", "titre": titre, "source": source,
                "ingredients": ingredients, "preparation": preparation,
                "categorie": categorie, "image": image, "commentaires": commentaires,
                "date": datetime.now().strftime("%d/%m/%Y")
            }
            requests.post(URL_SCRIPT, json=payload)
            st.cache_data.clear(); st.session_state.page = "home"; st.rerun()

# ======================================================
# SHOPPING
# ======================================================
elif st.session_state.page == "shopping":
    st.header("🛒 Liste d'épicerie")
    if st.button("🚫 Vider"): st.session_state.shopping_list = []; st.rerun()
    if not st.session_state.shopping_list: st.info("Liste vide !")
    for idx, item in enumerate(st.session_state.shopping_list):
        c1, c2 = st.columns([4,1])
        c1.write(f"• {item}")
        if c2.button("❌", key=f"del_{idx}"):
            st.session_state.shopping_list.pop(idx); st.rerun()
