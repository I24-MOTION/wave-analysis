from vehicle_analysis import decompose_trajectory_fixed
from scipy.signal import find_peaks
from tqdm import tqdm
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from mycolor import get_colors

def SAG_track(file, lane_file,file_root_local,file_path, seg_speed=15):
    print('=========the critical speed is set as:', seg_speed, '=========')
    data = pd.read_csv(file_path + '/' + file + '/' + lane_file)
    lane_number = int(lane_file.split('_')[2][0])
    print(
        f'Processing file: {file}, lane number: {lane_number}'
    )
    vehicle_ids = data['v_id'].unique()
    wave_front_list = []
    wave_tail_list = []
    for vehicle_id in tqdm(vehicle_ids):
        vehicle_data = data[data['v_id'] == vehicle_id].copy().reset_index(drop=True)
        vehicle_data = decompose_trajectory_fixed(vehicle_data, fixed_speed=seg_speed)
        vehicle_data = vehicle_data.iloc[::].reset_index(drop=True)
        peaks, _ = find_peaks(vehicle_data.oscillation_space)
        for peak in peaks:
            if np.abs(vehicle_data.speed[peak]-seg_speed) <=5:
                wave_front_list.append((vehicle_data.time[peak], vehicle_data.space[peak],
                                        vehicle_data.speed[peak], vehicle_data.v_id[peak], 1))
        peaks, _ = find_peaks(-vehicle_data.oscillation_space)
        for peak in peaks:
            if np.abs(vehicle_data.speed[peak]-seg_speed) <=5:
                wave_tail_list.append((vehicle_data.time[peak], vehicle_data.space[peak],
                                       vehicle_data.speed[peak], vehicle_data.v_id[peak], 2))
    wave_front = pd.DataFrame(wave_front_list, columns=['time', 'space', 'speed', 'v_id', 'wave_type'])
    wave_tail = pd.DataFrame(wave_tail_list, columns=['time', 'space', 'speed', 'v_id', 'wave_type'])
    wave_front['lane'] = lane_number
    wave_tail['lane'] = lane_number
    all_points = pd.concat([wave_front, wave_tail], axis=0).reset_index(drop=True)
    all_points['unique_index'] = all_points.index
    wave_tail = all_points[all_points['wave_type'] == 2].copy().reset_index(drop=True)
    wave_front = all_points[all_points['wave_type'] == 1].copy().reset_index(drop=True)
    if not os.path.exists(file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}'):
        os.makedirs(file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}')
    wave_tail.to_csv(file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/wave_tail_{seg_speed}.csv',
                     index=False)
    print(
        'File saved:' + file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/wave_tail_{seg_speed}.csv')
    wave_front.to_csv(file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/wave_front_{seg_speed}.csv',
                      index=False)
    print(
        'File saved:' + file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/wave_front_{seg_speed}.csv')
    pair_data = pd.DataFrame()
    vehicle_id_list = all_points['v_id'].unique()
    for vehicle_id in vehicle_id_list[:]:
        # print(vehicle_id)
        vehicle_data = all_points[all_points['v_id'] == vehicle_id].copy().reset_index(drop=True)
        # sort the vehicle_data by time
        vehicle_data = vehicle_data.sort_values(by='time').reset_index(drop=True)
        if (len(vehicle_data) > 1):
            if (vehicle_data['wave_type'][0] == 2):
                vehicle_data = vehicle_data.iloc[1:].reset_index(drop=True)
                vehicle_data = vehicle_data.sort_values(by='time', ascending=False).reset_index(drop=True)
                if (vehicle_data['wave_type'][0] == 1):
                    vehicle_data = vehicle_data.iloc[1:].reset_index(drop=True)
            # split the raw_data into two parts based on the wave type and sort by time, and then combine them in column
            vehicle_front = vehicle_data[vehicle_data['wave_type'] == 1].sort_values(by='time').reset_index(drop=True)
            vehicle_tail = vehicle_data[vehicle_data['wave_type'] == 2].sort_values(by='time').reset_index(drop=True)
            # merge the raw_data
            vehicle_pair_data = pd.concat([vehicle_front, vehicle_tail], axis=1).reset_index(drop=True)
            vehicle_pair_data.columns = ['time_front', 'space_front', 'speed_front', 'v_id_front', 'wave_type_front',
                                         'lane_front', 'unique_index_front', 'time_tail', 'space_tail', 'speed_tail',
                                         'v_id_tail', 'wave_type_tail', 'lane_tail', 'unique_index_tail']
            pair_data = pd.concat([pair_data, vehicle_pair_data], axis=0).reset_index(drop=True)
    pair_data = pair_data.dropna()
    pair_data = pair_data.reset_index(drop=True)
    if not os.path.exists(file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}'):
        os.makedirs(file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}')
    pair_data.to_csv(file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/pair_data_{seg_speed}.csv',
                     index=False)
    # show the raw_data is saved
    print(
        'File saved:' + file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/pair_data_{seg_speed}.csv')
    print('========= start finding the trajectories of wave fronts and tails =========')
    plt.rc('text', usetex=True)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 60
    wave_front = pd.read_csv(
        file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/wave_front_{seg_speed}.csv')
    wave_tail = pd.read_csv(
        file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/wave_tail_{seg_speed}.csv')
    lane_wave = wave_front
    pair_data = pd.read_csv(
        file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/pair_data_{seg_speed}.csv')
    # pair_data check if there are na
    pair_data.isna().sum()
    trace = []
    lane_wave['mask'] = 0
    all_record = len(lane_wave)
    # lane_wave = lane_wave[lane_wave['mask'] == 0]
    vt_list = lane_wave.v_id.unique()
    # vt_list sort by number
    vt_list = np.sort(vt_list)
    trace_id = 0
    # lane_wave = lane_wave[lane_wave['mask'] == 0]
    while (len(lane_wave[lane_wave['mask'] == 0]) > 0):
        percentage = round(100 - len(lane_wave[lane_wave['mask'] == 0]) / all_record * 100, 2)
        if trace_id % 30 == 0:
            print(f"{trace_id} wave fronts are found, remaining {int(100 - percentage)}% unchecked")
        # print(trace_id, len(lane_wave[lane_wave['mask'] == 0]/all_record))
        trace_id += 1
        lane_wave = lane_wave[lane_wave['mask'] == 0]
        vt_list = lane_wave.v_id.unique()
        # vt_list sort by number
        vt_list = np.sort(vt_list)
        # print(vt_list)
        vt_data = lane_wave[lane_wave.v_id == vt_list[0]].iloc[0:1]
        lane_wave.loc[vt_data.index, 'mask'] = 1
        # vt_data.loc[:, 'mask'] = 1
        time = vt_data.time.values[0]
        space = vt_data.space.values[0]
        unique_id = vt_data.unique_index.values[0]
        trace.append([time, space, vt_list[0], trace_id, unique_id])
        vt_index_old = vt_list[0]
        for vt_index in vt_list[1:]:
            if (vt_index - vt_index_old) == 1:
                vt_data = lane_wave[lane_wave.v_id == vt_index]
                local_data = vt_data[(vt_data.time <= time + 15)
                                     & (vt_data.time >= time - 5)
                                     & (vt_data.space >= space - 0.02)
                                     & (vt_data.space <= space + 0.05)]
                # local_data = local_data[local_data.v_id == (vt_index +1)]
                local_data = local_data.sort_values(by='time', ascending=False)
                vt_index_old = vt_index
                if (len(local_data) == 0):
                    # print('no data found')
                    # jump out of the "while" loop if no raw_data is found
                    break
                if (len(local_data) > 1):
                    local_data = local_data.iloc[0].to_frame().T
                    lane_wave.loc[local_data.index, 'mask'] = 1
                    time = local_data.time.values[0]
                    space = local_data.space.values[0]
                    unique_id = local_data.unique_index.values[0]
                    trace.append([time, space, vt_index, trace_id, unique_id])
                # local_data = local_data.iloc[0]
                if (len(local_data) == 1):
                    lane_wave.loc[local_data.index, 'mask'] = 1
                    time = local_data.time.values[0]
                    space = local_data.space.values[0]
                    unique_id = local_data.unique_index.values[0]
                    trace.append([time, space, vt_index, trace_id, unique_id])
    wave_front = pd.DataFrame(trace, columns=['time', 'space', 'v_id', 'trace_id', 'unique_id'])
    print(f"========= all the wave front trajectories are found, total number {trace_id} =========")
    grouped = wave_front.groupby('trace_id')
    plt.figure(figsize=(45, 15))
    for name, group in grouped:
        if (len(group) > 1):
            plt.plot(group.time, group.space,linewidth=4)
    # set plt.yaxis inverse
    plt.gca().invert_yaxis()
    plt.xlabel('Time (HH:MM)')
    plt.ylabel('Mile Marker')
    # plt.title(file + ' ' + 'Lane ' + str(lane_number) + f' with critical speed {seg_speed} mph')
    plt.grid(linestyle='--', lw=2, alpha=1)
    plt.xlim(0, 14400)
    plt.xticks(np.arange(0, 14401, 1800), ['6:00', '6:30', '7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00'])
    plt.ylim(62.7, 58.7)
    # add labels on 59, 60.5, 61, 61.5, 62, 62.5
    plt.yticks(np.arange(59, 62.6, 0.5), ['59','59.5','60', '60.5', '61', '61.5', '62', '62.5'])
    plt.savefig(file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/wave_front_traj_{seg_speed}.pdf',
                dpi=300, bbox_inches='tight')
    plt.close()
    # wave_traj.to_csv('wave_trace/wave_front_traj.csv', index=False)
    # merge the wave_traj[['trace_id','unique_id']] with pair_data on unique_id and unique_index_front
    pair_data = pd.merge(pair_data, wave_front[['trace_id', 'unique_id']],
                         how='left', left_on='unique_index_front', right_on='unique_id')
    # pair_data drop the column unique_id
    pair_data = pair_data.drop(columns='unique_id')
    # change the specific column name to something
    pair_data = pair_data.rename(columns={'trace_id': 'trace_id_front'})
    lane_wave = wave_tail
    trace = []
    lane_wave['mask'] = 0
    all_record = len(lane_wave)
    # lane_wave = lane_wave[lane_wave['mask'] == 0]
    vt_list = lane_wave.v_id.unique()
    # vt_list sort by number
    vt_list = np.sort(vt_list)
    trace_id = 0
    # lane_wave = lane_wave[lane_wave['mask'] == 0]
    while (len(lane_wave[lane_wave['mask'] == 0]) > 0):
        percentage = round(100 - len(lane_wave[lane_wave['mask'] == 0]) / all_record * 100, 2)
        if trace_id % 30 == 0:
            print(f"{trace_id} wave fronts are found, remaining {int(100 - percentage)}% unchecked")
        trace_id += 1
        lane_wave = lane_wave[lane_wave['mask'] == 0]
        vt_list = lane_wave.v_id.unique()
        # vt_list sort by number
        vt_list = np.sort(vt_list)
        vt_data = lane_wave[lane_wave.v_id == vt_list[0]].iloc[0:1]
        lane_wave.loc[vt_data.index, 'mask'] = 1
        # vt_data.loc[:, 'mask'] = 1
        time = vt_data.time.values[0]
        space = vt_data.space.values[0]
        unique_id = vt_data.unique_index.values[0]
        trace.append([time, space, vt_list[0], trace_id, unique_id])
        vt_index_old = vt_list[0]
        for vt_index in vt_list[1:]:
            if (vt_index - vt_index_old) == 1:
                vt_data = lane_wave[lane_wave.v_id == vt_index]
                local_data = vt_data[(vt_data.time <= time + 15)
                                     & (vt_data.time >= time - 5)
                                     & (vt_data.space >= space - 0.02)
                                     & (vt_data.space <= space + 0.05)]
                # local_data = local_data[local_data.v_id == (vt_index +1)]
                local_data = local_data.sort_values(by='time', ascending=False)
                vt_index_old = vt_index
                if (len(local_data) == 0):
                    # jump out of the "while" loop if no raw_data is found
                    break
                if (len(local_data) > 1):
                    # get the first one
                    local_data = local_data.iloc[0].to_frame().T
                    lane_wave.loc[local_data.index, 'mask'] = 1
                    time = local_data.time.values[0]
                    space = local_data.space.values[0]
                    unique_id = local_data.unique_index.values[0]
                    trace.append([time, space, vt_index, trace_id, unique_id])
                if (len(local_data) == 1):
                    lane_wave.loc[local_data.index, 'mask'] = 1
                    time = local_data.time.values[0]
                    space = local_data.space.values[0]
                    unique_id = local_data.unique_index.values[0]
                    trace.append([time, space, vt_index, trace_id, unique_id])
    print(f"========= all the wave tail trajectories are found, total number {trace_id} =========")
    wave_tail = pd.DataFrame(trace, columns=['time', 'space', 'v_id', 'trace_id', 'unique_id'])
    grouped = wave_tail.groupby('trace_id')
    plt.figure(figsize=(45, 15))
    for name, group in grouped:
        if (len(group) > 1):
            plt.plot(group.time, group.space,linewidth=4)
    # set plt.yaxis inverse
    plt.gca().invert_yaxis()
    plt.xlabel('Time (HH:MM)')
    plt.ylabel('Mile Marker')
    # plt.title(file + ' ' + 'Lane ' + str(lane_number) + f' with critical speed {seg_speed} mph')
    plt.grid(linestyle='--', lw=2, alpha=1)
    plt.xlim(0, 14400)
    plt.xticks(np.arange(0, 14401, 1800), ['6:00', '6:30', '7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00'])
    plt.ylim(62.7, 58.7)
    # add labels on 59, 60.5, 61, 61.5, 62, 62.5
    plt.yticks(np.arange(59, 62.6, 0.5), ['59','59.5','60', '60.5', '61', '61.5', '62', '62.5'])
    plt.savefig(file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/wave_tail_traj_{seg_speed}.pdf',
                dpi=300, bbox_inches='tight')
    plt.close()
    # merge the wave_traj[['trace_id','unique_id']] with pair_data on unique_id and unique_index_front
    pair_data = pd.merge(pair_data, wave_tail[['trace_id', 'unique_id']],
                         how='left', left_on='unique_index_tail', right_on='unique_id')
    # pair_data drop the column unique_id
    pair_data = pair_data.drop(columns='unique_id')
    # change the specific column name to something
    pair_data = pair_data.rename(columns={'trace_id': 'trace_id_tail'})
    # check if there's no filename or folder in the target root
    if not os.path.exists(file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}'):
        os.makedirs(file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}')
    pair_data.to_csv(
        file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/file_with_all_info_w_speed_{seg_speed}.csv',
        index=False)


import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm


def SAG_stitch(file_root_local, file, lane_file, seg_speed, file_path):
    plt.rc('text', usetex=True)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.size'] = 60
    lane_number = int(lane_file.split('_')[2][0])
    raw_data = pd.read_csv(
        file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/file_with_all_info_w_speed_{seg_speed}.csv')
    raw_data['trace_id_front'] = raw_data['trace_id_front'].astype(int)
    raw_data = raw_data.dropna()
    raw_data['trace_id_tail'] = raw_data['trace_id_tail'].astype(int)

    def get_unique_list(list_of_lists):
        all_list = [number for sublist in list_of_lists for number in sublist]
        unique_numbers = set(all_list)
        unique_list = list(unique_numbers)
        return unique_list

    all_front_trace = raw_data.trace_id_front.unique().tolist()
    data = pd.read_csv(file_path + '/' + file + '/' + lane_file)
    vehicle_ids = data['v_id'].unique()
    plt.figure(figsize=(45, 15))

    for vehicle_id in tqdm(vehicle_ids[::5]):
        vehicle_data = data[data['v_id'] == vehicle_id].copy().reset_index(drop=True)
        vehicle_data = vehicle_data.iloc[::].reset_index(drop=True)
        plt.plot(vehicle_data.time, vehicle_data.space, color='k', alpha=0.4, lw=1)

    c_id = 0
    data = raw_data.copy()
    cc_result = pd.DataFrame()
    for front_trace_id in all_front_trace[:]:
        if front_trace_id in data.trace_id_front.unique().tolist():
            temp = data[data.trace_id_front == front_trace_id].copy()
            front_trace = []
            front_trace.append([front_trace_id])
            unique_tail_list = temp.trace_id_tail.unique().tolist()

            for tail in unique_tail_list:
                temp_tail = data[data.trace_id_tail == tail]
                front_trace.append(temp_tail.trace_id_front.unique().tolist())

            unique_front_list = get_unique_list(front_trace)
            tail_trace_update = [[x] for x in unique_tail_list]
            front_trace_update = [[x] for x in unique_front_list]
            unique_tail_list_update = []
            unique_front_list_update = []
            count = 0
            while (count < 300):
                count += 1
                for front in unique_front_list:
                    temp_front = data[data.trace_id_front == front]
                    tail_trace_update.append(temp_front.trace_id_tail.unique().tolist())
                unique_tail_list_update = get_unique_list(tail_trace_update)
                for tail in unique_tail_list_update:
                    temp_tail = data[data.trace_id_tail == tail]
                    front_trace_update.append(temp_tail.trace_id_front.unique().tolist())
                unique_front_list_update = get_unique_list(front_trace_update)
                # unique_tail_list = unique_tail_list_update
                unique_front_list = unique_front_list_update

            test_tail = data[data.trace_id_tail.isin(unique_tail_list_update)].copy()
            test_front = data[data.trace_id_front.isin(unique_front_list_update)].copy()

            if (len(test_tail) >= 5 and len(test_front) >= 5):
                c_id += 1
                test_tail['c_id'] = c_id
                test_front['c_id'] = c_id
                cc_result = pd.concat([cc_result, test_tail, test_front], axis=0)
                if c_id > 0:
                    random_color = get_colors(c_id)
                    test_tail = data[data.trace_id_tail.isin(unique_tail_list_update)].copy()
                    test_tail['c_id'] = c_id
                    plt.scatter(test_tail.time_tail, test_tail.space_tail, color=random_color, marker='o', alpha=0.8,
                                s=20)
                    test_front = data[data.trace_id_front.isin(unique_front_list_update)].copy()
                    test_front['c_id'] = c_id
                    plt.scatter(test_front.time_front, test_front.space_front, color=random_color, marker='^',
                                facecolors='none', alpha=0.5, s=50)
                    plt.text(test_front.time_front.min() - 150, test_front.space_front.min(), 'C' + str(c_id),
                             fontsize=50)
            data = data[~data.trace_id_front.isin(unique_front_list_update)]
            data = data[~data.trace_id_tail.isin(unique_tail_list_update)].reset_index(drop=True)
    cc_result.to_csv(file_root_local + '/wave_cluster/' + file + f'/lane_{lane_number}' + f'/CC_{seg_speed}.csv',index=False)
    print('CC file saved:', file_root_local + '/wave_cluster/' + file + f'/lane_{lane_number}' + f'/CC_{seg_speed}.csv')
    plt.gca().invert_yaxis()
    plt.xlabel('Time (HH:MM)')
    plt.ylabel('Mile Marker')
    # plt.title(file + ' ' + 'Lane ' + str(lane_number) + f' with critical speed {seg_speed} mph')
    plt.grid(linestyle='--', lw=2, alpha=1)
    plt.xlim(0, 14400)
    plt.xticks(np.arange(0, 14401, 1800), ['6:00', '6:30', '7:00', '7:30', '8:00', '8:30', '9:00', '9:30', '10:00'])
    plt.ylim(62.7, 58.7)
    # add labels on 59, 60.5, 61, 61.5, 62, 62.5
    plt.yticks(np.arange(59, 62.6, 0.5), ['59','59.5','60', '60.5', '61', '61.5', '62', '62.5'])
    plt.savefig(
        file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/analysis_{seg_speed}_lane_{lane_number}.pdf',
        dpi=300, bbox_inches='tight')
    plt.close()
    print('Analysis file saved:', file_root_local + f'/wave_cluster/' + file + f'/lane_{lane_number}' + f'/analysis_{seg_speed}_lane_{lane_number}.pdf')
