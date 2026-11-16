import unittest
import numpy as np
from analysis import solve, simulate, SUPPLY

class AnalysisTests(unittest.TestCase):
    def test_optimal_objective_and_duality(self):
        r, d = solve()
        self.assertAlmostEqual(d['profit'],42142.85714285714,places=6)
        # Dual bound equals the primal objective; zero variable lower bounds.
        rhs=np.r_[SUPPLY,[35000,23000,0,0]]
        self.assertAlmostEqual(float(rhs @ r.ineqlin.marginals),r.fun,places=6)
    def test_extra_supply_cannot_reduce_optimum(self):
        _,base=solve()
        for i in range(4):
            supply=SUPPLY.copy();supply[i]+=2000
            _,case=solve(supply)
            self.assertGreaterEqual(case['profit']+1e-7,base['profit'])
    def test_zero_supply(self):
        # solve() emits undefined octane only for zero volumes; solver result remains feasible.
        with np.errstate(invalid='ignore'):
            _,d=solve(np.zeros(4))
        self.assertAlmostEqual(d['profit'],0)
    def test_seed_reproducible(self):
        x,_=simulate();y,_=simulate()
        np.testing.assert_array_equal(x,y)
    def test_simulation_mean_matches_analytic_expectation(self):
        _,d=simulate()
        # 4 standard errors allows ordinary sampling variation; clipping is negligible here.
        self.assertLess(abs(d['mean']-300000),4*d['sample_sd']/100)

if __name__=='__main__': unittest.main()
