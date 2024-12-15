import pytest
from modules.impot_societes import calcul_IS

def test_calcul_IS_tranche1():
    assert calcul_IS(30000) == 4500.0  # 30000 * 0.15

def test_calcul_IS_tranche1_limite():
    assert calcul_IS(42500) == 6375.0  # 42500 * 0.15

def test_calcul_IS_tranche2():
    assert calcul_IS(50000) == 8250.0  # (42500 * 0.15) + (7500 * 0.25)

def test_calcul_IS_zero_benefice():
    assert calcul_IS(0) == 0.0

def test_calcul_IS_negative_benefice():
    assert calcul_IS(-10000) == -1500.0  # -10000 * 0.15