import numpy as np
from lottery_statistical_forensics.analysis import marginal_test,pair_test
from lottery_statistical_forensics.rules import resolve_rule

def test_injected_bias_detected():
    _,m=resolve_rule("lotto")
    d=np.tile(np.arange(1,7),(100,1))
    assert marginal_test(d,m)["p_value"]<1e-9

def test_pair_analysis_runs():
    _,m=resolve_rule("lotto")
    d=np.array([[1,2,3,4,5,6],[7,8,9,10,11,12],[13,14,15,16,17,18],[19,20,21,22,23,24]])
    result=pair_test(d,m)
    assert "p_value" in result
