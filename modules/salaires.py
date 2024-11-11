from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List

import yaml

from modules.utils import calcul_impots_IR


@dataclass
class SalaireLog:
    salaire_super_brut: float = 0.0
    cotisations: float = 0.0
    salaire_net_avant_impot: float = 0.0
    impots_revenu: float = 0.0
    salaire_net_apres_impot: float = 0.0
    store_infos: List[str] = field(default_factory=list)

    def add_log(self, message: str):
        """Ajoute un message au log."""
        self.store_infos.append(message)


class SalairePresident(ABC):
    def __init__(self, salaire_super_brut, streamlit_output=None):
        with open("config/config.yaml", "r") as file:
            self.config_yaml = yaml.safe_load(file)

        self.log_data = SalaireLog(salaire_super_brut)

        self.streamlit_output = streamlit_output or []
        self.store_info("### Salaire")

    @abstractmethod
    def calcul_cotisations_sociales(self):
        pass

    @abstractmethod
    def calcul_impots_revenu(self, revenu_net_imposable):
        pass

    def calcul_salaire_net(self):
        pass

    def store_info(self, message):
        """Ajoute un message à la liste ou l'affiche selon le contexte Streamlit."""
        self.streamlit_output.append(message)
        self.log_data.add_log(message)


class SalaireSASU(SalairePresident):
    def __init__(self, salaire_brut):
        super().__init__(salaire_brut)

    def calcul_cotisations_sociales(self) -> float:
        cotisations_sociales = self.log_data.salaire_super_brut * 0.41
        return cotisations_sociales

    def calcul_impots_revenu(self, revenu_net_imposable) -> float:
        impots = calcul_impots_IR(self.config_yaml["tranches_IR"], revenu_net_imposable)
        return impots

    def calcul_salaire_net(self):
        self.store_info(f"Salaire super brut : :blue[{self.log_data.salaire_super_brut:.2f} €]")
        self.log_data.salaire_super_brut = self.log_data.salaire_super_brut

        cotisations = self.calcul_cotisations_sociales()
        self.store_info(f"Cotisations sociales : :red[{cotisations:.2f} €]")
        self.log_data.cotisations = round(cotisations,2)

        salaire_net_avant_impot = self.log_data.salaire_super_brut - cotisations
        self.store_info(f"Salaire net avant IR : {salaire_net_avant_impot:.2f} €")
        self.log_data.salaire_net_avant_impot = salaire_net_avant_impot

        impots_revenu = self.calcul_impots_revenu(salaire_net_avant_impot)
        self.store_info(f"Impôt sur le revenu : :red[{impots_revenu:.2f} €]")
        self.log_data.impots_revenu = impots_revenu

        salaire_net_apres_impot = salaire_net_avant_impot - impots_revenu
        self.store_info(f"Salaire net du président : :green[{salaire_net_apres_impot:.2f} €]")
        self.log_data.salaire_net_apres_impot = salaire_net_apres_impot
