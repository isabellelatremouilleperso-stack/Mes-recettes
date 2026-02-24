import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ======================================================
# 1. CONFIGURATION & DESIGN PREMIUM
# ======================================================
st.set_page_config(page_title="Chef Master Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    /* Fond sombre global */
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }
    
    /* Cartes Bibliothèque avec hauteur fixe pour alignement parfait */
    .recipe-card {
        background-color: #1e2129;
        border: 1px solid #3d4455;
        border-radius: 15px;
        padding: 10px;
        transition: 0.3s;
    }
    .recipe-card:hover { border-color: #e67e22; transform: translateY(-5px); }
    .recipe-img { width: 100%; height: 160px; object-fit: cover; border-radius: 10px; }
    
    /* Boutons et Inputs */
    .stButton>button { border-radius: 8px; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #262730 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)

# CONFIGURATION DES URLS (Vérifiez bien votre URL_SCRIPT après déploiement)
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# ======================================================
# 2. FONCTIONS DE SYNCHRONISATION (12 COLONNES)
# ======================================================
@st.cache_data(ttl=5)
def load_data():
    try:
        # Ajout d'un paramètre aléatoire pour forcer la mise à jour
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        # Définition stricte des 12 colonnes (A à L)
        expected = [
            'Date','Titre','Source','Ingrédients','Préparation','Date_Prevue',
            'Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires'
        ]
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except:
        return pd.DataFrame()

def send_action(payload):
    with st.spinner("📦 Synchronisation avec le Cloud..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=15)
            if "Success" in r.text:
                st.success("Action enregistrée !")
                st.cache_data.clear()
                time.sleep(1)
                return True
            else:
                st.error(f"Erreur Google : {r.text}")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")
    return False

# Initialisation du Session State
if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# ======================================================
# 3. BARRE LATÉRALE (NAVIGATION)
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()

    # --- LE BLOC D'AIDE RÉTABLI ICI ---
    st.divider()
    with st.expander("💡 Besoin d'aide ?"):
        aide_theme = st.selectbox("Choisir un thème :", 
            ["Guide d'utilisation", "Ajouter une recette", "Gérer l'épicerie", "Planning & Calendrier"])
        
        if aide_theme == "Guide d'utilisation":
            st.info("Bienvenue ! Utilisez le menu pour naviguer entre votre bibliothèque et vos outils.")
        elif aide_theme == "Ajouter une recette":
            st.write("Cliquez sur **Ajouter**. Remplissez le titre, les ingrédients et les temps. Vous pouvez aussi l'envoyer directement au planning.")
        elif aide_theme == "Gérer l'épicerie":
            st.write("Dans une recette, cochez les ingrédients et cliquez sur le bouton bleu pour les envoyer dans votre liste d'achats.")
        elif aide_theme == "Planning & Calendrier":
            st.write("Planifiez une date pour envoyer la recette dans l'onglet Planning et créer un événement sur votre Google Calendar.")

# ======================================================
# 4. LOGIQUE DES PAGES
# ======================================================

# --- TROUVE LA PAGE HOME ET REMPLACE-LA ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    
    col_search, col_filter = st.columns([2, 1])
    search = col_search.text_input("🔍 Rechercher...", placeholder="Ex: Poulet Coco")
    cat_f = col_filter.selectbox("Filtrer par catégorie", CATEGORIES)

    if not df.empty:
        filtered = df.copy()
        if search: 
            filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": 
            filtered = filtered[filtered['Catégorie'] == cat_f]
        
        # Grille alignée (3 colonnes) avec police adaptée
        rows = filtered.reset_index(drop=True)
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        st.markdown(f"""
                        <div class="recipe-card" style="height: 380px; display: flex; flex-direction: column; justify-content: space-between;">
                            <div>
                                <img src="{img}" class="recipe-img">
                                <h4 style="margin: 10px 0 5px 0; font-size: 0.95rem; height: 65px; overflow-y: auto; color: white; line-height: 1.2;">
                                    {row['Titre']}
                                </h4>
                                <p style="color: #e67e22; font-size: 0.8rem; margin:0; font-weight: bold;">
                                    👥 {row.get('Portions', 'N/A')} | ⏱ {row.get('Temps_Prepa', 'N/A')}
                                </p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Ouvrir la fiche", key=f"btn_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"; st.rerun()
    else:
        st.info("Votre bibliothèque est vide.")

# --- PAGE: DÉTAILS (VERSION FINALE : ÉTOILES + JE L'AI FAITE) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    # --- PAGE: DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data

    # C'EST ICI QUE TU COLLES LE BLOC DE LA POUBELLE
    col_back, col_del = st.columns([5, 1])
    with col_back:
        if st.button("⬅ Retour"): 
            st.session_state.page = "home"; st.rerun()
    with col_del:
        if st.button("🗑️", help="Supprimer cette recette"):
            st.session_state.confirm_delete = True

    if st.session_state.get('confirm_delete', False):
        st.warning(f"Voulez-vous vraiment supprimer '{r['Titre']}' ?")
        c1, c2 = st.columns(2)
        if c1.button("✅ Oui, supprimer", type="primary"):
            if send_action({"action": "delete", "titre": r['Titre']}):
                st.session_state.confirm_delete = False
                st.session_state.page = "home"
                st.rerun()
        if c2.button("❌ Annuler"):
            st.session_state.confirm_delete = False
            st.rerun()
    # FIN DU BLOC POUBELLE

    # Ensuite le reste de ton code (Titre, Image, etc.) continue ici...
    st.title(f"🍳 {r['Titre']}")
    # ...
    if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    
    st.title(f"🍳 {r['Titre']}")
    
    # Informations rapides
    st.info(f"💡 **Aide Mémoire :** Portions : **{r['Portions']}** | Prépa : **{r['Temps_Prepa']}** | Cuisson : **{r['Temps_Cuisson']}**")
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        
        st.write("---")
        st.subheader("⭐ Mon Avis")
        
        # Le système d'étoiles (1 à 5)
        # On essaie de récupérer la note si elle existe, sinon 3 par défaut
        note = st.feedback("stars", key="recipe_rating")
        
        # La case "Je l'ai faite !"
        fait = st.checkbox("✅ Je l'ai faite !", value=False, help="Cochez cette case si vous avez déjà testé cette recette.")
        
        comm = st.text_area("Mes astuces personnelles", value=r.get('Commentaires',''), placeholder="Ex: Ajouter un peu plus de sel...")
        
        if st.button("💾 Sauvegarder mon avis", use_container_width=True):
            # On combine la note, le statut "fait" et le commentaire pour la colonne L
            statut_fait = "DONE" if fait else "A TESTER"
            nouveau_comm = f"[{statut_fait}] Note: {note if note else '?'}/5 - {comm}"
            
            if send_action({"action":"update_notes", "titre": r['Titre'], "commentaires": nouveau_comm}):
                st.toast("Avis enregistré !")

    with col_r:
        st.subheader("🛒 Ingrédients")
        ing_list = str(r['Ingrédients']).split("\n")
        temp_to_add = []
        for i, item in enumerate(ing_list):
            if item.strip():
                if st.checkbox(item.strip(), key=f"ing_check_{i}"):
                    temp_to_add.append(item.strip())
        
        if st.button("➕ Ajouter à l'épicerie", use_container_width=True, type="primary"):
            if temp_to_add:
                for selection in temp_to_add:
                    if selection not in st.session_state.shopping_list:
                        st.session_state.shopping_list.append(selection)
                st.toast(f"✅ {len(temp_to_add)} ingrédients ajoutés !")
                time.sleep(1)
                st.rerun()

        st.write("---")
        st.subheader("📝 Mode opératoire")
        st.info(r['Préparation'] if r['Préparation'].strip() else "Aucune instruction.")
# --- PAGE: AJOUTER ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    with st.form("form_add", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            t = st.text_input("Titre de la recette *")
            cat = st.selectbox("Catégorie", CATEGORIES[1:])
        with col2:
            src = st.text_input("Source (Instagram, Web...)")
            img = st.text_input("URL de l'image")
        
        st.write("⏱ **Détails rapides**")
        c_port, c_prepa, c_cuis = st.columns(3)
        portions = c_port.text_input("Portions (ex: 4p)")
        t_prepa = c_prepa.text_input("Préparation (ex: 15min)")
        t_cuisson = c_cuis.text_input("Cuisson (ex: 30min)")
        
        ing = st.text_area("Ingrédients (un par ligne) *")
        pre = st.text_area("Préparation")
        
        st.write("---")
        plan_now = st.checkbox("Planifier immédiatement au calendrier")
        date_plan = st.date_input("Date choisie", value=datetime.now())

        if st.form_submit_button("💾 Enregistrer la recette", use_container_width=True):
            if t and ing:
                f_date = date_plan.strftime("%d/%m/%Y")
                payload = {
                    "action": "add", "titre": t, "categorie": cat, "source": src, "image": img,
                    "ingredients": ing, "preparation": pre, "portions": portions,
                    "t_prepa": t_prepa, "t_cuisson": t_cuisson,
                    "date": datetime.now().strftime("%d/%m/%Y"),
                    "date_prevue": f_date if plan_now else ""
                }
                if send_action(payload):
                    if plan_now:
                        send_action({"action":"calendar", "titre": t, "date_prevue": f_date, "ingredients": ing})
                    st.session_state.page = "home"; st.rerun()

# --- PAGE: ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste de Courses")
    if st.button("🗑 Tout vider"): st.session_state.shopping_list = []; st.rerun()
    for idx, item in enumerate(st.session_state.shopping_list):
        c_txt, c_del = st.columns([0.85, 0.15])
        c_txt.write(f"✅ **{item}**")
        if c_del.button("❌", key=f"del_{idx}"):
            st.session_state.shopping_list.pop(idx); st.rerun()

# --- PAGE: PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Planning des repas")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ''].sort_values('Date_Prevue')
        if plan.empty: st.info("Aucun repas planifié.")
        else:
            for _, row in plan.iterrows():
                st.write(f"🗓 **{row['Date_Prevue']}** — {row['Titre']}")







