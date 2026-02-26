import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time
from bs4 import BeautifulSoup
import urllib.parse

# ======================================================
# CONFIGURATION
# ======================================================
st.set_page_config(page_title="Mes Recettes Pro", layout="wide", page_icon="🍳")

st.markdown("""
<style>
.stApp { background-color: #0e1117; color: #e0e0e0; }
h1, h2, h3 { color: #e67e22 !important; }
.recipe-card {
    background-color: #1e2129;
    border: 1px solid #3d4455;
    border-radius: 12px;
    padding: 10px;
    height: 230px;
}
.recipe-img {
    width: 100%;
    height: 130px;
    object-fit: cover;
    border-radius: 8px;
}
.recipe-title {
    color: white;
    margin-top: 8px;
    font-size: 0.95rem;
    font-weight: bold;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

URL_CSV = "TON_LIEN_CSV"
URL_CSV_SHOP = "TON_LIEN_SHOP"
URL_SCRIPT = "TON_LIEN_SCRIPT"

CATEGORIES = ["Poulet","Bœuf","Porc","Agneau","Poisson","Fruits de mer","Pâtes","Riz","Légumes","Soupe","Salade","Entrée","Plat Principal","Dessert","Petit-déjeuner","Goûter","Apéro","Sauce","Boisson","Autre"]

# ======================================================
# FONCTIONS
# ======================================================
def send_action(payload):
    try:
        r = requests.post(URL_SCRIPT, json=payload, timeout=15)
        if "Success" in r.text:
            st.cache_data.clear()
            return True
    except:
        pass
    return False

def scrape_url(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        title = soup.find('h1')
        title = title.text.strip() if title else "Recette Importée"
        elements = soup.find_all(['li','p'])
        content = "\n".join(
            dict.fromkeys(
                [el.text.strip() for el in elements if 10 < len(el.text.strip()) < 500]
            )
        )
        return title, content
    except:
        return None, None

@st.cache_data(ttl=5)
def load_data():
    try:
        df = pd.read_csv(f"{URL_CSV}&nocache={time.time()}").fillna('')
        cols = ['Date','Titre','Source','Ingrédients','Préparation','Date_Prevue','Image','Catégorie','Portions','Temps_Prepa','Temps_Cuisson','Commentaires','Note']
        df.columns = cols[:len(df.columns)]
        return df
    except:
        return pd.DataFrame()

if "page" not in st.session_state:
    st.session_state.page = "home"

# ======================================================
# SIDEBAR
# ======================================================
with st.sidebar:
    st.title("🍳 Mes Recettes")

    if st.button("📚 Bibliothèque", use_container_width=True):
        st.session_state.page="home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True):
        st.session_state.page="planning"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True):
        st.session_state.page="shop"; st.rerun()
    if st.button("➕ Ajouter", use_container_width=True, type="primary"):
        st.session_state.page="add"; st.rerun()
    if st.button("⭐ Play Store", use_container_width=True):
        st.session_state.page="playstore"; st.rerun()
    if st.button("❓ Aide", use_container_width=True):
        st.session_state.page="help"; st.rerun()

# ======================================================
# PAGE ACCUEIL
# ======================================================
if st.session_state.page == "home":

    st.header("📚 Ma Bibliothèque")
    df = load_data()

    if not df.empty:
        search = st.text_input("🔍 Rechercher")
        mask = df['Titre'].str.contains(search, case=False, na=False)
        rows = df[mask].reset_index(drop=True)

        for i in range(0,len(rows),3):
            cols = st.columns(3)
            for j in range(3):
                if i+j < len(rows):
                    row = rows.iloc[i+j]
                    img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/150"

                    with cols[j]:
                        st.markdown(f"""
                        <div class="recipe-card">
                        <img src="{img}" class="recipe-img">
                        <div class="recipe-title">{row["Titre"]}</div>
                        </div>
                        """, unsafe_allow_html=True)

                        if st.button("Voir", key=f"v{i+j}"):
                            st.session_state.recipe_data=row.to_dict()
                            st.session_state.page="details"
                            st.rerun()
    else:
        st.info("Aucune recette.")

# ======================================================
# PAGE DÉTAILS
# ======================================================
elif st.session_state.page=="details":

    r=st.session_state.recipe_data

    if st.button("⬅ Retour"):
        st.session_state.page="home"; st.rerun()

    st.header(r["Titre"])

    st.subheader("⭐ Ma note")
    note=st.slider("Note",0,5,int(float(r.get("Note",0))))
    comm=st.text_area("Commentaires",value=r.get("Commentaires",""))

    if st.button("💾 Sauvegarder"):
        send_action({"action":"edit","titre":r["Titre"],"Note":note,"Commentaires":comm})
        st.success("Enregistré")

    st.subheader("🛒 Ingrédients")
    st.write(r.get("Ingrédients",""))

    st.subheader("📝 Préparation")
    st.write(r.get("Préparation",""))

# ======================================================
# PAGE AJOUTER (PROPRE)
# ======================================================
elif st.session_state.page=="add":

    st.header("➕ Ajouter une recette")
    tab1,tab2,tab3=st.tabs(["🌐 Site","🎬 Vidéo","📝 Manuel"])

    with tab1:
        url=st.text_input("URL recette")
        if st.button("Analyser"):
            if url:
                t,c=scrape_url(url)
                if t:
                    st.session_state.temp_t=t
                    st.session_state.temp_c=c

        if "temp_t" in st.session_state:
            t=st.text_input("Titre",value=st.session_state.temp_t)
            c=st.text_area("Contenu",value=st.session_state.temp_c,height=300)
            if st.button("Enregistrer"):
                send_action({"action":"add","titre":t,"preparation":c,"source":url})
                del st.session_state.temp_t
                del st.session_state.temp_c
                st.session_state.page="home"
                st.rerun()

    with tab2:
        t=st.text_input("Titre vidéo")
        u=st.text_input("Lien vidéo")
        if st.button("Sauvegarder vidéo"):
            if t and u:
                send_action({"action":"add","titre":t,"source":u})
                st.session_state.page="home"
                st.rerun()

    with tab3:
        with st.form("form"):
            t=st.text_input("Titre *")
            cat=st.selectbox("Catégorie",CATEGORIES)
            txt=st.text_area("Contenu",height=300)
            submit=st.form_submit_button("Enregistrer")
            if submit and t:
                send_action({"action":"add","titre":t,"catégorie":cat,"ingredients":txt})
                st.session_state.page="home"
                st.rerun()

# ======================================================
# PAGE PLAYSTORE
# ======================================================
elif st.session_state.page=="playstore":
    st.header("⭐ Mes Recettes Pro")
    st.write("⭐ 4.9 | 1 000+ téléchargements")
    if st.button("Installer"):
        st.success("Application installée 🎉")
    if st.button("Retour"):
        st.session_state.page="home"; st.rerun()

# ======================================================
# PAGE AIDE
# ======================================================
elif st.session_state.page=="help":
    st.header("❓ Aide")
    st.write("Ajoutez des recettes via URL, vidéo ou manuel.")
    if st.button("Retour"):
        st.session_state.page="home"; st.rerun()
