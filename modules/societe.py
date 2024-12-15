from abc import ABC, abstractmethod
import numpy as np
import streamlit as st
import plotly.express as px

from modules.impot_societes import calcul_IS
from modules.impot_revenu import calcul_IR

class Societe(ABC):
    def __init__(self, ca_previsionnel, charges, remuneration_president, taux_cotisation):
        self.ca_previsionnel = ca_previsionnel
        self.charges = charges
        self.remuneration_president = remuneration_president
        self.taux_cotisation = taux_cotisation
        self.results: dict = {"SASU": {}, "EURL": {}}

    @abstractmethod
    def calcul_cotisations_president(self):
        pass

    def calcul_is(self, benefice_reel):
        return calcul_IS(benefice_reel)

    def calcul_benefice_reel(self):
        cotisations_president = self.calcul_cotisations_president()
        total_depenses_reelles = np.sum([self.charges, self.remuneration_president, cotisations_president])
        return self.ca_previsionnel - total_depenses_reelles, cotisations_president

    def calcul_impots_ir(self, tranches_ir):
        return calcul_IR(tranches_ir, self.remuneration_president)

    def calcul_total_impots(self, cotisations_president, impots_ir, impots_is):
        return np.sum([cotisations_president, impots_ir, impots_is])

    def display_text_results(self, benefice_reel, cotisations_president, impots_ir, impots_is, total_impots):
        logs = []
        logs.append("-----------------------------------------------------")
        logs.append(f"Chiffre d'affaires prévisionnel: {self.ca_previsionnel}")
        logs.append("-----------------------------------------------------")
        logs.append(f"Dépenses réelles: {self.charges}")
        logs.append(f"Rémunération président: {self.remuneration_president}")
        logs.append(f"Cotisations président: {cotisations_president}")
        logs.append(f"Total dépenses réelles: {self.charges + self.remuneration_president + cotisations_president}")
        logs.append("")
        logs.append("-----------------------------------------------------")
        logs.append(f"Bénéfice réel: {benefice_reel}")
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
        logs.append(f"Le chef d'entreprise touche un salaire de : {self.remuneration_president - impots_ir}")
        logs.append(f"Il reste {benefice_reel - impots_is} euros à distribuer")
        logs.append("-----------------------------------------------------\n")

        for log in logs:
            st.text(log)

class EURL(Societe):
    def calcul_cotisations_president(self):
        if self.remuneration_president < 1100:
            return 1100
        return self.remuneration_president * (self.taux_cotisation / 100)

class SASU(Societe):
    def calcul_cotisations_president(self):
        return self.remuneration_president * (self.taux_cotisation / 100)
