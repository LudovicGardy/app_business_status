### Comparaison salaire président SASU vs EURL

from types import SimpleNamespace
from typing import Callable

import plotly.express as px
import streamlit as st
import yaml
from hyperopt import hp

from ..calculs import Scenario
from ..optimization import objective, run_optimization


class DisplayResults:
    def __init__(self, **kwargs):
        self.params = SimpleNamespace(**kwargs)
        with open("config/taxes.yaml", "r") as file:
            self.config_yaml = yaml.safe_load(file)

    def text(self):
        st.write("### Resultats nets")
        st.divider()
        st.write(f"\+ chiffre affaire HT: :green[{self.params.chiffre_affaire_HT} €]")
        st.write(f"\- charges deductibles: :red[{self.params.charges_deductibles} €]")
        st.write(
            f"\= benefices apres charges deductibles: :blue[{self.params.benefice_apres_charges_deductibles} €]"
        )
        st.divider()
        st.write(
            f"\- salaire recu par le president: :red[{self.params.salaire_annuel_sansCS_avantIR} €]"
        )
        st.write(
            f"\- charges sur salaire president: :red[{self.params.CS_sur_salaire_annuel} €]"
        )
        st.write(
            f"\= benefices apres salaire president: :blue[{self.params.benefices_apres_salaire_president} €]"
        )
        st.divider()
        st.write(
            f"\- impots sur les societes: :red[{self.params.impots_sur_les_societes} €]"
        )
        st.write(
            f"\= societe resultat net apres IS: :blue[{self.params.societe_resultat_net_apres_IS} €]"
        )
        st.divider()
        st.write("### Dividendes")
        st.write(
            f"\- dividendes recus par president annuellement: :red[{self.params.dividendes_recus} €]"
        )
        st.write(
            f"\- charges sur dividendes: :red[{self.params.charges_sur_dividendes} €]"
        )
        st.write(f"\= reste tresorerie: :blue[{self.params.reste_tresorerie} €]")
        st.divider()
        st.write("### Resultats pour le president")
        st.write(
            f"- Revenu imposable annuel: {self.params.president_imposable_total} € \n  - Salaire: {self.params.salaire_annuel_sansCS_avantIR} € (imposable: {self.params.salaire_annuel_sansCS_avantIR} €) \n  - Dividendes: {self.params.dividendes_recus} € (imposable: {self.params.supplement_IR} €)"
        )
        st.write(
            f"Pour un revenu imposable annuel de {self.params.president_imposable_total:.2f} €, l'impot dû est de {self.params.impot_sur_le_revenu:.2f} €"
        )
        st.write(
            f"Après impot sur le revenu, le président gagne {self.params.president_net_apres_IR:.2f} €"
        )
        st.divider()
        st.write(
            f"ℹ️ Total des charges sur le chiffre d'affaires H.T. sans la TVA: {self.params.taxes_total} €"
        )
        st.write(
            f"ℹ️ TVA facturée approximativement (non comptée dans les calculs): {self.params.chiffre_affaire_HT * self.config_yaml['TVA']['taux_normal']/100} €"
        )
        st.write(
            f"ℹ️ Total facturé approximatif (TTC): {self.params.chiffre_affaire_HT + self.params.chiffre_affaire_HT * (self.config_yaml['TVA']['taux_normal']/100)} €"
        )
        st.divider()

    def plot(self):
        labels = [
            "Salaire Net",
            "Dividendes",
            "Reste en trésorerie",
            "Taxes",
            "Charges déductibles",
        ]
        values = [
            self.params.salaire_annuel_sansCS_avantIR,
            self.params.dividendes_recus,
            self.params.reste_tresorerie,
            self.params.taxes_total,
            self.params.charges_deductibles,
        ]

        color_map = {
            "Salaire Net": "lightgreen",
            "Dividendes": "limegreen",
            "Reste en trésorerie": "green",
            "Taxes": "salmon",
            "Charges déductibles": "red",
        }

        fig = px.pie(
            values=values,
            names=labels,
            title=f"Répartition financière après simulation pour un C.A. H.T. de {self.params.chiffre_affaire_HT} €",
            color=labels,
            color_discrete_map=color_map,
        )

        st.plotly_chart(fig, use_container_width=True)


class OptimizeIncome:
    def __init__(self, space: dict[str, hp.choice], objective: Callable):
        with st.spinner("Optimisation en cours..."):
            best_params, trials = run_optimization(space, objective)
            print("best_params:", best_params)

            best_params["salaire_annuel_sansCS_avantIR"] = trials.best_trial["result"][
                "write_results_dict"
            ]["salaire_annuel_sansCS_avantIR"]

            # Write best trial in session state for display in the sidebar
            st.session_state["best_trial"]["salaire_annuel_sansCS_avantIR"] = (
                best_params["salaire_annuel_sansCS_avantIR"]
            )
            st.session_state["best_trial"]["dividendes_recus"] = trials.best_trial[
                "result"
            ]["write_results_dict"]["dividendes_recus"]
            st.session_state["best_trial"]["reste_tresorerie"] = trials.best_trial[
                "result"
            ]["write_results_dict"]["reste_tresorerie"]
            st.session_state["best_trial"]["loss"] = -trials.best_trial["result"][
                "loss"
            ]
            st.session_state["best_trial"]["type_societe"] = best_params["type_societe"]
            st.session_state["best_trial"]["choix_fiscal"] = best_params["choix_fiscal"]
            st.session_state["best_trial"]["proportion_dividende"] = best_params[
                "proportion_dividende"
            ]
            st.session_state["best_trial"]["charges_deductibles"] = best_params[
                "charges_deductibles"
            ]

            st.rerun()


class Home:
    def __init__(self):
        self.status_possibles = ["SASU", "EURL"]
        self.fiscalites_possibles = ["flat_tax", "bareme"]

        tabs = st.tabs(["⚙️ Configurations", "📊 Résultats & détails"])

        with tabs[0]:
            self.run()
        with tabs[1]:
            self.results.plot()
            with st.expander("Voir les détails"):
                self.results.text()

    def run(self):
        st.write("### Résultats annuels de la société")
        col1, col2 = st.columns(2)

        with col1:
            self.chiffre_affaire_HT = st.number_input(
                "Chiffre d'affaires HT (€)",
                min_value=0,
                value=200000,
                step=1000,
            )
            st.session_state["chiffre_affaire_HT"] = self.chiffre_affaire_HT
        with col2:
            self.charges_deductibles = st.number_input(
                "Charges déductibles (€)",
                min_value=0,
                value=st.session_state["charges_deductibles"],
                step=1000,
            )
            st.session_state["charges_deductibles"] = self.charges_deductibles

        salaire_avec_CS_maximum = (
            st.session_state["chiffre_affaire_HT"]
            - st.session_state["charges_deductibles"]
        )
        salaire_avec_CS_minimum = 0

        with st.expander(
            "🎛️ Accéder aux autres réglages (pas nécessaire en cas d'optimisation)"
        ):
            # Paramètres legaux et fiscaux
            st.write("### Paramètres légaux et fiscaux")
            col1, col2, col3 = st.columns(3)

            with col1:
                self.type_societe = st.selectbox(
                    "Type de société",
                    self.status_possibles,
                    index=st.session_state["type_societe"],
                )
            with col2:
                self.choix_fiscal = st.selectbox(
                    "Régime fiscal des dividendes",
                    self.fiscalites_possibles,
                    index=st.session_state["choix_fiscal"],
                )
            with col3:
                self.capital_social_societe = st.number_input(
                    "Capital social de la société (€)",
                    min_value=0,
                    value=1000,
                    step=1000,
                )
                st.session_state["capital_social_societe"] = self.capital_social_societe

            st.write("### Salaire du président et Dividendes")

            col1, col2 = st.columns(2)

            with col1:
                self.salaire_annuel_sansCS_avantIR = st.number_input(
                    "Salaire annuel du président (€)",
                    min_value=0,
                    value=st.session_state["salaire_annuel_sansCS_avantIR"],
                    step=1000,
                )

            with col2:
                self.proportion_du_resultat_versee_en_dividende = (
                    st.slider(
                        "Proportion du résultat après IS versée en dividendes (%)",
                        min_value=0,
                        max_value=100,
                        value=st.session_state[
                            "proportion_du_resultat_versee_en_dividende"
                        ],
                    )
                    / 100.0
                )

        self.display_results()

        with st.container(border=True):
            col1, col2 = st.columns(2)
            with col1:
                if self.results.params.societe_resultat_net_apres_IS < 0:
                    st.write(
                        f"Disponible pour dividendes: :red[{self.results.params.societe_resultat_net_apres_IS} €]"
                    )
                else:
                    st.write(
                        f"Disponible pour dividendes: :green[{self.results.params.societe_resultat_net_apres_IS} €]"
                    )
            with col2:
                if self.results.params.president_net_apres_IR < 0:
                    st.write(
                        f"Revenu net après IR: :red[{self.results.params.president_net_apres_IR} €]"
                    )
                else:
                    st.write(
                        f"Revenu net après IR: :green[{self.results.params.president_net_apres_IR} €]"
                    )

            col1, col2 = st.columns(2)
            with col1:
                if self.results.params.reste_tresorerie < 0:
                    st.write(
                        f"Reste tresorerie: :red[{self.results.params.reste_tresorerie} €]"
                    )
                else:
                    st.write(
                        f"Reste tresorerie: :green[{self.results.params.reste_tresorerie} €]"
                    )

        self.optimization(salaire_avec_CS_minimum, salaire_avec_CS_maximum)

    def optimization(self, salaire_avec_CS_minimum, salaire_avec_CS_maximum):
        space = {
            "type_societe": hp.choice("type_societe", self.status_possibles),
            "choix_fiscal": hp.choice("choix_fiscal", self.fiscalites_possibles),
            "salaire_annuel_avecCS_avantIR": hp.quniform(
                "salaire_annuel_avecCS_avantIR",
                salaire_avec_CS_minimum,
                salaire_avec_CS_maximum,
                100,
            ),
            "proportion_dividende": hp.quniform(
                "proportion_dividende", 0, 1, 0.1
            ),  # Proportion of the result paid as dividends
            "charges_deductibles": hp.quniform(
                "charges_deductibles",
                st.session_state["charges_deductibles"] - 1,
                st.session_state["charges_deductibles"],
                1,
            ),  # This parameter should not be optimized but is here for the optimization to work
        }

        with st.sidebar:
            if st.button("🎯 Lancer l'optimisation du revenu"):
                optim = OptimizeIncome(space, objective)

        if st.session_state["best_trial"]:
            with st.sidebar:
                st.sidebar.write(
                    "Voici les résultats de l'optimisation. Utilisez les paramètres ci-dessous pour maximiser votre revenu net et consulter les détails dans l'application."
                )
                st.sidebar.write("### Paramètres légaux et fiscaux")
                st.sidebar.info(
                    f"Type de société: {self.status_possibles[st.session_state['best_trial']['type_societe']]}",
                    icon="🎛️",
                )
                st.sidebar.info(
                    f"Choix fiscal: {self.fiscalites_possibles[st.session_state['best_trial']['choix_fiscal']]}",
                    icon="🎛️",
                )
                st.sidebar.info(
                    f"Salaire net annuel: {st.session_state['best_trial']['salaire_annuel_sansCS_avantIR']:.2f} €",
                    icon="🎛️",
                )
                st.sidebar.info(
                    f"Dividendes avant impôts: {st.session_state['best_trial']['dividendes_recus']:.2f} € ({int(st.session_state['best_trial']['proportion_dividende']*100)}%)",
                    icon="🎛️",
                )
                st.sidebar.info(
                    f"Reste trésorerie: {st.session_state['best_trial']['reste_tresorerie']:.2f} €",
                    icon="🎛️",
                )
                st.sidebar.write("### Revenus après impôts")
                st.sidebar.success(
                    f"Meilleur revenu net après impots: {round(st.session_state['best_trial']['loss'],2)} €",
                    icon="✅",
                )

    def display_results(self):
        params = {
            "charges_deductibles": self.charges_deductibles,
            "type_societe": self.type_societe,
            "choix_fiscal": self.choix_fiscal,
            "salaire_annuel_avecCS_avantIR": self.salaire_annuel_sansCS_avantIR,
            "proportion_dividende": self.proportion_du_resultat_versee_en_dividende,
            "running_hyperopt": False,
        }
        scenario = Scenario(params)

        self.results = DisplayResults(
            chiffre_affaire_HT=self.chiffre_affaire_HT,
            charges_deductibles=self.charges_deductibles,
            benefice_apres_charges_deductibles=scenario.resultat_net.benefice_apres_charges_deductibles,
            salaire_annuel_sansCS_avantIR=scenario.resultat_net.salaire_annuel_sansCS_avantIR,
            CS_sur_salaire_annuel=scenario.resultat_net.charges_sociales_sur_salaire_president,
            benefices_apres_salaire_president=scenario.resultat_net.benefices_apres_salaire_president,
            impots_sur_les_societes=scenario.resultat_net.impots_sur_les_societes,
            societe_resultat_net_apres_IS=scenario.resultat_net.societe_resultat_net_apres_IS,
            charges_sur_dividendes=scenario.resultat_dividendes.charges_sur_dividendes,
            dividendes_recus=scenario.resultat_dividendes.dividendes_recus_par_president_annuellement,
            reste_tresorerie=scenario.resultat_dividendes.reste_tresorerie,
            president_imposable_total=scenario.president_imposable_total,
            impot_sur_le_revenu=scenario.resultat_IR.impot_sur_le_revenu,
            president_net_apres_IR=scenario.president_net_apres_IR,
            taxes_total=scenario.taxes_total,
            supplement_IR=scenario.resultat_dividendes.supplement_IR,
        )


if __name__ == "__main__":
    calculator = Home()
