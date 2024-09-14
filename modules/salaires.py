from abc import ABC, abstractmethod
import yaml

from modules.utils import calcul_impots_IR

# Classe abstraite pour la structure des présidents de sociétés
class SalairePresident(ABC):
    def __init__(self, salaire_brut):
        self.salaire_brut = salaire_brut

        with open("../config/config.yaml", "r") as file:
            self.config_yaml = yaml.safe_load(file)

    @abstractmethod
    def calcul_cotisations_sociales(self):
        pass

    @abstractmethod
    def calcul_impots_revenu(self, revenu_net_imposable):
        pass

    def calcul_salaire_net(self):
        # Calcul des cotisations sociales
        cotisations = self.calcul_cotisations_sociales()
        
        # Calcul du salaire net avant impôt
        salaire_net_avant_impot = self.salaire_brut - cotisations
        
        # Calcul des impôts en fonction du salaire net imposable
        impots = self.calcul_impots_revenu(salaire_net_avant_impot)
        
        # Calcul du salaire net après impôt
        salaire_net_apres_impot = salaire_net_avant_impot - impots
        
        return salaire_net_apres_impot

# Implémentation pour un président de SASU
class SalaireSASU(SalairePresident):
    def __init__(self, salaire_brut):
        super().__init__(salaire_brut)

    def calcul_cotisations_sociales(self):
        # Les cotisations sociales pour un président de SASU sont d'environ 41%
        cotisations_sociales = self.salaire_brut * 0.41
        return cotisations_sociales

    def calcul_impots_revenu(self, revenu_net_imposable):
        # Calcul de l'impôt sur le revenu en fonction du salaire net avant impôt
        impots = calcul_impots_IR(self.config_yaml['tranches_IR'], revenu_net_imposable)
        return impots