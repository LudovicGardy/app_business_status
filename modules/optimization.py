import streamlit as st
from hyperopt import hp, fmin, tpe, Trials, STATUS_OK
from modules.calcul_dividendes import calcul_dividendes
from modules.calcul_IR import calculer_IR
from modules.calcul_resultat import calcul_resultat_net
 
# Fonction objectif
def objective(hyperopt_params):

    # Calculs basés sur le code que tu as fourni
    benefice_apres_charges_deductibles, societe_resultat_net_apres_IS, salaire_annuel_sansCS_avantIR, CS_sur_salaire_annuel, benefices_apres_salaire_president, impots_sur_les_societes = calcul_resultat_net(
        st.session_state['chiffre_affaire_HT'], hyperopt_params['charges_deductibles'], hyperopt_params['type_societe'], hyperopt_params['salaire_annuel_avecCS_avantIR'], hyperopt=True
    )
    charges_sur_dividendes, dividendes_recus, reste_tresorerie, supplement_IR = calcul_dividendes(
        societe_resultat_net_apres_IS, hyperopt_params['proportion_dividende'], hyperopt_params['type_societe'], hyperopt_params['choix_fiscal'], st.session_state['capital_social_societe']
    )
    president_imposable_total = salaire_annuel_sansCS_avantIR + supplement_IR
    impot_sur_le_revenu = calculer_IR(president_imposable_total)
    president_net_apres_IR = salaire_annuel_sansCS_avantIR + dividendes_recus - impot_sur_le_revenu

    write_results_dict = {
        'chiffre_affaire_HT': st.session_state['chiffre_affaire_HT'],
        'charges_deductibles': hyperopt_params['charges_deductibles'],
        'benefice_apres_charges_deductibles': benefice_apres_charges_deductibles,
        'salaire_annuel_sansCS_avantIR': salaire_annuel_sansCS_avantIR, #et non pas <salaire_annuel_avecCS_avantIR>. Voir [NOTE] dans calcul_resultat pour les explications
        'CS_sur_salaire_annuel': CS_sur_salaire_annuel,
        'benefices_apres_salaire_president': benefices_apres_salaire_president,
        'impots_sur_les_societes': impots_sur_les_societes,
        'societe_resultat_net_apres_IS': societe_resultat_net_apres_IS,
        'charges_sur_dividendes': charges_sur_dividendes,
        'dividendes_recus': dividendes_recus,
        'reste_tresorerie': reste_tresorerie,
        'president_imposable_total': president_imposable_total,
        'impot_sur_le_revenu': impot_sur_le_revenu,
        'president_net_apres_IR': president_net_apres_IR,
        'taxes_total': CS_sur_salaire_annuel + impots_sur_les_societes + charges_sur_dividendes + impot_sur_le_revenu,
        'supplement_IR': supplement_IR,
    }

    # Hyperopt minimise la fonction objectif, donc on utilise l'opposé du revenu pour le maximiser
    return {'loss': -president_net_apres_IR, 'status': STATUS_OK, 'dividendes_recus': dividendes_recus, 'reste_tresorerie': reste_tresorerie, 'write_results_dict': write_results_dict}


# Configuration de l'optimisation
def run_optimization(space, objective):
    trials = Trials()
    best = fmin(
        objective,
        space=space,
        algo=tpe.suggest,
        max_evals=1000,
        trials=trials,
        
    )
    return best, trials