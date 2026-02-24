import streamlit as st
import requests
import pandas as pd

# ==============================
# CONFIGURATION
# ==============================
st.set_page_config(page_title="Livre de Recettes", page_icon="👩‍🍳", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .recipe-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #f0f0f0;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    .fiche-titre {
        font-size: 42px;
        font-weight: 800;
        color: #1f2937;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================
# LIENS
# ==============================
URL_CSV = "TON_LIEN_CSV_ICI"
URL_SCRIPT = "TON_LIEN_SCRIPT_ICI"

# ==============================
# MÉMOIRE
# ==============================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "recipe_data" not in st.session_state:
    st.session_state.recipe_data = None

if "liste_epicerie" not in st.session_state:
    st.session_state.liste_epicerie = []

# ==============================
# MENU
# ==============================
with st.sidebar:
    st.title("👩‍🍳 Menu")

    if st.session_state.page == "ajouter":
        default_index = 1
    elif st.session_state.page == "liste":
        default_index = 2
    else:
        default_index = 0

    choix = st.radio(
        "Navigation",
        ["📚 Bibliothèque", "➕ Ajouter", "🛒 Épicerie"],
        index=default_index
    )

    if choix == "📚 Bibliothèque":
        if st.session_state.page != "details":
            st.session_state.page = "home"

    elif choix == "➕ Ajouter":
        st.session_state.page = "ajouter"

    elif choix == "🛒 Épicerie":
        st.session_state.page = "liste"

# ==============================
# PAGE AJOUTER
# ==============================
if st.session_state.page == "ajouter":

    st.title("➕ Nouvelle Recette")

    with st.form("form_add", clear_on_submit=True):
        titre = st.text_input("Nom du plat")
        image = st.text_input("Lien image")
        ingredients = st.text_area("Ingrédients (un par ligne)")
        preparation = st.text_area("Préparation")

        if st.form_submit_button("🚀 Enregistrer"):
            if titre:
                response = requests.post(
                    URL_SCRIPT,
                    json={
                        "titre": titre,
                        "image": image,
                        "ingredients": ingredients,
                        "preparation": preparation
                    }
                )

                if response.status_code == 200:
                    st.success("Recette enregistrée ! 🎉")
                    st.balloons()
                else:
                    st.error("Erreur lors de l'enregistrement.")
            else:
                st.warning("Le nom du plat est obligatoire.")

# ==============================
# PAGE DÉTAILS
# ==============================
elif st.session_state.page == "details":

    if st.session_state.recipe_data is not None:

        row = st.session_state.recipe_data

        if st.button("⬅️ Retour"):
            st.session_state.page = "home"
            st.rerun()

        st.markdown(f"<div class='fiche-titre'>{row['titre']}</div>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 🛒 Ingrédients")

            ingredients_text = str(row["ingredients"])

            for ligne in ingredients_text.split("\n"):
                if ligne.strip():
                    st.write(f"✅ {ligne.strip()}")

            if st.button("➕ Ajouter à l'épicerie"):
                st.session_state.liste_epicerie.append({
                    "titre": row["titre"],
                    "ingredients": ingredients_text
                })
                st.toast("Ajouté à la liste !")

        with col2:
            if str(row["image"]).startswith("http"):
                st.image(row["image"], use_container_width=True)

        st.markdown("### 👨‍🍳 Préparation")
        st.info(row["preparation"])

    else:
        st.session_state.page = "home"
        st.rerun()

# ==============================
# PAGE ÉPICERIE
# ==============================
elif st.session_state.page == "liste":

    st.title("🛒 Ma Liste d'épicerie")

    if not st.session_state.liste_epicerie:
        st.info("Votre liste est vide.")
    else:
        for item in st.session_state.liste_epicerie:
            with st.expander(f"📍 {item['titre']}"):
                st.write(item["ingredients"])

        if st.button("🗑️ Vider la liste"):
            st.session_state.liste_epicerie = []
            st.rerun()

# ==============================
# PAGE ACCUEIL
# ==============================
else:

    st.title("📚 Bibliothèque")

    try:
        df = pd.read_csv(URL_CSV)

        # Vérification sécurité
        required_columns = {"titre", "ingredients", "preparation", "image"}
        if not required_columns.issubset(set(df.columns)):
            st.error("Les colonnes du Google Sheets ne correspondent pas.")
            st.write("Colonnes détectées :", df.columns)
        else:

            cols = st.columns(3)

            for index, row in df.iterrows():

                with cols[index % 3]:

                    st.markdown('<div class="recipe-card">', unsafe_allow_html=True)

                    image_url = row["image"] if str(row["image"]).startswith("http") else "https://via.placeholder.com/200"

                    st.image(image_url, use_container_width=True)
                    st.write(f"**{row['titre']}**")

                    if st.button("Voir la fiche", key=f"btn_{index}"):
                        st.session_state.recipe_data = row
                        st.session_state.page = "details"
                        st.rerun()

                    st.markdown('</div>', unsafe_allow_html=True)

    except Exception:
        st.error("⚠️ Problème de connexion au Google Sheets.")
        st.info("Vérifiez que le fichier est publié sur le Web en format CSV.")
