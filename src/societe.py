from abc import ABC, abstractmethod

import numpy as np
import plotly.express as px
import streamlit as st

from src.impot_revenu import calcul_IR
from src.impot_societes import calcul_IS


class Societe(ABC):
    def __init__(self, ca_previsionnel, charges, salaire_president, taux_cotisation):
        self.ca_previsionnel = ca_previsionnel
        self.charges = charges
        self.salaire_president = salaire_president
        self.taux_cotisation = taux_cotisation
        self.results: dict = {"SASU": {}, "EURL": {}}

    @abstractmethod
    def calcul_cotisations_president(self):
        pass

    def calcul_is(self, benefice_reel):
        return calcul_IS(benefice_reel)

    def calcul_benefice_reel(self):
        cotisations_president = self.calcul_cotisations_president()
        total_depenses_reelles = np.sum([self.charges, self.salaire_president, cotisations_president])
        return self.ca_previsionnel - total_depenses_reelles, cotisations_president

    def calcul_impots_ir(self, tranches_ir):
        return calcul_IR(tranches_ir, self.salaire_president)

    def calcul_total_impots(self, cotisations_president, impots_ir, impots_is):
        return np.sum([cotisations_president, impots_ir, impots_is])

    def display_text_results(self, benefice_reel, cotisations_president, impots_ir, impots_is, total_impots):
        logs = []
        logs.append("-----------------------------------------------------")
        logs.append(f"Chiffre d'affaires prévisionnel: {self.ca_previsionnel}")
        logs.append("-----------------------------------------------------")
        logs.append(f"Dépenses réelles: {self.charges}")
        logs.append(f"Salaire président: {self.salaire_president}")
        logs.append(f"Cotisations président: {cotisations_president}")
        logs.append(f"Total dépenses réelles: {self.charges + self.salaire_president + cotisations_president}")
        logs.append("")
        logs.append("-----------------------------------------------------")
        logs.append(f"Bénéfice réel (assujetti à IS): {benefice_reel}")
        logs.append("C'est ce montant que l'administration fiscale va retenir.")
        logs.append("-----------------------------------------------------\n")
        logs.append("-----------------------------------------------------")
        logs.append(f"Impôts sur le revenu: {impots_ir}")
        logs.append("-----------------------------------------------------\n")
        logs.append("-----------------------------------------------------")
        logs.append(f"Impôts sur les sociétés: {impots_is}")
        logs.append("-----------------------------------------------------\n")
        logs.append("-----------------------------------------------------")
        logs.append(f"TOTAL COTISATIONS ET IMPÔTS À PAYER: {total_impots}")
        logs.append("-----------------------------------------------------\n")
        logs.append("-----------------------------------------------------")
        logs.append(f"Le chef d'entreprise touche un salaire de : {self.salaire_president - impots_ir}")
        logs.append(f"Il reste {benefice_reel - impots_is} euros à distribuer")
        logs.append("-----------------------------------------------------\n")

        for log in logs:
            st.text(log)

class EURL(Societe):
    def calcul_cotisations_president(self):
        if self.salaire_president < 1100:
            return 1100
        return self.salaire_president * (self.taux_cotisation / 100)

class SASU(Societe):
    def calcul_cotisations_president(self):
        return self.salaire_president * (self.taux_cotisation / 100)

    def calcul_dividendes_net(self, tranches_ir, config_yaml, mode_imposition="flat_tax"):
        """
        Calcule les dividendes nets pour la SASU selon le mode d'imposition choisi.
        Args:
            tranches_ir (list): tranches d'IR
            config_yaml (dict): configuration extraite du YAML
            mode_imposition (str): 'flat_tax' ou 'bareme'
        Returns:
            dict: {
                'dividendes_net': Montant net perçu sur les dividendes,
                'dividendes_imposables': Base IR après abattement (barème),
                'impots_ir': Montant total IR (salaire + dividendes abattus si barème, sinon IR sur salaire seul),
                'impots_flat_tax': IR sur dividendes (flat tax),
                'prelevements_sociaux': Prélèvements sociaux sur dividendes,
                'base_ir_totale': Base IR totale utilisée (barème),
                'mode_imposition': mode,
            }
        """
        from src.impot_revenu import calcul_IR
        benefice_distribuable = self.results.get("benefice_reel", 0) - self.results.get("impots_is", 0)
        if benefice_distribuable < 0:
            benefice_distribuable = 0

        # Extraction des taux depuis la config YAML
        prelevements_sociaux_taux = config_yaml["SASU"]["dividendes"].get("prelevements_sociaux_total", 17.2) / 100
        tmi_taux = config_yaml["SASU"]["dividendes"].get("TMI", 12.8) / 100
        abattement_dividendes = config_yaml["SASU"]["dividendes"].get("abattement", 40) / 100

        # Prélèvements sociaux sur dividendes (toujours sur brut)
        prelevements_sociaux = benefice_distribuable * prelevements_sociaux_taux if benefice_distribuable > 0 else 0.0

        if mode_imposition == "flat_tax":
            # Flat tax : IR 12,8% + PS sur dividendes
            impots_flat_tax = benefice_distribuable * tmi_taux
            dividendes_net = benefice_distribuable - impots_flat_tax - prelevements_sociaux
            dividendes_imposables = benefice_distribuable  # pas d'abattement
            # IR sur salaire UNIQUEMENT (flat tax sur dividendes déjà inclus)
            impots_ir = self.calcul_impots_ir(tranches_ir)
            base_ir_totale = self.salaire_president
        else:
            # Barème progressif : abattement sur dividendes, ajout au salaire, IR sur le total
            dividendes_imposables = benefice_distribuable * (1 - abattement_dividendes)
            base_ir_totale = self.salaire_president + dividendes_imposables
            impots_ir = calcul_IR(tranches_ir, base_ir_totale)
            # Prélèvements sociaux restent dus sur le brut
            dividendes_net = benefice_distribuable - prelevements_sociaux - (impots_ir - self.calcul_impots_ir(tranches_ir))
            # impots_ir - self.calcul_impots_ir(tranches_ir) = part IR sur dividendes
            impots_flat_tax = 0.0  # pas de flat tax en barème
        return {
            'dividendes_net': dividendes_net,
            'dividendes_imposables': dividendes_imposables,
            'impots_ir': impots_ir,
            'impots_flat_tax': impots_flat_tax,
            'prelevements_sociaux': prelevements_sociaux,
            'base_ir_totale': base_ir_totale,
            'mode_imposition': mode_imposition,
        }
