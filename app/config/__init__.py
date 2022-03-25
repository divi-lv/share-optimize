import numpy as np

# Number of time instants
TS = 8

# Length of time instants in [s]
DELTA_T = 30 * 60

# Start and end times in [s]
START_TIME = 12 * 60 * 60
END_TIME = START_TIME + DELTA_T * TS

# List of time instants
TIME_INSTANTS = list(np.arange(
    START_TIME,
    END_TIME, 
    DELTA_T,
).astype(int))

# Day of week
WEEKDAY = 0