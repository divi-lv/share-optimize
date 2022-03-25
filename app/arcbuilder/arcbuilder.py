import json

import numpy as np
from shapely.geometry import Point, Polygon

import app.config as config
import app.arcbuilder.config as lconfig

def arcbuilder(
    sector_data,
    traffic_data,
    profit_data,
    cluster_data
):
    SECTORS = [
        {
            'id': sector['properties']['name'],
            'idx': idx,
            'capacity': 5,
            'power': 100 / (2 * 60 * 60) if (
                sector['properties']['name'] in lconfig.CHARGERS
            ) else 0,
        }
        for idx, sector in enumerate(
            sector_data
        )
    ]
    PROFIT_DT = profit_data['dt']
    PROFITS = profit_data['sectors']

    def generate_arcs_waiting(sectors, time_intervals):
        return [
            {
                'id': f'aw-{i["id"]}-{t0}',
                'energy_variation': (t1 - t0) * i['power'],
                'time_start': t0,
                'time_end': t1,
                'station_start': i['id'],
                'station_end': i['id'],
            }
            for i in sectors
            for t0, t1 in np.transpose([time_intervals[:-1], time_intervals[1:]])
        ]

    def generate_arcs_moving(
        sectors,
        distances,
        time_intervals,
        time_limit,
        relocation_cost
    ):
        arcs_r = []
        for idx_start, i_start in enumerate(sectors):
            for idx_end, i_end in enumerate(sectors):
                if i_start['id'] == i_end['id']:
                    continue
                delta_t = distances[idx_start][idx_end]
                if delta_t > time_limit * 60:
                    continue
                for t in time_intervals:
                    if t + delta_t > time_intervals[-1]:
                        break
                    time_end = next(i for i in time_intervals if i >= t + delta_t)
                    arcs_r.append({
                        'id': f'ar-{i_start["id"]}-{i_end["id"]}-{t}',
                        'profit': -relocation_cost * delta_t,
                        'time_start': t,
                        'time_end': time_end,
                        'station_start': i_start['id'],
                        'station_end': i_end['id'],
                    })
        return arcs_r

    def generate_arcs_customer(cluster_data):
        return []

    arcs_w = generate_arcs_waiting(SECTORS, config.TIME_INSTANTS)
    arcs_wx = []
    if lconfig.W_PROFIT_TYPE == 'end':
        arcs_wx = [
            aw | {
                'id': aw['id'][:1] + 'x' + aw['id'][1:],
                'profit': (
                    PROFITS[
                        aw['station_start']
                    ][
                        'profit'
                    ][
                        config.WEEKDAY
                    ][
                        int(aw['time_start'] / PROFIT_DT)
                    ] * len(config.TIME_INSTANTS) * config.DELTA_T / PROFIT_DT if (
                        aw['time_end'] == config.TIME_INSTANTS[-1]
                    ) else 0
                ),
            } for aw in arcs_w
        ]
    if lconfig.W_PROFIT_TYPE == 'all':
        arcs_wx = [
            aw | {
                'id': aw['id'][:1] + 'x' + aw['id'][1:],
                'profit': (
                    PROFITS[
                        aw['station_start']
                    ][
                        'profit'
                    ][
                        config.WEEKDAY
                    ][
                        int(aw['time_start'] / PROFIT_DT)
                    ] * config.DELTA_T / PROFIT_DT
                ),
            } for aw in arcs_w
        ]
    arcs_wy = [
        aw | {
            'id': aw['id'][:1] + 'y' + aw['id'][1:],
            'profit': 0,
        } for aw in arcs_w
    ]
    arcs_wz = [
        aw | {
            'id': aw['id'][:1] + 'z' + aw['id'][1:],
            'profit': aw['energy_variation'] * lconfig.ALPHA,
        } for aw in arcs_w
    ]
    arcs_r = generate_arcs_moving(
        SECTORS,
        traffic_data,
        config.TIME_INSTANTS,
        lconfig.TIME_LIMIT,
        lconfig.RELOCATION_COST,
    )
    arcs_t = []
    arcs_c = generate_arcs_customer(cluster_data)
    arc_data = {
        'sectors': SECTORS,
        'time_instants': config.TIME_INSTANTS,
        'arcs_wx': arcs_wx,
        'arcs_wy': arcs_wy,
        'arcs_wz': arcs_wz,
        'arcs_r': arcs_r,
        'arcs_t': arcs_t,
        'arcs_c': arcs_c,
    }
    return {
        'data': arc_data,
    }