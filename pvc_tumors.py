"""Partial volume correction on centered tumors

Uses toolbox PETPVC from:
https://github.com/UCL/PETPVC
For Windows: go to "Releases", install "PETPVC-1.2.4-win.exe" and add "PETPVC/bin" to your path

Only tested with methods "GTM" and "RBV" (more on:
https://nipype.readthedocs.io/en/latest/api/generated/nipype.interfaces.petpvc.html#id3)

Output in "FET_20_40_tumors_pvc"
"""


import tkinter
from tkinter import filedialog
from tqdm import tqdm
import os
import glob
import subprocess
import SimpleITK as sitk
from config import data_path, PET_dir, time_range


overwrite = False

method = "GTM"
os.chdir(os.path.join(data_path, PET_dir))

if time_range[-3:] == "Act":
    suffix = "Act_"
else:
    suffix = ""

tumor_dir = time_range + "_tumors_multiple"
masks_path = time_range + "_tumor_masks_segments"

root = tkinter.Tk()
root.withdraw()
masks_dir = filedialog.askdirectory(parent=root, initialdir=masks_path, title='Tumor masks segments dir').rsplit("/", 1)[-1]

output_dir = os.path.join(time_range + "_tumors_pvc", masks_dir + "_" + method)
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

if method == "GTM":
    file_reader = sitk.ImageFileReader()
    CastFil = sitk.CastImageFilter()
    CastFil.SetOutputPixelType(sitk.sitkFloat32)
    means_dir = os.path.join(output_dir, "means")
    if not os.path.isdir(means_dir):
        os.makedirs(means_dir)

os.chdir(os.path.join(masks_path, masks_dir))
masks_4d_filenames = glob.glob("tumor_mask*")
print(masks_4d_filenames)
# masks_4d_filenames = ["masks_Pat_004.nii"]
os.chdir(os.path.join("..", ".."))

for masks_4d_filename in tqdm(masks_4d_filenames):
    output_name = os.path.join(output_dir, "centered_tumor_" + suffix + masks_4d_filename.split(".")[0].split("_")[-1] + "_" + method + ".nii")

    if not overwrite and os.path.isfile(output_name):
        continue

    i_cmd = os.path.join(tumor_dir, "centered_tumor_" + suffix + masks_4d_filename.split("_")[-1])
    m_cmd = os.path.join(masks_path, masks_dir, masks_4d_filename)

    if method == "GTM":
        means_filename = "centered_tumor_" + suffix + masks_4d_filename.split(".")[0].split("_")[-1] + "_" + "gtm_means" + ".txt"
        print(means_filename)
        o_cmd = os.path.join(means_dir, means_filename)
    else:
        o_cmd = output_name
    x = "2.03499"
    y = "2.03499"
    z = "2.425"

    cmd = 'petpvc -i "' + i_cmd + '" -m "' + m_cmd + '" -o "' + o_cmd + '" --pvc ' + method
    cmd += ' -x ' + x + ' -y ' + y + ' -z ' + z
    print(cmd)
    subprocess.call(cmd, shell=True)

    if method == "GTM":
        try:
            with open(os.path.join(means_dir, means_filename)) as file:
                gtm_means = file.read().split("\t")
                print(gtm_means)
                gtm_means = gtm_means[2:]
                for i in range(len(gtm_means)):
                     gtm_means[i] = float(gtm_means[i][:-3])

                file_reader.SetFileName(os.path.join(masks_path, masks_dir, masks_4d_filename))
                file_reader.SetExtractSize([128, 128, 63, 0])
                file_reader.SetOutputPixelType(sitk.sitkFloat32)
                for index, mean in enumerate(gtm_means):
                    file_reader.SetExtractIndex([0, 0, 0, index])
                    if index == 0:
                        image_from_masks = file_reader.Execute() * 0
                    else:
                        image_from_masks += file_reader.Execute() * mean

                sitk.WriteImage(image_from_masks, output_name)
        except ValueError:
            continue

