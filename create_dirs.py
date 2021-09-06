"""Create directories

Creates needed directories in the data directory specified in "config.py"
"""


import os
from config import data_path, PET_dir, time_range


os.chdir(data_path)

BG_dir = "BG"
if not os.path.isdir(BG_dir):
    os.makedirs(BG_dir)

VOI_dir = "Conf"
if not os.path.isdir(VOI_dir):
    os.makedirs(VOI_dir)

if not os.path.isdir(os.path.join(PET_dir, time_range)):
    os.makedirs(os.path.join(PET_dir, time_range))