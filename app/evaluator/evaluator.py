import json

import pandas as pd
import numpy as np
from shapely.geometry import Point, Polygon
from tqdm import tqdm
from scipy.ndimage import gaussian_filter

from . import config as config

def evaluator(history_data, sector_data):
    # Prepare sector data
    SECTORS = [
        {
            'id': sector['properties']['name'],
            'polygon': Polygon(sector['geometry']['coordinates'][0]),
            'capacity': 10,
            'profit': np.zeros((7, config.TN)),
            'total_count': np.ones((7, config.TN)),
            'count': np.zeros((7, config.TN)),
        }
        for sector in sector_data
    ]

    # Prepare history data
    df = pd.read_json(json.dumps(history_data), orient='records')
    df['wait_time'] = (df['rental_start_time'] - df['device_placement_time'])
    df['wait_time'] = df['wait_time'].apply(lambda x: int((x.seconds) / (24 * 3600 / config.TN)))
    df['weekday'] = df['device_placement_time'].apply(lambda x: x.weekday())
    df['device_placement_time'] = df['device_placement_time'].apply(
        lambda x: int((x.hour * 3600 + x.minute * 60 + x.second) / (24 * 3600 / config.TN)) % config.TN
    )
    df = df[[
        'rental_start_lat',
        'rental_start_lng',
        'device_placement_time',
        'total',
        'wait_time',
        'weekday',
    ]]

    # Count profit and utility
    for row in df.iterrows():
        row = row[1]
        point = Point(row['rental_start_lng'], row['rental_start_lat'])
        sector = None
        for i in SECTORS:
            if i['polygon'].contains(point):
                sector = i['id']
                break
        if sector == None:
            continue
        for t in range(int(row['wait_time'] + 1)):
            hour = int((row['device_placement_time'] + t) % config.TN)
            weekday = int((row['weekday'] + int((row['device_placement_time'] + t) / config.TN)) % 7)
            i['total_count'][weekday][hour] += 1
        t = row['wait_time']
        hour = int((row['device_placement_time'] + t) % config.TN)
        weekday = int((row['weekday'] + int((row['device_placement_time'] + t) / config.TN)) % 7)
        i['profit'][weekday][hour] += row['total']
        i['count'][weekday][hour] += 1

    # Compile data and return it
    return {
        'tn': config.TN,
        'dt': 3600 * 24 / config.TN,
        'sectors': {
            i['id']: {
                'profit': [
                    list(np.around(gaussian_filter(
                        i['profit'][day] / i['total_count'][day],
                        sigma=6*config.TN/96,
                        mode='wrap',
                    ), 2))
                    for day in range(0, 7)
                ],
                'utility': [
                    list(np.around(gaussian_filter(
                        i['count'][day] / i['total_count'][day],
                        sigma=6*config.TN/96,
                        mode='wrap',
                    ), 2))
                    for day in range(0, 7)
                ]
            }
            for i in SECTORS
        },
    }