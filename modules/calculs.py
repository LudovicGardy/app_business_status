class calculer_IR:
    def __init__(self, revenu_annuel):
        # Définition des tranches et des taux
        tranches = [(0, 11295, 0), (11296, 29787, 0.11), (29788, 82342, 0.30), (82343, 177106, 0.41), (177107, float('inf'), 0.45)]
        impot_sur_le_revenu = 0

        # Calcul de l'impôt pour chaque tranche
        for min_tranche, max_tranche, taux in tranches:
            if revenu_annuel > min_tranche:
                # Calcul de la part du revenu dans la tranche actuelle
                revenu_dans_tranche = min(revenu_annuel, max_tranche) - min_tranche
                # Application du taux d'imposition à cette part
                impot_tranche = revenu_dans_tranche * taux
                impot_sur_le_revenu += impot_tranche
                # Si le revenu est supérieur à la tranche maximale, arrêter le calcul
                if revenu_annuel <= max_tranche:
                    break

        print()
        print(f"Pour un revenu annuel imposable de {revenu_annuel:.2f}€, l'impôt dû est de {impot_sur_le_revenu:.2f} €.")

        self.impot_sur_le_revenu = impot_sur_le_revenu
class calcul_dividendes:
    def __init__(self, societe_resultat_net_apres_IS, proportion_du_resultat_versee_en_dividende, type_societe, choix_fiscal, capital_social_societe):
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

        self.charges_sur_dividendes = charges_sur_dividendes
        self.dividendes_recus_par_president_annuellement = dividendes_recus_par_president_annuellement
        self.reste_tresorerie = reste_tresorerie
        self.supplement_IR = supplement_IR
class calcul_resultat_net:
    
    def __init__(self, chiffre_affaire_HT, charges_deductibles, type_societe, salaire_annuel_sansCS_avantIR, hyperopt=False):
        '''
        CS = charges sociales. 
        salaire_annuel_sansCS_avantIR: par exemple 30000€ de celui-ci coûteront 54000€ (salaire + charges sociales) à l'entreprise en SASU.
        '''

        ### [NOTE] On doit réaliser cette opération car le salaire optimisé peut varier de 0
        ### Jusqu'à [C.A.h.t. - charges_déductibles]. Or en réalité le salaire à optimiser
        ### devrait être un pourcentage de [C.A.h.t. - charges_déductibles - charges_sociales_sur_salaire_president],
        ### et comme les charges sociales sur le salaire du président varient en fonction du type de société,
        ### et que le type de société est une variable d'entrée de la fonction objective, on doit recalculer le salaire
        ### du président en fonction du type de société, attribué par hyperopt.
        ### Par exemple : un somme alouée de 54000€ pour un SASU donnera un salaire net de 30000€, soit une charge
        ### de 24000€ (54000*0.444).
        ### --> On veut faire les prévisions sur le 30000€ (salaire reçu), pas sur le 54000€ (coût du salaire, que l'on
        ### calcule justement dans cette fonction avec <charges_sociales_sur_salaire_president>).
        ### Pour ce même exemple, on aura (30000€ * 0.8) = 24000€.
        if hyperopt:
            if type_societe == "EURL":
                salaire_annuel_sansCS_avantIR *= 0.310 
            if type_societe == "SASU": 
                salaire_annuel_sansCS_avantIR *= 0.444

        print()
        print("### calcul_resultat_net \n-------------------------")
        ###-----------------------------------------------------------------
        ### Calcul de la marge globale
        print(f"+ marge_globale: {chiffre_affaire_HT}")
        print(f"- charges_deductibles: {charges_deductibles}")
        benefice_apres_charges_deductibles = chiffre_affaire_HT - charges_deductibles
        print(f"= benefice_apres_charges_deductibles: {benefice_apres_charges_deductibles} €")
        print()

        ###-----------------------------------------------------------------
        ### Calcul des charges sociales sur le salaire du président
        taux_charges_sociales_EURL = 0.45 #0.689655
        taux_charges_sociales_SASU = 0.80 #0.555555

        print(f"- salaire_recu_par_le_president: {salaire_annuel_sansCS_avantIR}")

        if type_societe == "EURL":
            charges_sociales_sur_salaire_president = round(taux_charges_sociales_EURL * salaire_annuel_sansCS_avantIR)
        if type_societe == "SASU":
            charges_sociales_sur_salaire_president = round(taux_charges_sociales_SASU * salaire_annuel_sansCS_avantIR)
        print(f"- charges_sur_salaire_president: {charges_sociales_sur_salaire_president}")

        benefices_apres_salaire_president = benefice_apres_charges_deductibles - salaire_annuel_sansCS_avantIR - charges_sociales_sur_salaire_president
        print(f"= benefices_apres_salaire_president: {benefices_apres_salaire_president} €")
        print()

        ###-----------------------------------------------------------------
        ### Calcul de l'impot sur les sociétés
        seuil = 38120
        if benefices_apres_salaire_president <= seuil:
            impots_sur_les_societes = round(benefices_apres_salaire_president * 0.15)
        else:
            impots_sur_les_societes = round(seuil * 0.15 + (benefices_apres_salaire_president - seuil) * 0.25)
        print(f"- impots_sur_les_societes: {impots_sur_les_societes}")

        ###-----------------------------------------------------------------
        # Calcul du resultat net apres impot
        societe_resultat_net_apres_IS = round(benefices_apres_salaire_president - impots_sur_les_societes)
        print(f"= societe_resultat_net_apres_IS: {societe_resultat_net_apres_IS} €") # disponible pour dividendes

        salaire_annuel_sansCS_avantIR#salaire_annuel_recu_par_le_president

        self.benefice_apres_charges_deductibles = benefice_apres_charges_deductibles
        self.societe_resultat_net_apres_IS = societe_resultat_net_apres_IS
        self.salaire_annuel_sansCS_avantIR = salaire_annuel_sansCS_avantIR
        self.charges_sociales_sur_salaire_president = charges_sociales_sur_salaire_president
        self.benefices_apres_salaire_president = benefices_apres_salaire_president
        self.impots_sur_les_societes = impots_sur_les_societes