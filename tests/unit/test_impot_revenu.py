import pytest
from src.impot_revenu import calcul_IR

def test_calcul_IR_no_tax():
    tranches_ir = [(0, 10000, 0), (10000, 25000, 10), (25000, 50000, 20)]
    base_imposable = 5000
    assert calcul_IR(tranches_ir, base_imposable) == 0

def test_calcul_IR_single_tranche():
    tranches_ir = [(0, 10000, 0), (10000, 25000, 10), (25000, 50000, 20)]
    base_imposable = 15000
    assert calcul_IR(tranches_ir, base_imposable) == 500

def test_calcul_IR_multiple_tranches():
    tranches_ir = [(0, 10000, 0), (10000, 25000, 10), (25000, 50000, 20)]
    base_imposable = 30000
    assert calcul_IR(tranches_ir, base_imposable) == 2500

def test_calcul_IR_above_all_tranches():
    tranches_ir = [(0, 10000, 0), (10000, 25000, 10), (25000, 50000, 20)]
    base_imposable = 60000
    assert calcul_IR(tranches_ir, base_imposable) == 6500

def test_calcul_IR_edge_case():
    tranches_ir = [(0, 10000, 0), (10000, 25000, 10), (25000, 50000, 20)]
    base_imposable = 25000
    assert calcul_IR(tranches_ir, base_imposable) == 1500