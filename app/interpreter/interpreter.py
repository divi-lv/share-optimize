import pandas as pd
import numpy as np

def interpreter(transcript):
    def trace(
        df,
        station_start,
        time_start,
        object_type,
        path=pd.DataFrame(columns=[
            'station_start',
            'station_end',
            'time_start',
            'time_end',
            'arc_type',
        ]),
    ):
        df_s = df[
            (df['station_start'] == station_start) &
            (df['time_start'] == time_start) &
            (df['object_type'] == object_type)
        ]
        for row in df_s.iterrows():
            if row[1]['count'] > 0:
                df.at[row[0], 'count'] -= 1
                path = path.append({
                    'station_start': row[1]['station_start'],
                    'station_end': row[1]['station_end'],
                    'time_start': row[1]['time_start'],
                    'time_end': row[1]['time_end'],
                    'arc_type': row[1]['arc_type'],
                }, ignore_index=True)
                return trace(
                    df,
                    station_start = row[1]['station_end'],
                    time_start = row[1]['time_end'],
                    object_type = object_type,
                    path = path,
                )
        return path, df[df['count'] > 0]

    def trace_all_obj(df, object_type):
        df = df.copy()
        df = df[df['object_type'] == object_type]
        paths = []
        while df.empty == False:
            seed = df.loc[pd.to_numeric(df['time_start']).idxmin()]
            path, df = trace(
                df,
                seed['station_start'],
                seed['time_start'],
                object_type,
            )
            paths.append(path)
        return paths
    
    df = transcript

    xi = trace_all_obj(df, 'x')
    yi = trace_all_obj(df, 'y')
    zi = trace_all_obj(df, 'z')

    def time_to_str(seconds):
        hour = f'{np.floor(seconds / (60*60) % 24).astype(int)}'
        if len(hour) < 2:
            hour = '0' + hour
        mins = f'{np.floor(seconds / 60 % 60).astype(int)}'
        if len(mins) < 2:
            mins = '0' + mins
        return f'{hour}:{mins}'

    return {
        'relocators': [
            '\n'.join([
                f"{time_to_str(instr['time_start'])} -- Move (in) a vehicle from {instr['station_start']} to {instr['station_end']}" if instr['arc_type'] == 'r' else
                f"{time_to_str(instr['time_start'])} -- Wait at {instr['station_start']}" if instr['arc_type'] == 'w' else
                f"{time_to_str(instr['time_start'])} -- Walk from {instr['station_start']} to {instr['station_end']}"
                for _, instr in y.iterrows()
            ])
            for y in yi
        ],
        'vehicles_x': [
            '\n'.join([
                f"{time_to_str(instr['time_start'])} -- Get relocated from {instr['station_start']} to {instr['station_end']}" if instr['arc_type'] == 'r' else
                f"{time_to_str(instr['time_start'])} -- Idle at {instr['station_start']}" if instr['arc_type'] == 'w' else
                f"{time_to_str(instr['time_start'])} -- Get hired from {instr['station_start']} to {instr['station_end']}"
                for _, instr in x.iterrows()
            ])
            for x in xi
        ],
        'vehicles_z': [
            '\n'.join([
                f"{time_to_str(instr['time_start'])} -- Get relocated from {instr['station_start']} to {instr['station_end']}" if instr['arc_type'] == 'r' else
                f"{time_to_str(instr['time_start'])} -- Idle (or charge) at {instr['station_start']}"
                for _, instr in z.iterrows()
            ])
            for z in zi
        ],
    }