import os
import SAGCC as SAG
from multiprocessing import Pool, cpu_count

def process_file(args):
    file, lane_file, seg_speed, file_root_local, file_path = args
    SAG.SAG_track(file, lane_file, file_root_local=file_root_local, file_path=file_path, seg_speed=seg_speed)
    SAG.SAG_stitch(file_root_local, file, lane_file, file_path=file_path, seg_speed=seg_speed)

def main(file_path, file_root_local):
    # seg_speeds = [1, 5, 10, 15, 20, 25, 30, 35, 40]
    # file_list = ['2022-11-22', '2022-11-28', '2022-11-29', '2022-11-30', '2022-12-01', '2022-12-02']
    seg_speeds = [15]
    file_list = ['2022-11-22']

    tasks = []
    for seg_speed in seg_speeds:
        for file in file_list:
            if file == '.DS_Store':
                continue
            lane_files = os.listdir(os.path.join(file_path, file))
            lane_files.sort()
            for lane_file in lane_files:
                if lane_file == '.DS_Store':
                    continue
                tasks.append((file, lane_file, seg_speed, file_root_local, file_path))

    with Pool(processes=cpu_count()) as pool:
        pool.map(process_file, tasks)

if __name__ == "__main__":
    file_path = 'data/vt_data'
    file_root_local = 'results'
    main(file_path, file_root_local)
