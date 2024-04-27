def calculer_IR(revenu_annuel):
    # Définition des tranches et des taux
    tranches = [(0, 11295, 0), (11296, 29787, 0.11), (29788, 82342, 0.30), (82343, 177106, 0.41), (177107, float('inf'), 0.45)]
    impot_total = 0

    # Calcul de l'impôt pour chaque tranche
    for min_tranche, max_tranche, taux in tranches:
        if revenu_annuel > min_tranche:
            # Calcul de la part du revenu dans la tranche actuelle
            revenu_dans_tranche = min(revenu_annuel, max_tranche) - min_tranche
            # Application du taux d'imposition à cette part
            impot_tranche = revenu_dans_tranche * taux
            impot_total += impot_tranche
            # Si le revenu est supérieur à la tranche maximale, arrêter le calcul
            if revenu_annuel <= max_tranche:
                break

    print()
    print(f"Pour un revenu annuel imposable de {revenu_annuel:.2f}€, l'impôt dû est de {impot_total:.2f} €.")
    return impot_total
