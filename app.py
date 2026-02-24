import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ======================================================
# CONFIGURATION & DESIGN PREMIUM
# ======================================================
st.set_page_config(
    page_title="Chef Master Pro", 
    layout="wide", 
    page_icon="👨‍🍳",
    initial_sidebar_state="expanded"
)

# Style CSS Injecté pour un look "Dark Mode Luxury"
st.markdown("""
<style>
    /* Global */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Titres */
    h1, h2, h3 { color: #e67e22 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    /* Cartes Recettes */
    .recipe-card {
        background-color: #1e2129;
        border-radius: 15px;
        border: 1px solid #3d4455;
        padding: 0px;
        transition: 0.3s;
        margin-bottom: 20px;
    }
    .recipe-card:hover { 
        transform: translateY(-5px); 
        border-color: #e67e22; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.4);
    }
    
    /* Badge Catégorie */
    .category-badge {
        background-color: #e67e22;
        color: white;
        padding: 2px 10px;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Help Boxes Custom */
    .help-card {
        background: linear-gradient(145deg, #23272f, #1e2129);
        padding: 20px;
        border-radius: 15px;
        border-left: 5px solid #e67e22;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION API ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# ======================================================
# FONCTIONS CŒUR
# ======================================================
@st.cache_data(ttl=60)
def load_data():
    try:
        df = pd.read_csv(URL_CSV).fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except Exception as e:
        st.error(f"⚠️ Erreur de connexion aux données : {e}")
        return pd.DataFrame()

def send_update(payload):
    with st.spinner("Mise à jour du grimoire..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=10)
            if r.status_code == 200:
                st.success("Synchronisation réussie !")
                st.cache_data.clear()
                return True
        except:
            st.error("Erreur de réseau. Vérifiez votre connexion.")
    return False

# Initialisation Session
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}

# ======================================================
# BARRE LATÉRALE (NAVIGATION)
# ======================================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>👨‍🍳 CHEF PRO</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Navigation avec icônes
    nav_home = st.button("📚 Ma Bibliothèque", use_container_width=True)
    nav_plan = st.button("📅 Planning Repas", use_container_width=True)
    nav_shop = st.button(f"🛒 Liste d'achats ({len(st.session_state.shopping_list)})", use_container_width=True)
    
    st.write("---")
    nav_add = st.button("➕ Ajouter une Recette", use_container_width=True, type="primary")
    nav_help = st.button("❓ Aide & Support", use_container_width=True)
    
    if nav_home: st.session_state.page = "home"; st.rerun()
    if nav_plan: st.session_state.page = "planning"; st.rerun()
    if nav_shop: st.session_state.page = "shopping"; st.rerun()
    if nav_add: st.session_state.page = "add"; st.rerun()
    if nav_help: st.session_state.page = "aide"; st.rerun()

# ======================================================
# PAGE: BIBLIOTHÈQUE (HOME)
# ======================================================
if st.session_state.page == "home":
    st.title("📚 Ma Bibliothèque Culinaire")
    df = load_data()
    
    col_search, col_filter = st.columns([2, 1])
    with col_search:
        query = st.text_input("🔍 Rechercher une saveur...", placeholder="Nom de la recette...")
    with col_filter:
        cat_filter = st.selectbox("Filtrer par type", CATEGORIES)

    if not df.empty:
        # Filtrage dynamique
        filtered = df.copy()
        if query:
            filtered = filtered[filtered['Titre'].str.contains(query, case=False)]
        if cat_filter != "Toutes":
            filtered = filtered[filtered['Catégorie'] == cat_filter]

        if filtered.empty:
            st.warning("Aucune recette ne correspond à votre recherche.")
        else:
            cols = st.columns(3)
            for idx, row in filtered.reset_index(drop=True).iterrows():
                with cols[idx % 3]:
                    # Container Carte
                    with st.container():
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400x250?text=No+Image"
                        st.markdown(f"""
                        <div class="recipe-card">
                            <img src="{img}" style="width:100%; height:180px; object-fit:cover; border-radius:15px 15px 0 0;">
                            <div style="padding:15px;">
                                <span class="category-badge">{row['Catégorie']}</span>
                                <h4 style="margin:10px 0;">{row['Titre']}</h4>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Consulter", key=f"view_{idx}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"
                            st.rerun()
    else:
        st.info("Votre carnet est vide. Commencez par ajouter une recette !")

# ======================================================
# PAGE: DETAILS (LE CŒUR DE L'APPLI)
# ======================================================
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour à la liste"): st.session_state.page = "home"; st.rerun()
    
    st.title(f"🍳 {r['Titre']}")
    
    col_left, col_right = st.columns([1, 1.2])
    
    with col_left:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/600", use_container_width=True)
        
        with st.expander("⭐ Notes & Commentaires", expanded=True):
            note = st.select_slider("Ma satisfaction", options=["🌑","🌘","🌗","🌖","🌕"], value="🌕")
            comment = st.text_area("Observations (ex: 'Moins de sel')", value=r.get('Commentaires',''))
            if st.button("Enregistrer mes notes"):
                send_update({"action":"update_notes","titre":r['Titre'],"commentaires":comment})

        with st.expander("📅 Planification"):
            date_p = st.date_input("Pour quand ?", value=datetime.now())
            if st.button("Ajouter au calendrier"):
                success = send_update({
                    "action":"update", "titre_original": r['Titre'], "titre": r['Titre'],
                    "ingredients": r['Ingrédients'], "preparation": r['Préparation'],
                    "categorie": r['Catégorie'], "image": r['Image'], 
                    "date_prevue": date_p.strftime("%d/%m/%Y")
                })
                if success: st.rerun()

    with col_right:
        # Calculateur de portions
        portions = st.number_input("Nombre de personnes", min_value=1, value=4, step=1)
        st.subheader("🛒 Ingrédients")
        
        st.info("Cochez ce qu'il vous manque pour l'ajouter à la liste de courses.")
        raw_ings = str(r['Ingrédients']).split("\n")
        selected_to_buy = []
        for i, ing in enumerate(raw_ings):
            if ing.strip():
                if st.checkbox(ing.strip(), key=f"ing_{i}"):
                    selected_to_buy.append(ing.strip())
        
        if st.button("➕ Ajouter la sélection à l'épicerie", use_container_width=True):
            st.session_state.shopping_list.extend([x for x in selected_to_buy if x not in st.session_state.shopping_list])
            st.toast(f"{len(selected_to_buy)} articles ajoutés !", icon="🛒")

        st.divider()
        st.subheader("📝 Préparation")
        st.markdown(f">{r['Préparation']}")

# ======================================================
# PAGE: SHOPPING (LISTE DE COURSES)
# ======================================================
elif st.session_state.page == "shopping":
    st.title("🛒 Ma Liste de Courses")
    
    if not st.session_state.shopping_list:
        st.info("Votre panier est vide.")
    else:
        col_list, col_action = st.columns([2, 1])
        with col_action:
            if st.button("🗑 Vider toute la liste", type="primary", use_container_width=True):
                st.session_state.shopping_list = []
                st.rerun()
            
            # Optionnel: Générer un texte pour copier/coller sur WhatsApp
            shop_text = "\n".join([f"- {item}" for item in st.session_state.shopping_list])
            st.download_button("📩 Exporter la liste (TXT)", shop_text, file_name="courses.txt")

        with col_list:
            for idx, item in enumerate(st.session_state.shopping_list):
                c1, c2 = st.columns([0.9, 0.1])
                c1.write(f"⬜ {item}")
                if c2.button("❌", key=f"del_{idx}"):
                    st.session_state.shopping_list.pop(idx)
                    st.rerun()

# ======================================================
# PAGE: PLANNING
# ======================================================
elif st.session_state.page == "planning":
    st.title("📅 Planning de la Semaine")
    df = load_data()
    plan = df[df['Date_Prevue'] != ''].copy()
    
    if plan.empty:
        st.info("Rien de prévu au menu pour le moment.")
    else:
        # Tri par date (nécessite conversion)
        plan['dt'] = pd.to_datetime(plan['Date_Prevue'], format="%d/%m/%Y", errors='coerce')
        plan = plan.sort_values('dt')
        
        for _, row in plan.iterrows():
            with st.expander(f"📌 {row['Date_Prevue']} — {row['Titre']}"):
                st.write(f"**Catégorie:** {row['Catégorie']}")
                if st.button("Voir la recette complète", key=f"plan_btn_{row['Titre']}"):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"
                    st.rerun()

# ======================================================
# PAGE: AJOUTER
# ======================================================
elif st.session_state.page == "add":
    st.title("➕ Nouvelle Recette")
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            titre = st.text_input("Nom du plat *")
            cat = st.selectbox("Catégorie", CATEGORIES[1:])
            img_url = st.text_input("Lien de l'image (URL)")
        with col2:
            source = st.text_input("Source (Instagram, Web, Maman...)")
            date_now = datetime.now().strftime("%d/%m/%Y")
        
        ingreds = st.text_area("Ingrédients (un par ligne)", help="Exemple:\n200g de Pâtes\n1 filet d'huile")
        prepa = st.text_area("Étapes de préparation")
        
        submitted = st.form_submit_button("💾 Sauvegarder dans ma bibliothèque", use_container_width=True)
        if submitted:
            if not titre or not ingreds:
                st.error("Le titre et les ingrédients sont obligatoires.")
            else:
                success = send_update({
                    "action":"add", "titre":titre, "source":source, 
                    "ingredients":ingreds, "preparation":prepa, 
                    "categorie":cat, "image":img_url, "date":date_now
                })
                if success:
                    st.session_state.page = "home"
                    st.rerun()

# ======================================================
# PAGE: AIDE
# ======================================================
elif st.session_state.page == "aide":
    st.title("❓ Aide & Astuces")
    st.markdown("""
    <div class="help-card">
        <h3>🚀 Bien démarrer</h3>
        <p><b>Images :</b> Pour afficher une photo, faites un clic droit sur une image sur internet et choisissez "Copier l'adresse de l'image", puis collez-la dans le formulaire.</p>
        <p><b>Liste de courses :</b> Elle est temporaire. Si vous fermez votre navigateur, elle se videra. Pensez à l'exporter !</p>
        <p><b>Synchronisation :</b> L'application se synchronise avec Google Sheets. Si vous modifiez le fichier manuellement, cliquez sur 'Actualiser'.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
