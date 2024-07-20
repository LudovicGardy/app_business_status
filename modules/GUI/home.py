### Comparaison salaire président SASU vs EURL

import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from hyperopt import hp, fmin, tpe, Trials, STATUS_OK
from types import SimpleNamespace

from ..calculs import calculer_IR, calcul_resultat_net, calcul_dividendes
from ..optimization import objective, run_optimization


class DisplayResults:
    def __init__(self, **kwargs):
        self.params = SimpleNamespace(**kwargs)

    def text_results(self):
        st.write("### Resultats nets")
        st.divider()
        st.write(f"\+ chiffre affaire HT: :green[{self.params.chiffre_affaire_HT} €]")
        st.write(f"\- charges deductibles: :red[{self.params.charges_deductibles} €]")
        st.write(f"\= benefices apres charges deductibles: :blue[{self.params.benefice_apres_charges_deductibles} €]")
        st.divider()
        st.write(f"\- salaire recu par le president: :red[{self.params.salaire_annuel_sansCS_avantIR} €]")
        st.write(f"\- charges sur salaire president: :red[{self.params.CS_sur_salaire_annuel} €]")
        st.write(f"\= benefices apres salaire president: :blue[{self.params.benefices_apres_salaire_president} €]")
        st.divider()
        st.write(f"\- impots sur les societes: :red[{self.params.impots_sur_les_societes} €]")
        st.write(f"\= societe resultat net apres IS: :blue[{self.params.societe_resultat_net_apres_IS} €]")
        st.divider()
        st.write("### Dividendes")
        st.write(f"\- dividendes recus par president annuellement: :red[{self.params.dividendes_recus} €]")
        st.write(f"\- charges sur dividendes: :red[{self.params.charges_sur_dividendes} €]")
        st.write(f"\= reste tresorerie: :blue[{self.params.reste_tresorerie} €]")
        st.divider()
        st.write("### Resultats pour le president")
        st.write(f"- Revenu annuel imposable: {self.params.president_imposable_total} € \n  - Salaire: {self.params.salaire_annuel_sansCS_avantIR} € (imposable: {self.params.salaire_annuel_sansCS_avantIR} €) \n  - Dividendes: {self.params.dividendes_recus} € (imposable: {self.params.supplement_IR} €)")
        st.write(f"Pour un revenu annuel de {self.params.president_imposable_total:.2f} €, l'impot dû est de {self.params.impot_sur_le_revenu:.2f} €.")
        st.write(f"Après import sur le revenu, le président gagne {self.params.president_net_apres_IR:.2f} €.")
        st.divider()
        st.write(f"Nota Bene 1: TVA facturée approximativement (non comptée dans les calculs): {self.params.chiffre_affaire_HT * 0.2} €")
        st.write(f"Nota Bene 2: Total des charges sans la TVA: {self.params.taxes_total} €")
        st.divider()

    def plot_results(self):
        st.divider()

        labels = ['Salaire Net', 'Dividendes', 'Reste en trésorerie', 'Taxes', 'Charges déductibles']
        values = [self.params.salaire_annuel_sansCS_avantIR, self.params.dividendes_recus, self.params.reste_tresorerie, self.params.taxes_total, self.params.charges_deductibles]

        color_map = {
            'Salaire Net': 'lightgreen',
            'Dividendes': 'limegreen',
            'Reste en trésorerie': 'green',
            'Taxes': 'salmon',
            'Charges déductibles': 'red'
        }

        fig = px.pie(values=values, names=labels, title=f"Répartition financière après simulation pour un C.A. H.T. de {self.params.chiffre_affaire_HT} €", 
                color=labels,
                color_discrete_map=color_map)
                    #  color_discrete_sequence=px.colors.sequential.RdBu)
        
        st.plotly_chart(fig, use_container_width=True)

class OptimizeIncome:
    def __init__(self, space):
        best_params, trials = run_optimization(space, objective)
        st.write(f"Meilleurs paramètres:")

        st.write(f"  . Dividendes reçus par le président: {trials.best_trial['result']['dividendes_recus']:.2f} €")
        st.write(f"  . Reste en trésorerie: {trials.best_trial['result']['reste_tresorerie']:.2f} €")
        st.write(f"  . Meilleur revenu net après IR: {-trials.best_trial['result']['loss']} €")    
        
        best_params['salaire_annuel_sansCS_avantIR'] = trials.best_trial['result']['write_results_dict']['salaire_annuel_sansCS_avantIR'] #int(best_params['salaire_annuel'])

        ### Set new values and refresh
        st.session_state['type_societe'] = int(best_params['type_societe'])
        st.session_state['choix_fiscal'] = int(best_params['choix_fiscal'])
        st.session_state['salaire_annuel_sansCS_avantIR'] = int(best_params['salaire_annuel_sansCS_avantIR'])
        st.session_state['proportion_du_resultat_versee_en_dividende'] = int(best_params['proportion_dividende'] * 100)
        st.session_state['charges_deductibles'] = int(best_params['charges_deductibles'])
        print("best_params:", best_params)

class IncomeCalculator:

    def __init__(self):
        self.run()

    def run(self):

        st.title("Simulateur de coûts, salaires et dividendes pour SASU et EURL")

        ###-----------------------------------------------------------------------
        ### OPTIMISATION
        ##- Resultats societe
        salaire_avecCS_maximum = st.session_state['chiffre_affaire_HT'] - st.session_state['charges_deductibles']
        salaire_avec_CS_minimum = 0

        # Définition de l'espace de recherche
        space = {
            'type_societe': hp.choice('type_societe', ['SASU', 'EURL']),
            'choix_fiscal': hp.choice('choix_fiscal', ['flat_tax', 'bareme']),
            'salaire_annuel_avecCS_avantIR': hp.quniform('salaire_annuel_avecCS_avantIR', salaire_avec_CS_minimum, salaire_avecCS_maximum, 100),
            'proportion_dividende': hp.quniform('proportion_dividende', 0, 1,0.1),  # Proportion des dividendes entre 0 et 1 (0% à 100%)
            'charges_deductibles': hp.quniform('charges_deductibles', st.session_state['charges_deductibles'], st.session_state['chiffre_affaire_HT']-st.session_state['charges_deductibles'], 1000)  # Exemple: charges déductibles entre 0 et 10000 euros,
        }

        ##- Resultats societe
        st.divider()
        st.write("### Résultats annuels de la société")
        col1, col2 = st.columns(2)

        with col1:
            chiffre_affaire_HT = st.number_input("Chiffre d'affaires HT (€)", min_value=0, value=st.session_state['chiffre_affaire_HT'], step=1000)
        with col2:
            charges_deductibles = st.number_input("Charges déductibles (€)", min_value=0, value=st.session_state['charges_deductibles'], step=1000)

        if st.button('Optimiser le revenu du président'):
            optim = OptimizeIncome(space)

        ##-----------------------------------------------------------------------
        ## ANALYSE UNITAIRE
        ##- Paramètres legaux et fiscaux
        st.divider()
        st.write("### Paramètres legaux et fiscaux")
        col1, col2, col3 = st.columns(3)

        with col1:
            type_societe = st.selectbox("Type de société", ["SASU", "EURL"], index=st.session_state['type_societe'])
        with col2:
            choix_fiscal = st.selectbox("Régime fiscal des dividendes", ["flat_tax", "bareme"], index=st.session_state['choix_fiscal'])
        with col3:
            capital_social_societe = st.number_input("Capital social de la société (€)", min_value=0, value=st.session_state['capital_social_societe'], step=1000)

        ##- Salaire president et Dividendes
        # st.divider()
        st.write("### Salaire du président et Dividendes")

        col1, col2 = st.columns(2)

        with col1:
            salaire_annuel_sansCS_avantIR = st.number_input("Salaire annuel du président (€)", min_value=0, value=st.session_state['salaire_annuel_sansCS_avantIR'], step=1000)
        with col2:
            proportion_du_resultat_versee_en_dividende = st.slider("Proportion du résultat après IS versée en dividendes (%)", min_value=0, max_value=100, value=st.session_state['proportion_du_resultat_versee_en_dividende']) / 100.0

        if st.button('Afficher les résultats'):

            self.resultat_net = calcul_resultat_net(
                chiffre_affaire_HT, charges_deductibles, type_societe, salaire_annuel_sansCS_avantIR
            )
            self.resultat_dividendes = calcul_dividendes(
                self.resultat_net.societe_resultat_net_apres_IS, proportion_du_resultat_versee_en_dividende, type_societe, choix_fiscal, capital_social_societe
            )
            president_imposable_total = self.resultat_net.salaire_annuel_sansCS_avantIR + self.resultat_dividendes.supplement_IR

            self.resultat_IR = calculer_IR(president_imposable_total)
            president_net_apres_IR = self.resultat_net.salaire_annuel_sansCS_avantIR + self.resultat_dividendes.dividendes_recus_par_president_annuellement - self.resultat_IR.impot_sur_le_revenu
            taxes_total = self.resultat_net.charges_sociales_sur_salaire_president + self.resultat_net.impots_sur_les_societes + self.resultat_dividendes.charges_sur_dividendes + self.resultat_IR.impot_sur_le_revenu

            results = DisplayResults(chiffre_affaire_HT=chiffre_affaire_HT,
                                     charges_deductibles=charges_deductibles,
                                    benefice_apres_charges_deductibles=self.resultat_net.benefice_apres_charges_deductibles,
                                    salaire_annuel_sansCS_avantIR=self.resultat_net.salaire_annuel_sansCS_avantIR,
                                    CS_sur_salaire_annuel=self.resultat_net.charges_sociales_sur_salaire_president,
                                    benefices_apres_salaire_president=self.resultat_net.benefices_apres_salaire_president,
                                    impots_sur_les_societes=self.resultat_net.impots_sur_les_societes,
                                    societe_resultat_net_apres_IS=self.resultat_net.societe_resultat_net_apres_IS,
                                    charges_sur_dividendes=self.resultat_dividendes.charges_sur_dividendes,
                                    dividendes_recus=self.resultat_dividendes.dividendes_recus_par_president_annuellement,
                                    reste_tresorerie=self.resultat_dividendes.reste_tresorerie,
                                    president_imposable_total=president_imposable_total,
                                    impot_sur_le_revenu=self.resultat_IR.impot_sur_le_revenu,
                                    president_net_apres_IR=president_net_apres_IR,
                                    taxes_total=taxes_total,
                                    supplement_IR=self.resultat_dividendes.supplement_IR)
                        
            results.plot_results()
            results.text_results()

if __name__ == '__main__':
    calculator = IncomeCalculator()