import os
import numpy as np
import SimpleITK as sitk

from config import data_path, PET_dir, time_range


# os.chdir(os.path.join(data_path, PET_dir, time_range + "_tumor_masks"))
os.chdir(os.path.join(data_path, "Conf"))

print(os.getcwd())
minmaxfilter = sitk.MinimumMaximumImageFilter()
minmaxfilter.GetMaximum()

mask_file_list = os.listdir()

nr_of_vois = 0
i=0
for mask_file in mask_file_list:
    mask = sitk.ReadImage(mask_file)
    mask_np = sitk.GetArrayFromImage(mask)
    minmaxfilter.Execute(mask)
    print(int(minmaxfilter.GetMaximum()))
    nr_of_vois += minmaxfilter.GetMaximum()
    print(nr_of_vois)
    #
    # if (mask_np.max() != 1.0):
    #     print(mask_file)
    #     print(mask_np.shape)
    #     print(mask_np.max())
    #     print("\n")
    #     i += 1
    # for key in mask.GetMetaDataKeys():
        # print(f"{key} = {mask.GetMetaData(key)}")
