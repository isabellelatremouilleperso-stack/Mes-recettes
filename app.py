def scrape_url(url):
    import re
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=12)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'html.parser')

        # 1. Extraction du Titre
        title = "Recette Importée"
        h1_tag = soup.find('h1')
        if h1_tag:
            title = h1_tag.get_text().strip()

        # 2. Nettoyage du bruit (on enlève ce qui n'est pas de la nourriture)
        for junk in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "ins", "button"]):
            junk.extract()

        # 3. Ciblage des conteneurs
        # On cherche les zones qui contiennent "ingredient" ou "recipe-ing"
        ing_container = soup.find(class_=re.compile(r'ingredient|recipe-ing', re.I))
        # On cherche les zones qui contiennent "instruction" ou "step"
        prep_container = soup.find(class_=re.compile(r'instruction|preparation|method|steps|direction', re.I))

        # --- LOGIQUE INGRÉDIENTS ---
        ing_list = []
        # Si on a trouvé un conteneur spécifique, on ne cherche que dedans
        source_ingredients = ing_container if ing_container else soup
        
        # On cherche les <li> (puces) qui sont le standard des ingrédients
        for el in source_ingredients.find_all('li'):
            # separator=" " est vital pour ne pas coller "10" et "grammes" -> "10grammes"
            txt = el.get_text(separator=" ").strip()
            # Nettoyage des espaces doubles
            txt = re.sub(r'\s+', ' ', txt)
            
            # FILTRE : On garde si c'est une ligne de taille raisonnable et pas un lien menu
            if 3 < len(txt) < 150:
                if not any(x in txt.lower() for x in ["connexion", "mon compte", "partager", "imprimer", "newsletter"]):
                    ing_list.append(f"❑ {txt}")

        # --- LOGIQUE PRÉPARATION ---
        prep_list = []
        source_prep = prep_container if prep_container else soup
        
        # On cherche les paragraphes ou les puces d'instructions
        for el in source_prep.find_all(['p', 'li']):
            txt = el.get_text(separator=" ").strip()
            txt = re.sub(r'\s+', ' ', txt)
            
            # On garde les blocs de texte assez longs pour être des étapes
            if len(txt) > 20:
                if not any(x in txt.lower() for x in ["cookies", "droits réservés", "abonnez-vous", "cliquez ici"]):
                    prep_list.append(txt)

        # 4. Finalisation (Suppression des doublons en gardant l'ordre)
        final_ing = "\n".join(list(dict.fromkeys(ing_list)))
        final_prep = "\n\n".join(list(dict.fromkeys(prep_list)))

        return title, final_ing, final_prep

    except Exception as e:
        return "Recette inconnue", "", f"Erreur lors de l'extraction : {e}"
