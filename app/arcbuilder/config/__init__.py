def TIME_INCREASE(TIME_DISTANCES):
    return TIME_DISTANCES * 1.2 + 5 * 60

# Value of one percent battery charge in EUR cents
ALPHA = 12.5

W_PROFIT_TYPE = 'end' # ['end', 'all']

# Cost of relocation in EUR cents per second
RELOCATION_COST = 0.05

# Maximum allowed time to spend on one arc in [min]
TIME_LIMIT = 30

CHARGERS = [
    'Olimpia',
    'Akropole',
]