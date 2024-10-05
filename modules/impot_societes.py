from abc import ABC, abstractmethod
import yaml

class ImpotSociete(ABC):
    def __init__(
        self,
        resultat_net_avant_impot: float,
        type_societe: str,
    ):
        with open("config/config.yaml", "r") as file:
            self.config_yaml = yaml.safe_load(file)

        print("\n### Calcul de l'impôt sur les sociétés\n-------------------------")
        self.resultat_net_avant_impot = resultat_net_avant_impot
        self.type_societe = type_societe

        # Appel à la méthode abstraite pour le calcul de l'IS
        self.calcul_impot()

    @abstractmethod
    def calcul_impot(self):
        """Méthode à implémenter pour le calcul de l'impôt en fonction du type de société."""
        pass

class ImpotSocieteSASU(ImpotSociete):
    def calcul_impot(self):
        """Calcul de l'impôt sur les sociétés pour une SASU selon les tranches IS."""
        tranches = self.config_yaml["SASU"]["tranches_IS"]
        self.impot_a_payer = 0
        for tranche in tranches:
            min_val, max_val, taux = tranche
            max_val = max_val if max_val != 'inf' else float('inf')  # Gestion de 'inf' dans le YAML
            if self.resultat_net_avant_impot > min_val:
                taxable_income = min(self.resultat_net_avant_impot, max_val) - min_val
                self.impot_a_payer += taxable_income * taux / 100
        self.impot_a_payer = round(self.impot_a_payer)
        print(f"Impôt sur les sociétés (SASU) : {self.impot_a_payer} €")

class ImpotSocieteEURL(ImpotSociete):
    def calcul_impot(self):
        """Calcul de l'impôt sur les sociétés pour une EURL."""
        tranches = self.config_yaml["SASU"]["tranches_IS"]  # Même tranches IS pour l'exemple
        self.impot_a_payer = 0
        for tranche in tranches:
            min_val, max_val, taux = tranche
            max_val = max_val if max_val != 'inf' else float('inf')
            if self.resultat_net_avant_impot > min_val:
                taxable_income = min(self.resultat_net_avant_impot, max_val) - min_val
                self.impot_a_payer += taxable_income * taux / 100
        self.impot_a_payer = round(self.impot_a_payer)
        print(f"Impôt sur les sociétés (EURL) : {self.impot_a_payer} €")