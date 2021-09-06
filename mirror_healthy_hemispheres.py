"""Mirror tumor-free brain hemisphere

Processes centered PET Scans and creates tumor-free PETs
with the help of centered VOIs (needed to figure out which hemisphere has to be mirrored)

Ignores patient nrs listed in not_for_brain.txt
"""


import SimpleITK as sitk
import numpy as np
import os
import glob
from tqdm import tqdm
from config import data_path, time_range, PET_dir

overwrite = False

if PET_dir[-3:] == "Act":
    suffix = "_Act"
else:
    suffix = ""

with open(os.path.join("not_for_brain.txt")) as file:
    excluded_brains = file.read().split("\n")
print("Number of brains to exclude:", len(excluded_brains))

os.chdir(data_path)

output_path = os.path.join(PET_dir, time_range + "_mirrored")

if not os.path.isdir(output_path):
    os.makedirs(output_path)

os.chdir(os.path.join(PET_dir, time_range + "_centered"))
suffix = time_range[-3:]

filenames = glob.glob("centered*")
# print(filenames)

valid_brains = []
for i in range(len(filenames)):
    if filenames[i].split(".")[0][-3:] not in excluded_brains:
        valid_brains.append(filenames[i])

print("Valid brains: ", valid_brains)
print("Total of", str(len(valid_brains)), "brains")

for filename in tqdm(valid_brains):
    output_filename = "mirrored" + filename[8:]

    # skip iteration if mirrored brain already exists
    if not overwrite and os.path.exists(os.path.join("..", "..", output_path, output_filename)):
        continue

    image = sitk.ReadImage(filename)
    tumor_VOI = sitk.ReadImage(os.path.join("..", "..", "Conf", "Pat_" + "VOI_" + filename.split(".")[0][-3:] + ".nii"))

    image_array = sitk.GetArrayFromImage(image)
    tumor_VOI_array = sitk.GetArrayFromImage(tumor_VOI)

    if np.sum(tumor_VOI_array[:, :, :64]) > np.sum(tumor_VOI_array[:, :, 64:]):
        # for z in range(image_array.shape[0]):
        #     for y in range(image_array.shape[1]):
        #         for x in range(64, 128):
        #             image_array[z, y, x] = image_array[z, y, 127-x]
        image_array[:, :, :64] = 0
    else:
        image_array[:, :, 64:] = 0

    image_array = image_array + np.flip(image_array, axis=2)
    mirrored = sitk.GetImageFromArray(image_array)
    mirrored.CopyInformation(image)

    if time_range[-3:] == "Act":
        # sitk.WriteImage(mirrored*1000, os.path.join("..", "..", output_path, output_filename))
        sitk.WriteImage(mirrored, os.path.join("..", "..", output_path, output_filename))
    else:
        sitk.WriteImage(mirrored, os.path.join("..", "..", output_path, output_filename))
