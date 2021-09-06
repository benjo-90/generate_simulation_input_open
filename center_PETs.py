"""Center PET scans with pmod transformation files

Uses .mat transformations from pmod in dir "pmod_transformations"
to center PET scans.

Needs fixing: still not extracting the same exact translation and rotation parameters from .mat file
"""


import os
import SimpleITK as sitk
import scipy.io
from tqdm import tqdm
from helper_functions.nifti_functions import affine_transformation_pmod
from config import PET_dir, time_range, data_path

overwrite = False

os.chdir(data_path)
if PET_dir[-3:] == "Act":
    suffix = "_Act"
else:
    suffix = ""
output_path = os.path.join(time_range + "_centered")

os.chdir(os.path.join(PET_dir))
if not os.path.isdir(output_path):
    os.makedirs(output_path)

os.chdir(time_range)
filenames = os.listdir()

for filename in tqdm(filenames):
    pat_nr = filename.split(".")[0][-3:]
    output_filename = "centered_Pat" + suffix + "_" + pat_nr + ".nii"

    if not overwrite and os.path.isfile(os.path.join("..", output_path, output_filename)):
        continue

    file_dir = os.path.dirname(__file__)
    transformation_dict = scipy.io.loadmat(os.path.join(file_dir, "pmod_transformations", pat_nr + ".mat"))
    image = sitk.ReadImage(filename)

    centered_image = affine_transformation_pmod(image, transformation_dict, interpolation="Linear")

    sitk.WriteImage(centered_image, os.path.join("..", output_path, output_filename))



