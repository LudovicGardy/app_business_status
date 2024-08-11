from typing import Any, Callable, Dict, Tuple

import streamlit as st
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe

from modules.calculs import Scenario


# Objective function
def objective(hyperopt_params: Dict[str, Any]) -> Dict[str, Any]:
    hyperopt_params["running_hyperopt"] = True
    scenario = Scenario(hyperopt_params)

    write_results_dict = {
        "chiffre_affaire_HT": st.session_state["chiffre_affaire_HT"],
        "charges_deductibles": hyperopt_params["charges_deductibles"],
        "benefice_apres_charges_deductibles": scenario.resultat_net.benefice_apres_charges_deductibles,
        "salaire_annuel_sansCS_avantIR": scenario.resultat_net.salaire_annuel_sansCS_avantIR,  # et non pas <salaire_annuel_avecCS_avantIR>. Voir [NOTE] dans calcul_resultat pour les explications
        "CS_sur_salaire_annuel": scenario.resultat_net.charges_sociales_sur_salaire_president,
        "benefices_apres_salaire_president": scenario.resultat_net.benefices_apres_salaire_president,
        "impots_sur_les_societes": scenario.resultat_net.impots_sur_les_societes,
        "societe_resultat_net_apres_IS": scenario.resultat_net.societe_resultat_net_apres_IS,
        "charges_sur_dividendes": scenario.resultat_dividendes.charges_sur_dividendes,
        "dividendes_recus": scenario.resultat_dividendes.dividendes_recus_par_president_annuellement,
        "reste_tresorerie": scenario.resultat_dividendes.reste_tresorerie,
        "president_imposable_total": scenario.president_imposable_total,
        "impot_sur_le_revenu": scenario.resultat_IR.impot_sur_le_revenu,
        "president_net_apres_IR": scenario.president_net_apres_IR,
        "taxes_total": scenario.resultat_net.charges_sociales_sur_salaire_president
        + scenario.resultat_net.impots_sur_les_societes
        + scenario.resultat_dividendes.charges_sur_dividendes
        + scenario.resultat_IR.impot_sur_le_revenu,
        "supplement_IR": scenario.resultat_dividendes.supplement_IR,
    }

    # Hyperopt minimise la fonction objectif, donc on utilise l'opposé du revenu pour le maximiser
    return {
        "loss": -scenario.president_net_apres_IR,
        "status": STATUS_OK,
        "dividendes_recus": scenario.resultat_dividendes.dividendes_recus_par_president_annuellement,
        "reste_tresorerie": scenario.resultat_dividendes.reste_tresorerie,
        "write_results_dict": write_results_dict,
    }


# Configuration de l'optimisation
def run_optimization(
    space: Dict[str, Any], objective: Callable
) -> Tuple[Dict[str, Any], Trials]:
    trials = Trials()
    best = fmin(
        objective,
        space=space,
        algo=tpe.suggest,
        max_evals=1000,
        trials=trials,
    )
    return best, trials
