def calcul_impots_IR(tranches_ir, base_imposable):
    impots_ir = 0
    for tranche in tranches_ir:
        min_val, max_val, taux = tranche
        if base_imposable > min_val:
            taxable_income = min(base_imposable, max_val) - min_val
            impots_ir += taxable_income * taux / 100

    return impots_ir