from config import data_path, PET_dir, time_range
import os
import SimpleITK as sitk


os.chdir(os.path.join(data_path, PET_dir, time_range + "_centered_test"))
print(os.getcwd())
print(os.listdir())

for file in os.listdir():
    image = sitk.ReadImage(file)
    sitk.WriteImage(image, file.split(".")[0] + ".nii")