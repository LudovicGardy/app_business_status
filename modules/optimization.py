import streamlit as st
from hyperopt import hp, fmin, tpe, Trials, STATUS_OK
from modules.calculs import calcul_dividendes, calculer_IR, calcul_resultat_net
 
# Objective function
def objective(hyperopt_params):

    # Calculs basés sur le code que tu as fourni
    resultat_net = calcul_resultat_net(
        st.session_state['chiffre_affaire_HT'], hyperopt_params['charges_deductibles'], hyperopt_params['type_societe'], hyperopt_params['salaire_annuel_avecCS_avantIR'], hyperopt=True
    )
    resultat_dividendes = calcul_dividendes(
        resultat_net.societe_resultat_net_apres_IS, hyperopt_params['proportion_dividende'], hyperopt_params['type_societe'], hyperopt_params['choix_fiscal'], st.session_state['capital_social_societe']
    )
    president_imposable_total = resultat_net.salaire_annuel_sansCS_avantIR + resultat_dividendes.supplement_IR
    resultat_IR = calculer_IR(president_imposable_total)
    president_net_apres_IR = resultat_net.salaire_annuel_sansCS_avantIR + resultat_dividendes.dividendes_recus_par_president_annuellement - resultat_IR.impot_sur_le_revenu

    write_results_dict = {
        'chiffre_affaire_HT': st.session_state['chiffre_affaire_HT'],
        'charges_deductibles': hyperopt_params['charges_deductibles'],
        'benefice_apres_charges_deductibles': resultat_net.benefice_apres_charges_deductibles,
        'salaire_annuel_sansCS_avantIR': resultat_net.salaire_annuel_sansCS_avantIR, #et non pas <salaire_annuel_avecCS_avantIR>. Voir [NOTE] dans calcul_resultat pour les explications
        'CS_sur_salaire_annuel': resultat_net.charges_sociales_sur_salaire_president,
        'benefices_apres_salaire_president': resultat_net.benefices_apres_salaire_president,
        'impots_sur_les_societes': resultat_net.impots_sur_les_societes,
        'societe_resultat_net_apres_IS': resultat_net.societe_resultat_net_apres_IS,
        'charges_sur_dividendes': resultat_dividendes.charges_sur_dividendes,
        'dividendes_recus': resultat_dividendes.dividendes_recus_par_president_annuellement,
        'reste_tresorerie': resultat_dividendes.reste_tresorerie,
        'president_imposable_total': president_imposable_total,
        'impot_sur_le_revenu': resultat_IR.impot_sur_le_revenu,
        'president_net_apres_IR': president_net_apres_IR,
        'taxes_total': resultat_net.charges_sociales_sur_salaire_president + resultat_net.impots_sur_les_societes + resultat_dividendes.charges_sur_dividendes + resultat_IR.impot_sur_le_revenu,
        'supplement_IR': resultat_dividendes.supplement_IR,
    }

    # Hyperopt minimise la fonction objectif, donc on utilise l'opposé du revenu pour le maximiser
    return {'loss': -president_net_apres_IR, 'status': STATUS_OK, 'dividendes_recus': resultat_dividendes.dividendes_recus_par_president_annuellement, 'reste_tresorerie': resultat_dividendes.reste_tresorerie, 'write_results_dict': write_results_dict}


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