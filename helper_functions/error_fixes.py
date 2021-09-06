import os
import SimpleITK as sitk
from config import PET_dir, time_range, data_path
from helper_functions.nifti_functions import normalize_image


# # Fix different spacing of VOI 064
# os.chdir(os.path.join("..", data_path, "Conf_centered"))
# mask = sitk.ReadImage("centered_Pat_VOI_064.nii")
# os.chdir(os.path.join("..", PET_dir))
# image = sitk.ReadImage(os.path.join(time_range + "_centered", "centered_Pat_064.nii"))
#
# resample = sitk.ResampleImageFilter()
# new_spacing = image.GetSpacing()
# print(image.GetSpacing())
# mask.SetSpacing(image.GetSpacing())
# print(mask.GetSpacing())
#
# sitk.WriteImage(mask, os.path.join("..", "Conf_centered", "centered_Pat_VOI_064.nii"))


# Fix wrong value range 0-2 to 0-1 of BG 205, 231, 315
CastFil = sitk.CastImageFilter()
CastFil.SetOutputPixelType(sitk.sitkInt16)
os.chdir(os.path.join("..", data_path))
BG_filenames = ["Pat_BG_205.nii", "Pat_BG_231.nii", "Pat_BG_315.nii"]
for BG_filename in BG_filenames:
    BG = sitk.ReadImage(os.path.join("BG", BG_filename))
    BG_array = sitk.GetArrayFromImage(BG)
    BG_array[BG_array >= 1] = 1
    BG_new = sitk.GetImageFromArray(BG_array)
    BG_new.CopyInformation(BG)
    sitk.WriteImage(BG_new, (os.path.join("BG", BG_filename)))

    BG_centered = sitk.ReadImage(os.path.join("BG_centered", "centered_" + BG_filename))
    BG_centered_array = sitk.GetArrayFromImage(BG_centered)
    BG_centered_array[BG_centered_array >= 1] = 1
    BG_centered_new = sitk.GetImageFromArray(BG_centered_array)
    BG_centered_new.CopyInformation(BG_centered)
    sitk.WriteImage(BG_centered_new, (os.path.join("BG_centered", "centered_" + BG_filename)))






