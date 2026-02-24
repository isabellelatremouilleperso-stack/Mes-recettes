import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ======================================================
# 1. CONFIGURATION DE LA PAGE & DESIGN (LE LOOK PRO)
# ======================================================
st.set_page_config(page_title="Chef Master Pro", layout="wide", page_icon="🍳")

# Injection CSS pour le look Sombre Premium
st.markdown("""
<style>
    /* Fond global noir profond */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    
    /* Style des titres en orange corail */
    h1, h2, h3 { color: #e67e22 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

    /* Cartes des recettes dans la bibliothèque */
    .recipe-card-container {
        background-color: #1e2129;
        border: 1px solid #3d4455;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 20px;
        transition: 0.3s;
        text-align: center;
    }
    .recipe-card-container:hover {
        border-color: #e67e22;
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    
    /* Image dans la carte */
    .recipe-img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        border-radius: 10px;
        margin-bottom: 10px;
    }

    /* Boutons personnalisés */
    .stButton>button {
        border-radius: 8px;
        border: none;
        transition: 0.3s;
    }
    
    /* Barre latérale */
    [data-testid="stSidebar"] { background-color: #161a21; border-right: 1px solid #3d4455; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 2. CONFIGURATION DES LIENS
# ======================================================
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# ======================================================
# 3. FONCTIONS TECHNIQUES (LE MOTEUR)
# ======================================================
@st.cache_data(ttl=10)
def load_data():
    try:
        # Cache busting pour forcer Google à rafraîchir le fichier
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Commentaires']
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except:
        return pd.DataFrame()

def send_to_google(payload):
    with st.spinner("📦 Synchronisation avec le livre de recettes..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=15)
            if "Success" in r.text:
                st.success("C'est enregistré dans le Cloud !")
                st.cache_data.clear()
                time.sleep(2) # Temps pour Google de mettre à jour le lien CSV
                return True
            else:
                st.error(f"Réponse Google : {r.text}")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")
    return False

# Initialisation des variables de session
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# ======================================================
# 4. BARRE LATÉRALE (NAVIGATION)
# ======================================================
with st.sidebar:
    st.markdown("<h1 style='text-align: center;'>👨‍🍳 Chef Pro</h1>", unsafe_allow_html=True)
    st.write("---")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter une recette", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🔄 Actualiser les données", use_container_width=True): st.cache_data.clear(); st.rerun()

# ======================================================
# 5. PAGES DE L'APPLICATION
# ======================================================

# --- PAGE: ACCUEIL / BIBLIOTHÈQUE ---
if st.session_state.page == "home":
    st.title("📚 Ma Bibliothèque")
    df = load_data()
    
    col_s, col_f = st.columns([2, 1])
    with col_s: search = st.text_input("🔍 Rechercher une recette...", placeholder="Ex: Poulet coco")
    with col_f: cat_f = st.selectbox("Filtrer", CATEGORIES)

    if not df.empty:
        filtered = df.copy()
        if search: filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": filtered = filtered[filtered['Catégorie'] == cat_f]
        
        # Affichage en grille de 3 colonnes
        cols = st.columns(3)
        for idx, row in filtered.reset_index(drop=True).iterrows():
            with cols[idx % 3]:
                img_url = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400x250?text=Pas+D'image"
                st.markdown(f"""
                    <div class="recipe-card-container">
                        <img src="{img_url}" class="recipe-img">
                        <h4 style="margin: 10px 0;">{row['Titre']}</h4>
                        <p style="font-size: 0.8rem; color: #e67e22;">{row['Catégorie']}</p>
                    </div>
                """, unsafe_allow_html=True)
                if st.button("Voir la fiche", key=f"view_{idx}", use_container_width=True):
                    st.session_state.recipe_data = row.to_dict()
                    st.session_state.page = "details"; st.rerun()
    else:
        st.info("Votre bibliothèque est vide. Ajoutez votre première recette !")

# --- PAGE: DETAILS D'UNE RECETTE ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.title(f"🍳 {r['Titre']}")
    col1, col2 = st.columns([1, 1.2])

    with col1:
        img_full = r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/600x400"
        st.image(img_full, use_container_width=True)
        st.write("---")
        st.subheader("📅 Planifier")
        d_plan = st.date_input("Choisir une date", value=datetime.now())
        if st.button("Enregistrer au planning"):
            payload = {"action": "update", "titre_original": r['Titre'], "date_prevue": d_plan.strftime("%d/%m/%Y")}
            if send_to_google(payload): st.rerun()

    with col2:
        st.subheader("🛒 Ingrédients")
        ing_list = str(r['Ingrédients']).split("\n")
        selected_items = []
        for i, item in enumerate(ing_list):
            if item.strip():
                if st.checkbox(item, key=f"check_{i}"):
                    selected_items.append(item)
        
        if st.button("Ajouter la sélection à ma liste", use_container_width=True):
            st.session_state.shopping_list.extend([x for x in selected_items if x not in st.session_state.shopping_list])
            st.toast("Liste mise à jour !")

        st.write("---")
        st.subheader("📝 Préparation")
        st.info(r['Préparation'])

# --- PAGE: AJOUTER ---
elif st.session_state.page == "add":
    st.header("➕ Nouvelle Recette")
    with st.form("form_add", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            new_t = st.text_input("Titre de la recette *")
            new_c = st.selectbox("Catégorie", CATEGORIES[1:])
        with c2:
            new_s = st.text_input("Source (Instagram, TikTok...)")
            new_i = st.text_input("URL de l'image")
        
        new_ing = st.text_area("Ingrédients (un par ligne) *")
        new_pre = st.text_area("Instructions de préparation")
        
        if st.form_submit_button("Sauvegarder la recette", use_container_width=True):
            if new_t and new_ing:
                p = {
                    "action": "add", "titre": new_t, "categorie": new_c, "source": new_s,
                    "image": new_i, "ingredients": new_ing, "preparation": new_pre,
                    "date": datetime.now().strftime("%d/%m/%Y")
                }
                if send_to_google(p): 
                    st.session_state.page = "home"; st.rerun()
            else:
                st.error("Le titre et les ingrédients sont obligatoires !")

# --- PAGE: PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning des repas")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ''].sort_values('Date_Prevue')
        if plan.empty: st.info("Rien de prévu au menu.")
        else:
            for _, row in plan.iterrows():
                st.write(f"🗓 **{row['Date_Prevue']}** — {row['Titre']}")
    
# --- PAGE: SHOP ---
elif st.session_state.page == "shop":
    st.header("🛒 Liste de courses")
    if st.button("🗑 Tout vider"): st.session_state.shopping_list = []; st.rerun()
    for item in st.session_state.shopping_list:
        st.write(f"✅ {item}")
