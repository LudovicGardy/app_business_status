from abc import ABC, abstractmethod
import yaml

class Dividendes(ABC):
    def __init__(
        self,
        dividendes_verses: float,
        type_societe: str,
        choix_fiscal: str 
    ):
        with open("../config/config.yaml", "r") as file:
            self.config_yaml = yaml.safe_load(file)

        print("\n### Calcul des dividendes\n-------------------------")
        self.dividendes_verses = dividendes_verses
        self.type_societe = type_societe
        self.choix_fiscal = choix_fiscal
        self.calcul_imposition()

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
        print(f"Prélèvement TMI (12,8%) : {tmi} €")

        # Imposition totale sous la flat tax
        self.imposition_totale = tmi + prelevements_sociaux_total
        self.dividendes_net = round(self.dividendes_verses - self.imposition_totale)  # Non imposable (flat tax)

        print(f"Imposition totale (flat tax) : {self.imposition_totale} €")
        print(f"Dividendes nets (flat tax) pour SASU : {self.dividendes_net} €")

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

        print(f"Dividendes versés : {self.dividendes_verses} €")
        print()
        print(f"CSG déductible (6,8%) : {csg_deductible_amount} €")
        print(f"CSG non déductible (2,4%) : {csg_non_deductible_amount} €")
        print(f"CRDS (0,5%) : {crds_amount} €")
        print(f"Solidarité (7,5%) : {solidarite_amount} €")
        print(f"Total des prélèvements sociaux : {prelevements_sociaux_total} €")

        return prelevements_sociaux_total, csg_deductible_amount

    def calcul_bareme(self, test_scenario=False):   
        """Calcul des dividendes pour une SASU sous le régime du barème progressif."""
        # Prélèvements sociaux
        prelevements_sociaux_total, self.csg_deductible_amount = self.calcul_prelevements_sociaux()

        # Abattement de 40 % sur les dividendes versés
        abattement = self.dividendes_verses * 40 / 100
        self.base_imposable = self.dividendes_verses - abattement 
        print(f"Abattement (40%) : {abattement} €")
        print(f"Base imposable après abattement : {self.base_imposable} €")

        if test_scenario:
            # Application des tranches d'impôt sur le revenu (IR)
            impots_ir = calcul_impots_IR(self.config_yaml["tranches_IR"],self.base_imposable)
            impots_ir = round(impots_ir)
            print(f"Imposition via barème progressif pour SASU : {impots_ir} €")

            # Imposition totale en tenant compte de la CSG déductible
            self.imposition_totale = impots_ir + prelevements_sociaux_total - self.csg_deductible_amount
            self.dividendes_net = round(self.dividendes_verses - self.imposition_totale)

            print(f"Imposition totale (barème) : {self.imposition_totale} €")
            print(f"Dividendes nets (barème) pour SASU : {self.dividendes_net} €")