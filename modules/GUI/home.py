### Comparaison salaire président SASU vs EURL

from types import SimpleNamespace
from typing import Callable
import plotly.express as px
import streamlit as st
import yaml
from hyperopt import hp

from modules.dividendes import DividendesSASU
from modules.impot_societes import ImpotSocieteSASU
from modules.salaires import SalaireSASU
from modules.utils import calcul_impots_IR


class StreamlitWidgets:
    def __init__(self):
        self.status_possibles = ["SASU"]  # , "EURL"]
        self.fiscalites_possibles = ["flat_tax", "bareme"]

        tabs = st.tabs(["⚙️ Configurations", "📊 Résultats & détails"])

        with tabs[0]:
            self.set_streamlit_widgets()
        with tabs[1]:
            st.write("### Détails des calculs")

    def set_streamlit_widgets(self):
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
                value=st.session_state.get("charges_deductibles", 50000),
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
            # Paramètres légaux et fiscaux
            st.write("### Paramètres légaux et fiscaux")
            col1, col2, col3 = st.columns(3)

            with col1:
                self.type_societe = st.selectbox(
                    "Type de société",
                    self.status_possibles,
                    index=st.session_state.get("type_societe", 0),
                )
            with col2:
                self.choix_fiscal = st.selectbox(
                    "Régime fiscal des dividendes",
                    self.fiscalites_possibles,
                    index=st.session_state.get("choix_fiscal", 0),
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
                    value=st.session_state.get("salaire_annuel_sansCS_avantIR", 50000),
                    step=1000,
                )

            with col2:
                self.proportion_du_resultat_versee_en_dividende = (
                    st.slider(
                        "Proportion du résultat après IS versée en dividendes (%)",
                        min_value=0,
                        max_value=100,
                        value=st.session_state.get(
                            "proportion_du_resultat_versee_en_dividende", 50
                        ),
                    )
                    / 100.0
                )


class Home(StreamlitWidgets):
    def __init__(self):
        super().__init__()

        self.calculs_salaire_president()
        with st.container(border=True):
            self.display_salaire_president()
        with st.container(border=True):
            st.write("### Charges déductibles")
            st.write(f"Charges déductibles : :red[{self.charges_deductibles:.2f} €]")
        self.calculs_impot_societe()
        with st.container(border=True):
            self.display_impot_societe()
        self.calculs_dividendes()
        with st.container(border=True):
            self.display_dividendes()

    def calculs_salaire_president(self):
        self.salaire_president = SalaireSASU(self.salaire_annuel_sansCS_avantIR)
        self.salaire_president.calcul_salaire_net()

    def calculs_dividendes(self):
        # Calcul des dividendes versés
        self.dividendes_verses = (
            self.chiffre_affaire_HT
            - self.charges_deductibles
            - self.salaire_president.log_data.salaire_super_brut
            - self.impot_societe.impot_a_payer
        ) * self.proportion_du_resultat_versee_en_dividende

        # Calcul de l'imposition des dividendes
        self.dividendes = DividendesSASU(
            self.dividendes_verses,
            self.type_societe,
            self.choix_fiscal,
        )

    def display_salaire_president(self):
        # Affichage des messages texte
        for message in self.salaire_president.streamlit_output:
            st.write(message)

        # Graphiques interactifs à partir des résultats stockés
        log_data = self.salaire_president.log_data

        # Création d'un dataframe pour faciliter la visualisation
        data = {
            "Catégories": [
                "Salaire brut",
                "Cotisations sociales",
                "Salaire net avant IR",
                "Impôt sur le revenu",
                "Salaire net après IR",
            ],
            "Montants (€)": [
                log_data.salaire_super_brut,
                log_data.cotisations,
                log_data.salaire_net_avant_impot,
                log_data.impots_revenu,
                log_data.salaire_net_apres_impot,
            ],
        }

        fig = px.bar(
            data,
            x="Catégories",
            y="Montants (€)",
            title="Répartition du salaire et imposition",
            labels={"Montants (€)": "Montants en euros"},
        )

        st.plotly_chart(fig)

    def display_impot_societe(self):
        # Affichage des messages texte
        st.write("### Impôt sur les sociétés")
        st.write(f"Impôt sur les sociétés : :red[{self.impot_societe.impot_a_payer} €]")

    def display_dividendes(self):
        # Affichage des messages texte
        for message in self.dividendes.streamlit_output:
            st.write(message)

        # Graphiques interactifs à partir des résultats stockés
        log_data = self.dividendes.log_data

        # Création d'un dataframe pour faciliter la visualisation
        data = {
            "Catégories": [
                "Dividendes versés",
                "Prélèvement TMI",
                "Imposition totale",
                "Dividendes nets",
                "Prélèvements sociaux",
                "CSG déductible",
                "Base imposable",
            ],
            "Montants (€)": [
                log_data.dividendes_verses,
                log_data.tmi,
                log_data.imposition_totale,
                log_data.dividendes_net,
                log_data.prelevements_sociaux_total,
                log_data.csg_deductible_amount,
                log_data.base_imposable,
            ],
        }

        fig = px.bar(
            data,
            x="Catégories",
            y="Montants (€)",
            title="Répartition des dividendes et imposition",
            labels={"Montants (€)": "Montants en euros"},
        )

        st.plotly_chart(fig)

    def calculs_impot_societe(self):
        self.impot_societe = ImpotSocieteSASU(
            self.chiffre_affaire_HT
            - self.charges_deductibles
            - self.salaire_president.log_data.salaire_net_apres_impot,
            self.type_societe,
        )


if __name__ == "__main__":
    calculator = Home()
