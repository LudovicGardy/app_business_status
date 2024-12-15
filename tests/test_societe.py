import unittest
from modules.societe import Societe, EURL, SASU

class TestSociete(unittest.TestCase):

    def setUp(self):
        self.eurl = EURL(100000, 30000, 20000, 45)
        self.sasu = SASU(100000, 30000, 20000, 45)

    def test_calcul_cotisations_president_eurl(self):
        self.assertEqual(self.eurl.calcul_cotisations_president(), 9000)

    def test_calcul_cotisations_president_sasu(self):
        self.assertEqual(self.sasu.calcul_cotisations_president(), 9000)

    def test_calcul_benefice_reel_eurl(self):
        benefice_reel, cotisations_president = self.eurl.calcul_benefice_reel()
        self.assertEqual(benefice_reel, 41000)
        self.assertEqual(cotisations_president, 9000)

    def test_calcul_benefice_reel_sasu(self):
        benefice_reel, cotisations_president = self.sasu.calcul_benefice_reel()
        self.assertEqual(benefice_reel, 41000)
        self.assertEqual(cotisations_president, 9000)

    def test_calcul_is(self):
        self.assertEqual(self.eurl.calcul_is(41000), calcul_IS(41000))
        self.assertEqual(self.sasu.calcul_is(41000), calcul_IS(41000))

    def test_calcul_impots_ir(self):
        tranches_ir = [10000, 20000, 30000]
        self.assertEqual(self.eurl.calcul_impots_ir(tranches_ir), calcul_IR(tranches_ir, 20000))
        self.assertEqual(self.sasu.calcul_impots_ir(tranches_ir), calcul_IR(tranches_ir, 20000))

    def test_calcul_total_impots(self):
        cotisations_president = 9000
        impots_ir = 5000
        impots_is = 10000
        self.assertEqual(self.eurl.calcul_total_impots(cotisations_president, impots_ir, impots_is), 24000)
        self.assertEqual(self.sasu.calcul_total_impots(cotisations_president, impots_ir, impots_is), 24000)

if __name__ == '__main__':
    unittest.main()