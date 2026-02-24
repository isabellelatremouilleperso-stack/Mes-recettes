import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# ======================================================
# 1. CONFIGURATION & DESIGN
# ======================================================
st.set_page_config(page_title="Mes Recettes", layout="wide", page_icon="🍳")

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
        if search: filtered = filtered[filtered['Titre'].str.contains(search, case=False)]
        if cat_f != "Toutes": 
            filtered = filtered[filtered['Catégorie'].str.contains(cat_f, case=False, na=False)]
        
        rows = filtered.reset_index(drop=True)
        for i in range(0, len(rows), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(rows):
                    row = rows.iloc[i + j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"
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
    else: st.info("Votre bibliothèque est vide.")

# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    col_back, col_del = st.columns([5, 1])
    with col_back:
        if st.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    with col_del:
        if st.button("🗑️"): st.session_state.confirm_delete = True

    if st.session_state.get('confirm_delete', False):
        st.error("Supprimer ?")
        cb1, cb2 = st.columns(2)
        if cb1.button("✅ Oui"):
            if send_action({"action": "delete", "titre": r['Titre']}):
                st.session_state.confirm_delete = False; st.session_state.page = "home"; st.rerun()
        if cb2.button("❌ Non"): st.session_state.confirm_delete = False; st.rerun()

    st.title(f"🍳 {r['Titre']}")
    
    # Affichage des badges catégories dans les détails
    c_list = r['Catégorie'].split(", ")
    badge_html = "".join([f'<span style="background-color: #e67e22; color: white; padding: 3px 10px; border-radius: 12px; margin-right: 5px; font-size: 0.8rem;">{c}</span>' for c in c_list if c])
    st.markdown(badge_html, unsafe_allow_html=True)
    st.info(f"Portions : {r['Portions']} | Prépa : {r['Temps_Prepa']} | Cuisson : {r['Temps_Cuisson']}")
    
    col_l, col_r = st.columns([1, 1.2])
    with col_l:
        st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400")
        source_val = str(r['Source'])
        if source_val.startswith("http"):
            st.markdown(f'<a href="{source_val}" target="_blank" class="source-btn">🔗 Voir la vidéo originale</a>', unsafe_allow_html=True)
        
        st.subheader("⭐ Mon Avis")
        note = st.feedback("stars", key=f"note_{r['Titre']}")
        fait = st.checkbox("✅ Faite !")
        if st.button("💾 Sauver l'avis", use_container_width=True):
            nouveau_comm = f"[{'DONE' if fait else 'A TESTER'}] Note: {note}/5"
            send_action({"action":"update_notes", "titre": r['Titre'], "commentaires": nouveau_comm})

    with col_r:
        st.subheader("🛒 Ingrédients")
        ing_list = str(r['Ingrédients']).split("\n")
        temp_to_add = []
        for i, item in enumerate(ing_list):
            if item.strip() and st.checkbox(item.strip(), key=f"ing_{i}"):
                temp_to_add.append(item.strip())
        if st.button("➕ Ajouter à l'épicerie"):
            st.session_state.shopping_list.extend(temp_to_add); st.toast("Ajouté !")

# --- AJOUTER ---
elif st.session_state.page == "add":
    st.header("➕ Ajouter une recette")
    with st.form("form_add", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            t = st.text_input("Titre *")
            cat_list = st.multiselect("Catégories", CATEGORIES[1:])
            cat = ", ".join(cat_list)
        with c2:
            src = st.text_input("Lien Source")
            img = st.text_input("URL Image")
        
        st.write("⏱ Détails")
        cp, cpr, ccu = st.columns(3)
        port = cp.text_input("Portions")
        prep = cpr.text_input("Prépa")
        cuis = ccu.text_input("Cuisson")
        
        ing = st.text_area("Ingrédients *")
        pre = st.text_area("Préparation")
        
        if st.form_submit_button("💾 Enregistrer", use_container_width=True):
            if t and ing:
                payload = {"action": "add", "titre": t, "categorie": cat, "source": src, "image": img, "ingredients": ing, "preparation": pre, "portions": port, "t_prepa": prep, "t_cuisson": cuis, "date": datetime.now().strftime("%d/%m/%Y")}
                if send_action(payload):
                    st.session_state.page = "home"; st.rerun()

# --- PAGE: PLANNING (VERSION AVEC NETTOYAGE) ---
elif st.session_state.page == "planning":
    st.header("📅 Mon Agenda Gourmand")
    df = load_data()
    
    if not df.empty:
        # On filtre les recettes qui ont une date prévue
        plan = df[df['Date_Prevue'] != ''].copy()
        
        if plan.empty:
            st.info("Votre agenda est vide. Planifiez des recettes depuis leur fiche détail !")
        else:
            # Tri par date
            plan['dt_object'] = pd.to_datetime(plan['Date_Prevue'], format='%d/%m/%Y', errors='coerce')
            plan = plan.sort_values('dt_object')

            for _, row in plan.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="background-color: #1e2129; border-left: 5px solid #e67e22; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                        <span style="color: #e67e22; font-weight: bold;">🗓 {row['Date_Prevue']}</span>
                        <h3 style="margin: 5px 0; color: white !important;">{row['Titre']}</h3>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([1, 1])
                    
                    # Bouton 1 : Voir la recette
                    if c1.button("📖 Voir la recette", key=f"view_{row['Titre']}", use_container_width=True):
                        st.session_state.recipe_data = row.to_dict()
                        st.session_state.page = "details"; st.rerun()
                    
                    # Bouton 2 : Terminé (Nettoie l'app mais garde le calendrier Google)
                    if c2.button("✅ Repas terminé", key=f"done_{row['Titre']}", use_container_width=True, help="Retire du planning ici, mais reste dans Google Calendar"):
                        # On envoie une mise à jour à Google Sheets pour effacer SEULEMENT la date prévue
                        if send_action({"action": "update", "titre_original": row['Titre'], "date_prevue": ""}):
                            st.toast(f"Bravo ! {row['Titre']} retiré du planning.")
                            time.sleep(1)
                            st.rerun()
                st.write("---")
    else:
        st.error("Impossible de charger les données.")

