import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ======================================================
# 1. CONFIGURATION & DESIGN
# ======================================================
st.set_page_config(page_title="Chef Master Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    h1, h2, h3 { color: #e67e22 !important; }
    .recipe-card {
        background-color: #1e2129; border: 1px solid #3d4455;
        border-radius: 15px; padding: 10px; transition: 0.3s;
    }
    .recipe-card:hover { border-color: #e67e22; transform: translateY(-5px); }
    .recipe-img { width: 100%; height: 160px; object-fit: cover; border-radius: 10px; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    /* Style pour le bouton source */
    .source-btn {
        background-color: #3d4455; color: white; text-align: center; 
        padding: 10px; border-radius: 8px; font-weight: bold; 
        margin-bottom: 15px; text-decoration: none; display: block;
    }
    .source-btn:hover { background-color: #e67e22; color: white; }
</style>
""", unsafe_allow_html=True)

URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"
CATEGORIES = ["Toutes","Poulet","Bœuf","Porc","Poisson","Pâtes","Riz","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Autre"]

# ======================================================
# 2. FONCTIONS TECHNIQUES
# ======================================================
@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        expected = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires']
        if len(df.columns) >= len(expected):
            df.columns = expected[:len(df.columns)]
        return df
    except:
        return pd.DataFrame()

def send_action(payload):
    with st.spinner("📦 Synchronisation..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=15)
            if "Success" in r.text:
                st.success("Réussi !")
                st.cache_data.clear()
                time.sleep(1)
                return True
            st.error(f"Erreur : {r.text}")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")
    return False

if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}
if "shopping_list" not in st.session_state: st.session_state.shopping_list = []

# ======================================================
# 3. BARRE LATÉRALE
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Ma Cuisine")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button(f"🛒 Épicerie ({len(st.session_state.shopping_list)})", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()

    st.divider()
    with st.expander("💡 Besoin d'aide ?"):
        aide_theme = st.selectbox("Thème :", ["Général", "Ajout", "Courses", "Calendrier"])
        if aide_theme == "Général": st.info("Naviguez via le menu latéral.")
        elif aide_theme == "Ajout": st.write("Collez le lien Instagram/TikTok dans le champ 'Source'.")
        elif aide_theme == "Courses": st.write("Cochez les ingrédients pour les envoyer à l'épicerie.")
        elif aide_theme == "Calendrier": st.write("Planifiez pour voir dans Google Calendar.")

# ======================================================
# 4. LOGIQUE DES PAGES
# ======================================================

# --- ACCUEIL ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("🔍 Rechercher...", placeholder="Ex: Lasagnes")
    cat_f = c2.selectbox("Filtrer par catégorie", CATEGORIES)

    if not df.empty:
        filtered = df.copy()
        
        # Recherche par titre
        if search: 
            filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        
        # FILTRE MULTI-CATÉGORIES CORRIGÉ
        if cat_f != "Toutes": 
            # On vérifie si la catégorie choisie est contenue dans la liste des catégories de la recette
            filtered = filtered[filtered['Catégorie'].str.contains(cat_f, case=False, na=False)]
        
        rows = filtered.reset_index(drop=True)
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
                        
                        # Affichage des catégories en petits badges sous le titre
                        cats = str(row['Catégorie']).split(", ")
                        badges = "".join([f'<span style="background-color: #3d4455; color: #e67e22; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; margin-right: 4px;">{c}</span>' for c in cats if c])

                        st.markdown(f"""
                        <div class="recipe-card" style="height: 400px; display: flex; flex-direction: column; justify-content: space-between;">
                            <div>
                                <img src="{img}" class="recipe-img">
                                <h4 style="margin: 10px 0 5px 0; font-size: 0.95rem; height: 50px; overflow-y: auto; color: white;">{row['Titre']}</h4>
                                <div style="margin-bottom: 8px;">{badges}</div>
                                <p style="color: #e67e22; font-size: 0.8rem; margin:0;">👥 {row['Portions']} | ⏱ {row['Temps_Prepa']}</p>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if st.button("Ouvrir", key=f"btn_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict()
                            st.session_state.page = "details"; st.rerun()
    else: 
        st.info("Votre bibliothèque est vide.")

# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    
    col_back, col_del = st.columns([5, 1])
    with col_back:
        if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    with col_del:
        if st.button("🗑️", help="Supprimer définitivement"):
            st.session_state.confirm_delete = True

    if st.session_state.get('confirm_delete', False):
        st.error(f"Voulez-vous vraiment supprimer '{r['Titre']}' ?")
        cb1, cb2 = st.columns(2)
        if cb1.button("✅ Oui, supprimer", type="primary"):
            if send_action({"action": "delete", "titre": r['Titre']}):
                st.session_state.confirm_delete = False
                st.session_state.page = "home"; st.rerun()
        if cb2.button("❌ Annuler"):
            st.session_state.confirm_delete = False; st.rerun()

    st.title(f"🍳 {r['Titre']}")
    st.info(f"💡 Portions : {r['Portions']} | Prépa : {r['Temps_Prepa']} | Cuisson : {r['Temps_Cuisson']}")
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        
        # --- BOUTON SOURCE CLIQUABLE ---
        source_val = str(r['Source'])
        if source_val.startswith("http"):
            st.markdown(f'<a href="{source_val}" target="_blank" class="source-btn">🔗 Voir la vidéo originale</a>', unsafe_allow_html=True)
        elif source_val:
            st.caption(f"Source : {source_val}")
        
        st.subheader("⭐ Mon Avis")
        note = st.feedback("stars", key=f"note_{r['Titre']}")
        fait = st.checkbox("✅ Je l'ai faite !", value=False)
        comm = st.text_area("Mes astuces personnelles", value=r.get('Commentaires',''))
        if st.button("💾 Sauvegarder l'avis", use_container_width=True):
            statut = "DONE" if fait else "A TESTER"
            nouveau_comm = f"[{statut}] Note: {note if note else '?'}/5 - {comm}"
            send_action({"action":"update_notes", "titre": r['Titre'], "commentaires": nouveau_comm})
        
        st.write("---")
        st.subheader("📅 Planifier")
        d_p = st.date_input("Choisir une date :", value=datetime.now())
        if st.button("📅 Envoyer au Calendrier"):
            f_date = d_p.strftime("%d/%m/%Y")
            if send_action({"action":"update", "titre_original": r['Titre'], "date_prevue": f_date}):
                send_action({"action":"calendar", "titre": r['Titre'], "date_prevue": f_date, "ingredients": r['Ingrédients']})

    with col_r:
        st.subheader("🛒 Ingrédients")
        ing_list = str(r['Ingrédients']).split("\n")
        temp_to_add = []
        for i, item in enumerate(ing_list):
            if item.strip():
                if st.checkbox(item.strip(), key=f"ing_ch_{i}"):
                    temp_to_add.append(item.strip())
        
        if st.button("➕ Ajouter à l'épicerie", use_container_width=True, type="primary"):
            for s in temp_to_add:
                if s not in st.session_state.shopping_list:
                    st.session_state.shopping_list.append(s)
            st.toast("✅ Ingrédients ajoutés !")

        st.divider()
        st.subheader("📝 Préparation")
        st.info(r['Préparation'] if r['Préparation'].strip() else "Aucune instruction saisie.")

# --- AJOUTER ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    with st.form("form_add", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            t = st.text_input("Titre *")
           # Choix multiple au lieu d'un seul
cat_list = st.multiselect("Catégories (choisissez-en plusieurs)", CATEGORIES[1:])
# On transforme la liste en texte "Poulet, Plat Principal" pour l'enregistrer
cat = ", ".join(cat_list)
        with c2:
            src = st.text_input("Lien de la source (Instagram, TikTok, FB...)")
            img = st.text_input("URL Image")
        
        st.write("⏱ Détails")
        cp, cpr, ccu = st.columns(3)
        port = cp.text_input("Portions (ex: 4p)")
        prep = cpr.text_input("Prépa (ex: 15min)")
        cuis = ccu.text_input("Cuisson (ex: 20min)")
        
        ing = st.text_area("Ingrédients * (un par ligne)")
        pre = st.text_area("Préparation")
        
        if st.form_submit_button("💾 Enregistrer la recette", use_container_width=True):
            if t and ing:
                payload = {
                    "action": "add", "titre": t, "categorie": cat, "source": src, "image": img,
                    "ingredients": ing, "preparation": pre, "portions": port,
                    "t_prepa": prep, "t_cuisson": cuis,
                    "date": datetime.now().strftime("%d/%m/%Y")
                }
                if send_action(payload):
                    st.session_state.page = "home"; st.rerun()

# --- ÉPICERIE ---
elif st.session_state.page == "shop":
    st.header("🛒 Ma Liste de Courses")
    if st.button("🗑 Tout vider"): st.session_state.shopping_list = []; st.rerun()
    for idx, item in enumerate(st.session_state.shopping_list):
        ct, cd = st.columns([0.8, 0.2])
        ct.write(f"✅ **{item}**")
        if cd.button("❌", key=f"del_shop_{idx}"):
            st.session_state.shopping_list.pop(idx); st.rerun()

# --- PAGE: PLANNING (VERSION AMÉLIORÉE) ---
elif st.session_state.page == "planning":
    st.header("📅 Mon Agenda Gourmand")
    df = load_data()
    
    if not df.empty:
        # On filtre les recettes qui ont une date prévue
        plan = df[df['Date_Prevue'] != ''].copy()
        
        if plan.empty:
            st.info("Votre agenda est vide. Planifiez des recettes depuis leur fiche détail !")
        else:
            # Conversion des dates pour un tri correct
            plan['dt_object'] = pd.to_datetime(plan['Date_Prevue'], format='%d/%m/%Y', errors='coerce')
            plan = plan.sort_values('dt_object')

            # Affichage sous forme de timeline
            for _, row in plan.iterrows():
                with st.container():
                    # Style de la carte planning
                    st.markdown(f"""
                    <div style="background-color: #1e2129; border-left: 5px solid #e67e22; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                        <span style="color: #e67e22; font-weight: bold; font-size: 1.1rem;">🗓 {row['Date_Prevue']}</span>
                        <h3 style="margin: 5px 0; color: white !important;">{row['Titre']}</h3>
                        <p style="font-size: 0.85rem; color: #a0a0a0; margin: 0;">🍴 {row['Catégorie']} | ⏱ {row['Temps_Prepa']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Boutons d'action pour le planning
                    c1, c2, c3 = st.columns([1, 1, 2])
                    if c1.button("📖 Voir Recette", key=f"plan_view_{row['Titre']}"):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()
                    
                    if c2.button("🚫 Retirer", key=f"plan_rm_{row['Titre']}", help="Enlever du planning"):
                        if send_action({"action": "update", "titre_original": row['Titre'], "date_prevue": ""}):
                            st.rerun()
                    st.write("") # Espace entre les jours
    else:
        st.error("Impossible de charger les données.")


