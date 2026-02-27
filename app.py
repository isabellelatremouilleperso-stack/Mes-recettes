# ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.markdown('<div style="text-align:center;"><img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" style="width:120px; border-radius:50%; border:4px solid #e67e22;"></div>', unsafe_allow_html=True)
    st.title("🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page="home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page="planning"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page="shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER RECETTE", use_container_width=True): st.session_state.page="add"; st.rerun()
    if st.button("⭐ Play Store", use_container_width=True): st.session_state.page="playstore"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): st.session_state.page="help"; st.rerun()

# --- ACCUEIL ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if not df.empty:
        c1, c2 = st.columns([2,1])
        search = c1.text_input("🔍 Rechercher...")
        cat_choisie = c2.selectbox("📁 Filtrer", ["Toutes"] + sorted(list(df['Catégorie'].unique())))
        mask = df['Titre'].str.contains(search, case=False, na=False)
        if cat_choisie != "Toutes": mask = mask & (df['Catégorie'] == cat_choisie)
        rows = df[mask].reset_index(drop=True)
        for i in range(0, len(rows), 2):
            cols = st.columns(2)
            for j in range(2):
                if i+j < len(rows):
                    row = rows.iloc[i+j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                        st.markdown(f'<div class="recipe-card"><div class="recipe-img-container"><img src="{img}"></div><div class="recipe-content"><div class="recipe-title-text">{row["Titre"]}</div></div></div>', unsafe_allow_html=True)
                        if st.button("📖 Ouvrir", key=f"open_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page="details"; st.rerun()

# --- DÉTAILS & IMPRESSION ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    c_back, c_edit, c_print, c_del = st.columns(4)
    if c_back.button("⬅ Retour", use_container_width=True): st.session_state.page="home"; st.rerun()
    with c_print:
        st.markdown('<a href="javascript:window.print()" style="text-decoration:none;"><div style="background:#e67e22; color:white; padding:8px; border-radius:8px; text-align:center; font-weight:bold; border:1px solid #d35400;">🖨️ Imprimer</div></a>', unsafe_allow_html=True)
    if c_del.button("🗑️ Supprimer", use_container_width=True):
        if send_action({"action":"delete","titre":r['Titre']}): st.session_state.page="home"; st.rerun()
    st.header(f"📖 {r.get('Titre','Sans titre')}")
    col_g, col_d = st.columns([1, 1.2])
    with col_g: st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
    with col_d:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r.get('Ingrédients','')).split("\n") if l.strip()]
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        for i, l in enumerate(ings): st.checkbox(l, key=f"c_{i}")
        st.markdown('</div>', unsafe_allow_html=True)
        html_p = '<div class="only-print">'
        for l in ings: html_p += f'<p style="color:black !important; margin:0; font-size:14pt;">• {l}</p>'
        st.markdown(html_p + '</div>', unsafe_allow_html=True)
    st.subheader("👨‍🍳 Étapes")
    st.write(r.get('Préparation','-'))

# --- PLAY STORE ---
elif st.session_state.page == "playstore":
    st.markdown('<h1 style="color:white;">Mes Recettes Pro</h1><p style="color:#01875f; font-weight:bold;">VosSoins Inc.</p>', unsafe_allow_html=True)
    if st.button("Installer", use_container_width=True):
        st.image("https://i.postimg.cc/HnxJDBjf/cartoon-hand-bomb-vector-template-(2).jpg", width=250)
        time.sleep(2); st.success("✓ Installé")
    st.image(["https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg","https://i.postimg.cc/YCkg460C/shared-image-(5).jpg","https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg"], width=200)
    if st.button("⬅ Retour"): st.session_state.page="home"; st.rerun()

# --- AIDE (RESTAURÉE) ---
elif st.session_state.page == "help":
    st.header("❓ Aide & Astuces")
    ca, cb = st.columns(2)
    with ca:
        st.markdown('<div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #e67e22; margin-bottom:10px;"><h3>📝 Ajouter Recette</h3><p>🌐 Site Web, 🎬 Vidéo ou 📝 Vrac pour ajouter vos recettes.</p></div>', unsafe_allow_html=True)
        st.markdown('<div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #e67e22;"><h3>🔍 Rechercher</h3><p>Recherchez par titre ou filtre par catégorie.</p></div>', unsafe_allow_html=True)
    with cb:
        st.markdown('<div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #e67e22; margin-bottom:10px;"><h3>🛒 Liste d’Épicerie</h3><p>Cochez les ingrédients pour les ajouter. Retirez ou videz à tout moment.</p></div>', unsafe_allow_html=True)
        st.markdown('<div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #e67e22;"><h3>📅 Planning</h3><p>Planifiez vos repas et accédez aux fiches.</p></div>', unsafe_allow_html=True)
    if st.button("⬅ Retour à la Bibliothèque", use_container_width=True): st.session_state.page="home"; st.rerun()

# --- AJOUTER ---
elif st.session_state.page == "add":
    st.header("📥 Ajouter")
    if st.button("⬅ Annuler"): st.session_state.page="home"; st.rerun()
    with st.form("add_f"):
        t = st.text_input("Titre")
        cat = st.selectbox("Catégorie", CATEGORIES)
        ing = st.text_area("Ingrédients")
        ins = st.text_area("Instructions")
        if st.form_submit_button("💾 Sauvegarder"):
            if t and ing:
                if send_action({"action":"add","titre":t,"Catégorie":cat,"Ingrédients":ing,"Préparation":ins}):
                    st.session_state.page="home"; st.rerun()

# --- ÉPICERIE & PLANNING (SIMPLIFIÉS) ---
elif st.session_state.page == "shop":
    st.header("🛒 Liste d'épicerie")
    if st.button("⬅ Retour"): st.session_state.page="home"; st.rerun()
    st.info("Consultez votre Google Sheet pour gérer la liste complète.")
elif st.session_state.page == "planning":
    st.header("📅 Planning")
    if st.button("⬅ Retour"): st.session_state.page="home"; st.rerun()
    st.info("Planifiez vos repas dans l'onglet Planning de votre fichier.")
 # ======================
# SIDEBAR
# ======================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" 
             style="width: 120px; height: 120px; border-radius: 50%; border: 4px solid #e67e22; object-fit: cover;">
    </div>
    """, unsafe_allow_html=True)
    st.title("🍳 Mes Recettes")
    if st.button("📚 Bibliothèque", use_container_width=True): st.session_state.page="home"; st.rerun()
    if st.button("📅 Planning", use_container_width=True): st.session_state.page="planning"; st.rerun()
    if st.button("🛒 Épicerie", use_container_width=True): st.session_state.page="shop"; st.rerun()
    st.divider()
    if st.button("➕ AJOUTER RECETTE", use_container_width=True): st.session_state.page="add"; st.rerun()
    if st.button("⭐ Play Store", use_container_width=True): st.session_state.page="playstore"; st.rerun()
    if st.button("❓ Aide", use_container_width=True): st.session_state.page="help"; st.rerun()

# --- ACCUEIL ---
if st.session_state.page == "home":
    st.header("📚 Ma Bibliothèque")
    df = load_data()
    if not df.empty:
        c1, c2 = st.columns([2,1])
        search = c1.text_input("🔍 Rechercher...", placeholder="Ex: Lasagne...")
        cat_choisie = c2.selectbox("📁 Filtrer", ["Toutes"] + sorted(list(df['Catégorie'].unique())))
        mask = df['Titre'].str.contains(search, case=False, na=False)
        if cat_choisie != "Toutes": mask = mask & (df['Catégorie'] == cat_choisie)
        rows = df[mask].reset_index(drop=True)
        for i in range(0, len(rows), 2):
            cols = st.columns(2)
            for j in range(2):
                if i+j < len(rows):
                    row = rows.iloc[i+j]
                    with cols[j]:
                        img = row['Image'] if "http" in str(row['Image']) else "https://via.placeholder.com/400"
                        st.markdown(f'<div class="recipe-card"><div class="recipe-img-container"><img src="{img}"></div><div class="recipe-content"><div class="recipe-title-text">{row["Titre"]}</div></div></div>', unsafe_allow_html=True)
                        if st.button("📖 Ouvrir", key=f"open_{i+j}", use_container_width=True):
                            st.session_state.recipe_data = row.to_dict(); st.session_state.page="details"; st.rerun()

# --- DÉTAILS & IMPRESSION (FOND BLANC CORRIGÉ) ---
elif st.session_state.page == "details":
    r = st.session_state.recipe_data
    c_back, c_edit, c_print, c_del = st.columns(4)
    if c_back.button("⬅ Retour", use_container_width=True): st.session_state.page="home"; st.rerun()
    with c_print:
        st.markdown('<a href="javascript:window.print()" style="text-decoration:none;"><div style="background:#e67e22; color:white; padding:8px; border-radius:8px; text-align:center; font-weight:bold; border:1px solid #d35400;">🖨️ Imprimer</div></a>', unsafe_allow_html=True)
    if c_del.button("🗑️ Supprimer", use_container_width=True):
        if send_action({"action":"delete","titre":r['Titre']}): st.session_state.page="home"; st.rerun()
    st.header(f"📖 {r.get('Titre','Sans titre')}")
    col_g, col_d = st.columns([1, 1.2])
    with col_g: st.image(r['Image'] if "http" in str(r['Image']) else "https://via.placeholder.com/400", use_container_width=True)
    with col_d:
        st.subheader("🛒 Ingrédients")
        ings = [l.strip() for l in str(r.get('Ingrédients','')).split("\n") if l.strip()]
        st.markdown('<div class="no-print">', unsafe_allow_html=True)
        for i, l in enumerate(ings): st.checkbox(l, key=f"c_{i}")
        st.markdown('</div>', unsafe_allow_html=True)
        html_p = '<div class="only-print">'
        for l in ings: html_p += f'<p style="color:black !important; margin:0; font-size:14pt;">• {l}</p>'
        st.markdown(html_p + '</div>', unsafe_allow_html=True)
    st.subheader("👨‍🍳 Étapes")
    st.write(r.get('Préparation','-'))

# --- PAGE PLAY STORE (VERSION COMPLÈTE AVEC LA BOMBE) ---
elif st.session_state.page == "playstore":
    st.markdown("""
        <style>
        .play-title { font-size: 2.2rem; font-weight: 600; color: white; margin-bottom: 0px; }
        .play-dev { color: #01875f; font-weight: 500; font-size: 1.1rem; margin-bottom: 20px; }
        .play-stats { display: flex; justify-content: flex-start; gap: 40px; border-top: 1px solid #3c4043; border-bottom: 1px solid #3c4043; padding: 15px 0; margin-bottom: 25px; }
        .stat-box { text-align: center; }
        .stat-val { font-size: 1.1rem; font-weight: bold; color: white; display: block; }
        .stat-label { font-size: 0.8rem; color: #bdc1c6; }
        </style>
    """, unsafe_allow_html=True)

    c_info, c_logo = st.columns([2, 1])
    with c_info:
        st.markdown('<div class="play-title">Mes Recettes Pro</div>', unsafe_allow_html=True)
        st.markdown('<div class="play-dev">VosSoins Inc.</div>', unsafe_allow_html=True)
        st.markdown('<div class="play-stats"><div class="stat-box"><span class="stat-val">4,9 ⭐</span><span class="stat-label">1,44 k avis</span></div><div class="stat-box"><span class="stat-val">100 k+</span><span class="stat-label">Téléchargements</span></div><div class="stat-box"><span class="stat-val">E</span><span class="stat-label">Tout le monde</span></div></div>', unsafe_allow_html=True)
    with c_logo:
        st.markdown('<div style="text-align:right;"><img src="https://i.postimg.cc/RCX2pdr7/300DPI-Zv2c98W9GYO7.png" style="width:130px; border-radius:20%; border:1px solid #3c4043;"></div>', unsafe_allow_html=True)

    # --- L'ANIMATION DE LA BOMBE ---
    btn_place = st.empty()
    if btn_place.button("Installer", key="install_play", use_container_width=True):
        btn_place.empty()
        st.image("https://i.postimg.cc/HnxJDBjf/cartoon-hand-bomb-vector-template-(2).jpg", width=300)
        time.sleep(2.5)
        st.markdown("<h3 style='color:#01875f;'>✓ Installé avec succès</h3>", unsafe_allow_html=True)

    st.write("✨ Cette appli est proposée pour tous vos appareils")
    st.image(["https://i.postimg.cc/CxYDZG5M/shared-image-(6).jpg","https://i.postimg.cc/YCkg460C/shared-image-(5).jpg","https://i.postimg.cc/NjYTy6F5/shared-image-(7).jpg"], width=230)
    if st.button("⬅ Retour", use_container_width=True): st.session_state.page="home"; st.rerun()

# --- PAGE AIDE (RESTAURÉE) ---
elif st.session_state.page == "help":
    st.header("❓ Aide & Astuces")
    ca, cb = st.columns(2)
    with ca:
        st.markdown('<div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #e67e22; margin-bottom:15px;"><h3>📝 Ajouter Recette</h3><p>🌐 Site Web, 🎬 Vidéo ou 📝 Vrac pour ajouter vos recettes facilement.</p></div>', unsafe_allow_html=True)
        st.markdown('<div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #e67e22;"><h3>🔍 Rechercher</h3><p>Utilisez la barre de recherche par titre ou filtrez par catégorie.</p></div>', unsafe_allow_html=True)
    with cb:
        st.markdown('<div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #e67e22; margin-bottom:15px;"><h3>🛒 Épicerie</h3><p>Cochez les ingrédients pour les envoyer dans votre liste de courses.</p></div>', unsafe_allow_html=True)
        st.markdown('<div style="background:#1e1e1e; padding:15px; border-radius:10px; border-left:5px solid #e67e22;"><h3>📅 Planning</h3><p>Organisez vos repas de la semaine en un clic.</p></div>', unsafe_allow_html=True)
    if st.button("⬅ Retour à la Bibliothèque", use_container_width=True): st.session_state.page="home"; st.rerun()

# --- AJOUTER RECETTE ---
elif st.session_state.page == "add":
    st.header("📥 Ajouter une Recette")
    if st.button("⬅ Annuler"): st.session_state.page="home"; st.rerun()
    with st.form("add_form_final"):
        t = st.text_input("Nom de la recette")
        cat = st.selectbox("Catégorie", CATEGORIES)
        ing = st.text_area("Ingrédients (un par ligne)")
        ins = st.text_area("Instructions / Étapes")
        img_url = st.text_input("Lien de l'image (URL)")
        if st.form_submit_button("💾 ENREGISTRER"):
            if t and ing:
                if send_action({"action":"add","titre":t,"Catégorie":cat,"Ingrédients":ing,"Préparation":ins,"Image":img_url}):
                    st.success("Ajouté !"); time.sleep(1); st.session_state.page="home"; st.rerun()   
