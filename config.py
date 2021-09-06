import os


data_path = os.path.join("data")

PET_dirs = [
    "PET_TBR",          # TBR
    "PET_Act",          # Activity
    "PET_test",         # test set
    "PET_Act_test",     # test set Act
]

time_ranges = [
    "FET_5_10",
    "FET_10_30",
    "FET_20_40"
]

PET_dir = PET_dirs[0]
time_range = time_ranges[2]

if PET_dir == PET_dirs[1] or PET_dir == PET_dirs[3]:
    time_range += "_Act"

lower_threshold_tumor = 1.6
upper_threshold_tumor = 5000
