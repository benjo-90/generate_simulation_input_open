"""Create tumor masks for PETPVC

Creates tumor masks of segmented tumors for later use within PETPVC

For "evenly" and "adapted" specifiy "nr_of_segments" (background included). Lowest non-zero value is used
as lowest threshold

For "evenly" specify "highest_threshold"

"adapted" uses max-value as highest threshold

Output directory e.g. "t_20201118_seg_9_adapted" in "FET_20_40_tumor_masks_segments"
Output files are "nr_of_segments"-dimensional images

Used thresholds will be either saved in one txt-file (custom)
or in several txt-files in "thresholds" dir (evenly, adapted)
"""


import SimpleITK as sitk
import os
import glob
import numpy as np
from tqdm import tqdm
import time
from datetime import datetime
from config import data_path, PET_dir, time_range, lower_threshold_tumor

os.chdir(os.path.join(data_path, PET_dir))

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

tumors_dir = time_range + "_tumors_multiple"

if threshold_mode == threshold_modes[0] or threshold_mode == threshold_modes[1]:
    nr_of_segments = 2

else:
    # set thresholds manually, last segment contains values bigger than last threshold
    thresholds = [0.3, 1.8, 2.2, 3.0]
    thresholds = [i * scale for i in thresholds]
    nr_of_segments = len(thresholds) + 1


now = datetime.now()
tumor_pvc_dir = time_range + "_tumor_masks_segments"
output_dir_current = "t_" + now.strftime("%Y%m%d") + suffix + "_seg_" + str(nr_of_segments) + "_" + threshold_mode
output_dir = os.path.join(tumor_pvc_dir, output_dir_current)
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
else:
    thresholds_dir = os.path.join(output_dir, "thresholds")
    os.makedirs(thresholds_dir)

binary_filter = sitk.BinaryThresholdImageFilter()
minmax_filter = sitk.MinimumMaximumImageFilter()

os.chdir(tumors_dir)
input_filenames = glob.glob("centered*")
# input_filenames = ["centered_tumor_Act_001.nii"]
for filename in tqdm(input_filenames):
    image = sitk.ReadImage(filename)
    image_array = sitk.GetArrayFromImage(image)
    minmax_filter.Execute(image)
    image_max_value = minmax_filter.GetMaximum()
    highest_threshold = image_max_value

    if threshold_mode == threshold_modes[0] or threshold_mode == threshold_modes[1]:
        image_array = sitk.GetArrayFromImage(image)
        try:
            lowest_threshold = np.min(image_array[np.nonzero(image_array)])
        except ValueError:
            lowest_threshold = 0

        if threshold_mode == threshold_modes[0]:
            # non-adapted thresholds
            # use evenly spaced thresholds
            highest_threshold = 2.05 * scale
            width = (highest_threshold - lowest_threshold) / (nr_of_segments - 2)
            # thresholds = [np.round(i, 2) for i in np.arange(lowest_threshold, highest_threshold+width, width)]
            thresholds = [lowest_threshold + width * i for i in range(nr_of_segments - 1)]
        else:
            width = (highest_threshold-lowest_threshold)/(nr_of_segments-1)
            thresholds = [lowest_threshold + width*i for i in range(nr_of_segments)]
            # add 1 to last threshold to avoid that last mask contains only one voxel
            thresholds[-1] = thresholds[-1] + 1

        threshold_output = "thresholds_" + filename.split(".")[0].split("_")[-1] + ".txt"
        with open(os.path.join("..", thresholds_dir, threshold_output), "a") as file:
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

        errors = []
        try:
            masks.append(binary_filter.Execute(image))
        except Exception as e:
            errors.append(filename)
            print(e)
            print(Exception)
            print(filename)
            continue

        lower = upper

        if index == (len(thresholds)-1) and (threshold_mode == threshold_modes[2] or threshold_mode == threshold_modes[0]):
            binary_filter.SetLowerThreshold(lower)
            binary_filter.SetUpperThreshold(lower*10)
            masks.append(binary_filter.Execute(image))

    masks_4d = sitk.JoinSeries(masks)
    output_filename = "tumor_mask_segments_" + filename.split(".")[0].split("_")[-1] + ".nii"
    sitk.WriteImage(masks_4d, os.path.join("..", output_dir, output_filename))

print(time.time()-t0)

print(errors)

# bgMin = 0.0000
# bgMax = 29.99999
# bgLabel = gtm_means[0]
#
# blackMin = 30.0000
# blackMax = 89.99999
# blackLabel = gtm_means[1]
#
# grayMin = 90.0000
# grayMax = 119.999999
# grayLabel = gtm_means[2]
#
# whiteMin = 120.0000
# whiteMax = 250
# whiteLabel = gtm_means[3]
#
# with open("output_gtm.txt") as file:
#     gtm_means = file.read().split("\t")
#     gtm_means = gtm_means[2:]
#     for i in range(len(gtm_means)):
#         gtm_means[i] = float(gtm_means[i][:-3])
#
# image_array[(image_array >= bgMin) * (image_array <= bgMax)] = bgLabel
# image_array[(image_array >= grayMin) * (image_array <= grayMax)] = grayLabel
# image_array[(image_array >= whiteMin) * (image_array <= whiteMax)] = whiteLabel
# image_array[(image_array >= blackMin) * (image_array <= blackMax)] = blackLabel


#
# print(gtm_means)
#
# segmented_image = sitk.GetImageFromArray(image_array)
# segmented_image.CopyInformation(image)
#
# sitk.Show(segmented_image)