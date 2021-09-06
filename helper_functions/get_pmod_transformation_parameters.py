import os
import SimpleITK as sitk
import scipy.io
from tqdm import tqdm
import glob
from helper_functions.nifti_functions import get_affine_transformation_parameters_pmod
from config import PET_dir, time_range, data_path

## not complete yet

os.chdir(os.path.join("..", data_path, "pmod_transformations"))
transformations = glob.glob("*.mat")

for transformation in transformations[:2]:
    print(transformation)
    transformation_dict = scipy.io.loadmat(transformation)
    get_affine_transformation_parameters(transformation_dict, show=True)


