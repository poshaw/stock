# src/logic/growth.py

from datetime import datetime

def calculate_cagr(series):
    """
    Expects a list of (date, value) tuples sorted with newest first.
    Returns CAGR as a decimal (e.g., 0.08 for 8%).
    """
    try:
        if len(series) < 2:
            return None

        # sort oldest to newest
        series.sort(key=lambda x: x[0])
        start_date, start_val = series[0]
        end_date, end_val = series[-1]

        if not (start_val and end_val) or start_val <= 0:
            return None

        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        years = (end_dt - start_dt).days / 365.25

        if years <= 0:
            return None

        return ((end_val / start_val) ** (1 / years)) - 1
    except Exception as e:
        print(f"[CAGR] Error calculating CAGR: {e}")
        return None
