import os
import h5py
import numpy as np
from analyze_fix_stationary import analyze_fix_stationary

FT_DATA_IDXES = {'ft_frame':0, 'ft_x':14, 'ft_y':15, 'ft_theta':16, 'ft_movement_speed':18, 'ft_fwd':19, 'ft_side':20, 'ft_timestamps':21}
# do not change ft_timestamps



# User supplied file names
fictrac_data_fn = "/home/clandinin/lib/flystim1/examples/fictrac-202207071318.dat"
hdf_fn = "/home/clandinin/lib/flystim1/examples/202207071318.h5"

# Infer save path and save prefix from above
save_path = os.path.join('/', *fictrac_data_fn.split('/')[:-1])
save_prefix = hdf_fn.split('/')[-1].split('.')[0]

# Open up fictrac and hdf file
ft_data_handler = open(fictrac_data_fn, 'r')
h5f = h5py.File(hdf_fn, 'a')

# Get needed info from hdf
trials = h5f.require_group('trials')
trial_0 = trials.require_group('000')
iti = h5f.attrs['iti']
n_trials = h5f.attrs['n_trials']


# Process through ft_data_handler until it gets to the frame iti before first trial
start_time_next_trial = trial_0.attrs['start_time']
ft_data_next = dict.fromkeys(FT_DATA_IDXES.keys(), [])

curr_time = 0
while curr_time < start_time_next_trial - iti:
    ft_line = ft_data_handler.readline()
    ft_toks = ft_line.split(", ")
    curr_time = float(ft_toks[FT_DATA_IDXES['ft_timestamps']])/1e3

while curr_time < start_time_next_trial:
    ft_line = ft_data_handler.readline()
    ft_toks = ft_line.split(", ")
    curr_time = float(ft_toks[FT_DATA_IDXES['ft_timestamps']])/1e3
    for k in FT_DATA_IDXES.keys():
        ft_data_next[k].append(float(ft_toks[FT_DATA_IDXES[k]]))

# Loop through trials and create trial groups and datasets
ft_line = ft_data_handler.readline()
for t in range(n_trials):
    save_dir_prefix = os.path.join(save_path, save_prefix+"_t"+f'{t:03}')

    fs_timestamps = np.loadtxt(save_dir_prefix+'_fs_timestamps.txt')

    ft_data = ft_data_next
    ft_data_next = dict.fromkeys(FT_DATA_IDXES.keys(), [])

    if t < n_trials-1:
        start_time_next_trial = trial.attrs['end_time'] + iti
    else: #t == n_trials-1
        start_time_next_trial = np.infty

    while ft_line!="" and curr_time < start_time_next_trial:
        ft_toks = ft_line.split(", ")
        curr_time = float(ft_toks[FT_DATA_IDXES['ft_timestamps']])/1e3
        for k in FT_DATA_IDXES.keys():
            ft_data[k].append(float(ft_toks[FT_DATA_IDXES[k]]))
        if curr_time >= trial.attrs['end_time']:
            for k in FT_DATA_IDXES.keys():
                ft_data_next[k].append(float(ft_toks[FT_DATA_IDXES[k]]))
        ft_line = ft_data_handler.readline()

    # trial
    trial = trials.require_group(f'{t:03}')
    trial.create_dataset("fs_timestamps", data=fs_timestamps)
    for k in FT_DATA_IDXES.keys():
        if k == 'ft_timestamps':
            trial.create_dataset(k, data=np.array(ft_data[k])/1e3)
        else:
            trial.create_dataset(k, data=ft_data[k])


ft_data_handler.close()
h5f.close()

# Delete flystim txt output files
fs_txt_files = [x for x in os.listdir(save_path) if x.startswith(save_prefix) and x.endswith('.txt')]
for txt_fn in fs_txt_files:
    os.remove(os.path.join(save_path, txt_fn))

# Run quick analysis post experiment
_=analyze_fix_stationary(hdf_fn, front_region=[-15,15])