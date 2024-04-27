### Comparaison salaire président SASU vs EURL

import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from hyperopt import hp, fmin, tpe, Trials, STATUS_OK

from modules.calcul_IR import calculer_IR
from modules.calcul_resultat import calcul_resultat_net
from modules.calcul_dividendes import calcul_dividendes
from modules.optimization import run_optimization
from modules.config import firebase_credentials, page_config, data_URL, azure_credentials, bigquery_credentials

###-----------------------------------------------------------------------
### CONFIGS
st.set_page_config(page_title=page_config().get('page_title'), 
                    page_icon = page_config().get('page_icon'),  
                    layout = page_config().get('layout'),
                    initial_sidebar_state = page_config().get('initial_sidebar_state'))

###-----------------------------------------------------------------------
### PARAMETERS
if 'type_societe' not in st.session_state:
    st.session_state['type_societe'] = 0
if 'choix_fiscal' not in st.session_state:
    st.session_state['choix_fiscal'] = 0
if 'capital_social_societe' not in st.session_state:
    st.session_state['capital_social_societe'] = 1000
if 'chiffre_affaire_HT' not in st.session_state:
    st.session_state['chiffre_affaire_HT'] = 200000
if 'charges_deductibles' not in st.session_state:
    st.session_state['charges_deductibles'] = 32000
if 'salaire_annuel_sansCS_avantIR' not in st.session_state:
    st.session_state['salaire_annuel_sansCS_avantIR'] = 10000
if 'proportion_du_resultat_versee_en_dividende' not in st.session_state:
    st.session_state['proportion_du_resultat_versee_en_dividende'] = 90

class Calculator:

    def __init__(self):
        pass

    ###-----------------------------------------------------------------------
    ### FUNCTIONS
    def steup_sidebar():
        '''
        Set up the sidebar.
        '''

        logo_path = page_config().get('page_logo')
        desired_width = 60

        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.image(logo_path, width=desired_width)
        with col2:
            st.write('# Sotis A.I.')

        st.caption('''Ce prototype est conçu pour fournir des insights plus clairs sur le choix entre deux structures juridiques françaises courantes : la EURL et la SASU.
                    \nVisitez https://www.sotisanalytics.com pour en savoir plus, signaler un problème, suggérer une idée ou me contacter. Profitez de votre exploration !
                    \nSotis A.I.© 2024''')

        st.divider()

        # # Définir les options d'onglet dans la sidebar
        # page = st.sidebar.radio("Navigate to", ('Page 1', 'Page 2'))

        # # Gestion des pages selon l'onglet sélectionné
        # if page == 'Page 1':
        #     st.title("Page 1")
        #     st.write("Contenu de la Page 1 - Vous pouvez mettre ici des informations ou des fonctionnalités liées à la comparaison des structures EURL vs SASU.")
        # elif page == 'Page 2':
        #     st.title("Page 2")
        #     st.write("Contenu de la Page 2 - Cette page pourrait inclure, par exemple, des calculatrices fiscales ou des analyses de responsabilité pour chaque structure juridique.")

    def write_results(chiffre_affaire_HT, 
                    charges_deductibles, 
                    benefice_apres_charges_deductibles, 
                    salaire_annuel_sansCS_avantIR, 
                    CS_sur_salaire_annuel,
                    benefices_apres_salaire_president,
                    impots_sur_les_societes,
                    societe_resultat_net_apres_IS,
                    charges_sur_dividendes,
                    dividendes_recus,
                    reste_tresorerie,
                    president_imposable_total,
                    impot_sur_le_revenu,
                    president_net_apres_IR,
                    taxes_total, 
                    supplement_IR
                    ):

        ### Affichage des résultats
        st.write("### Resultats nets")
        st.divider()
        st.write(f"\+ chiffre affaire HT: :green[{chiffre_affaire_HT} €]")
        st.write(f"\- charges deductibles: :red[{charges_deductibles} €]")
        st.write(f"\= benefices apres charges deductibles: :blue[{benefice_apres_charges_deductibles} €]")
        st.divider()
        st.write(f"\- salaire recu par le president: :red[{salaire_annuel_sansCS_avantIR} €]")
        st.write(f"\- charges sur salaire president: :red[{CS_sur_salaire_annuel} €]")
        st.write(f"\= benefices apres salaire president: :blue[{benefices_apres_salaire_president} €]")
        st.divider()
        st.write(f"\- impots sur les societes: :red[{impots_sur_les_societes} €]")
        st.write(f"\= societe resultat net apres IS: :blue[{societe_resultat_net_apres_IS} €]")
        st.divider()
        st.write("### Dividendes")
        st.write(f"\- dividendes recus par president annuellement: :red[{dividendes_recus} €]")
        st.write(f"\- charges sur dividendes: :red[{charges_sur_dividendes} €]")
        st.write(f"\= reste tresorerie: :blue[{reste_tresorerie} €]")
        st.divider()
        st.write("### Resultats pour le president")
        st.write(f"- Revenu annuel imposable: {president_imposable_total} € \n  - Salaire: {salaire_annuel_sansCS_avantIR} € (imposable: {salaire_annuel_sansCS_avantIR} €) \n  - Dividendes: {dividendes_recus} € (imposable: {supplement_IR} €)")
        st.write(f"Pour un revenu annuel de {president_imposable_total:.2f} €, l'impot dû est de {impot_sur_le_revenu:.2f} €.")
        st.write(f"Après import sur le revenu, le président gagne {president_net_apres_IR:.2f} €.")
        st.divider()
        st.write(f"Nota Bene 1: TVA facturée approximativement (non comptée dans les calculs): {chiffre_affaire_HT * 0.2} €")
        st.write(f"Nota Bene 2: Total des charges sans la TVA: {taxes_total} €")
        st.divider()

    ###-----------------------------------------------------------------------
    ### SIDEBAR
    with st.sidebar:
        steup_sidebar()

    ###-----------------------------------------------------------------------
    ### TITLE
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
        st.divider()
        benefice_apres_charges_deductibles, societe_resultat_net_apres_IS, salaire_annuel_sansCS_avantIR, CS_sur_salaire_annuel, benefices_apres_salaire_president, impots_sur_les_societes = calcul_resultat_net(
            chiffre_affaire_HT, charges_deductibles, type_societe, salaire_annuel_sansCS_avantIR
        )
        charges_sur_dividendes, dividendes_recus, reste_tresorerie, supplement_IR = calcul_dividendes(
            societe_resultat_net_apres_IS, proportion_du_resultat_versee_en_dividende, type_societe, choix_fiscal, capital_social_societe
        )
        president_imposable_total = salaire_annuel_sansCS_avantIR + supplement_IR

        impot_sur_le_revenu = calculer_IR(president_imposable_total)
        president_net_apres_IR = salaire_annuel_sansCS_avantIR + dividendes_recus - impot_sur_le_revenu
        taxes_total = CS_sur_salaire_annuel + impots_sur_les_societes + charges_sur_dividendes + impot_sur_le_revenu

        labels = ['Salaire Net', 'Dividendes', 'Reste en trésorerie', 'Taxes', 'Charges déductibles']
        values = [salaire_annuel_sansCS_avantIR, dividendes_recus, reste_tresorerie, taxes_total, charges_deductibles]

        color_map = {
            'Salaire Net': 'lightgreen',
            'Dividendes': 'limegreen',
            'Reste en trésorerie': 'green',
            'Taxes': 'salmon',
            'Charges déductibles': 'red'
        }

        fig = px.pie(values=values, names=labels, title=f"Répartition financière après simulation pour un C.A. H.T. de {chiffre_affaire_HT} €", 
                color=labels,
                color_discrete_map=color_map)
                    #  color_discrete_sequence=px.colors.sequential.RdBu)
        
        st.plotly_chart(fig, use_container_width=True)
        
        write_results(chiffre_affaire_HT, 
                    charges_deductibles, 
                    benefice_apres_charges_deductibles, 
                    salaire_annuel_sansCS_avantIR, 
                    CS_sur_salaire_annuel, 
                    benefices_apres_salaire_president, 
                    impots_sur_les_societes, 
                    societe_resultat_net_apres_IS, 
                    charges_sur_dividendes, 
                    dividendes_recus, 
                    reste_tresorerie, 
                    president_imposable_total, 
                    impot_sur_le_revenu, 
                    president_net_apres_IR, 
                    taxes_total,
                    supplement_IR)
