from types import SimpleNamespace
from typing import Any, Dict

import streamlit as st
import yaml


class Scenario:
    def __init__(self, params: Dict[str, Any]):
        self.params = params  # SimpleNamespace(**kwargs)
        self.calculate_scenario()

    def calculate_scenario(self):
        resultat_net = ResultatNet(
            st.session_state["chiffre_affaire_HT"],
            self.params["charges_deductibles"],
            self.params["type_societe"],
            self.params["salaire_annuel_avecCS_avantIR"],
            self.params["running_hyperopt"],
        )
        resultat_dividendes = Dividendes(
            resultat_net.societe_resultat_net_apres_IS,
            self.params["proportion_dividende"],
            self.params["type_societe"],
            self.params["choix_fiscal"],
            st.session_state["capital_social_societe"],
        )
        president_imposable_total = (
            resultat_net.salaire_annuel_sansCS_avantIR
            + resultat_dividendes.supplement_imposable
        )
        resultat_IR = ImpotRevenus(president_imposable_total)
        president_net_apres_IR = (
            resultat_net.salaire_annuel_sansCS_avantIR
            + resultat_dividendes.dividendes_recus_par_president_annuellement
            - resultat_IR.impot_sur_le_revenu
        )
        taxes_total = (
            resultat_net.charges_sociales_sur_salaire_president
            + resultat_net.impots_sur_les_societes
            + resultat_IR.impot_sur_le_revenu
            + resultat_dividendes.supplement_IR
        )

        self.resultat_net = resultat_net
        self.resultat_dividendes = resultat_dividendes
        self.resultat_IR = resultat_IR
        self.president_imposable_total = president_imposable_total
        self.president_net_apres_IR = president_net_apres_IR
        self.taxes_total = taxes_total


class ImpotRevenus:
    def __init__(self, revenu_annuel: float):
        with open("config/taxes.yaml", "r") as file:
            config_yaml = yaml.safe_load(file)

        impot_sur_le_revenu = 0

        # Calcul de l'impôt pour chaque tranche
        for min_tranche, max_tranche, taux_pcent in config_yaml["tranches_IR"]:
            taux = taux_pcent / 100
            if revenu_annuel > min_tranche:
                # Calcul de la part du revenu dans la tranche actuelle
                revenu_dans_tranche = min(revenu_annuel, max_tranche) - min_tranche
                # Application du taux d'imposition à cette part
                impot_tranche = revenu_dans_tranche * taux
                impot_sur_le_revenu += impot_tranche
                # Si le revenu est supérieur à la tranche maximale, arrêter le calcul
                if revenu_annuel <= max_tranche:
                    break

        print()
        print(
            f"Pour un revenu annuel imposable de {revenu_annuel:.2f}€, l'impôt dû est de {impot_sur_le_revenu:.2f} €."
        )

        self.impot_sur_le_revenu = impot_sur_le_revenu


class Dividendes:
    #https://www.indy.fr/blog/imposition-dividendes-bareme-progressif-pfu/
    #https://www.l-expert-comptable.com/a/531891-dividendes-et-impot-sur-le-revenu.html
    def __init__(
        self,
        societe_resultat_net_apres_IS: float,
        proportion_du_resultat_versee_en_dividende: float,
        type_societe: str,
        choix_fiscal: str,
        capital_social_societe: float,
    ):
        with open("config/taxes.yaml", "r") as file:
            self.config_yaml = yaml.safe_load(file)

        print("\n### calcul_dividendes \n-------------------------")

        self.montant_verse_en_dividendes_au_president_annuellement = (
            societe_resultat_net_apres_IS * proportion_du_resultat_versee_en_dividende
        )

        if (
            type_societe == "EURL"
            and self.montant_verse_en_dividendes_au_president_annuellement
            > capital_social_societe * 0.1
        ):
            self.montant_verse_en_dividendes_au_president_annuellement = (
                capital_social_societe - 1
            )

        if choix_fiscal == "flat_tax":
            self.flat_tax_choice()
        elif choix_fiscal == "bareme":
            self.bareme_choice()


        reste_tresorerie = round(
            societe_resultat_net_apres_IS
            - self.montant_verse_en_dividendes_au_president_annuellement
        )
        print(f"= reste_tresorerie: {reste_tresorerie} €")

        # self.charges_sur_dividendes = charges_sur_dividendes
        self.dividendes_recus_par_president_annuellement = (
            self.dividendes_recus_par_president_annuellement
        )
        self.reste_tresorerie = reste_tresorerie
        self.supplement_imposable = self.supplement_imposable

    def flat_tax_choice(self):
        prelevements_sociaux_cout = self.montant_verse_en_dividendes_au_president_annuellement * self.config_yaml["dividendes"]["prelevements_sociaux"] / 100
        TMI_cout = self.montant_verse_en_dividendes_au_president_annuellement * self.config_yaml["dividendes"]["TMI"] / 100
        self.supplement_imposable = 0
        self.supplement_IR = 0
        self.dividendes_recus_par_president_annuellement = round(
            self.montant_verse_en_dividendes_au_president_annuellement
            - TMI_cout
            - prelevements_sociaux_cout
        )

    def bareme_choice(self):
        dividendes_abattus = (
            self.montant_verse_en_dividendes_au_president_annuellement
            - self.montant_verse_en_dividendes_au_president_annuellement * self.config_yaml["dividendes"]["abattement"] / 100
        )

        CSG_cout = self.montant_verse_en_dividendes_au_president_annuellement * self.config_yaml["dividendes"]["CSG"] / 100
        prelevements_sociaux_cout = self.supplement_IR =  self.montant_verse_en_dividendes_au_president_annuellement * self.config_yaml["dividendes"]["prelevements_sociaux"] / 100
        self.supplement_imposable = dividendes_abattus - CSG_cout

        self.dividendes_recus_par_president_annuellement = round(
            self.montant_verse_en_dividendes_au_president_annuellement
            - prelevements_sociaux_cout
        )

class ResultatNet:
    def __init__(
        self,
        chiffre_affaire_HT: float,
        charges_deductibles: float,
        type_societe: str,
        salaire_annuel_sansCS_avantIR: float,
        running_hyperopt=False,
    ):
        with open("config/taxes.yaml", "r") as file:
            self.config_yaml = yaml.safe_load(file)

        """
        CS = charges sociales.
        salaire_annuel_sansCS_avantIR: par exemple 30000€ de celui-ci coûteront 54000€ (salaire + charges sociales) à l'entreprise en SASU.
        """

        ### [NOTE] On doit réaliser cette opération car le salaire optimisé peut varier de 0
        ### jusqu'à [C.A.h.t. - charges_déductibles]. Or en réalité le salaire à optimiser
        ### devrait être un pourcentage de [C.A.h.t. - charges_déductibles - charges_sociales_sur_salaire_president],
        ### et comme les charges sociales sur le salaire du président varient en fonction du type de société,
        ### et que le type de société est une variable d'entrée de la fonction objective, on doit recalculer le salaire
        ### du président en fonction du type de société, attribué par hyperopt.
        ### Par exemple : un somme alouée de 54000€ pour un SASU donnera un salaire net de 30000€, soit une charge
        ### de 24000€ (54000*0.444).
        ### --> On veut faire les prévisions sur le 30000€ (salaire reçu), pas sur le 54000€ (coût du salaire, que l'on
        ### calcule justement dans cette fonction avec <charges_sociales_sur_salaire_president>).
        ### Pour ce même exemple, on aura (30000€ * 0.8) = 24000€.
        if running_hyperopt:
            if type_societe == "EURL":
                salaire_annuel_sansCS_avantIR *= (
                    self.config_yaml["societe"]["EURL"]["charges_sociales"][
                        "taux_inverse_approximatif"
                    ]
                    / 100
                )
            if type_societe == "SASU":
                salaire_annuel_sansCS_avantIR *= (
                    self.config_yaml["societe"]["SASU"]["charges_sociales"][
                        "taux_inverse_approximatif"
                    ]
                    / 100
                )

        print()
        print("### calcul_resultat_net \n-------------------------")
        ###-----------------------------------------------------------------
        ### Calcul de la marge globale
        print(f"+ marge_globale: {chiffre_affaire_HT}")
        print(f"- charges_deductibles: {charges_deductibles}")
        benefice_apres_charges_deductibles = chiffre_affaire_HT - charges_deductibles
        print(
            f"= benefice_apres_charges_deductibles: {benefice_apres_charges_deductibles} €"
        )
        print()

        ###-----------------------------------------------------------------
        ### Calcul des charges sociales sur le salaire du président
        taux_charges_sociales_EURL = (
            self.config_yaml["societe"]["EURL"]["charges_sociales"]["taux"] / 100
        )
        taux_charges_sociales_SASU = (
            self.config_yaml["societe"]["SASU"]["charges_sociales"]["taux"] / 100
        )

        print(f"- salaire_recu_par_le_president: {salaire_annuel_sansCS_avantIR}")

        if type_societe == "EURL":
            charges_sociales_sur_salaire_president = round(
                taux_charges_sociales_EURL * salaire_annuel_sansCS_avantIR
            )
        if type_societe == "SASU":
            charges_sociales_sur_salaire_president = round(
                taux_charges_sociales_SASU * salaire_annuel_sansCS_avantIR
            )
        print(
            f"- charges_sur_salaire_president: {charges_sociales_sur_salaire_president}"
        )

        benefices_apres_salaire_president = (
            benefice_apres_charges_deductibles
            - salaire_annuel_sansCS_avantIR
            - charges_sociales_sur_salaire_president
        )
        print(
            f"= benefices_apres_salaire_president: {benefices_apres_salaire_president} €"
        )
        print()

        ###-----------------------------------------------------------------
        ### Calcul de l'impot sur les sociétés
        seuil = self.config_yaml["societe"]["SASU"]["tranches_IS"][-1][0]
        if benefices_apres_salaire_president <= seuil:
            impots_sur_les_societes = round(
                benefices_apres_salaire_president
                * self.config_yaml["societe"]["SASU"]["tranches_IS"][0][-1]
                / 100
            )
        else:
            impots_sur_les_societes = round(
                seuil * self.config_yaml["societe"]["SASU"]["tranches_IS"][0][-1] / 100
                + (benefices_apres_salaire_president - seuil)
                * self.config_yaml["societe"]["SASU"]["tranches_IS"][1][-1]
                / 100
            )
        print(f"- impots_sur_les_societes: {impots_sur_les_societes}")

        ###-----------------------------------------------------------------
        # Calcul du resultat net apres impot
        societe_resultat_net_apres_IS = round(
            benefices_apres_salaire_president - impots_sur_les_societes
        )
        print(
            f"= societe_resultat_net_apres_IS: {societe_resultat_net_apres_IS} €"
        )  # disponible pour dividendes

        self.benefice_apres_charges_deductibles = benefice_apres_charges_deductibles
        self.societe_resultat_net_apres_IS = societe_resultat_net_apres_IS
        self.salaire_annuel_sansCS_avantIR = salaire_annuel_sansCS_avantIR
        self.charges_sociales_sur_salaire_president = (
            charges_sociales_sur_salaire_president
        )
        self.benefices_apres_salaire_president = benefices_apres_salaire_president
        self.impots_sur_les_societes = impots_sur_les_societes
