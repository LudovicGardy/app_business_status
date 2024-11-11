from dataclasses import dataclass, field
from typing import List
from abc import ABC, abstractmethod
import yaml

from modules.utils import calcul_impots_IR

@dataclass
class DividendLog:
    dividendes_verses: float
    tmi: float = 0.0
    imposition_totale: float = 0.0
    dividendes_net: float = 0.0
    base_imposable: float = 0.0
    csg_deductible_amount: float = 0.0
    prelevements_sociaux_total: float = 0.0
    csg_non_deductible_amount: float = 0.0
    crds_amount: float = 0.0
    solidarite_amount: float = 0.0
    abattement: float = 0.0
    impots_ir: float = 0.0
    store_infos: List[str] = field(default_factory=list)

    def add_log(self, message: str):
        """Ajoute un message au log."""
        self.store_infos.append(message)

class Dividendes(ABC):
    def __init__(
        self,
        dividendes_verses: float,
        type_societe: str,
        choix_fiscal: str,
        streamlit_output=None 
    ):
        with open("config/config.yaml", "r") as file:
            self.config_yaml = yaml.safe_load(file)

        # Initialise l'objet DividendLog pour stocker les résultats
        self.log_data = DividendLog(dividendes_verses=dividendes_verses)
        self.dividendes_verses = dividendes_verses
        self.type_societe = type_societe
        self.choix_fiscal = choix_fiscal
        self.streamlit_output = streamlit_output or []
        self.store_info("### Dividendes")
        self.calcul_imposition()

    def store_info(self, message):
        """Ajoute un message à la liste ou l'affiche selon le contexte Streamlit."""
        self.streamlit_output.append(message)
        self.log_data.add_log(message)

    @abstractmethod
    def calcul_imposition(self):
        """Méthode à implémenter pour calculer les charges spécifiques."""
        pass

class DividendesSASU(Dividendes):
    def calcul_imposition(self):
        """Calcul des dividendes en fonction du choix fiscal pour une SASU."""
        if self.choix_fiscal == "flat_tax":
            self.calcul_flat_tax()
        elif self.choix_fiscal == "bareme":
            self.calcul_bareme()

    def calcul_flat_tax(self):
        """Calcul des dividendes pour une SASU sous le régime de la flat tax."""
        prelevements_sociaux_total, _ = self.calcul_prelevements_sociaux()

        # Prélèvement de 12,8 % sur les dividendes pour l'impôt sur le revenu (TMI)
        tmi = self.dividendes_verses * self.config_yaml["SASU"]["dividendes"]["TMI"] / 100
        self.store_info(f"Prélèvement TMI (12,8%) : {tmi} €")
        self.log_data.tmi = tmi

        # Imposition totale sous la flat tax
        self.imposition_totale = tmi + prelevements_sociaux_total
        self.log_data.imposition_totale = self.imposition_totale
        self.dividendes_net = round(self.dividendes_verses - self.imposition_totale)  
        self.log_data.dividendes_net = self.dividendes_net

        self.store_info(f"Imposition totale (flat tax) : :red[{self.imposition_totale:.2f} €]")
        self.store_info(f"Dividendes nets (flat tax) pour SASU : :green[{self.dividendes_net:.2f} €]")

        # La base imposable est de 0 sous flat tax
        self.log_data.base_imposable = 0
        self.log_data.csg_deductible_amount = 0

    def calcul_prelevements_sociaux(self):
        """Calcul détaillé des prélèvements sociaux pour une SASU."""
        prelevements_sociaux_data = self.config_yaml["SASU"]["dividendes"]["prelevements_sociaux"]
        csg_deductible = prelevements_sociaux_data[0]["CSG_deductible"] / 100
        csg_non_deductible = prelevements_sociaux_data[1]["CSG_non_deductible"] / 100
        crds = prelevements_sociaux_data[2]["CRDS"] / 100
        solidarite = prelevements_sociaux_data[3]["solidarite"] / 100

        csg_deductible_amount = self.dividendes_verses * csg_deductible
        csg_non_deductible_amount = self.dividendes_verses * csg_non_deductible
        crds_amount = self.dividendes_verses * crds
        solidarite_amount = self.dividendes_verses * solidarite

        prelevements_sociaux_total = (
            csg_deductible_amount
            + csg_non_deductible_amount
            + crds_amount
            + solidarite_amount
        )

        # Log et stockage des prélèvements sociaux
        self.store_info(f"Dividendes versés : :blue[{self.dividendes_verses:.2f} €]")
        self.store_info(f"CSG déductible (6,8%) : {csg_deductible_amount:.2f} €")
        self.store_info(f"CSG non déductible (2,4%) : {csg_non_deductible_amount:.2f} €")
        self.store_info(f"CRDS (0,5%) : {crds_amount:.2f} €")
        self.store_info(f"Solidarité (7,5%) : {solidarite_amount:.2f} €")
        self.store_info(f"Total des prélèvements sociaux : {prelevements_sociaux_total:.2f} €")

        # Stockage dans la dataclass
        self.log_data.csg_deductible_amount = csg_deductible_amount
        self.log_data.csg_non_deductible_amount = csg_non_deductible_amount
        self.log_data.crds_amount = crds_amount
        self.log_data.solidarite_amount = solidarite_amount
        self.log_data.prelevements_sociaux_total = prelevements_sociaux_total

        return prelevements_sociaux_total, csg_deductible_amount

    def calcul_bareme(self, test_scenario=False):
        """Calcul des dividendes pour une SASU sous le régime du barème progressif."""
        prelevements_sociaux_total, self.csg_deductible_amount = self.calcul_prelevements_sociaux()

        abattement = self.dividendes_verses * 40 / 100
        self.base_imposable = self.dividendes_verses - abattement 
        self.store_info(f"Abattement (40%) : {abattement:.2f} €")
        self.store_info(f"Base imposable après abattement : {self.base_imposable:.2f} €")

        self.log_data.abattement = abattement
        self.log_data.base_imposable = self.base_imposable

        if test_scenario:
            # Application des tranches d'impôt sur le revenu (IR)
            impots_ir = calcul_impots_IR(self.config_yaml["tranches_IR"], self.base_imposable)
            impots_ir = round(impots_ir)
            self.store_info(f"Imposition via barème progressif pour SASU : {impots_ir:.2f} €")
            self.log_data.impots_ir = impots_ir

            # Imposition totale en tenant compte de la CSG déductible
            self.imposition_totale = impots_ir + prelevements_sociaux_total - self.csg_deductible_amount
            self.dividendes_net = round(self.dividendes_verses - self.imposition_totale)

            self.store_info(f"Imposition totale (barème) : {self.imposition_totale:.2f} €")
            self.store_info(f"Dividendes nets (barème) pour SASU : {self.dividendes_net:.2f} €")

            self.log_data.imposition_totale = self.imposition_totale
            self.log_data.dividendes_net = self.dividendes_net
