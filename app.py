import streamlit as st
import requests

# Config de la page
st.set_page_config(page_title="Mon Grimoire", page_icon="👩‍🍳", layout="centered")

# --- CONFIGURATION ---
# Assure-toi que c'est bien ton DERNIER lien /exec
URL_GOOGLE = "https://script.google.com/macros/s/AKfycbzE-RJTsmY5q9kKfS6TRAshgCbCGrk9H1e7YOmwfCsnBlR2lzrl35oEbHc0zITw--_z/exec"

st.title("🧙‍♀️ Mon Grimoire Numérique")

# Menu
menu = st.sidebar.selectbox("Navigation", ["Ajouter une recette", "Aide"])

if menu == "Ajouter une recette":
    st.subheader("📝 Nouvelle Recette")
    
    with st.form("form_recette", clear_on_submit=True):
        titre = st.text_input("Nom du plat *")
        source = st.text_input("Lien ou Source")
        date_plan = st.date_input("Planifier pour le (Calendrier)", value=None)
        
        ingredients = st.text_area("Ingrédients")
        preparation = st.text_area("Étapes de préparation")
        
        submit = st.form_submit_button("✨ Sauvegarder et Planifier")
        
        if submit:
            if titre:
                payload = {
                    "titre": titre,
                    "source": source,
                    "ingredients": ingredients,
                    "preparation": preparation,
                    "date_prevue": str(date_plan) if date_plan else ""
                }
                try:
                    res = requests.post(URL_GOOGLE, json=payload)
                    if res.status_code == 200:
                        st.success(f"C'est fait ! '{titre}' est dans le grimoire et le calendrier.")
                        st.balloons()
                    else:
                        st.error("Erreur lors de l'envoi.")
                except:
                    st.error("Impossible de joindre le script Google.")
            else:
                st.warning("Le nom du plat est obligatoire.")

else:
    st.info("Utilisez le formulaire pour remplir votre Google Sheets automatiquement.")



