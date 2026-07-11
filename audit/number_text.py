from num2words import num2words


def montant_en_lettres(montant):
    """Convierte un montant (float/int) a texto en francés con 'dirhams'."""
    if montant is None:
        return "Zéro dirham"
    try:
        montant = float(montant)
    except (ValueError, TypeError):
        return str(montant)

    partie_entiere = int(montant)
    partie_decimale = round((montant - partie_entiere) * 100)

    if partie_entiere == 0 and partie_decimale == 0:
        return "Zéro dirham"

    texte = ""
    if partie_entiere > 0:
        mots = num2words(partie_entiere, lang='fr')
        texte = f"{mots} dirhams" if partie_entiere > 1 else f"{mots} dirham"

    if partie_decimale > 0:
        mots_dec = num2words(partie_decimale, lang='fr')
        if texte:
            texte += " et "
        texte += f"{mots_dec} centimes" if partie_decimale > 1 else f"{mots_dec} centime"

    # Capitalize first letter
    if texte:
        texte = texte[0].upper() + texte[1:]

    return texte
