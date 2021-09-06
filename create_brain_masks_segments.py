"""Create brain masks for PETPVC

Creates brain masks of mirrored tumor-free brains for later use within PETPVC

For "evenly" and "adapted" specifiy "nr_of_segments" (background included)
and "lowest_threshold".

For "evenly" specify also "highest_threshold"

In contrast to "evenly", "adapted" uses 99.95 percentile as hightes threshold (516 highest voxels in last segment)

Output directory e.g. "b_20201118_seg_9_adapted" in "FET_20_40_pvc_brain_masks"
Output files are "nr_of_segments"-dimensional images

Used thresholds will be either saved in one txt-file (custom)
or in several txt-files in "thresholds" dir (evenly, adapted)
"""


import SimpleITK as sitk
import os
import numpy as np
import glob
from tqdm import tqdm
import time
from datetime import datetime
from config import data_path, time_range, PET_dir

t0 = time.time()
threshold_modes = ["evenly",
                   "adapted",
                   "custom"]

threshold_mode = threshold_modes[1]

if time_range[-3:] == "Act":
    # scale = 2500
    scale = 1
    suffix = "_Act"
else:
    scale = 1
    suffix = ""

if threshold_mode == threshold_modes[0] or threshold_mode == threshold_modes[1]:
    lowest_threshold = 0.3 * scale
    nr_of_segments = 9

    if threshold_mode == threshold_modes[0]:
        # non-adapted thresholds
        # use evenly spaced thresholds
        highest_threshold = 2.05 * scale
        width = (highest_threshold-lowest_threshold)/(nr_of_segments-2)
        # thresholds = [np.round(i, 2) for i in np.arange(lowest_threshold, highest_threshold+width, width)]
        thresholds = [lowest_threshold + width*i for i in range(nr_of_segments-1)]

else:
    # set thresholds manually
    thresholds = [0.3, 0.9, 1.2, 2.5]
    thresholds = [i * scale for i in thresholds]
    nr_of_segments = len(thresholds) + 1

# print("Total of", str(len(thresholds)), "clusters (without top-cluster for values >", str(thresholds[-1]) + ")")
# print("with following thresholds:")
# print(thresholds)


os.chdir(os.path.join(data_path, PET_dir))
now = datetime.now()
output_dir_current = "b_" + now.strftime("%Y%m%d") + suffix + "_seg_" + str(nr_of_segments) + "_" + threshold_mode
output_dir = os.path.join(time_range + "_mirrored_brain_masks_segments", output_dir_current)
counter = 1
while os.path.isdir(output_dir):
    output_dir = os.path.join(output_dir.rsplit(os.path.sep, 1)[0], output_dir_current + "_" + str(counter))
    counter += 1
os.makedirs(output_dir)

# if not adapted
if threshold_mode == threshold_modes[0] or threshold_mode == threshold_modes[2]:
    with open(os.path.join(output_dir, "_thresholds.txt"), "a") as file:
        for nr in thresholds:
            file.write(str(nr) + "\n")

os.chdir(time_range + "_mirrored")

if threshold_mode == threshold_modes[1]:
    thresholds_dir = os.path.join("..", output_dir, "thresholds")
    os.makedirs(thresholds_dir)

binary_filter = sitk.BinaryThresholdImageFilter()
minmax_filter = sitk.MinimumMaximumImageFilter()

input_filenames = glob.glob("mirrored*.nii")
# input_filenames = ["mirrored_Pat_221.nii"]

for filename in tqdm(input_filenames):
    image = sitk.ReadImage(filename)
    image_array = sitk.GetArrayFromImage(image)
    minmax_filter.Execute(image)
    image_max_value = minmax_filter.GetMaximum()
    image_array = sitk.GetArrayFromImage(image)
    # 516 highest voxels in last segment
    highest_threshold = np.percentile(image_array, 99.95)

    if threshold_mode == threshold_modes[1]:
        width = (highest_threshold-lowest_threshold)/(nr_of_segments-2)
        thresholds = [lowest_threshold + width*i for i in range(nr_of_segments-1)]

        threshold_output = "thresholds_" + filename.split(".")[0][-3:] + ".txt"
        with open(os.path.join(thresholds_dir, threshold_output), "a") as file:
            for nr in thresholds:
                file.write(str(nr) + "\n")

    masks = []
    lower = 0
    for index, upper in enumerate(thresholds):
        # binary_filter.SetLowerThreshold(lower)
        # binary_filter.SetUpperThreshold(upper)
        # binary_map_array = sitk.GetArrayFromImage(binary_filter.Execute(image))
        # if index == 0:
        #     binary_maps_array = binary_map_array[:, :, :, np.newaxis]
        # else:
        #     binary_maps_array = np.append(binary_maps_array, binary_map_array[:, :, :, np.newaxis], axis=3)
        # lower = upper

        # binary_filter.SetLowerThreshold(lower)
        # binary_filter.SetUpperThreshold(upper)
        # binary_filter.SetInsideValue(index)
        # if index == 0:
        #     segmentation_map = binary_filter.Execute(image)
        # else:
        #     segmentation_map += binary_filter.Execute(image)
        # lower = upper

        binary_filter.SetLowerThreshold(lower)
        binary_filter.SetUpperThreshold(upper)
        masks.append(binary_filter.Execute(image))
        lower = upper

        if index == len(thresholds)-1:
            binary_filter.SetLowerThreshold(lower)

            if threshold_mode == threshold_modes[2]:
                binary_filter.SetUpperThreshold(lower*10)
            else:
                binary_filter.SetUpperThreshold(image_max_value)

            masks.append(binary_filter.Execute(image))

    masks_4d = sitk.JoinSeries(masks)
    output_filename = "brain_mask_segments_" + filename.split("_", 1)[-1] + ".nii"
    sitk.WriteImage(masks_4d, os.path.join("..", output_dir, output_filename))

print(time.time()-t0)
