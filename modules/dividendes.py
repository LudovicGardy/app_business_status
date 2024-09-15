from abc import ABC, abstractmethod
import yaml

from modules.utils import calcul_impots_IR
class Dividendes(ABC):
    def __init__(
        self,
        dividendes_verses: float,
        type_societe: str,
        choix_fiscal: str,
        streamlit_output=None  # Ajout d'un argument pour capturer les messages
    ):
        with open("config/config.yaml", "r") as file:
            self.config_yaml = yaml.safe_load(file)

        self.dividendes_verses = dividendes_verses
        self.type_societe = type_societe
        self.choix_fiscal = choix_fiscal
        self.streamlit_output = streamlit_output or []  # Liste pour capturer les messages
        self.log_message("\n### Calcul des dividendes\n-------------------------")
        self.calcul_imposition()

    def log_message(self, message):
        """Ajoute un message à la liste ou l'affiche selon le contexte Streamlit."""
        self.streamlit_output.append(message)  # Capture les messages

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
        self.log_message(f"Prélèvement TMI (12,8%) : {tmi} €")

        # Imposition totale sous la flat tax
        self.imposition_totale = tmi + prelevements_sociaux_total
        self.dividendes_net = round(self.dividendes_verses - self.imposition_totale)  # Non imposable (flat tax)

        self.log_message(f"Imposition totale (flat tax) : {self.imposition_totale} €")
        self.log_message(f"Dividendes nets (flat tax) pour SASU : {self.dividendes_net} €")

        self.base_imposable = 0
        self.csg_deductible_amount = 0

    def calcul_prelevements_sociaux(self):
        """Calcul détaillé des prélèvements sociaux pour une SASU."""
        # Extraction des taux de prélèvements sociaux depuis le YAML
        prelevements_sociaux_data = self.config_yaml["SASU"]["dividendes"]["prelevements_sociaux"]
        csg_deductible = prelevements_sociaux_data[0]["CSG_deductible"] / 100
        csg_non_deductible = prelevements_sociaux_data[1]["CSG_non_deductible"] / 100
        crds = prelevements_sociaux_data[2]["CRDS"] / 100
        solidarite = prelevements_sociaux_data[3]["solidarite"] / 100

        # Calcul des différentes composantes des prélèvements sociaux
        csg_deductible_amount = self.dividendes_verses * csg_deductible
        csg_non_deductible_amount = self.dividendes_verses * csg_non_deductible
        crds_amount = self.dividendes_verses * crds
        solidarite_amount = self.dividendes_verses * solidarite

        # Total des prélèvements sociaux
        prelevements_sociaux_total = (
            csg_deductible_amount
            + csg_non_deductible_amount
            + crds_amount
            + solidarite_amount
        )

        self.log_message(f"Dividendes versés : {self.dividendes_verses} €")
        self.log_message(f"CSG déductible (6,8%) : {csg_deductible_amount} €")
        self.log_message(f"CSG non déductible (2,4%) : {csg_non_deductible_amount} €")
        self.log_message(f"CRDS (0,5%) : {crds_amount} €")
        self.log_message(f"Solidarité (7,5%) : {solidarite_amount} €")
        self.log_message(f"Total des prélèvements sociaux : {prelevements_sociaux_total} €")

        return prelevements_sociaux_total, csg_deductible_amount

    def calcul_bareme(self, test_scenario=False):   
        """Calcul des dividendes pour une SASU sous le régime du barème progressif."""
        # Prélèvements sociaux
        prelevements_sociaux_total, self.csg_deductible_amount = self.calcul_prelevements_sociaux()

        # Abattement de 40 % sur les dividendes versés
        abattement = self.dividendes_verses * 40 / 100
        self.base_imposable = self.dividendes_verses - abattement 
        self.log_message(f"Abattement (40%) : {abattement} €")
        self.log_message(f"Base imposable après abattement : {self.base_imposable} €")

        if test_scenario:
            # Application des tranches d'impôt sur le revenu (IR)
            impots_ir = calcul_impots_IR(self.config_yaml["tranches_IR"], self.base_imposable)
            impots_ir = round(impots_ir)
            self.log_message(f"Imposition via barème progressif pour SASU : {impots_ir} €")

            # Imposition totale en tenant compte de la CSG déductible
            self.imposition_totale = impots_ir + prelevements_sociaux_total - self.csg_deductible_amount
            self.dividendes_net = round(self.dividendes_verses - self.imposition_totale)

            self.log_message(f"Imposition totale (barème) : {self.imposition_totale} €")
            self.log_message(f"Dividendes nets (barème) pour SASU : {self.dividendes_net} €")
