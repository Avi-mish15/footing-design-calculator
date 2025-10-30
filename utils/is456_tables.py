"""
IS 456:2000 Table 19 helper – τc values and utilities.
Used for footing design checks (Module V).
"""
import math

TAU_C_TABLE = {
    15: [0.28, 0.36, 0.44, 0.52, 0.60],
    20: [0.29, 0.36, 0.43, 0.50, 0.57],
    25: [0.29, 0.36, 0.42, 0.49, 0.56],
    30: [0.30, 0.36, 0.42, 0.48, 0.54],
    35: [0.30, 0.35, 0.41, 0.47, 0.53],
    40: [0.31, 0.35, 0.40, 0.46, 0.52],
}
PERC_STEEL = [0.15, 0.25, 0.50, 0.75, 1.0]

def get_tau_c(fck, p):
    """Interpolate tau_c from IS 456 Table 19 safely (handles equal fck)"""
    fck_list = sorted(TAU_C_TABLE.keys())
    fck_low = max([f for f in fck_list if f <= fck])
    fck_high = min([f for f in fck_list if f >= fck])
    vals_low = TAU_C_TABLE[fck_low]
    vals_high = TAU_C_TABLE[fck_high]

    # Interpolate along p (percentage steel)
    for i in range(len(PERC_STEEL) - 1):
        if PERC_STEEL[i] <= p <= PERC_STEEL[i + 1]:
            p1, p2 = PERC_STEEL[i], PERC_STEEL[i + 1]
            tau_low = vals_low[i] + (vals_low[i + 1] - vals_low[i]) * (p - p1) / (p2 - p1)
            tau_high = vals_high[i] + (vals_high[i + 1] - vals_high[i]) * (p - p1) / (p2 - p1)
            # Avoid divide-by-zero if fck matches a table grade exactly
            if fck_high == fck_low:
                return tau_low
            return tau_low + (tau_high - tau_low) * (fck - fck_low) / (fck_high - fck_low)
    return vals_low[0]



def round_to_0_1(x):
    return round(x * 10) / 10.0

def round_to_10(x):
    return math.ceil(x / 10.0) * 10
