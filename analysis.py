"""Reproducible scenario analysis. Educational inputs, not business forecasts."""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog
from scipy.stats import t

OUT = Path(__file__).parent / 'outputs'
OUT.mkdir(exist_ok=True)
COST = np.array([17., 18., 20.5, 23.])
OCTANE = np.array([86., 88., 92., 96.])
SUPPLY = np.array([20000., 15000., 15000., 10000.])
PRICE = np.array([19.5, 22.])
DEMAND = np.array([35000., 23000.])
MIN_OCTANE = np.array([89., 93.])

def solve(supply=SUPPLY):
    # Variable order: raw1 Regular, raw1 Premium, raw2 Regular, ...
    margin = (PRICE[None, :] - COST[:, None]).ravel()
    A, b = [], []
    for i in range(4):
        row = np.zeros((4, 2)); row[i, :] = 1
        A.append(row.ravel()); b.append(supply[i])
    for j in range(2):
        row = np.zeros((4, 2)); row[:, j] = 1
        A.append(row.ravel()); b.append(DEMAND[j])
    for j in range(2):
        row = np.zeros((4, 2)); row[:, j] = MIN_OCTANE[j] - OCTANE
        A.append(row.ravel()); b.append(0)
    A, b = np.array(A), np.array(b)
    result = linprog(-margin, A_ub=A, b_ub=b, bounds=(0, None), method='highs')
    assert result.success, result.message
    x = result.x.reshape(4, 2)
    assert np.all(x >= -1e-7)
    assert np.max(A @ result.x - b) < 1e-6
    volume = x.sum(axis=0)
    return result, {
        'allocation_by_raw_regular_premium': x.tolist(),
        'volumes': volume.tolist(),
        'blended_octane': ((x * OCTANE[:, None]).sum(axis=0) / volume).tolist(),
        'supply_used': x.sum(axis=1).tolist(),
        'profit': float(-result.fun),
        'revenue': float(volume @ PRICE),
        'input_cost': float(x.sum(axis=1) @ COST),
        'constraint_slack': result.ineqlin.residual.tolist(),
        'local_profit_value_per_extra_unit_constraint': (-result.ineqlin.marginals).tolist(),
        'solver': result.message,
    }

def simulate(n=10000, seed=20261116):
    rng = np.random.default_rng(seed)
    demand = np.maximum(rng.normal(10000, 2000, n), 0)
    price = rng.uniform(50, 70, n)
    unit_cost = np.maximum(rng.normal(30, 5, n), 0)
    contribution = demand * (price - unit_cost)
    mean = contribution.mean(); sd = contribution.std(ddof=1)
    half = t.ppf(.975, n-1) * sd / np.sqrt(n)
    return contribution, {
        'seed': seed, 'scenarios': n, 'mean': float(mean), 'sample_sd': float(sd),
        'sample_min': float(contribution.min()), 'sample_max': float(contribution.max()),
        'mean_monte_carlo_95_ci': [float(mean-half), float(mean+half)],
        'scenario_2_5_and_97_5_percentiles': np.quantile(contribution,[.025,.975]).tolist(),
        'fraction_positive': float((contribution>0).mean()),
        'fraction_above_200000': float((contribution>200000).mean()),
        'fraction_above_400000': float((contribution>400000).mean()),
        'fixed_cost_scenarios': [
            {'monthly_fixed_cost': fixed, 'mean_net_after_fixed_cost': float(mean-fixed),
             'fraction_net_loss': float((contribution-fixed<0).mean())}
            for fixed in [0,100000,200000,300000]],
        'interpretation': 'Simulated contribution before fixed/launch costs; independent inputs; zero-clipped normal demand and costs. CI measures simulation precision conditional on assumed distributions, not business uncertainty.'
    }

def main():
    _, base = solve()
    assert abs(base['profit'] - 42142.85714285714) < 1e-5
    sensitivity = []
    for i in range(4):
        s = SUPPLY.copy(); s[i] += 2000
        _, case = solve(s)
        sensitivity.append({'raw_input':i+1,'extra_barrels':2000,
                            'profit_gain':case['profit']-base['profit'],
                            'new_volumes':case['volumes']})
    # Check the reported rounded solution without claiming it is the only optimum.
    reported = np.array([[11428.57,0],[9107.14,5892.86],[14464.29,535.71],[0,10000]])
    reported_profit = float((reported*(PRICE[None,:]-COST[:,None])).sum())
    assert np.all(reported >= 0)
    assert np.all(reported.sum(axis=1) <= SUPPLY + .02)
    assert np.all(reported.sum(axis=0) <= DEMAND + .02)
    assert np.all((reported * (OCTANE[:,None]-MIN_OCTANE[None,:])).sum(axis=0) >= -.02)
    assert abs(reported_profit-base['profit']) < .02
    values, mc = simulate()
    again, _ = simulate(); assert np.array_equal(values, again)
    assert mc['mean_monte_carlo_95_ci'][0] < mc['mean'] < mc['mean_monte_carlo_95_ci'][1]
    assert mc['scenario_2_5_and_97_5_percentiles'][1] > mc['mean_monte_carlo_95_ci'][1]
    output = {'optimization':base,'supply_sensitivity':sensitivity,
              'reported_rounded_allocation_profit':reported_profit,'simulation':mc,
              'checks':'Solver feasible/optimal; supply/demand/octane/nonnegativity checked; reference objective checked; seeded reproducibility checked.'}
    (OUT/'results.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    np.savetxt(OUT/'simulation.csv',values,header='simulated_monthly_contribution',comments='')
    counts, bins = np.histogram(values,bins=25)
    bars=''.join(f'<rect x="{60+i*28}" y="{340-250*c/max(counts)}" width="25" height="{250*c/max(counts)}" fill="#176b73"/>' for i,c in enumerate(counts))
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="420"><rect width="820" height="420" fill="#f7f9fb"/><text x="40" y="35" font-family="Arial" font-size="23">Simulated monthly contribution</text><text x="40" y="60" font-family="Arial" font-size="14">10,000 scenarios | seed 20261116 | before fixed and launch costs</text>{bars}<path d="M60 340H760" stroke="#333"/><text x="60" y="368" font-family="Arial">${bins[0]:,.0f}</text><text x="660" y="368" font-family="Arial">${bins[-1]:,.0f}</text><text x="40" y="403" font-family="Arial" font-size="13">Illustrative assumptions, not an actual company forecast.</text></svg>'
    (OUT/'contribution-distribution.svg').write_text(svg,encoding='utf-8')
    print(json.dumps(output,indent=2))

if __name__ == '__main__': main()
