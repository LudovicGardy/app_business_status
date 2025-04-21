def calcul_IR(tranches_ir, base_imposable):
    """
    Calcule l'IR (Impôt sur le Revenu) en fonction des tranches.
    Args:
        tranches_ir (list): Liste de tranches d'imposition.
        base_imposable (float): La base imposable en euros.

    Returns:
        float: Le montant total de l'IR.
    """
    ir_total = 0
    for tranche in tranches_ir:
        min_val, max_val, taux = tranche
        if base_imposable > min_val:
            taxable_income = min(base_imposable, max_val) - min_val
            ir_total += taxable_income * taux / 100

    return ir_total