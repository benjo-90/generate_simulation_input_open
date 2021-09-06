"""Rename PET scans, BGs and VOIs

ONLY USE IT IF FILES ARE NOT ALREADY IN THE FOLLOWING FORM:
"Pat_007.nii", "Pat_Act_007.nii", "Pat_BG_007.nii", "Pat_VOI_007.nii", ...

Extracts patient nr from between 1st and 2nd "_" in original filename
and renames PET scans for further processing

Uncomment only lines which are needed and comment them again after use to prevent unwanted renaming!
"""


import os
from config import data_path, PET_dir, time_range


if PET_dir[-3:] == "Act":
    suffix = "Act_"
else:
    suffix = ""

os.chdir(data_path)

# # Renaming PET scans
# os.chdir(os.path.join(PET_dir, time_range))
# for filename in os.listdir():
#     os.rename(filename, "Pat_" + suffix + filename.split("_")[1] + ".nii")
# os.chdir(os.path.join("..", ".."))
# print("PET scans successfully renamed.")
#
# # Renaming VOIs
# os.chdir(os.path.join("Conf"))
# for filename in os.listdir():
#     os.rename(filename, "Pat_" + "VOI_" + filename.split("_")[1] + ".nii")
# os.chdir(os.path.join(".."))
# print("VOIs successfully renamed.")
#
# # Renaming BGs
# os.chdir(os.path.join("BG"))
# for filename in os.listdir():
#     os.rename(filename, "Pat_" + "BG_" + filename.split("_")[1] + ".nii")
# print("BGs successfully renamed.")


