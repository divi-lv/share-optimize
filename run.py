import json
from pathlib import Path

import pandas as pd
import numpy as np
import requests
from shapely.geometry import Point, Polygon

from app.evaluator import evaluator
from app.arcbuilder import arcbuilder
from app.solver import solver
from app.interpreter import interpreter

print('Loading data... ')
df = pd.read_excel('data/history.xlsx')
history_data = json.loads(df.to_json(orient='records', date_format='iso'))
sector_data = json.load(open('data/sectors.json'))['features']
def get_traffic_data():
    SECTORS = [
        {
            'id': sector['properties']['name'],
            'idx': idx,
            'lat': np.around(Polygon(
                sector['geometry']['coordinates'][0]
            ).centroid.coords[0][1], 5),
            'lng': np.around(Polygon(
                sector['geometry']['coordinates'][0]
            ).centroid.coords[0][0], 5),
        }
        for idx, sector in enumerate(
            json.load(open('data/sectors.json'))['features']
        )
    ]
    URL = ''.join([
        'http://router.project-osrm.org/table/v1/driving/',
        ';'.join([
            f'{sector["lat"]},{sector["lng"]}'
            for sector in SECTORS
        ]),
    ])

    TIME_DISTANCES = requests.get(url = URL).json()['durations']
    return np.array(TIME_DISTANCES) * 1.2 + 300
traffic_data = get_traffic_data()
vehicle_data = json.load(open('data/vehicles.json'))
relocator_data = json.load(open('data/relocators.json'))


print('Evaluating sectors... ')
profit_data = evaluator.evaluator(history_data, sector_data)


print('Generating arcs... ')
arc_data = arcbuilder.arcbuilder(
    sector_data,
    traffic_data,
    profit_data,
    [],
)


print('Initializing and running solver... ')
transcript, value = solver.solver(
    arc_data['data'],
    vehicle_data=vehicle_data,
    relocator_data=relocator_data,
)

print('Estimating base value... ')
_, base_value = solver.solver(
    arc_data['data'],
    vehicle_data=vehicle_data,
    relocator_data=json.loads('{"relocators": []}')
)

print('Interpreting results... ')
instructions = interpreter.interpreter(transcript)
for idx, v in enumerate(instructions['relocators']):
    print(f'\n=== Relocator {idx} ===')
    print(v)

for idx, v in enumerate(instructions['vehicles_x']):
    print(f'\n=== Vehicle x-{idx} ===')
    print(v)

for idx, v in enumerate(instructions['vehicles_z']):
    print(f'\n=== Vehicle z-{idx} ===')
    print(v)

print(f'=== Solution efficiency ===')
print(f'\nModel attained a value of {value} which is an improvement from the inactivity value of {base_value}')
