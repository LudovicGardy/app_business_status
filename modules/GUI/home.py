### Comparaison salaire président SASU vs EURL

from types import SimpleNamespace
from typing import Callable

import plotly.express as px
import streamlit as st
import yaml
from hyperopt import hp

from ..dividendes import DividendesSASU
from ..impot_societes import ImpotSocieteSASU
from ..salaires import SalaireSASU
from ..utils import calcul_impots_IR


class Home:
    def __init__(self):
        self.status_possibles = ["SASU", "EURL"]
        self.fiscalites_possibles = ["flat_tax", "bareme"]

        tabs = st.tabs(["⚙️ Configurations", "📊 Résultats & détails"])

        with tabs[0]:
            self.run()
        with tabs[1]:
            st.write("### Détails des calculs")
            # self.results.plot()
            # with st.expander("Voir les détails"):
                # self.results.text()

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

        # self.display_results()

        # with st.container(border=True):
        #     col1, col2 = st.columns(2)
        #     with col1:
        #         if self.results.params.societe_resultat_net_apres_IS < 0:
        #             st.write(
        #                 f"Disponible pour dividendes: :red[{self.results.params.societe_resultat_net_apres_IS} €]"
        #             )
        #         else:
        #             st.write(
        #                 f"Disponible pour dividendes: :green[{self.results.params.societe_resultat_net_apres_IS} €]"
        #             )
        #     with col2:
        #         if self.results.params.president_net_apres_IR < 0:
        #             st.write(
        #                 f"Revenu net après IR: :red[{self.results.params.president_net_apres_IR} €]"
        #             )
        #         else:
        #             st.write(
        #                 f"Revenu net après IR: :green[{self.results.params.president_net_apres_IR} €]"
        #             )

        #     col1, col2 = st.columns(2)
        #     with col1:
        #         if self.results.params.reste_tresorerie < 0:
        #             st.write(
        #                 f"Reste tresorerie: :red[{self.results.params.reste_tresorerie} €]"
        #             )
        #         else:
        #             st.write(
        #                 f"Reste tresorerie: :green[{self.results.params.reste_tresorerie} €]"
        #             )

if __name__ == "__main__":
    calculator = Home()
