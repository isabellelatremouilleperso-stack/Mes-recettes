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

# --- REMPLACE CES LIENS PAR LES TIENS ---
URL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=0&single=true&output=csv"
URL_CSV_SHOP = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRaY9boJAnQ5mh6WZFzhlGfmYO-pa9k_WuDIU9Gj5AusWeiHWIUPiSBmcuw7cSVX9VsGxxwB_GeE7u_/pub?gid=1037930000&single=true&output=csv"
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
    with st.spinner("📦 Synchronisation Cloud..."):
        try:
            r = requests.post(URL_SCRIPT, json=payload, timeout=20)
            if "Success" in r.text:
                st.success("Réussi !")
                st.cache_data.clear()
                time.sleep(0.5)
                return True
            st.error(f"Erreur : {r.text}")
        except Exception as e:
            st.error(f"Erreur de connexion : {e}")
    return False

if "page" not in st.session_state: st.session_state.page = "home"
if "recipe_data" not in st.session_state: st.session_state.recipe_data = {}

# ======================================================
# 3. BARRE LATÉRALE (AVEC AIDE CORRIGÉE)
# ======================================================
with st.sidebar:
    st.title("👨‍🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page = "home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page = "planning"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page = "shop"; st.rerun()
    st.write("---")
    if st.button("➕ Ajouter une recette", type="primary", use_container_width=True): st.session_state.page = "add"; st.rerun()
    if st.button("🔄 Actualiser", use_container_width=True): st.cache_data.clear(); st.rerun()

    st.divider()
    if "show_help" not in st.session_state: st.session_state.show_help = False
    
    if st.button("❓ Aide & Astuces", use_container_width=True):
        st.session_state.show_help = not st.session_state.show_help

    if st.session_state.show_help:
        with st.expander("📖 Guide Rapide", expanded=True):
            t1, t2, t3 = st.tabs(["➕", "🛒", "📅"])
            with t1: st.write("**Ajout :** Remplissez Titre & Ingrédients.")
            with t2: st.write("**Courses :** Cochez dans la recette pour sauver au Cloud.")
            with t3: st.write("**Planning :** 'Terminé' nettoie l'app mais reste sur Google.")

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
        if cat_f != "Toutes": filtered = filtered[filtered['Catégorie'].str.contains(cat_f, case=False, na=False)]
        
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
                        st.markdown(f'<div class="recipe-card"><img src="{img}" class="recipe-img"><h4 style="color:white;">{row["Titre"]}</h4>{badges}</div>', unsafe_allow_html=True)
                        if st.button("Ouvrir", key=f"btn_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
    else: st.info("Bibliothèque vide.")

# --- DÉTAILS ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    
    if not r:
        st.error("Erreur de chargement des données.")
        if st.button("Retour à l'accueil"): st.session_state.page = "home"; st.rerun()
        st.stop()

    col_back, col_del = st.columns([5, 1])
    if col_back.button("⬅ Retour"): st.session_state.page = "home"; st.rerun()
    if col_del.button("🗑️"): st.session_state.confirm_delete = True

    if st.session_state.get('confirm_delete', False):
        st.error("Supprimer cette recette ?")
        if st.button("✅ Confirmer Suppression"):
            if send_action({"action": "delete", "titre": r['Titre']}):
                st.session_state.confirm_delete = False; st.session_state.page = "home"; st.rerun()
        if st.button("❌ Annuler"): st.session_state.confirm_delete = False; st.rerun()

    st.title(f"🍳 {r['Titre']}")
    st.info(f"Portions : {r.get('Portions', '?')} | Prépa : {r.get('Temps_Prepa', '?')} | Cuisson : {r.get('Temps_Cuisson', '?')}")
    
    col_l, col_r = st.columns([1, 1.2])
    
    # --- COLONNE GAUCHE : IMAGE ET NOTES ---
    with col_l:
        img_url = r.get('Image', '')
        st.image(img_url if "http" in str(img_url) else "https://via.placeholder.com/400")
        
        if str(r.get('Source', '')).startswith("http"):
            st.markdown(f'<a href="{r["Source"]}" target="_blank" class="source-btn">🔗 Ouvrir le lien </a>', unsafe_allow_html=True)
        
        st.subheader("⭐ Avis & Notes")
        comm_actuel = str(r.get('Commentaires', ''))
        
        # Logique pour garder les étoiles allumées
        default_stars = None
        if "Note: " in comm_actuel:
            try:
                default_stars = int(comm_actuel.split("Note: ")[1].split("/5")[0]) - 1
            except: pass

        note = st.feedback("stars", key=f"note_{r['Titre']}", default=default_stars)
        txt_comm = st.text_area("Mes notes :", value=comm_actuel.split(" | ")[1] if " | " in comm_actuel else comm_actuel)
        
        if st.button("💾 Sauver l'avis"):
            val_note = note if note is not None else default_stars
            note_str = f"{val_note + 1}/5" if val_note is not None else "?"
            valeur_finale = f"Note: {note_str} | {txt_comm}"
            if send_action({"action":"update_notes", "titre": r['Titre'], "commentaires": valeur_finale}):
                st.session_state.recipe_data['Commentaires'] = valeur_finale
                st.rerun()
        
        st.divider()
        d_p = st.date_input("Planifier le :", value=datetime.now())
        if st.button("📅 Envoyer au Calendrier"):
            f_date = d_p.strftime("%d/%m/%Y")
            if send_action({"action":"update", "titre_original": r['Titre'], "date_prevue": f_date}):
                send_action({"action":"calendar", "titre": r['Titre'], "date_prevue": f_date, "ingredients": r['Ingrédients']})

    # --- COLONNE DROITE : INGRÉDIENTS ET PRÉPARATION (CE QUI MANQUAIT) ---
    with col_r:
        st.subheader("🛒 Ingrédients")
        ing_brut = r.get('Ingrédients', '')
        if ing_brut:
            ing_list = str(ing_brut).split("\n")
            temp_to_add = []
            for i, item in enumerate(ing_list):
                if item.strip() and st.checkbox(item.strip(), key=f"ing_{i}"):
                    temp_to_add.append(item.strip())
            
            if st.button("➕ Ajouter à l'épicerie"):
                for s in temp_to_add:
                    send_action({"action": "add_shop", "article": s})
                st.toast("Ajouté !")
        else:
            st.write("Aucun ingrédient répertorié.")

        st.divider()
        st.subheader("📝 Préparation")
        prep_txt = r.get('Préparation', 'Aucune instruction.')
        st.write(prep_txt)
# --- AJOUTER ---
elif st.session_state.page == "add":
    st.header("➕ Nouvelle Recette")
    with st.form("form_add", clear_on_submit=True):
        t = st.text_input("Titre *")
        cat = ", ".join(st.multiselect("Catégories", CATEGORIES[1:]))
        c1, c2 = st.columns(2)
        src = c1.text_input("Lien Vidéo")
        img = c2.text_input("URL Image")
        cp, cpr, ccu = st.columns(3)
        port, prep, cuis = cp.text_input("Portions"), cpr.text_input("Prépa"), ccu.text_input("Cuisson")
        ing = st.text_area("Ingrédients *")
        pre = st.text_area("Préparation")
        if st.form_submit_button("💾 Enregistrer"):
            if t and ing:
                payload = {"action": "add", "titre": t, "categorie": cat, "source": src, "image": img, "ingredients": ing, "preparation": pre, "portions": port, "t_prepa": prep, "t_cuisson": cuis, "date": datetime.now().strftime("%d/%m/%Y")}
                if send_action(payload): st.session_state.page = "home"; st.rerun()

# --- ÉPICERIE (PERMANENTE) ---
elif st.session_state.page == "shop":
    st.header("🛒 Liste d'Épicerie")
    if st.button("🗑 Tout vider"):
        if send_action({"action": "clear_shop"}): st.rerun()
    try:
        df_shop = pd.read_csv(f"{URL_CSV_SHOP}&nocache={time.time()}")
        if not df_shop.empty:
            for idx, row in df_shop.iterrows():
                item = row['Article']
                if pd.isna(item): continue
                c_a, c_b = st.columns([0.8, 0.2])
                c_a.write(f"✅ **{item}**")
                if c_b.button("❌", key=f"del_{idx}"):
                    if send_action({"action": "remove_item_shop", "article": item}): st.rerun()
        else: st.info("Liste vide.")
    except: st.error("Erreur de chargement. Vérifiez l'URL_CSV_SHOP.")

# --- PLANNING ---
elif st.session_state.page == "planning":
    st.header("📅 Agenda")
    df = load_data()
    if not df.empty:
        plan = df[df['Date_Prevue'] != ''].copy()
        if plan.empty: st.info("Rien de prévu.")
        else:
            plan['dt_object'] = pd.to_datetime(plan['Date_Prevue'], format='%d/%m/%Y', errors='coerce')
            plan = plan.sort_values('dt_object')
            for _, row in plan.iterrows():
                st.markdown(f'<div style="background-color:#1e2129; border-left:5px solid #e67e22; padding:15px; border-radius:10px; margin-bottom:10px;"><b>{row["Date_Prevue"]}</b> - {row["Titre"]}</div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                if c1.button("📖 Voir", key=f"p_v_{row['Titre']}", use_container_width=True):
                    st.session_state.recipe_data = row.to_dict(); st.session_state.page = "details"; st.rerun()
                if c2.button("✅ Terminé", key=f"p_d_{row['Titre']}", use_container_width=True):
                    if send_action({"action": "update", "titre_original": row['Titre'], "date_prevue": ""}): st.rerun()






