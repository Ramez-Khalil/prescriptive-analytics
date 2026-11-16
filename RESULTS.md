# Results and interpretation

## Optimization

An independent HiGHS solve reproduces the reported maximum daily contribution of **$42,142.86**, with 35,000 Regular and 16,428.57 Premium barrels, meeting octane minima of 89 and 93. A different allocation among raw materials reaches the same objective: do not describe the original allocation as uniquely optimal.

Adding 2,000 barrels of one raw input at a time, holding existing unit costs and other constraints fixed, produces these incremental daily contributions:

| Input | Incremental contribution |
|---|---:|
| Raw 1 | $0.00 |
| Raw 2 | $857.14 |
| Raw 3 | $1,571.43 |
| Raw 4 | $2,285.71 |

Raw 4 therefore has the largest tested benefit, under the tested assumptions. These values do not authorize a sourcing commitment and exclude additional acquisition costs. The coefficients are scenario assumptions, not current market prices.

## Simulation

New seeded run, not an attempt to replicate an unavailable old seed:

- Mean monthly contribution before fixed/launch costs: **$301,166.62**.
- Standard deviation: **$98,728.66**.
- 95% Monte Carlo interval for the mean: **$299,231.34â€“$303,101.90**.
- Central 95% simulated outcome range: **$134,814.11â€“$510,726.33**.

All 10,000 sampled contributions were positive, but this is neither a guarantee nor evidence that a real product launch is risk-free. At an illustrative $200,000 monthly fixed cost, 15.25% of sampled outcomes become losses; at $300,000, 52.96% become losses. These are sensitivity examples, not estimates of actual operating costs.

