import streamlit as st


class About:
    def __init__(self):
        tabs = st.tabs(["À propos", "Objectifs", "Ressources", "Contact et Support"])

        with tabs[0]:
            self.a_propos()
        with tabs[1]:
            self.objectifs()
        with tabs[2]:
            self.ressources()
        with tabs[3]:
            self.contact_support()

    def a_propos(self):
        st.write("""
            ### À propos de l'application

            Bienvenue sur notre application de visualisation et d'optimisation des revenus pour les présidents d'entreprises SASU et EURL. Cette application a été conçue pour aider les entrepreneurs à mieux comprendre et optimiser leurs revenus en fonction de divers paramètres financiers et fiscaux.

            #### Fonctionnalités de l'application

            Notre application vous permet de :

            1. **Choisir le statut social :**
                - **EURL (Entreprise Unipersonnelle à Responsabilité Limitée)**
                - **SASU (Société par Actions Simplifiée Unipersonnelle)**

            2. **Simuler les revenus :**
                - **Dividendes**
                - **Salaires**
                - **Proportion des revenus** (combinaison de dividendes et salaires)

            3. **Sélectionner le choix d'imposition :**
                - **Impôt sur le revenu (IR)**
                - **Impôt sur les sociétés (IS)**
                - **Flat tax** (prélèvement forfaitaire unique)

            4. **Saisir le chiffre d'affaires :**
                - Estimez vos revenus en fonction de votre chiffre d'affaires annuel.

            5. **Définir le capital social de votre société :**
                - Impact du capital social sur la fiscalité et les charges sociales.

            6. **Inclure les charges déductibles :**
                - Prenez en compte les différentes charges déductibles pour une estimation précise de vos revenus nets.

            7. **Choisir ou laisser l'algorithme optimiser :**
                - Vous pouvez soit choisir manuellement les paramètres, soit laisser l'algorithme définir les options optimales pour maximiser vos revenus.

            """)

    def objectifs(self):
        st.write("""
            #### Objectifs de l'application
            
            - **Clarté :** Offrir une visualisation claire et intuitive des différentes options fiscales et sociales.
            - **Optimisation :** Aider les entrepreneurs à maximiser leurs revenus nets en optimisant la combinaison de salaires et de dividendes.
            - **Éducation :** Fournir des informations pertinentes et à jour sur les régimes fiscaux et sociaux applicables.
            """)

    def ressources(self):
        st.write("""
            #### Ressources Utiles

            Pour vous aider à approfondir vos connaissances et à vérifier les informations, voici quelques liens utiles :

            1. **Sites gouvernementaux :**
                - [Service-public.fr - Statuts juridiques des entreprises](https://www.service-public.fr/professionnels-entreprises/vosdroits/F31228)
                - [Impôts.gouv.fr - Fiscalité des entreprises](https://www.impots.gouv.fr/portail/professionnel/entreprise)
                - [URSSAF - Cotisations sociales des indépendants](https://www.urssaf.fr/portail/home/independants.html)

            2. **Simulateurs et calculatrices en ligne :**
                - [Simulateur de calcul des charges sociales des indépendants](https://www.urssaf.fr/portail/home/independants/estimations-des-cotisations.html)
                - [Simulateur d'impôt sur les sociétés](https://www.impots.gouv.fr/portail/simulateurs)
                - [Simulateur de prélèvement forfaitaire unique (Flat Tax)](https://www.impots.gouv.fr/portail/particulier/questions/je-souhaite-connaitre-les-modalites-du-prelevement-forfaitaire-unique-pfu-ou-flat)

            3. **Articles et guides pratiques :**
                - [Guide complet sur le choix du statut juridique (SASU vs EURL)](https://www.lecoindesentrepreneurs.fr/comparatif-sasu-eurl/)
                - [Tout savoir sur la flat tax](https://www.lafinancepourtous.com/pratique/fiscalite/flat-tax-prelevement-forfaitaire-unique/)
                - [Optimiser les revenus d'un dirigeant de société](https://www.legifiscal.fr/articles-fiscaux/000244-optimiser-revenus-dirigeant.html)
            """)

    def contact_support(self):
        st.write("""
            #### Contact et Support

            Pour toute question ou assistance, n'hésitez pas à nous [contacter](https://sotisanalytics.com/contact).

            Nous espérons que cette application vous sera utile et vous permettra d'optimiser efficacement vos revenus en tant que président de SASU ou EURL. Merci d'utiliser notre application et bonne optimisation !
            """)