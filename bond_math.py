"""Bond math helpers for fixed-income securities."""

import numpy as np
import pandas as pd

def coupon_freq_mat(c, T, ytm, fv=100, k=1, summary_table=True):
    """Compute price, duration, and convexity for a coupon bond."""
    if k <= 0:
        raise ValueError("k must be strictly positive.")
    if T <= 0:
        raise ValueError("T must be strictly positive.")

    periods = int(round(k * T))
    coupon = c * fv / k
    payment_times = np.arange(1, periods + 1)
    cashflows = np.full(periods, coupon, dtype=float)
    cashflows[-1] += fv

    disc = (1 + ytm / k) ** payment_times
    pv_cashflows = cashflows / disc
    price = float(pv_cashflows.sum())

    times_years = payment_times / k
    d_mac = float((times_years * pv_cashflows).sum() / price)
    d_mod = d_mac / (1 + ytm / k)
    conv = float((times_years * (times_years + 1 / k) * pv_cashflows).sum() / (price * (1 + ytm / k) ** 2))

    summary = pd.DataFrame([{
        'Coupon': coupon,
        'DCF': price,
        'Macaulay duration': d_mac,
        'Modified duration': d_mod,
        'Dollar duration': d_mod * price / 100,
        'Convexity': conv,
        'Dollar convexity': conv * price / 100,
    }])
    if summary_table:
        print(summary)
    return summary

def amortization_table(c, T, ytm, fv=100, k=1, summary_table=True):
    """Build a bond amortization schedule using the effective-interest method."""
    if k <= 0:
        raise ValueError("k must be strictly positive.")
    if T <= 0:
        raise ValueError("T must be strictly positive.")

    periods = int(round(k * T))
    coupon = c * fv / k

    cashflows = np.full(periods, coupon, dtype=float)
    cashflows[-1] += fv
    period_rate = ytm / k
    discount = (1 + period_rate) ** np.arange(1, periods + 1)
    beginning_balance = float((cashflows / discount).sum())

    rows = []
    current_balance = beginning_balance
    for period in range(1, periods + 1):
        interest_income = current_balance * period_rate
        amortization = interest_income - coupon
        ending_balance = current_balance + amortization
        rows.append({
            'Period': period,
            'Beginning balance': current_balance,
            'Coupon payment': coupon,
            'Interest at YTM': interest_income,
            'Amortization': amortization,
            'Ending balance': ending_balance,
        })
        current_balance = ending_balance

    table = pd.DataFrame(rows)
    if summary_table:
        print(table)
    return table

def coupon_continuous(c, T, ytm, fv=100):
    """Compute price and duration for a bond discounted with continuous compounding."""
    if T <= 0:
        raise ValueError("T must be strictly positive.")

    periods = int(round(T))
    coupon = c * fv
    times = np.arange(1, periods + 1)
    cashflows = np.full(periods, coupon, dtype=float)
    cashflows[-1] += fv

    pv_cashflows = cashflows * np.exp(-ytm * times)
    price = float(pv_cashflows.sum())
    macaulay_duration = float((times * pv_cashflows).sum() / price)
    return {
        'Coupon': coupon,
        'DCF': price,
        'Macaulay duration': macaulay_duration,
    }

def dcf(cf, ytm=None, r=None, times=None):
    """Discount a cash-flow vector with either a scalar YTM or per-period rates."""
    pv = 0
    if r is None:
        if ytm is None:
            raise ValueError("Provide either ytm or r.")
        r = np.repeat(ytm, cf.shape[0])
    if times is None:
        times = np.array(range(1, cf.shape[0] + 1))
    for rate, payment, t in zip(r, cf, times):
        pv += payment / (1 + rate)**t
    return pv
