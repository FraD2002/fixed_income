"""
Security definitions used by the fixed-income pricing utilities.
"""

from __future__ import annotations

import numpy as np


class SelfAmortizingMortgage:
    def __init__(self, dates=None, early=False, rate=5.5 / 100, T=6, N=100):
        """Create a level-payment self-amortizing mortgage.

        Inputs:
        - early: whether prepayment is allowed
        - T: maturity in years (number of payment periods)
        - N: face value (principal)
        - rate: yearly interest rate
        - dates: optional payment dates as a 1D numpy array
        """
        if T <= 0:
            raise ValueError("T must be positive.")

        self.T = int(T)
        self.early = bool(early)
        self.rate = float(rate)
        if dates is None:
            self.dates = np.arange(1, self.T + 1)
        else:
            self.dates = np.asarray(dates)

        if self.dates.ndim != 1:
            raise ValueError("dates must be a one-dimensional array.")
        if self.dates.size != self.T:
            raise ValueError("dates length must match T.")

        # Coupon chosen to set value N at time 0 for the quoted mortgage rate.
        self.coupon = N / sum(1 / pow(1 + self.rate, i) for i in range(1, self.T + 1))
        if self.early:
            self._compute_balance(N)

    def get_cf(self, t, r, *args, **kwargs):
        """Return scheduled mortgage cash flow at a given (time, rate) node."""
        return self.coupon

    def exercise_early(self, current_value, val_if_exercise_early, t, r):
        """Return True if early exercise should be taken."""
        if not self.early:
            print("WARNING: this should not be called when early exercise is not allowed.")
            return False
        return current_value > val_if_exercise_early

    def _compute_balance(self, N):
        """Compute principal balance, interest, and principal legs for each payment."""
        bal_st = [N]
        interest = []
        princ = []
        for i in range(self.T + 1):  # for each payment until maturity
            interest.append(bal_st[i] * self.rate)
            princ.append(self.coupon - interest[i])
            if i < self.T:
                bal_st.append(bal_st[i] - self.coupon + interest[i])
        self.balances = bal_st
        self.interest = interest
        self.princ = princ

    def cf_early_exercise(self, t, r):
        """Return payoff if prepayment is exercised at time t."""
        if not hasattr(self, "balances"):
            raise ValueError("No balances available. Initialize with early=True to enable prepayment.")

        # Borrower prepays remaining principal and skips future scheduled payments.
        return self.balances[t]

    def get_raw_cf_mat(self, interest_rate_tree, *args, **kwargs):
        """Build the security payoff matrix with same horizon as the input rate tree."""
        payoff_mat = np.zeros((interest_rate_tree.shape[0] + 1, interest_rate_tree.shape[0] + 1))
        for time in reversed(range(1, payoff_mat.shape[0])):
            for node in range(time + 1):
                payoff_mat[node, time] = self.get_cf(time, interest_rate_tree[max(node - 1, 0), time - 1],
                                                     *args, **kwargs)
        return payoff_mat
