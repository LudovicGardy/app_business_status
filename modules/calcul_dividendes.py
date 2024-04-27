def calcul_dividendes(societe_resultat_net_apres_IS, proportion_du_resultat_versee_en_dividende, type_societe, choix_fiscal, capital_social_societe):
    print("\n### calcul_dividendes \n-------------------------")

    montant_verse_en_dividendes_au_president_annuellement = societe_resultat_net_apres_IS * proportion_du_resultat_versee_en_dividende

    if type_societe == "EURL" and montant_verse_en_dividendes_au_president_annuellement > capital_social_societe * 0.1: 
        montant_verse_en_dividendes_au_president_annuellement = capital_social_societe-1

    if choix_fiscal == "flat_tax":
        taux_dividendes = 0.30
        charges_sur_dividendes = round(montant_verse_en_dividendes_au_president_annuellement * taux_dividendes)
        print(f"- charges_sur_dividendes: {charges_sur_dividendes}")
        dividendes_recus_par_president_annuellement = round(montant_verse_en_dividendes_au_president_annuellement - charges_sur_dividendes)
        print(f"- dividendes_recus_par_president_annuellement: {dividendes_recus_par_president_annuellement}")
        reste_tresorerie = round(societe_resultat_net_apres_IS - montant_verse_en_dividendes_au_president_annuellement)
        print(f"= reste_tresorerie: {reste_tresorerie} €")
        supplement_IR = 0
    elif choix_fiscal == "bareme":
        taux_dividendes = 0.17
        charges_sur_dividendes = round(montant_verse_en_dividendes_au_president_annuellement * taux_dividendes)
        dividendes_recus_par_president_annuellement = montant_verse_en_dividendes_au_president_annuellement - charges_sur_dividendes
        reste_tresorerie = round(societe_resultat_net_apres_IS - montant_verse_en_dividendes_au_president_annuellement)
        print(f"= reste_tresorerie: {reste_tresorerie} €")
        dividendes_abbatement_IR = 0.4
        supplement_IR = round(dividendes_recus_par_president_annuellement * (1 - dividendes_abbatement_IR),2)

    return charges_sur_dividendes, dividendes_recus_par_president_annuellement, reste_tresorerie, supplement_IR
