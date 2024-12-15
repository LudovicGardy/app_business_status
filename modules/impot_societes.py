def calcul_IS(benefice):
    """
    Calcule l'IS (Impôt sur les Sociétés) en fonction des tranches.
    Tranches IS :
        - 15% jusqu'à 42 500 €
        - 25% au-delà de 42 500 €

    Args:
        benefice (float): Le bénéfice imposable en euros.

    Returns:
        float: Le montant total de l'IS.
    """
    tranche1_limite = 42500  # Limite de la première tranche
    taux_tranche1 = 0.15  # Taux de la première tranche (15%)
    taux_tranche2 = 0.25  # Tau de la deuxième tranche (25%)

    if benefice <= tranche1_limite:
        is_total = benefice * taux_tranche1
    else:
        is_tranche1 = tranche1_limite * taux_tranche1
        is_tranche2 = (benefice - tranche1_limite) * taux_tranche2
        is_total = is_tranche1 + is_tranche2

    return round(is_total, 2)