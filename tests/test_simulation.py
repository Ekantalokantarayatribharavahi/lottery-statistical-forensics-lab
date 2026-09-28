import numpy as np
from lottery_statistical_forensics.rules import resolve_rule
from lottery_statistical_forensics.simulation import simulate_draws

def test_simulation_shape_range_and_uniqueness():
    _,m=resolve_rule("lotto")
    d=simulate_draws(m,500,7)
    assert d.shape==(500,6)
    assert np.all((d>=1)&(d<=52))
    assert all(len(set(r))==6 for r in d)

def test_seed_reproducible():
    _,m=resolve_rule("lotto")
    assert np.array_equal(simulate_draws(m,20,1),simulate_draws(m,20,1))
