"""
Common utility functions for day count and rate-convention conversions.
"""

import pandas as pd
import calendar

def iseom(date):
    """Return whether a datetime.date is at month end."""
    y = date.year
    m = date.month
    return calendar.monthrange(y, m)[1] == date.day

def count_days(date_1, date_2, method='30I/360', T=None):
    """Compute day-count difference between two dates with a selected convention."""
    if (method == 'actual'):
        delta = date_2 - date_1
        return abs(delta.days)

    if (method == '30I/360'):
        y2 = date_2.year
        y1 = date_1.year
        m2 = date_2.month
        m1 = date_1.month
        d2 = date_2.day
        d1 = date_1.day
        if iseom(date_1):  # If D1 is last day of month...
            d1 = 30  # ... change D1 to 30
        # If D2 is last day of month and (date 2 is not maturity or M2 is not February)...
        if iseom(date_2) and (date_2 != T or m2 != 2):
            d2 = 30
        return abs(360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1))

    if (method == '30/360'):
        # TODO: add special cases here
        y2 = date_2.year
        y1 = date_1.year
        m2 = date_2.month
        m1 = date_1.month
        d2 = date_2.day
        d1 = date_1.day
        return abs(360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1))

    raise ValueError("Unsupported day-count method. Use 'actual', '30I/360', or '30/360'.")

def discount_from_zero(date_1, date_2, zero_rate, make_pct=True, met='30I/360', freq=2):
    """Convert a quoted zero rate into a discount factor."""
    if make_pct:
        zero_rate /= 100
    num_days = count_days(date_1, date_2, method=met, T=date_2)
    return 1 / (1 + zero_rate / freq) ** (freq * num_days / 360)

def forward_from_discount(discounts):
    """Return simple annualized forward rates (in percent) implied by discount factors."""
    if len(discounts) < 2:
        return pd.Series(dtype=float)

    values = []
    index = []
    for i in range(len(discounts) - 1):
        fwd_rate = (discounts.iloc[i] / discounts.iloc[i + 1] - 1) * 360 / count_days(discounts.index[i],
                                                                                      discounts.index[i + 1],
                                                                                      method='actual') * 100
        values.append(fwd_rate)
        index.append(discounts.index[i])

    return pd.Series(data=values, index=index, dtype=float)
