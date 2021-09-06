"""Connected threshold based tumor mask segmentation

Uses lower_threshold_tumor and upper_threshold_tumor from config.py
to segment binary tumor mask from centered PET scans with the help of centered VOIs and BGs (optional)

Set "normalize" to True to use the centered background VOIs to normalize voxels to TBR values before segmentation
"""


import numpy as np
import SimpleITK as sitk
import os
from tqdm import tqdm
from helper_functions.nifti_functions import normalize_image
from config import data_path, PET_dir, time_range, lower_threshold_tumor, upper_threshold_tumor

overwrite = True
normalize = False
save_part_VOIs = True

os.chdir(os.path.join(data_path, PET_dir))

if time_range[-3:] == "Act":
    units = "_Act"
else:
    units = ""

output_dir = time_range + "_tumor_masks_multiple2"
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

output_dir_tumors = time_range + "_tumors_multiple2"
if not os.path.isdir(output_dir_tumors):
    os.mkdir(output_dir_tumors)

output_dir_part_VOIs = "Conf_centered_part"
output_path_part_VOIs = os.path.join(os.path.realpath(__file__).rsplit(os.path.sep, 1)[0], data_path, output_dir_part_VOIs)

if not os.path.isdir(output_path_part_VOIs):
    os.makedirs(output_path_part_VOIs)

os.chdir(os.path.join(time_range + "_centered"))

mask_filter = sitk.MaskImageFilter()
lower = lower_threshold_tumor
upper = upper_threshold_tumor

CastFilBgMask = sitk.CastImageFilter()
CastFilBgMask.SetOutputPixelType(sitk.sitkInt64)

CastFilVOI = sitk.CastImageFilter()
CastFilVOI.SetOutputPixelType(sitk.sitkInt64)

CastFilVOIpart = sitk.CastImageFilter()
CastFilVOIpart.SetOutputPixelType(sitk.sitkFloat32)

ThresholdFilter = sitk.BinaryThresholdImageFilter()
# ThresholdFilter.SetInsideValue(0)
# ThresholdFilter.SetOutsideValue(1)
MinMaxFilter = sitk.MinimumMaximumImageFilter()

corrupted_files = []
mask_errors = []

input_filenames = os.listdir()
# input_filenames = ["centered_Pat_204.nii", "centered_Pat_205.nii"]
# input_filenames = ["centered_Pat_062.nii"]

suffix_dict = {"1": "a",
               "2": "b",
               "3": "c",
               "4": "d",
               "5": "e"}

for input_filename in tqdm(input_filenames):
    pat_nr = input_filename.rsplit(".")[0][-3:]

    if not overwrite and os.path.isfile(os.path.join("..", output_dir, output_filename)):
        continue

    tumor_VOI_filename = "centered_Pat_VOI_" + input_filename.split(".")[0][-3:] + ".nii"

    try:
        image = sitk.ReadImage(input_filename)
    except Exception as e:
        print("Error in '" + input_filename + "'")
        print(Exception)
        print(e)
        corrupted_files.append(input_filename)
        continue

    if normalize:
        bg_mask_filename = "centered_Pat_BG_" + input_filename.split(".")[0][-3:] + ".nii"
        bg_mask = sitk.ReadImage(os.path.join("..", "..", "BG_centered", bg_mask_filename))
        bg_mask = CastFilBgMask.Execute(bg_mask)
        image = normalize_image(image, bg_mask)

    tumor_VOI = sitk.ReadImage(os.path.join("..", "..", "Conf_centered", tumor_VOI_filename))
    # sitk.Show(tumor_VOI)

    MinMaxFilter.Execute(tumor_VOI)
    n_VOIs = int(MinMaxFilter.GetMaximum())

    if n_VOIs == 1:
        print(f"Nr of VOIs: {n_VOIs}")
        try:
            tumor_VOI = CastFilVOI.Execute(tumor_VOI)
            masked_image = mask_filter.Execute(image, tumor_VOI)
        except Exception as e:
            mask_errors.append(input_filename)
            print("Error in '" + input_filename + "'")
            print(Exception)
            print(e)
            continue

        masked_image_array = sitk.GetArrayFromImage(masked_image)
        ind = np.unravel_index(np.argmax(masked_image_array, axis=None), masked_image_array.shape)
        tumor_mask = sitk.ConnectedThreshold(masked_image,
                                             seedList=[(int(ind[2]), int(ind[1]), int(ind[0]))],
                                             lower=lower, upper=upper)
        masked_tumor = mask_filter.Execute(image, tumor_mask)

        output_filename = input_filename.rsplit("_")[0] + "_tumor_mask" + units + "_" + pat_nr + ".nii"
        output_filename_tumor = input_filename.rsplit("_")[0] + "_tumor" + units + "_" + pat_nr + ".nii"
        sitk.WriteImage(tumor_mask, os.path.join("..", output_dir, output_filename))
        sitk.WriteImage(masked_tumor, os.path.join("..", output_dir_tumors, output_filename_tumor))
        if save_part_VOIs:
            tumor_VOI = CastFilVOIpart.Execute(tumor_VOI)
            output_filename_part_VOI = "centered_Pat_VOI_" + pat_nr + ".nii"
            sitk.WriteImage(tumor_VOI, os.path.join(output_path_part_VOIs, output_filename_part_VOI))

    else:
        print(f"Nr of VOIs: {n_VOIs}")
        for VOI_nr in range(1, n_VOIs+1):
            try:
                ThresholdFilter.SetLowerThreshold(float(VOI_nr) - 0.5)
                ThresholdFilter.SetUpperThreshold(float(VOI_nr) + 0.5)
                tumor_VOI_part = ThresholdFilter.Execute(tumor_VOI)
                tumor_VOI_part = CastFilVOI.Execute(tumor_VOI_part)
                # sitk.Show(tumor_VOI_part)
                masked_image = mask_filter.Execute(image, tumor_VOI_part)
                # sitk.Show(masked_image)
            except Exception as e:
                mask_errors.append(input_filename)
                print("Error in '" + input_filename + "'")
                print(Exception)
                print(e)
                continue

            masked_image_array = sitk.GetArrayFromImage(masked_image)
            ind = np.unravel_index(np.argmax(masked_image_array, axis=None), masked_image_array.shape)
            tumor_mask = sitk.ConnectedThreshold(masked_image,
                                                 seedList=[(int(ind[2]), int(ind[1]), int(ind[0]))],
                                                 lower=lower, upper=upper)
            masked_tumor = mask_filter.Execute(image, tumor_mask)
            # sitk.Show(tumor_mask)
            output_filename = input_filename.rsplit("_")[0] + "_tumor_mask" + units + "_" + pat_nr + suffix_dict[str(VOI_nr)] + ".nii"
            output_filename_tumor = input_filename.rsplit("_")[0] + "_tumor" + units + "_" + pat_nr + suffix_dict[str(VOI_nr)] + ".nii"
            sitk.WriteImage(tumor_mask, os.path.join("..", output_dir, output_filename))
            sitk.WriteImage(masked_tumor, os.path.join("..", output_dir_tumors, output_filename_tumor))
            if save_part_VOIs:
                tumor_VOI_part = CastFilVOIpart.Execute(tumor_VOI_part)
                output_filename_part_VOI = "centered_Pat_VOI_" + pat_nr + suffix_dict[str(VOI_nr)] + ".nii"
                sitk.WriteImage(tumor_VOI_part, os.path.join(output_path_part_VOIs, output_filename_part_VOI))



if corrupted_files:
    print("Corrupted files:")
    for corrupted_file in corrupted_files:
        print(corrupted_file)

if mask_errors:
    print("Mask errors in following files:")
    for mask_error in mask_errors:
        print(mask_error)


