"""Connected threshold based tumor segmentation

Uses lower_threshold_tumor and upper_threshold_tumor from config.py
to segment tumors from centered PET scans with the help of centered VOIs and BGs (optional)

Set "normalize" to True to use the centered background VOIs to normalize voxels to TBR values before segmentation
"""


import numpy as np
import SimpleITK as sitk
import os
from tqdm import tqdm
from helper_functions.nifti_functions import normalize_image
from config import data_path, PET_dir, time_range, lower_threshold_tumor, upper_threshold_tumor

overwrite = False
normalize = False

os.chdir(os.path.join(data_path, PET_dir))

if time_range[-3:] == "Act":
    units = "_Act"
else:
    units = ""

output_dir = time_range + "_tumors"
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)

os.chdir(os.path.join(time_range + "_centered"))
input_filenames = os.listdir()

mask_filter = sitk.MaskImageFilter()
lower = lower_threshold_tumor
upper = upper_threshold_tumor

CastFil = sitk.CastImageFilter()
CastFil.SetOutputPixelType(sitk.sitkInt16)

CastFilImage = sitk.CastImageFilter()
CastFilImage.SetOutputPixelType(sitk.sitkFloat32)

corrupted_files = []
mask_errors = []

for input_filename in tqdm(input_filenames):
    pat_nr = input_filename.rsplit(".")[0][-3:]
    output_filename = input_filename.rsplit("_")[0] + "_tumor" + units + "_" + pat_nr + ".nii"

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
        bg_mask = CastFil.Execute(bg_mask)
        # 315 is not working with normalize? copied BG from 287 and renamed it to 315
        image = normalize_image(image, bg_mask)

    tumor_VOI = sitk.ReadImage(os.path.join("..", "..", "Conf_centered", tumor_VOI_filename))
    tumor_VOI = CastFil.Execute(tumor_VOI)

    try:
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
    tumor_mask = CastFilImage.Execute(tumor_mask)

    image = CastFilImage.Execute(image)
    sitk.WriteImage(tumor_mask*image, os.path.join("..", output_dir, output_filename))

if corrupted_files:
    print("Corrupted files:")
    for corrupted_file in corrupted_files:
        print(corrupted_file)

if mask_errors:
    print("Mask errors in following files:")
    for mask_error in mask_errors:
        print(mask_error)

