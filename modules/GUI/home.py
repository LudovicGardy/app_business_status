import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import sys
import yaml

sys.path.append("..")
sys.path.append("../..")

from modules.societe import EURL, SASU

with open("config/config.yaml", "r") as file:
    config_yaml = yaml.safe_load(file)

# Exemple d'utilisation

class StreamlitWidgets:
    def __init__(self):
        self.set_streamlit_widgets()


    def set_streamlit_widgets(self):
        st.sidebar.write("### Résultats annuels de la société")
        self.chiffre_affaire_HT = st.sidebar.number_input(
            "Chiffre d'affaires HT (€)",
            min_value=0,
            value=200000,
            step=1000,
        )
        self.charges_deductibles = st.sidebar.number_input(
            "Charges déductibles (€)",
            min_value=0,
            value=st.session_state.get("charges_deductibles", 50000),
            step=1000,
        )
        self.remuneration_president = st.sidebar.number_input(
            "Rémunération président (€)",
            min_value=0,
            value=st.session_state.get("remuneration president", 20000),
            step=1000,
        )
class Home(StreamlitWidgets):
    def __init__(self):
        super().__init__()
        self.get_results()

        tabs = st.tabs(["⚙️ Graphique", "📊 Tableau"])
        with tabs[0]:
            st.write("## Graphique comparatif des résultats")
            self.plot_results()
        with tabs[1]:
            st.write("## Tableau comparatif des résultats")
            self.display_results()


    def get_results(self):

        self.eurl = EURL(
            ca_previsionnel=self.chiffre_affaire_HT,
            charges=self.charges_deductibles,
            remuneration_president=self.remuneration_president,
            taux_cotisation=config_yaml["EURL"]['salaires']['charges_sociales']['taux_cotisation'],
        )

        self.eurl.results['EURL']['benefice_reel'], self.eurl.results['EURL']['cotisations_president'] = self.eurl.calcul_benefice_reel()
        self.eurl.results['EURL']['impots_ir'] = self.eurl.calcul_impots_ir(tranches_ir=config_yaml['tranches_IR'])
        self.eurl.results['EURL']['impots_is'] = self.eurl.calcul_is(self.eurl.results['EURL']['benefice_reel'])
        self.eurl.results['EURL']['total_impots'] = self.eurl.calcul_total_impots(self.eurl.results['EURL']['cotisations_president'], 
                                                                self.eurl.results['EURL']['impots_ir'], 
                                                                self.eurl.results['EURL']['impots_is'])

        self.sasu = SASU(
            ca_previsionnel=self.chiffre_affaire_HT,
            charges=self.charges_deductibles,
            remuneration_president=self.remuneration_president,
            taux_cotisation=config_yaml["SASU"]['salaires']['charges_sociales']['taux_cotisation'],
        )

        self.sasu.results['SASU']['benefice_reel'], self.sasu.results['SASU']['cotisations_president'] = self.sasu.calcul_benefice_reel()
        self.sasu.results['SASU']['impots_ir'] = self.sasu.calcul_impots_ir(tranches_ir=config_yaml['tranches_IR'])
        self.sasu.results['SASU']['impots_is'] = self.sasu.calcul_is(self.sasu.results['SASU']['benefice_reel'])
        self.sasu.results['SASU']['total_impots'] = self.sasu.calcul_total_impots(self.sasu.results['SASU']['cotisations_president'], 
                                                                self.sasu.results['SASU']['impots_ir'], 
                                                                self.sasu.results['SASU']['impots_is'])


    def display_results(self):
        """
        Affiche les résultats des calculs pour les deux types de sociétés sous forme de tableau comparatif avec les résultats en colonnes.
        """

        data = {
            "Indicateurs": [
                "Chiffre d'affaires prévisionnel",
                "Dépenses réelles",
                "Rémunération président",
                "Cotisations président",
                "Total dépenses réelles",
                "Bénéfice réel",
                "Impôts sur le revenu",
                "Impôts sur les sociétés",
                "TOTAL COTISATIONS ET IMPÔTS",
                "Salaire net (post-IR)",
                "Reste bénéfice net à distribuer (post-IS)",
                "[Optionnel] Divdendes net à la flat tax",
            ],
            "EURL": [
                f'<span style="color:blue">{self.eurl.ca_previsionnel}</span>',
                f'<span style="color:blue">{self.eurl.charges}</span>',
                f'<span style="color:blue">{self.eurl.remuneration_president}</span>',
                f'<span style="color:red">{self.eurl.results["EURL"]["cotisations_president"]}</span>',
                f'<span style="color:yellow">{self.eurl.charges + self.eurl.remuneration_president + self.eurl.results["EURL"]["cotisations_president"]}</span>',
                f'<span style="color:blue">{self.eurl.results["EURL"]["benefice_reel"]}</span>',
                f'<span style="color:red">{self.eurl.results["EURL"]["impots_ir"]}</span>',
                f'<span style="color:red">{self.eurl.results["EURL"]["impots_is"]}</span>',
                f'<span style="color:red">{self.eurl.results["EURL"]["total_impots"]}</span>',
                f'<span style="color:green">{self.eurl.remuneration_president - self.eurl.results["EURL"]["impots_ir"]}</span>',
                f'<span style="color:blue">{self.eurl.results["EURL"]["benefice_reel"] - self.eurl.results["EURL"]["impots_is"]}</span>',
                f'<span style="color:green">{None}</span>',
            ],
            "SASU": [
                f'<span style="color:blue">{self.sasu.ca_previsionnel}</span>',
                f'<span style="color:blue">{self.sasu.charges}</span>',
                f'<span style="color:blue">{self.sasu.remuneration_president}</span>',
                f'<span style="color:red">{self.sasu.results["SASU"]["cotisations_president"]}</span>',
                f'<span style="color:yellow">{self.sasu.charges + self.sasu.remuneration_president + self.sasu.results["SASU"]["cotisations_president"]}</span>',
                f'<span style="color:blue">{self.sasu.results["SASU"]["benefice_reel"]}</span>',
                f'<span style="color:red">{self.sasu.results["SASU"]["impots_ir"]}</span>',
                f'<span style="color:red">{self.sasu.results["SASU"]["impots_is"]}</span>',
                f'<span style="color:red">{self.sasu.results["SASU"]["total_impots"]}</span>',
                f'<span style="color:green">{self.sasu.remuneration_president - self.sasu.results["SASU"]["impots_ir"]}</span>',
                f'<span style="color:blue">{self.sasu.results["SASU"]["benefice_reel"] - self.sasu.results["SASU"]["impots_is"]}</span>',
                f'<span style="color:green">{(self.sasu.results["SASU"]["benefice_reel"] - self.sasu.results["SASU"]["impots_is"]) * 0.7}</span>',
            ]
        }

        df_results = pd.DataFrame(data)
        st.write(df_results.to_html(escape=False), unsafe_allow_html=True)
            
    def plot_results(self):
        """
        Interactive barplot using Plotly to compare values (income and taxes) for SASU and EURL.
        """
        # Extraire les résultats pour les deux statuts
        sasu_results = self.sasu.results["SASU"]
        eurl_results = self.eurl.results["EURL"]

        # Données à comparer
        labels = ["Bénéfice réel", "Cotisations président", "Impôts IR", "Impôts IS", "Total impôts"]
        sasu_values = [
            sasu_results["benefice_reel"],
            sasu_results["cotisations_president"],
            sasu_results["impots_ir"],
            sasu_results["impots_is"],
            sasu_results["total_impots"],
        ]
        eurl_values = [
            eurl_results["benefice_reel"],
            eurl_results["cotisations_president"],
            eurl_results["impots_ir"],
            eurl_results["impots_is"],
            eurl_results["total_impots"],
        ]

        # Création du graphe interactif
        fig = go.Figure()

        # Ajouter les barres SASU
        fig.add_trace(go.Bar(
            x=labels,
            y=sasu_values,
            name="SASU",
            marker_color='rgb(55, 83, 109)',
            text=[f"{v:,.0f}€" for v in sasu_values],
            textposition='auto'
        ))

        # Ajouter les barres EURL
        fig.add_trace(go.Bar(
            x=labels,
            y=eurl_values,
            name="EURL",
            marker_color='rgb(26, 118, 255)',
            text=[f"{v:,.0f}€" for v in eurl_values],
            textposition='auto'
        ))

        # Mise en forme
        fig.update_layout(
            title="Comparaison des résultats entre SASU et EURL",
            xaxis=dict(title="Catégories", tickangle=-45),
            yaxis=dict(title="Montants (€)", tickformat=",.0f"),
            barmode='group',
            bargap=0.15,  # Espace entre les groupes de barres
            bargroupgap=0.1,  # Espace entre les barres d'un groupe
            legend=dict(title="Type d'entreprise"),
            template="plotly_white"
        )

        # Affichage dans Streamlit
        st.plotly_chart(fig, use_container_width=True)
        
if __name__ == "__main__":
    calculator = Home()
