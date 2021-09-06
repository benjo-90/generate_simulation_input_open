"""Center BGs and VOIs with pmod transformation files

Uses .mat transformations from pmod in dir "pmod_transformations"
to center BGs and VOIs.

Needs fixing: still not extracting the same exact translation and rotation parameters from .mat file
"""


import os
import SimpleITK as sitk
import scipy.io
from tqdm import tqdm
from helper_functions.nifti_functions import affine_transformation_pmod
from config import data_path

overwrite = False

os.chdir(data_path)

output_path_BG = "BG_centered"
output_path_VOI = "Conf_centered"
if not os.path.isdir(output_path_BG):
    os.makedirs(output_path_BG)
if not os.path.isdir(output_path_VOI):
    os.makedirs(output_path_VOI)

BG_filenames = os.listdir("BG")
patient_nrs = [BG_filename.split(".")[0][-3:] for BG_filename in BG_filenames]

for patient_nr in tqdm(patient_nrs):
    output_filename_BG = "centered_Pat_BG" + "_" + patient_nr + ".nii"
    output_filename_VOI = "centered_Pat_VOI" + "_" + patient_nr + ".nii"

    centered_BG_exists = os.path.isfile(os.path.join(output_path_BG, output_filename_BG))
    centered_VOI_exists = os.path.isfile(os.path.join(output_path_VOI, output_filename_VOI))
    if not overwrite and centered_VOI_exists and centered_BG_exists:
        continue

    file_dir = os.path.dirname(__file__)
    transformation_dict = scipy.io.loadmat(os.path.join(file_dir, "pmod_transformations", patient_nr + ".mat"))

    if not centered_VOI_exists:
        VOI = sitk.ReadImage(os.path.join("Conf", "Pat_VOI_" + patient_nr + ".nii"))
        centered_VOI = affine_transformation_pmod(VOI, transformation_dict)
        VOI_filename = "centered_Pat_VOI_" + patient_nr + ".nii"
        sitk.WriteImage(centered_VOI, os.path.join(output_path_VOI, VOI_filename))

    if not centered_BG_exists:
        BG = sitk.ReadImage(os.path.join("BG", "Pat_BG_" + patient_nr + ".nii"))
        centered_BG = affine_transformation_pmod(BG, transformation_dict)
        BG_filename = "centered_Pat_BG_" + patient_nr + ".nii"
        sitk.WriteImage(centered_BG, os.path.join(output_path_BG, BG_filename))

# if not overwrite:
#     print(os.getcwd())
#     existing_pat_nrs = os.listdir(os.path.join("..", data_path, "BG_centered"))
#
#     # patient nr from filename, using sets for excluding existing files
#     existing_pat_nrs = set([existing_pat_nrs[i].split(".")[0][-3:] for i in range(len(existing_pat_nrs))])
#
#     # patient nr from filename, e.g. "001.mat"
#     transformations = set([filename[:3] for filename in transformations])
#     transformations = list(transformations - existing_pat_nrs)
#
# for transformation in tqdm(transformations):
#
#     transformation_dict = scipy.io.loadmat(transformation)
#     old_VOI = sitk.ReadImage(os.path.join("..", data_path, "Conf", "Pat_VOI_" + transformation[0:3] + ".nii"))
#     old_BG = sitk.ReadImage(os.path.join("..", data_path, "BG", "Pat_BG_" + transformation[0:3] + ".nii"))
#
#     centered_VOI = affine_transformation_pmod(old_VOI, transformation_dict)
#     centered_BG = affine_transformation_pmod(old_BG, transformation_dict)
#
#     VOI_filename = "centered_Pat_" + "VOI_" + transformation[0:3] + ".nii"
#     BG_filename = "centered_Pat_" + "BG_" + transformation[0:3] + ".nii"
#
#     sitk.WriteImage(centered_VOI, os.path.join("..", data_path, "Conf_centered", VOI_filename))
#     sitk.WriteImage(centered_BG, os.path.join("..", data_path, "BG_centered", BG_filename))



