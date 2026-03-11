# Fixed-Income
Methods and Classes useful when dealing with Fixed-Income Securities

## What is included
- `bond_math.py`: discounted cash-flow math, bond duration/convexity, and amortization helpers.
- `trees.py`: short-rate tree calibration and backward-induction security pricing.
- `securities.py`: security classes designed to plug into tree pricing (currently a self-amortizing mortgage).
- `black_prices.py`: closed-form caplet valuation functions (Black and Hull-White variants).
- `prepayment.py`: prepayment hazard/survival likelihood functions and gradients.
- `utils.py`: day-count and discount/forward-rate utilities.
- `monte_carlo.py`: placeholder module for future simulation methods.

## Quick start
```bash
python -m venv .venv
.venv\Scripts\activate
pip install numpy pandas scipy python-dateutil
```

Example usage:
```python
from Fixed_Income.bond_math import coupon_freq_mat
summary = coupon_freq_mat(c=0.05, T=5, ytm=0.045, fv=100, k=2, summary_table=False)
print(summary)
```

